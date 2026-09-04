""" Simple pandas queries over the flattened IATI activities/transactions CSV.

Field names and codes (activity_status, transaction_type) come from the IATI
standard codelists, so these queries work for any IATI activities XML, not
just the bundled sample - see data.py.

Each query passes `xml_source()` as the source; the raw table data is
embedded into the AI-facing text by `h.text_result` (see helpers/format.py).
"""
import difflib
import unicodedata

import pandas as pd

from mcp_iati import helpers as h
from mcp_iati.activities.country_aliases import country_code_for_name
from mcp_iati.activities.data import (
    activities_df,
    activity_dates_df,
    participating_orgs_df,
    sectors_df,
    transactions_df,
    xml_source,
)


_TRANSACTION_TYPE_FILTERS = {
    "2": "2",
    "commitment": "2",
    "out commitment": "2",
    "3": "3",
    "disbursement": "3",
}


def _transaction_type_code(value: str) -> str | None:
    """Normalize a supported analytical transaction-type filter."""
    return _TRANSACTION_TYPE_FILTERS.get(str(value).strip().casefold())


def _fold_text(value) -> str:
    """Casefold and strip diacritics for accent-insensitive matching.

    Published IATI names are inconsistent about accents (and chat models
    tend to restore them when quoting names back), so matching ignores
    them while responses keep the names exactly as published.
    """
    normalized = unicodedata.normalize("NFKD", str(value))
    return "".join(
        char
        for char in normalized
        if not unicodedata.combining(char)
    ).casefold()


def _folded(series: pd.Series) -> pd.Series:
    """Return a Series folded with `_fold_text` for matching."""
    return (
        series.fillna("")
        .astype(str)
        .map(_fold_text)
    )


def _named_sectors(sectors: pd.DataFrame) -> pd.DataFrame:
    """Normalize sector columns and fill missing DAC sector names.

    Publishers using the OECD DAC vocabulary (vocabulary 1) often omit the
    sector name because the code is enough; the standard name is restored
    from the DAC codelist so name-based search and display keep working.
    """
    sectors = sectors.copy()
    for column in (
        "activity_identifier",
        "sector_code",
        "sector_name",
        "vocabulary",
    ):
        sectors[column] = (
            sectors[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )
    missing_name = (
        (sectors["sector_name"] == "")
        & (sectors["vocabulary"] == "1")
    )
    sectors.loc[missing_name, "sector_name"] = sectors.loc[
        missing_name,
        "sector_code",
    ].map(h.dac_sector_name)
    return sectors


# Charts: at most this many per response, so a file with many currencies or
# sector vocabularies does not flood the chat (each chart is a collapsed
# message in the gateway).
MAX_CHARTS = 3

# Bars/slices drawn before folding the rest into "Other".
CHART_TOP_N = h.charts.DEFAULT_TOP_N


def _currency_label(currency) -> str:
    text = str(currency).strip() if currency is not None and str(currency) != "nan" else ""
    return text or "unknown currency"


def _year_totals_charts(grouped: pd.DataFrame) -> list[dict]:
    """One grouped bar chart per currency: commitment vs disbursement by year.

    ``grouped`` has one row per (year, transaction_type, currency) with the
    summed ``value``. Currencies are never mixed in one chart.
    """
    charts = []
    for currency, group in grouped.groupby("currency", sort=True, dropna=False):
        if len(group) < 2:
            continue
        years = sorted(int(year) for year in group["year"].unique())
        pivot = group.pivot_table(
            index="year",
            columns="transaction_type",
            values="value",
            aggfunc="sum",
        ).reindex(years)
        series = [
            (h.transaction_type_label(code), pivot[code].tolist())
            for code in sorted(pivot.columns)
        ]
        charts.append(h.charts.bar_chart(
            f"Commitments and disbursements by year ({_currency_label(currency)})",
            years,
            series,
        ))
    return charts[:MAX_CHARTS]


def _sector_totals_charts(grouped: pd.DataFrame, transaction_type_code: str) -> list[dict]:
    """One pie per (vocabulary, currency): share of the amount by sector.

    Uses the full grouping (not the limited rows) so the "Other" slice is
    the true remainder. Vocabularies are never mixed: the same activity is
    allocated once per vocabulary, so mixing them would double count.
    """
    charts = []
    type_label = h.transaction_type_label(transaction_type_code)
    for (vocabulary, currency), group in grouped.groupby(
        ["vocabulary", "currency"],
        sort=True,
        dropna=False,
    ):
        names = group["sector_name"].where(
            group["sector_name"] != "",
            group["sector_code"],
        )
        slices = h.charts.top_n_with_other(
            zip(
                (h.charts.short_label(name, 50) for name in names),
                group["allocated_value"],
            ),
            top_n=CHART_TOP_N,
            other_label="Other sectors",
        )
        if len(slices) < 2:
            continue
        charts.append(h.charts.pie_chart(
            f"{type_label} by sector: {h.charts.vocabulary_label(vocabulary)} "
            f"({_currency_label(currency)})",
            slices,
        ))
    return charts[:MAX_CHARTS]


def _sector_count_charts(shown: pd.DataFrame) -> list[dict]:
    """One bar chart per vocabulary: activities per sector (top N shown)."""
    charts = []
    for vocabulary, group in shown.groupby("vocabulary", sort=True, dropna=False):
        top = group.head(CHART_TOP_N)
        if len(top) < 2:
            continue
        charts.append(h.charts.bar_chart(
            f"Activities by sector: {h.charts.vocabulary_label(vocabulary)} (top {len(top)})",
            [h.charts.short_label(name) for name in top["display_name"]],
            [("Activities", top["activities"].tolist())],
        ))
    return charts[:MAX_CHARTS]


def _participating_org_charts(shown: pd.DataFrame) -> list[dict]:
    """Bar chart of the organisations with most activities.

    The reporting organisation participates in its own activities by
    definition (in the IADB files it is also listed under a second name for
    its capital window), which flattens every other bar; it is left out of
    the chart, never out of the table.
    """
    reporting_refs = set(
        activities_df()["reporting_org_ref"]
        .fillna("")
        .astype(str)
        .str.strip()
    ) - {""}
    top = shown[~shown["org_ref"].isin(reporting_refs)].head(CHART_TOP_N)
    if len(top) < 2:
        return []
    suffix = ", excluding the reporting organisation" if reporting_refs else ""
    return [h.charts.bar_chart(
        f"Participating organisations by number of activities (top {len(top)}{suffix})",
        [h.charts.short_label(name) for name in top["display_name"]],
        [("Activities", top["activities"].tolist())],
    )]


def _top_activity_charts(grouped: pd.DataFrame, transaction_type_code: str) -> list[dict]:
    """One bar chart per currency with the largest activities by amount."""
    charts = []
    type_label = h.transaction_type_label(transaction_type_code)
    for currency, group in grouped.groupby("currency", sort=True, dropna=False):
        top = group.head(CHART_TOP_N)
        if len(top) < 2:
            continue
        labels = [
            h.charts.short_label(title if str(title).strip() else identifier, 35)
            for title, identifier in zip(top["title"], top["activity_identifier"])
        ]
        charts.append(h.charts.bar_chart(
            f"Largest activities by {type_label.lower()} ({_currency_label(currency)})",
            labels,
            [(type_label, top["value"].tolist())],
        ))
    return charts[:MAX_CHARTS]


def _activity_transaction_charts(shown: pd.DataFrame, iati_identifier: str) -> list[dict]:
    """Cumulative amount per transaction type over time, one line chart per currency."""
    frame = shown[["transaction_date", "transaction_type", "value", "currency"]].copy()
    frame["date"] = pd.to_datetime(frame["transaction_date"], errors="coerce", format="mixed")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame["currency"] = frame["currency"].fillna("").astype(str).str.strip()
    frame["transaction_type"] = frame["transaction_type"].fillna("").astype(str).str.strip()
    frame = frame[frame["date"].notna() & frame["value"].notna()]
    charts = []
    for currency, group in frame.groupby("currency", sort=True):
        if len(group) < 3:
            continue
        dates = sorted(group["date"].unique())
        series = []
        for code, by_type in group.groupby("transaction_type", sort=True):
            per_date = by_type.groupby("date")["value"].sum().reindex(dates, fill_value=0.0)
            series.append((h.transaction_type_label(code), per_date.cumsum().tolist()))
        charts.append(h.charts.line_chart(
            f"Cumulative transactions of {iati_identifier} ({_currency_label(currency)})",
            [pd.Timestamp(date).strftime("%Y-%m-%d") for date in dates],
            series,
        ))
    return charts[:MAX_CHARTS]


def file_overview():
    """Return a general overview of the configured IATI data."""
    tool_name = "file_overview"
    activities = activities_df().copy()
    transactions = transactions_df().copy()

    if activities.empty:
        return h.empty_result(
            "No activities were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    activities["activity_identifier"] = (
        activities["activity_identifier"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    total_activities = activities[
        "activity_identifier"
    ].replace("", pd.NA).nunique()

    rows = [
        {
            "category": "File",
            "value": "Activities",
            "count": total_activities,
            "currency": "",
            "amount": "",
        }
    ]

    # Reporting organisations.
    activities["reporting_org_name"] = (
        activities["reporting_org_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    activities["reporting_org_ref"] = (
        activities["reporting_org_ref"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    activities["display_org"] = activities["reporting_org_name"].where(
        activities["reporting_org_name"] != "",
        activities["reporting_org_ref"],
    )
    activities["display_org"] = activities["display_org"].where(
        activities["display_org"] != "",
        "Unknown reporting organisation",
    )

    organisation_counts = (
        activities.groupby("display_org", dropna=False)[
            "activity_identifier"
        ]
        .nunique()
        .sort_index()
    )

    for organisation, count in organisation_counts.items():
        rows.append(
            {
                "category": "Reporting organisation",
                "value": organisation,
                "count": int(count),
                "currency": "",
                "amount": "",
            }
        )

    # Recipient countries.
    activities["recipient_country_name"] = (
        activities["recipient_country_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    activities["recipient_country_code"] = (
        activities["recipient_country_code"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    activities["display_country"] = activities[
        "recipient_country_name"
    ].where(
        activities["recipient_country_name"] != "",
        activities["recipient_country_code"],
    )
    activities["display_country"] = activities["display_country"].where(
        activities["display_country"] != "",
        "Unknown",
    )

    country_counts = (
        activities.groupby("display_country", dropna=False)[
            "activity_identifier"
        ]
        .nunique()
        .sort_index()
    )

    for country, count in country_counts.items():
        rows.append(
            {
                "category": "Recipient country",
                "value": country,
                "count": int(count),
                "currency": "",
                "amount": "",
            }
        )

    # Default currencies declared by activities.
    activities["default_currency"] = (
        activities["default_currency"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    currency_counts = (
        activities.loc[
            activities["default_currency"] != "",
            "default_currency",
        ]
        .value_counts()
        .sort_index()
    )

    for currency_code, count in currency_counts.items():
        rows.append(
            {
                "category": "Default currency",
                "value": currency_code,
                "count": int(count),
                "currency": currency_code,
                "amount": "",
            }
        )

    # Financial totals, kept separate by transaction type and currency.
    if not transactions.empty:
        transactions["transaction_type"] = (
            transactions["transaction_type"]
            .fillna("")
            .astype(str)
            .str.strip()
        )
        transactions["currency"] = (
            transactions["currency"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )
        transactions["value"] = pd.to_numeric(
            transactions["value"],
            errors="coerce",
        )

        default_currencies = activities[
            ["activity_identifier", "default_currency"]
        ].drop_duplicates(subset=["activity_identifier"])

        transactions = transactions.merge(
            default_currencies,
            on="activity_identifier",
            how="left",
        )
        transactions["default_currency"] = (
            transactions["default_currency"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.upper()
        )
        transactions["currency"] = transactions["currency"].where(
            transactions["currency"] != "",
            transactions["default_currency"],
        )
        transactions["currency"] = transactions["currency"].where(
            transactions["currency"] != "",
            "Unknown",
        )

        transaction_totals = (
            transactions.loc[
                transactions["value"].notna()
                & (transactions["transaction_type"] != "")
            ]
            .groupby(
                ["transaction_type", "currency"],
                dropna=False,
            )["value"]
            .agg(["count", "sum"])
            .reset_index()
        )
        transaction_totals["type_label"] = transaction_totals[
            "transaction_type"
        ].map(h.transaction_type_label)
        transaction_totals = transaction_totals.sort_values(
            ["type_label", "currency"],
            kind="mergesort",
        )

        for _, transaction in transaction_totals.iterrows():
            rows.append(
                {
                    "category": "Transaction total",
                    "value": transaction["type_label"],
                    "count": int(transaction["count"]),
                    "currency": transaction["currency"],
                    "amount": h.format_amount(transaction["sum"]),
                }
            )

    table = h.build_table(
        rows,
        [
            ("category", "Category"),
            ("value", "Value"),
            ("count", "Count"),
            ("currency", "Currency"),
            ("amount", "Amount"),
        ],
    )

    summary = (
        f"Found {total_activities} IATI activities, "
        f"{len(organisation_counts)} reporting organisation(s), "
        f"{len(country_counts)} recipient country value(s) and "
        f"{len(currency_counts)} default currency value(s). "
        "Financial totals are reported separately by transaction type "
        "and currency."
    )

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=len(rows),
        shown=len(rows),
    )


def date_coverage(date_kind: str = "all"):
    """Return activity and transaction date coverage."""
    tool_name = "date_coverage"
    selected_kind = str(date_kind).strip().casefold()

    if selected_kind not in {"activities", "transactions", "all"}:
        return h.empty_result(
            "Unsupported date kind. Use activities, transactions or all.",
            source_url=xml_source(),
        )

    rows = []

    def column_series(dataframe, column: str) -> pd.Series:
        if column in dataframe.columns:
            return (
                dataframe[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )
        return pd.Series(
            "",
            index=dataframe.index,
            dtype="string",
        )

    def add_date_row(
        raw_dates: pd.Series,
        dataset: str,
        date_type: str,
    ):
        has_value = raw_dates != ""
        parsed_dates = pd.to_datetime(
            raw_dates.where(has_value),
            errors="coerce",
            format="mixed",
            utc=True,
        )

        valid_dates = has_value & parsed_dates.notna()
        invalid_dates = has_value & parsed_dates.isna()

        earliest = ""
        latest = ""

        if valid_dates.any():
            earliest = (
                parsed_dates.loc[valid_dates]
                .min()
                .strftime("%Y-%m-%d")
            )
            latest = (
                parsed_dates.loc[valid_dates]
                .max()
                .strftime("%Y-%m-%d")
            )

        rows.append(
            {
                "dataset": dataset,
                "date_type": date_type,
                "earliest": earliest,
                "latest": latest,
                "records_with_date": int(valid_dates.sum()),
                "missing_dates": int((~has_value).sum()),
                "invalid_dates": int(invalid_dates.sum()),
            }
        )

    if selected_kind in {"activities", "all"}:
        activities = activities_df()
        # Some publishers report dates only as activity-date elements,
        # leaving the activities.csv date columns empty.
        fallback_dates = _activity_date_fallback()
        activity_ids = column_series(
            activities,
            "activity_identifier",
        )

        activity_date_columns = [
            ("Planned start", "planned_start_date", "1"),
            ("Actual start", "actual_start_date", "2"),
            ("Planned end", "planned_end_date", "3"),
            ("Actual end", "actual_end_date", "4"),
        ]

        for date_type, column, type_code in activity_date_columns:
            raw_dates = column_series(activities, column)
            fallback = fallback_dates.get(type_code)
            if fallback:
                mapped = activity_ids.map(fallback).fillna("")
                raw_dates = raw_dates.where(
                    raw_dates != "",
                    mapped,
                )
            add_date_row(
                raw_dates,
                "Activities",
                date_type,
            )

    if selected_kind in {"transactions", "all"}:
        transactions = transactions_df()
        add_date_row(
            column_series(transactions, "transaction_date"),
            "Transactions",
            "Transaction date",
        )

    table = h.build_table(
        rows,
        [
            ("dataset", "Dataset"),
            ("date_type", "Date type"),
            ("earliest", "Earliest date"),
            ("latest", "Latest date"),
            ("records_with_date", "Records with date"),
            ("missing_dates", "Missing dates"),
            ("invalid_dates", "Invalid dates"),
        ],
    )

    earliest_dates = [
        row["earliest"]
        for row in rows
        if row["earliest"]
    ]
    latest_dates = [
        row["latest"]
        for row in rows
        if row["latest"]
    ]

    if earliest_dates and latest_dates:
        summary = (
            f"Date coverage runs from {min(earliest_dates)} "
            f"to {max(latest_dates)}. Missing and invalid dates "
            "are reported separately for each date type."
        )
    else:
        summary = (
            "No valid dates were found for the selected date coverage. "
            "Missing and invalid dates are reported in the table."
        )

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=len(rows),
        shown=len(rows),
        filters={"date_kind": selected_kind},
    )


def list_category_values(
    category: str,
    limit: int = 100,
):
    """List values and counts for a supported categorical IATI field."""
    tool_name = "list_category_values"
    selected_category = str(category).strip().casefold()

    if limit < 1:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    category_specs = {
        "activity_status": {
            "label": "Activity status",
            "dataframe": activities_df,
            "column": "activity_status",
        },
        "transaction_type": {
            "label": "Transaction type",
            "dataframe": transactions_df,
            "column": "transaction_type",
        },
        "sector": {
            "label": "Sector",
            "dataframe": lambda: _named_sectors(sectors_df()),
            "column": "sector_code",
            "value_column": "sector_name",
            "vocabulary_column": "vocabulary",
        },
        "organisation_type": {
            "label": "Organisation type",
            "dataframe": activities_df,
            "column": "reporting_org_type",
        },
        "aid_type": {
            "label": "Aid type",
            "dataframe": activities_df,
            "column": "default_aid_type",
            "vocabulary_column": "default_aid_type_vocabulary",
        },
        "finance_type": {
            "label": "Finance type",
            "dataframe": activities_df,
            "column": "default_finance_type",
        },
        "flow_type": {
            "label": "Flow type",
            "dataframe": activities_df,
            "column": "default_flow_type",
        },
        "tied_status": {
            "label": "Tied status",
            "dataframe": activities_df,
            "column": "default_tied_status",
        },
        "collaboration_type": {
            "label": "Collaboration type",
            "dataframe": activities_df,
            "column": "collaboration_type",
        },
        "humanitarian": {
            "label": "Humanitarian",
            "dataframe": activities_df,
            "column": "humanitarian",
        },
        "default_currency": {
            "label": "Default currency",
            "dataframe": activities_df,
            "column": "default_currency",
        },
    }

    spec = category_specs.get(selected_category)
    if spec is None:
        supported = ", ".join(sorted(category_specs))
        return h.empty_result(
            f"Unsupported category. Use one of: {supported}.",
            source_url=xml_source(),
        )

    dataframe = spec["dataframe"]()
    code_column = spec["column"]

    if code_column not in dataframe.columns:
        return h.empty_result(
            f"Category '{selected_category}' is not available "
            "in the loaded IATI data.",
            source_url=xml_source(),
        )

    working = pd.DataFrame({
        "code": (
            dataframe[code_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )
    })

    value_column = spec.get("value_column")
    if value_column and value_column in dataframe.columns:
        explicit_values = (
            dataframe[value_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )
    else:
        explicit_values = pd.Series(
            "",
            index=dataframe.index,
            dtype="string",
        )

    vocabulary_column = spec.get("vocabulary_column")
    if vocabulary_column and vocabulary_column in dataframe.columns:
        working["vocabulary"] = (
            dataframe[vocabulary_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )
    else:
        working["vocabulary"] = ""

    working = working[working["code"] != ""].copy()

    if working.empty:
        return h.empty_result(
            f"No values were found for category "
            f"'{selected_category}'.",
            source_url=xml_source(),
        )

    formatted_values = working["code"].map(
        lambda value: h.category_value_label(
            selected_category,
            value,
        )
    )
    explicit_values = explicit_values.loc[working.index]

    working["value"] = explicit_values.where(
        explicit_values != "",
        formatted_values,
    )

    # AidType labels only apply to vocabulary 1 (OECD DAC).
    if selected_category == "aid_type":
        non_dac = ~working["vocabulary"].isin(["", "1"])
        working.loc[non_dac, "value"] = working.loc[
            non_dac,
            "code",
        ]

    counts = (
        working.groupby(
            ["code", "value", "vocabulary"],
            dropna=False,
        )
        .size()
        .reset_index(name="records")
    )
    counts["category"] = spec["label"]

    counts = counts.sort_values(
        ["records", "value", "code"],
        ascending=[False, True, True],
        kind="mergesort",
    )

    total = len(counts)
    shown = counts.head(limit)

    rows = shown[
        [
            "category",
            "code",
            "value",
            "vocabulary",
            "records",
        ]
    ].to_dict("records")

    table = h.build_table(
        rows,
        [
            ("category", "Category"),
            ("code", "Code"),
            ("value", "Value"),
            ("vocabulary", "Vocabulary"),
            ("records", "Records"),
        ],
    )

    summary = (
        f"Found {total} value(s) for category "
        f"'{selected_category}'."
    )

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total,
        shown=len(rows),
        filters={"category": selected_category},
        limit=limit,
    )


def search_activities(text: str, limit: int = 10):
    """Search IATI activities by text in their title, description, sectors
    or participating organisation names."""
    tool_name = "search_activities"

    search_text = str(text).strip()

    if not search_text:
        return h.empty_result(
            "A search text is required.",
            source_url=xml_source(),
        )

    if limit <= 0:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    needle = _fold_text(search_text)

    def _contains(series: pd.Series) -> pd.Series:
        return _folded(series).str.contains(needle, regex=False)

    activities = (
        activities_df()
        .drop_duplicates(subset=["activity_identifier"])
        .copy()
    )

    title_match = _contains(activities["title"])

    # The description column is optional: okfn_iati emits it for IATI 2.x
    # files, but tools must keep working with any activities CSV.
    if "description" in activities.columns:
        description_match = _contains(activities["description"])
    else:
        description_match = pd.Series(False, index=activities.index)

    sectors = _named_sectors(sectors_df())
    sector_hits = sectors[_contains(sectors["sector_name"])]
    sector_names = (
        sector_hits.groupby("activity_identifier")["sector_name"]
        .apply(
            lambda names: ", ".join(
                sorted({name for name in names if name})
            )
        )
        .to_dict()
    )

    orgs = participating_orgs_df()
    org_hits = orgs[_contains(orgs["org_name"])].copy()
    org_hits["activity_identifier"] = (
        org_hits["activity_identifier"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    org_hits["org_name"] = (
        org_hits["org_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    org_names = (
        org_hits.groupby("activity_identifier")["org_name"]
        .apply(
            lambda names: ", ".join(
                sorted({name for name in names if name})
            )
        )
        .to_dict()
    )

    matched_in = []
    for title_hit, description_hit, identifier in zip(
        title_match,
        description_match,
        activities["activity_identifier"],
    ):
        fields = []
        if title_hit:
            fields.append("title")
        if description_hit:
            fields.append("description")
        matched_sectors = sector_names.get(identifier)
        if matched_sectors:
            fields.append(f"sector ({matched_sectors})")
        matched_orgs = org_names.get(identifier)
        if matched_orgs:
            fields.append(f"participating org ({matched_orgs})")
        matched_in.append(", ".join(fields))
    activities["matched_in"] = matched_in

    all_matches = activities[activities["matched_in"] != ""]

    total = len(all_matches)
    matches = all_matches.head(limit)
    shown = len(matches)

    if matches.empty:
        return h.empty_result(
            f"No IATI activities found with '{search_text}' in their "
            "title, description, sectors or participating "
            "organisations.",
            source_url=xml_source(),
        )

    rows = matches[
        [
            "activity_identifier",
            "title",
            "activity_status",
            "matched_in",
        ]
    ].copy()

    table = h.build_table(
        rows.to_dict("records"),
        [
            ("activity_identifier", "IATI identifier"),
            ("title", "Title"),
            ("activity_status", "Status"),
            ("matched_in", "Matched in"),
        ],
        formatters={
            "activity_status": h.activity_status_label,
        },
    )

    summary = (
        f"Found {total} IATI activity(ies) matching '{search_text}' "
        "in their title, description, sectors or participating "
        "organisations."
    )

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total,
        shown=shown,
        filters={"text_contains": search_text},
        limit=limit,
    )


def list_activity_statuses():
    """List the activity statuses present in the configured IATI data."""
    tool_name = "list_activity_statuses"
    activities = activities_df()

    counts = (
        activities["activity_status"]
        .dropna()
        .astype(str)
        .value_counts()
        .sort_index()
    )

    if counts.empty:
        return h.empty_result(
            "No activity statuses were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    rows = [
        {
            "code": code,
            "status": h.activity_status_label(code),
            "activities": int(count),
        }
        for code, count in counts.items()
    ]

    table = h.build_table(
        rows,
        [
            ("code", "Status code"),
            ("status", "Activity status"),
            ("activities", "Activities"),
        ],
    )

    summary = (
        f"Found {len(rows)} activity status value(s) "
        f"across {sum(counts)} activities."
    )

    charts = []
    if len(rows) >= 2:
        charts.append(h.charts.pie_chart(
            "Activities by status",
            [(row["status"], row["activities"]) for row in rows],
        ))

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=len(rows),
        shown=len(rows),
        charts=charts,
    )


def _clean_cell(value) -> str:
    """Return a stripped string for a cell, mapping NaN/None to ""."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    return "" if text.casefold() == "nan" else text


def _activity_sector_labels(iati_identifier: str) -> list[str]:
    """Return display labels for the sectors of one activity."""
    sectors = _named_sectors(sectors_df())
    activity_sectors = sectors[
        sectors["activity_identifier"] == iati_identifier
    ]

    labels = []
    for _, sector in activity_sectors.iterrows():
        name = sector["sector_name"]
        code = sector["sector_code"]
        if name and code:
            label = f"{name} ({code})"
        else:
            label = name or code
        if not label:
            continue
        percentage = sector["percentage"]
        if pd.notna(percentage):
            label += f", {float(percentage):g}%"
        if label not in labels:
            labels.append(label)
    return labels


def _activity_date_fallback() -> dict[str, dict[str, str]]:
    """Map date-type codes to {activity_identifier: iso_date} lookups.

    Built from the optional activity-date elements table; the first
    non-empty date wins for each activity and date type.
    """
    dates = activity_dates_df()
    lookup: dict[str, dict[str, str]] = {}
    for _, date_row in dates.iterrows():
        identifier = _clean_cell(date_row.get("activity_identifier"))
        type_code = _clean_cell(date_row.get("type"))
        iso_date = _clean_cell(date_row.get("iso_date"))
        if not identifier or not type_code or not iso_date:
            continue
        lookup.setdefault(type_code, {}).setdefault(
            identifier,
            iso_date,
        )
    return lookup


def _activity_date_parts(iati_identifier: str) -> list[str]:
    """Return date labels from activity-date elements for one activity.

    Fallback for publishers that report dates only as activity-date
    elements, leaving the activities.csv date columns empty.
    """
    dates = activity_dates_df()
    date_ids = (
        dates["activity_identifier"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    dates = dates[date_ids == iati_identifier]

    keyed_parts = []
    for _, date_row in dates.iterrows():
        iso_date = _clean_cell(date_row.get("iso_date"))
        if not iso_date:
            continue
        type_code = _clean_cell(date_row.get("type"))
        label = h.activity_date_type_label(type_code)
        entry = (type_code, f"{label}: {iso_date}")
        if entry not in keyed_parts:
            keyed_parts.append(entry)
    # Codelist order: planned start, actual start, planned end, actual end.
    return [part for _, part in sorted(keyed_parts)]


def _participating_org_lines(iati_identifier: str) -> list[str]:
    """Return display lines for the participating organisations of one activity."""
    orgs = participating_orgs_df()
    org_ids = (
        orgs["activity_identifier"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    orgs = orgs[org_ids == iati_identifier]

    lines = []
    for _, org in orgs.iterrows():
        name = (
            _clean_cell(org.get("org_name"))
            or _clean_cell(org.get("org_ref"))
            or "Unknown organisation"
        )
        details = []
        role = _clean_cell(org.get("role"))
        if role:
            details.append(
                f"role: {h.organisation_role_label(role)}"
            )
        org_type = _clean_cell(org.get("org_type"))
        if org_type:
            details.append(
                "type: "
                + h.category_value_label(
                    "organisation_type",
                    org_type,
                )
            )
        line = f"  - {name}"
        if details:
            line += f" ({', '.join(details)})"
        if line not in lines:
            lines.append(line)
    return lines


def activity_summary(iati_identifier: str):
    """Return the main details and financial totals for one IATI activity."""
    tool_name = "activity_summary"
    iati_identifier = str(iati_identifier).strip()
    activities = activities_df()
    activity = activities[activities["activity_identifier"] == iati_identifier]

    if activity.empty:
        return h.empty_result(
            f"No IATI activity found with identifier '{iati_identifier}'.",
            source_url=xml_source(),
        )

    row = activity.iloc[0]

    def field(name: str) -> str:
        return _clean_cell(row.get(name))

    status_label = h.activity_status_label(row["activity_status"])

    txns = transactions_df()
    txns = txns[txns["activity_identifier"] == iati_identifier]
    totals = txns.groupby("transaction_type")["value"].sum()
    currency = row.get("default_currency") or ""

    # The text carries only the header; the per-type totals travel in the
    # table, which `text_result` embeds in full into the AI-facing text.
    lines = [
        f"{row['title']} ({iati_identifier})",
        f"Status: {status_label}",
        f"Reporting organisation: {row.get('reporting_org_name') or row.get('reporting_org_ref')}",
    ]

    description = field("description")
    if description:
        lines.append(f"Description: {description}")

    recipient = (
        field("recipient_country_name")
        or field("recipient_country_code")
    )
    if recipient:
        lines.append(f"Recipient country: {recipient}")

    date_parts = [
        f"{label}: {field(column)}"
        for label, column in [
            ("planned start", "planned_start_date"),
            ("actual start", "actual_start_date"),
            ("planned end", "planned_end_date"),
            ("actual end", "actual_end_date"),
        ]
        if field(column)
    ]
    if not date_parts:
        date_parts = _activity_date_parts(iati_identifier)
    if date_parts:
        lines.append("Dates: " + "; ".join(date_parts))

    sector_labels = _activity_sector_labels(iati_identifier)
    if sector_labels:
        lines.append("Sectors: " + "; ".join(sector_labels))

    # AidType labels only apply to vocabulary 1 (OECD DAC), like in
    # list_category_values.
    aid_vocabulary = field("default_aid_type_vocabulary")
    classification_parts = []
    for label, column, category in [
        ("Collaboration type", "collaboration_type", "collaboration_type"),
        ("Default flow type", "default_flow_type", "flow_type"),
        ("Default finance type", "default_finance_type", "finance_type"),
        ("Default aid type", "default_aid_type", "aid_type"),
        ("Default tied status", "default_tied_status", "tied_status"),
    ]:
        value = field(column)
        if not value:
            continue
        if category == "aid_type" and aid_vocabulary not in ("", "1"):
            display = value
        else:
            display = h.category_value_label(category, value)
        classification_parts.append(f"{label}: {display}")
    if classification_parts:
        lines.append("; ".join(classification_parts))

    org_lines = _participating_org_lines(iati_identifier)
    if org_lines:
        lines.append("Participating organisations:")
        lines.extend(org_lines)

    table = [["Transaction type", "Total", "Currency"]]
    for code, total in totals.items():
        table.append([h.transaction_type_label(code), h.format_amount(total), currency])

    return h.text_result(
        "\n".join(lines),
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=1,
        shown=1,
        filters={"iati_identifier": iati_identifier},
    )


def list_reporting_organisations():
    """List reporting organisations present in the configured IATI data."""
    tool_name = "list_reporting_organisations"
    activities = activities_df()

    organisations = activities[
        [
            "activity_identifier",
            "reporting_org_ref",
            "reporting_org_name",
        ]
    ].copy()

    # pandas represents empty CSV cells as NaN. Normalize them before
    # grouping so they never appear as "nan" in tool responses.
    organisations["reporting_org_ref"] = (
        organisations["reporting_org_ref"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    organisations["reporting_org_name"] = (
        organisations["reporting_org_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    organisations["display_name"] = organisations[
        "reporting_org_name"
    ].where(
        organisations["reporting_org_name"] != "",
        organisations["reporting_org_ref"],
    )

    organisations = organisations[
        organisations["display_name"] != ""
    ]

    if organisations.empty:
        return h.empty_result(
            "No reporting organisations were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    counts = (
        organisations.groupby(
            ["reporting_org_ref", "display_name"],
            dropna=False,
        )["activity_identifier"]
        .nunique()
        .reset_index(name="activities")
        .sort_values(
            ["activities", "display_name"],
            ascending=[False, True],
        )
    )

    rows = counts.to_dict("records")

    table = h.build_table(
        rows,
        [
            ("reporting_org_ref", "Organisation reference"),
            ("display_name", "Reporting organisation"),
            ("activities", "Activities"),
        ],
    )

    summary = (
        f"Found {len(rows)} reporting organisation(s) "
        f"across {len(organisations)} activities."
    )

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=len(rows),
        shown=len(rows),
    )


def list_participating_organisations(limit: int = 300):
    """List participating organisations present in the configured IATI data."""
    tool_name = "list_participating_organisations"

    if limit < 1:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    organisations = participating_orgs_df().copy()

    for column in (
        "activity_identifier",
        "org_ref",
        "org_name",
        "role",
    ):
        organisations[column] = (
            organisations[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    organisations["display_name"] = organisations["org_name"].where(
        organisations["org_name"] != "",
        organisations["org_ref"],
    )
    organisations = organisations[
        organisations["display_name"] != ""
    ]

    if organisations.empty:
        return h.empty_result(
            "No participating organisations were found in the loaded "
            "IATI data.",
            source_url=xml_source(),
        )

    organisations["role_label"] = organisations["role"].map(
        h.organisation_role_label
    )

    grouped = (
        organisations.groupby(
            ["org_ref", "display_name"],
            dropna=False,
        )
        .agg(
            activities=("activity_identifier", "nunique"),
            roles=(
                "role_label",
                lambda labels: ", ".join(
                    sorted({label for label in labels if label})
                ),
            ),
        )
        .reset_index()
        .sort_values(
            ["activities", "display_name"],
            ascending=[False, True],
            kind="mergesort",
        )
    )

    total = len(grouped)
    shown = grouped.head(limit)

    table = h.build_table(
        shown.to_dict("records"),
        [
            ("org_ref", "Organisation reference"),
            ("display_name", "Participating organisation"),
            ("roles", "Roles"),
            ("activities", "Activities"),
        ],
    )

    summary = (
        f"Found {total} participating organisation(s) "
        f"across {organisations['activity_identifier'].nunique()} "
        "activities, ordered by number of activities. An organisation "
        "can hold different roles in different activities. When "
        "filtering with filter_activities_by_participating_org, use the "
        "reference or the name exactly as published in this table."
    )

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total,
        shown=len(shown),
        limit=limit,
        charts=_participating_org_charts(shown),
    )


def list_recipient_countries():
    """List recipient countries present in the configured IATI data."""
    tool_name = "list_recipient_countries"
    activities = activities_df()

    countries = activities[
        [
            "activity_identifier",
            "recipient_country_code",
            "recipient_country_name",
        ]
    ].copy()

    countries["recipient_country_code"] = (
        countries["recipient_country_code"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    countries["recipient_country_name"] = (
        countries["recipient_country_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    countries["display_name"] = countries[
        "recipient_country_name"
    ].where(
        countries["recipient_country_name"] != "",
        countries["recipient_country_code"],
    )

    countries = countries[
        (countries["recipient_country_code"] != "")
        | (countries["display_name"] != "")
    ]

    if countries.empty:
        return h.empty_result(
            "No recipient countries were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    counts = (
        countries.groupby(
            ["recipient_country_code", "display_name"],
            dropna=False,
        )["activity_identifier"]
        .nunique()
        .reset_index(name="activities")
        .sort_values(
            ["activities", "display_name"],
            ascending=[False, True],
        )
    )

    table = h.build_table(
        counts.to_dict("records"),
        [
            ("recipient_country_code", "Country code"),
            ("display_name", "Recipient country"),
            ("activities", "Activities"),
        ],
    )

    summary = (
        f"Found {len(counts)} recipient country value(s) "
        f"across {countries['activity_identifier'].nunique()} activities."
    )

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=len(counts),
        shown=len(counts),
    )

class _Criterion:
    """One resolved filter criterion of `filter_activities`.

    `ids` is the set of activity identifiers that satisfy the criterion;
    `details` maps identifiers to the display text shown in the table
    (matched sectors or organisations, as published). `error` carries the
    empty-result message when the value could not be resolved, including
    the values available in the loaded data so the caller can retry.
    """

    def __init__(
        self,
        key: str,
        label: str,
        value: str,
        ids: set[str] | None = None,
        details: dict[str, str] | None = None,
        match_kind: str | None = None,
        resolved: str | None = None,
        error: str | None = None,
    ):
        self.key = key
        self.label = label
        self.value = value
        self.ids = ids if ids is not None else set()
        self.details = details or {}
        self.match_kind = match_kind
        self.resolved = resolved
        self.error = error


def _stripped(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def _available_preview(values, limit: int = 30) -> str:
    available = sorted({value for value in values if value})
    preview = "; ".join(available[:limit])
    suffix = "; ..." if len(available) > limit else ""
    return f"{preview}{suffix}"


def _resolve_country(country: str, activities: pd.DataFrame) -> _Criterion:
    """Resolve a recipient-country code or name to activity identifiers.

    Ladder: ISO code, exact published name, alias table (English,
    Spanish, Portuguese, French names -> ISO code), published-name
    substring, then close similarity on published names. The alias step
    keeps "Brasil" deterministic even when the file only says "Brazil".
    """
    criterion = _Criterion("recipient_country", "recipient country", country)
    codes = _stripped(activities["recipient_country_code"]).str.upper()
    names = _stripped(activities["recipient_country_name"])
    folded_names = _folded(names)
    ids = _stripped(activities["activity_identifier"])
    needle = _fold_text(country)

    def _pick(mask: pd.Series, kind: str) -> bool:
        if not mask.any():
            return False
        labels = sorted({
            f"{code} ({name})" if name else code
            for code, name in zip(codes[mask], names[mask])
        })
        criterion.ids = set(ids[mask])
        criterion.match_kind = kind
        criterion.resolved = ", ".join(labels)
        criterion.details = {}
        return True

    if _pick(codes == country.upper(), "ISO code"):
        return criterion
    if _pick(folded_names == needle, "exact name"):
        return criterion

    alias_code = country_code_for_name(country)
    if alias_code and _pick(codes == alias_code, "translated name"):
        return criterion
    if len(needle) >= 3 and _pick(
        folded_names.str.contains(needle, regex=False)
        & (folded_names != ""),
        "name substring",
    ):
        return criterion

    close = difflib.get_close_matches(
        needle,
        [name for name in folded_names.unique() if name],
        n=3,
        cutoff=0.8,
    )
    if close and _pick(folded_names.isin(close), "similar name"):
        return criterion

    available = _available_preview(
        f"{code} ({name})" if name else code
        for code, name in zip(codes, names)
    )
    hint = f" (ISO code {alias_code})" if alias_code else ""
    criterion.error = (
        f"No recipient country matches '{country}'{hint}. "
        f"Available recipient countries: {available}"
    )
    return criterion


def _resolve_sector(sector: str) -> _Criterion:
    """Resolve a sector code or name: exact code, exact name, substring."""
    criterion = _Criterion("sector", "sector", sector)
    sectors = _named_sectors(sectors_df())
    sectors = sectors[
        (sectors["sector_code"] != "") | (sectors["sector_name"] != "")
    ]
    if sectors.empty:
        criterion.error = "No sectors were found in the loaded IATI data."
        return criterion

    needle = _fold_text(sector)
    codes = _folded(sectors["sector_code"])
    names = _folded(sectors["sector_name"])

    matches = sectors[codes == needle]
    match_kind = "exact code"
    if matches.empty:
        matches = sectors[names == needle]
        match_kind = "exact name"
    if matches.empty:
        matches = sectors[names.str.contains(needle, regex=False)]
        match_kind = "name substring"

    if matches.empty:
        criterion.error = (
            f"No sector matches '{sector}'. Available sectors: "
            + _available_preview(
                name or code
                for name, code in zip(
                    sectors["sector_name"], sectors["sector_code"]
                )
            )
        )
        return criterion

    matched = matches.copy()
    matched["display"] = matched["sector_name"].where(
        matched["sector_name"] != "", matched["sector_code"]
    )
    has_both = (matched["sector_code"] != "") & (matched["sector_name"] != "")
    matched.loc[has_both, "display"] = (
        matched.loc[has_both, "sector_name"]
        + " ("
        + matched.loc[has_both, "sector_code"]
        + ")"
    )
    details = (
        matched.groupby("activity_identifier")["display"]
        .apply(lambda values: ", ".join(sorted(set(values))))
        .to_dict()
    )
    criterion.ids = set(details)
    criterion.details = details
    criterion.match_kind = match_kind
    criterion.resolved = ", ".join(sorted(set(matched["display"])))
    return criterion


def _resolve_organisation(organisation: str) -> _Criterion:
    """Resolve a participating organisation reference or name.

    Ladder: exact reference, exact name, then name substring combined
    with close similarity (published names are often misspelled, and
    substring alone would let a longer name shadow the intended one).
    """
    criterion = _Criterion(
        "participating_org", "participating organisation", organisation
    )
    orgs = participating_orgs_df().copy()
    for column in ("activity_identifier", "org_ref", "org_name", "role"):
        orgs[column] = _stripped(orgs[column])
    orgs = orgs[(orgs["org_ref"] != "") | (orgs["org_name"] != "")]
    if orgs.empty:
        criterion.error = (
            "No participating organisations were found in the loaded "
            "IATI data."
        )
        return criterion

    needle = _fold_text(organisation)
    refs = _folded(orgs["org_ref"])
    names = _folded(orgs["org_name"])

    matches = orgs[refs == needle]
    match_kind = "exact reference"
    if matches.empty:
        matches = orgs[names == needle]
        match_kind = "exact name"
    if matches.empty:
        substring_hits = names.str.contains(needle, regex=False)
        close_names = difflib.get_close_matches(
            needle, names.unique().tolist(), n=5, cutoff=0.85
        )
        matches = orgs[substring_hits | names.isin(close_names)]
        match_kind = "name substring or similar name"

    if matches.empty:
        criterion.error = (
            f"No participating organisation matches '{organisation}'. "
            "Available organisations: "
            + _available_preview(
                name or ref
                for name, ref in zip(orgs["org_name"], orgs["org_ref"])
            )
        )
        return criterion

    matched = matches.copy()
    matched["display"] = matched["org_name"].where(
        matched["org_name"] != "", matched["org_ref"]
    )
    has_role = matched["role"] != ""
    matched.loc[has_role, "display"] = (
        matched.loc[has_role, "display"]
        + " (role: "
        + matched.loc[has_role, "role"].map(h.organisation_role_label)
        + ")"
    )
    details = (
        matched.groupby("activity_identifier")["display"]
        .apply(lambda values: ", ".join(sorted(set(values))))
        .to_dict()
    )
    criterion.ids = set(details)
    criterion.details = details
    criterion.match_kind = match_kind
    criterion.resolved = ", ".join(
        sorted(set(
            matched["org_name"].where(
                matched["org_name"] != "", matched["org_ref"]
            )
        ))
    )
    return criterion


def _resolve_status(status: str, activities: pd.DataFrame) -> _Criterion:
    """Resolve an activity status given as a codelist code or label."""
    criterion = _Criterion("activity_status", "activity status", status)
    codes = _stripped(activities["activity_status"])
    ids = _stripped(activities["activity_identifier"])
    needle = _fold_text(status).replace("-", " ")

    present = sorted({code for code in codes.unique() if code})
    labels = {code: h.activity_status_label(code) for code in present}
    selected = [
        code for code in present
        if _fold_text(code) == needle or _fold_text(labels[code]) == needle
    ]
    match_kind = "exact code or label"
    if not selected:
        selected = [
            code for code in present
            if needle and needle in _fold_text(labels[code])
        ]
        match_kind = "label substring"

    if not selected:
        criterion.error = (
            f"No activity status matches '{status}'. Available statuses: "
            + "; ".join(f"{code} ({labels[code]})" for code in present)
        )
        return criterion

    mask = codes.isin(selected)
    criterion.ids = set(ids[mask])
    criterion.match_kind = match_kind
    criterion.resolved = ", ".join(
        f"{code} ({labels[code]})" for code in selected
    )
    return criterion


def _resolve_text(text: str, activities: pd.DataFrame) -> _Criterion:
    """Match free text against the activity title and description."""
    criterion = _Criterion("text_contains", "text", text)
    needle = _fold_text(text)
    ids = _stripped(activities["activity_identifier"])
    mask = _folded(activities["title"]).str.contains(needle, regex=False)
    if "description" in activities.columns:
        mask = mask | _folded(activities["description"]).str.contains(
            needle, regex=False
        )
    criterion.ids = set(ids[mask])
    criterion.match_kind = "title or description substring"
    return criterion


def _resolve_criteria(
    activities: pd.DataFrame,
    country: str = "",
    sector: str = "",
    organisation: str = "",
    status: str = "",
    text: str = "",
) -> list[_Criterion]:
    """Resolve each supplied (non-empty) filter value, in a fixed order."""
    criteria: list[_Criterion] = []
    if country:
        criteria.append(_resolve_country(country, activities))
    if sector:
        criteria.append(_resolve_sector(sector))
    if organisation:
        criteria.append(_resolve_organisation(organisation))
    if status:
        criteria.append(_resolve_status(status, activities))
    if text:
        criteria.append(_resolve_text(text, activities))
    return criteria


def _filter_table(shown: pd.DataFrame, criteria: list[_Criterion]):
    """Build the activities table with one extra column per detail filter.

    Country columns are shown when filtering by country or when neither
    sector nor organisation columns would otherwise identify the rows.
    """
    by_key = {criterion.key: criterion for criterion in criteria}
    columns = [
        ("activity_identifier", "IATI identifier"),
        ("title", "Title"),
        ("activity_status", "Status"),
    ]
    has_detail = "sector" in by_key or "participating_org" in by_key
    if "recipient_country" in by_key or not has_detail:
        columns += [
            ("recipient_country_code", "Country code"),
            ("recipient_country_name", "Recipient country"),
        ]
    if "sector" in by_key:
        shown["matched_sectors"] = shown["activity_identifier"].map(
            by_key["sector"].details
        )
        columns.append(("matched_sectors", "Sector"))
    if "participating_org" in by_key:
        shown["matched_orgs"] = shown["activity_identifier"].map(
            by_key["participating_org"].details
        )
        columns.append(("matched_orgs", "Participating organisation"))

    rows = shown[[column for column, _ in columns]].fillna("")
    return h.build_table(
        rows.to_dict("records"),
        columns,
        formatters={"activity_status": h.activity_status_label},
    )


def _filter_notes(criteria: list[_Criterion]) -> list[str]:
    """Explain, per criterion, how the input was matched and to what."""
    notes = []
    for criterion in criteria:
        if criterion.key == "text_contains":
            continue
        note = f"Matched by {criterion.match_kind}"
        if criterion.resolved:
            note += (
                f": {criterion.label} '{criterion.value}' resolved to "
                f"{criterion.resolved}"
            )
        notes.append(note + ".")
    if "participating_org" in {criterion.key for criterion in criteria}:
        notes.append(
            "The matched organisation names, as published, are in the "
            "table."
        )
    return notes


def filter_activities(
    country: str | None = None,
    sector: str | None = None,
    organisation: str | None = None,
    status: str | None = None,
    text: str | None = None,
    limit: int = 10,
    tool_name: str = "filter_activities",
):
    """Filter IATI activities by any combination of criteria.

    Every supplied criterion is resolved against the loaded data first
    (code, exact name, alias or fuzzy fallback, reported per criterion);
    activities must satisfy all of them. When one criterion resolves to
    nothing, the response says which one and lists the values available
    so the caller can retry with an exact value.

    `tool_name` lets the single-criterion wrappers keep their own glossary
    terms in the response (see `TOOL_GLOSSARY_TERMS`).
    """
    def _clean(value) -> str:
        return "" if value is None else str(value).strip()

    country = _clean(country)
    sector = _clean(sector)
    organisation = _clean(organisation)
    status = _clean(status)
    text = _clean(text)

    if not any((country, sector, organisation, status, text)):
        return h.empty_result(
            "At least one filter is required: country, sector, "
            "organisation, status or text.",
            source_url=xml_source(),
        )

    if limit < 1:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    activities = (
        activities_df()
        .drop_duplicates(subset=["activity_identifier"])
        .copy()
    )
    activities["activity_identifier"] = _stripped(
        activities["activity_identifier"]
    )

    criteria = _resolve_criteria(
        activities,
        country=country,
        sector=sector,
        organisation=organisation,
        status=status,
        text=text,
    )
    for criterion in criteria:
        if criterion.error:
            return h.empty_result(criterion.error, source_url=xml_source())

    selected_ids = set.intersection(*(c.ids for c in criteria))
    phrases = {
        "recipient_country": f"for recipient country '{country}'",
        "sector": f"for sector '{sector}'",
        "participating_org": (
            f"with participating organisation '{organisation}'"
        ),
        "activity_status": f"with activity status '{status}'",
        "text_contains": f"with '{text}' in the title or description",
    }
    description = " and ".join(phrases[c.key] for c in criteria)

    all_matches = activities[
        activities["activity_identifier"].isin(selected_ids)
    ]
    total = len(all_matches)
    if all_matches.empty:
        return h.empty_result(
            f"No IATI activities were found {description}.",
            source_url=xml_source(),
        )

    shown = all_matches.head(limit).copy()
    table = _filter_table(shown, criteria)
    summary = " ".join(
        [f"Found {total} IATI activity(ies) {description}."]
        + _filter_notes(criteria)
    )

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total,
        shown=len(shown),
        filters={criterion.key: criterion.value for criterion in criteria},
        limit=limit,
    )


def filter_activities_by_country(
    country: str,
    limit: int = 10,
):
    """Filter IATI activities by recipient country code or name.

    Thin wrapper over `filter_activities(country=...)`.
    """
    if not str(country).strip():
        return h.empty_result(
            "A recipient country code or name is required.",
            source_url=xml_source(),
        )
    return filter_activities(
        country=country,
        limit=limit,
        tool_name="filter_activities_by_country",
    )


def filter_activities_by_sector(
    sector: str,
    limit: int = 10,
):
    """Filter IATI activities by sector code or name.

    Thin wrapper over `filter_activities(sector=...)`.
    """
    if not str(sector).strip():
        return h.empty_result(
            "A sector code or name is required.",
            source_url=xml_source(),
        )
    return filter_activities(
        sector=sector,
        limit=limit,
        tool_name="filter_activities_by_sector",
    )


def filter_activities_by_participating_org(
    organisation: str,
    limit: int = 10,
):
    """Filter IATI activities by participating organisation.

    Thin wrapper over `filter_activities(organisation=...)`.
    """
    if not str(organisation).strip():
        return h.empty_result(
            "A participating organisation reference or name is required.",
            source_url=xml_source(),
        )
    return filter_activities(
        organisation=organisation,
        limit=limit,
        tool_name="filter_activities_by_participating_org",
    )


def list_sectors(limit: int = 100):
    """List sectors present in the configured IATI data."""
    tool_name = "list_sectors"
    if limit < 1:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    sectors = _named_sectors(sectors_df())

    sectors["display_name"] = sectors["sector_name"].where(
        sectors["sector_name"] != "",
        sectors["sector_code"],
    )

    sectors = sectors[
        (sectors["sector_code"] != "")
        | (sectors["display_name"] != "")
    ]

    if sectors.empty:
        return h.empty_result(
            "No sectors were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    counts = (
        sectors.groupby(
            [
                "vocabulary",
                "sector_code",
                "display_name",
            ],
            dropna=False,
        )["activity_identifier"]
        .nunique()
        .reset_index(name="activities")
        .sort_values(
            ["activities", "display_name"],
            ascending=[False, True],
        )
    )

    total = len(counts)
    shown = counts.head(limit)

    table = h.build_table(
        shown.to_dict("records"),
        [
            ("vocabulary", "Vocabulary"),
            ("sector_code", "Sector code"),
            ("display_name", "Sector"),
            ("activities", "Activities"),
        ],
    )

    summary = f"Found {total} sector value(s)."

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total,
        shown=len(shown),
        limit=limit,
        charts=_sector_count_charts(shown),
    )


def transaction_totals_by_year(
    year_from: int | None = None,
    year_to: int | None = None,
):
    """Group commitments and disbursements by year and currency.

    Only commitment and disbursement transactions are included. Amounts with
    different currencies are always reported separately.

    Args:
        year_from: Optional first year to include.
        year_to: Optional last year to include.

    Returns:
        A chronological table containing year, transaction type, currency and
        total amount.
    """
    tool_name = "transaction_totals_by_year"
    if year_from is not None and year_to is not None and year_from > year_to:
        return h.empty_result(
            "The year_from value cannot be greater than year_to.",
            source_url=xml_source(),
        )

    transactions = transactions_df().copy()

    if transactions.empty:
        return h.empty_result(
            "No transactions were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    transactions["transaction_type"] = transactions["transaction_type"].fillna("")
    transactions["transaction_date"] = (
        transactions["transaction_date"].fillna("").astype(str).str.strip()
    )

    allowed_types = {"2", "3"}
    transactions = transactions[
        transactions["transaction_type"].isin(allowed_types)
    ].copy()

    parsed_dates = pd.to_datetime(
        transactions["transaction_date"],
        errors="coerce",
        format="mixed",
    )
    transactions["year"] = parsed_dates.dt.year.astype("Int64")

    transactions = transactions[pd.notna(transactions["year"])].copy()

    if year_from is not None:
        transactions = transactions[transactions["year"] >= year_from]
    if year_to is not None:
        transactions = transactions[transactions["year"] <= year_to]

    transactions["value"] = pd.to_numeric(
        transactions["value"],
        errors="coerce",
    )
    transactions = transactions[pd.notna(transactions["value"])]

    if transactions.empty:
        return h.empty_result(
            "No transaction totals were found for the requested year range.",
            source_url=xml_source(),
        )

    activities = activities_df()[["activity_identifier", "default_currency"]].copy()
    activities = activities.drop_duplicates(subset=["activity_identifier"])
    activities["default_currency"] = (
        activities["default_currency"].fillna("").astype(str).str.strip()
    )

    transactions = transactions.merge(
        activities,
        on="activity_identifier",
        how="left",
    )

    transactions["currency"] = transactions["currency"].fillna("")
    transactions["currency"] = transactions["currency"].astype(str).str.strip()
    transactions["currency"] = transactions["currency"].where(
        transactions["currency"] != "",
        transactions["default_currency"],
    )
    transactions["currency"] = transactions["currency"].fillna("")

    grouped = (
        transactions.groupby(
            ["year", "transaction_type", "currency"],
            dropna=False,
        )["value"]
        .sum()
        .reset_index()
    )
    grouped = grouped.sort_values(
        ["year", "transaction_type", "currency"],
        kind="mergesort",
    )

    rows = []
    for _, row in grouped.iterrows():
        rows.append(
            {
                "year": int(row["year"]),
                "transaction_type": row["transaction_type"],
                "currency": row["currency"],
                "total": row["value"],
            }
        )

    table = h.build_table(
        rows,
        [
            ("year", "Year"),
            ("transaction_type", "Transaction type"),
            ("currency", "Currency"),
            ("total", "Total"),
        ],
        formatters={
            "transaction_type": h.transaction_type_label,
            "total": h.format_amount,
        },
    )

    summary = f"Found {len(rows)} annual transaction total(s)."
    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=len(rows),
        shown=len(rows),
        filters={
            "year_from": year_from,
            "year_to": year_to,
        },
        charts=_year_totals_charts(grouped),
    )


def transaction_totals_by_organisation(limit: int = 50):
    """Group commitments and disbursements by reporting organisation.

    Amounts with different currencies and transaction types are reported
    separately. The reporting organisation publishes the activity data and is
    not necessarily the organisation funding or implementing the activity.

    Args:
        limit: Maximum number of grouped rows to return. Default: 50.

    Returns:
        A table containing the organisation reference and name, transaction
        type, currency and total amount.
    """
    tool_name = "transaction_totals_by_organisation"
    if limit < 1:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    activities = activities_df()[
        [
            "activity_identifier",
            "reporting_org_ref",
            "reporting_org_name",
            "default_currency",
        ]
    ].copy()
    activities = activities.drop_duplicates(subset=["activity_identifier"])
    activities["reporting_org_ref"] = (
        activities["reporting_org_ref"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    activities["reporting_org_name"] = (
        activities["reporting_org_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    activities["default_currency"] = (
        activities["default_currency"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    transactions = transactions_df().copy()
    if transactions.empty:
        return h.empty_result(
            "No transactions were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    allowed_types = {"2", "3"}
    transactions = transactions[
        transactions["transaction_type"].isin(allowed_types)
    ].copy()
    transactions["value"] = pd.to_numeric(transactions["value"], errors="coerce")
    transactions = transactions[pd.notna(transactions["value"])].copy()

    if transactions.empty:
        return h.empty_result(
            "No transaction totals were found for the requested organisation grouping.",
            source_url=xml_source(),
        )

    transactions = transactions.merge(
        activities,
        on="activity_identifier",
        how="left",
    )

    transactions["reporting_org_ref"] = (
        transactions["reporting_org_ref"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["reporting_org_name"] = (
        transactions["reporting_org_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["default_currency"] = (
        transactions["default_currency"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    transactions["display_org_name"] = transactions["reporting_org_name"].where(
        transactions["reporting_org_name"] != "",
        transactions["reporting_org_ref"],
    )
    transactions["display_org_name"] = transactions["display_org_name"].where(
        transactions["display_org_name"] != "",
        "Unknown reporting organisation",
    )

    transactions["currency"] = (
        transactions["currency"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["currency"] = transactions["currency"].where(
        transactions["currency"] != "",
        transactions["default_currency"],
    )
    transactions["currency"] = transactions["currency"].fillna("")
    transactions["currency"] = transactions["currency"].astype(str).str.strip()
    transactions["currency"] = transactions["currency"].where(
        transactions["currency"] != "",
        "Unknown",
    )

    grouped = (
        transactions.groupby(
            [
                "reporting_org_ref",
                "display_org_name",
                "transaction_type",
                "currency",
            ],
            dropna=False,
        )["value"]
        .sum()
        .reset_index()
    )
    grouped = grouped.sort_values(
        ["display_org_name", "transaction_type", "currency"],
        kind="mergesort",
    )
    total = len(grouped)
    shown = grouped.head(limit)

    rows = [
        {
            "organisation_ref": row["reporting_org_ref"],
            "organisation_name": row["display_org_name"],
            "transaction_type": row["transaction_type"],
            "currency": row["currency"],
            "total": row["value"],
        }
        for _, row in shown.iterrows()
    ]

    table = h.build_table(
        rows,
        [
            ("organisation_ref", "Organisation reference"),
            ("organisation_name", "Reporting organisation"),
            ("transaction_type", "Transaction type"),
            ("currency", "Currency"),
            ("total", "Total"),
        ],
        formatters={
            "transaction_type": h.transaction_type_label,
            "total": h.format_amount,
        },
    )

    summary = f"Found {total} organisation transaction total(s)."
    interpretation = (
        "The amounts are associated with activities published by each "
        "reporting organisation. This does not necessarily imply that the "
        "organisation funded or implemented the funds."
    )
    return h.text_result(
        f"{summary}\n\n{interpretation}",
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total,
        shown=len(rows),
        limit=limit,
    )


def _sector_allocations(
    sectors: pd.DataFrame,
    vocabulary: str | None = None,
) -> pd.DataFrame:
    """Return sector allocation percentages that total 100 per activity."""
    sectors = sectors.copy()
    for column in [
        "activity_identifier",
        "sector_code",
        "sector_name",
        "vocabulary",
    ]:
        sectors[column] = (
            sectors[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )
    sectors["percentage"] = pd.to_numeric(
        sectors["percentage"],
        errors="coerce",
    )
    if vocabulary is not None:
        selected_vocabulary = str(vocabulary).strip()
        sectors = sectors[
            sectors["vocabulary"] == selected_vocabulary
        ].copy()
    allocation_rows = []
    for (activity_identifier, vocabulary_code), group in sectors.groupby(
        ["activity_identifier", "vocabulary"],
        dropna=False,
        sort=True,
    ):
        group = group.copy()
        if len(group) == 1 and group["percentage"].isna().all():
            group["percentage"] = 100.0
        valid = group[
            group["percentage"].notna()
            & group["percentage"].between(0, 100)
            & (group["percentage"] > 0)
        ].copy()
        valid_total = float(valid["percentage"].sum())
        if valid_total > 100.000001:
            allocation_rows.append({
                "activity_identifier": activity_identifier,
                "vocabulary": vocabulary_code or "Unknown",
                "sector_code": "",
                "sector_name": "Unallocated sector",
                "allocation_percentage": 100.0,
            })
            continue
        for row in valid.to_dict("records"):
            sector_name = row["sector_name"] or row["sector_code"]
            allocation_rows.append({
                "activity_identifier": activity_identifier,
                "vocabulary": vocabulary_code or "Unknown",
                "sector_code": row["sector_code"],
                "sector_name": sector_name or "Unknown sector",
                "allocation_percentage": float(row["percentage"]),
            })
        remainder = 100.0 - valid_total
        if remainder > 0.000001:
            allocation_rows.append({
                "activity_identifier": activity_identifier,
                "vocabulary": vocabulary_code or "Unknown",
                "sector_code": "",
                "sector_name": "Unallocated sector",
                "allocation_percentage": remainder,
            })
    return pd.DataFrame(
        allocation_rows,
        columns=[
            "activity_identifier",
            "vocabulary",
            "sector_code",
            "sector_name",
            "allocation_percentage",
        ],
    )


def transaction_totals_by_country(
    transaction_type: str = "2",
    currency: str | None = None,
    limit: int = 50,
):
    """Group commitments and disbursements by recipient country.

    Amounts with different currencies and transaction types are reported
    separately. Missing country names fall back to the country code, and
    missing country data falls back to "Unknown recipient country".
    """
    tool_name = "transaction_totals_by_country"
    if limit < 1:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    transaction_type_code = _transaction_type_code(transaction_type)
    if transaction_type_code is None:
        return h.empty_result(
            "Unsupported transaction type. Use commitment, disbursement, "
            "2 or 3.",
            source_url=xml_source(),
        )

    selected_currency = ""
    if currency is not None:
        selected_currency = str(currency).strip().upper()
        if not selected_currency:
            return h.empty_result(
                "Currency cannot be empty when provided.",
                source_url=xml_source(),
            )

    activities = activities_df()[
        [
            "activity_identifier",
            "recipient_country_code",
            "recipient_country_name",
            "default_currency",
        ]
    ].copy()
    activities = activities.drop_duplicates(subset=["activity_identifier"])
    for column in [
        "recipient_country_code",
        "recipient_country_name",
        "default_currency",
    ]:
        activities[column] = (
            activities[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    transactions = transactions_df().copy()
    if transactions.empty:
        return h.empty_result(
            "No transactions were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    transactions["transaction_type"] = (
        transactions["transaction_type"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["value"] = pd.to_numeric(transactions["value"], errors="coerce")
    transactions = transactions[
        (transactions["transaction_type"] == transaction_type_code)
        & transactions["value"].notna()
    ].copy()

    if transactions.empty:
        return h.empty_result(
            "No matching transactions were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    transactions = transactions.merge(
        activities,
        on="activity_identifier",
        how="left",
    )

    transactions["recipient_country_code"] = (
        transactions["recipient_country_code"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    transactions["recipient_country_name"] = (
        transactions["recipient_country_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["default_currency"] = (
        transactions["default_currency"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    transactions["currency"] = (
        transactions["currency"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    transactions["currency"] = transactions["currency"].where(
        transactions["currency"] != "",
        transactions["default_currency"],
    )
    transactions["currency"] = transactions["currency"].fillna("")
    transactions["currency"] = transactions["currency"].astype(str).str.strip()
    transactions["currency"] = transactions["currency"].where(
        transactions["currency"] != "",
        "Unknown",
    )

    if selected_currency:
        transactions = transactions[transactions["currency"] == selected_currency]

    if transactions.empty:
        return h.empty_result(
            f"No transactions were found for currency '{selected_currency}'.",
            source_url=xml_source(),
        )

    transactions["display_country_name"] = transactions[
        "recipient_country_name"
    ].where(
        transactions["recipient_country_name"] != "",
        transactions["recipient_country_code"],
    )
    transactions["display_country_name"] = transactions[
        "display_country_name"
    ].where(
        transactions["display_country_name"] != "",
        "Unknown recipient country",
    )

    grouped = (
        transactions.groupby(
            [
                "recipient_country_code",
                "display_country_name",
                "transaction_type",
                "currency",
            ],
            dropna=False,
        )["value"]
        .sum()
        .reset_index()
    )
    grouped = grouped.sort_values(
        ["currency", "value", "display_country_name"],
        ascending=[True, False, True],
        kind="mergesort",
    )
    total = len(grouped)
    shown = grouped.groupby(
        "currency",
        group_keys=False,
    ).head(limit)

    rows = []
    for _, row in shown.iterrows():
        rows.append(
            {
                "country_code": row["recipient_country_code"],
                "country_name": row["display_country_name"],
                "transaction_type": row["transaction_type"],
                "currency": row["currency"],
                "total": row["value"],
            }
        )

    table = h.build_table(
        rows,
        [
            ("country_code", "Country code"),
            ("country_name", "Recipient country"),
            ("transaction_type", "Transaction type"),
            ("currency", "Currency"),
            ("total", "Total"),
        ],
        formatters={
            "transaction_type": h.transaction_type_label,
            "total": h.format_amount,
        },
    )

    summary = f"Found {total} country transaction total(s)."
    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total,
        shown=len(rows),
        filters={
            "transaction_type": transaction_type_code,
            "currency": selected_currency or None,
        },
        limit=limit,
    )


def transaction_totals_by_sector(
    transaction_type: str = "2",
    currency: str | None = None,
    vocabulary: str | None = None,
    limit: int = 50,
):
    """Allocate commitments and disbursements across sectors.

    Amounts are distributed using the published sector percentages. Different
    vocabularies and currencies are reported separately.
    """
    tool_name = "transaction_totals_by_sector"
    if limit < 1:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    transaction_type_code = _transaction_type_code(transaction_type)
    if transaction_type_code is None:
        return h.empty_result(
            "Unsupported transaction type. Use commitment, disbursement, "
            "2 or 3.",
            source_url=xml_source(),
        )

    selected_currency = ""
    if currency is not None:
        selected_currency = str(currency).strip().upper()
        if not selected_currency:
            return h.empty_result(
                "Currency cannot be empty when provided.",
                source_url=xml_source(),
            )

    transactions = transactions_df().copy()
    transactions["transaction_type"] = (
        transactions["transaction_type"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["value"] = pd.to_numeric(transactions["value"], errors="coerce")
    transactions = transactions[
        (transactions["transaction_type"] == transaction_type_code)
        & transactions["value"].notna()
    ].copy()

    if transactions.empty:
        return h.empty_result(
            "No matching transactions were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    activities = activities_df()[["activity_identifier", "default_currency"]].copy()
    activities = activities.drop_duplicates(subset=["activity_identifier"])
    activities["default_currency"] = (
        activities["default_currency"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    transactions = transactions.merge(
        activities,
        on="activity_identifier",
        how="left",
    )

    transactions["currency"] = (
        transactions["currency"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    transactions["currency"] = transactions["currency"].where(
        transactions["currency"] != "",
        transactions["default_currency"],
    )
    transactions["currency"] = transactions["currency"].fillna("")
    transactions["currency"] = transactions["currency"].astype(str).str.strip()
    transactions["currency"] = transactions["currency"].where(
        transactions["currency"] != "",
        "Unknown",
    )

    if selected_currency:
        transactions = transactions[transactions["currency"] == selected_currency]

    if transactions.empty:
        return h.empty_result(
            f"No transactions were found for currency '{selected_currency}'.",
            source_url=xml_source(),
        )

    sectors = _sector_allocations(
        _named_sectors(sectors_df()),
        vocabulary=vocabulary,
    )
    transaction_activity_ids = set(
        transactions["activity_identifier"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    allocated_activity_ids = set(
        sectors["activity_identifier"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    missing_activity_ids = sorted(
        transaction_activity_ids - allocated_activity_ids
    )

    if missing_activity_ids:
        fallback_vocabulary = (
            str(vocabulary).strip()
            if vocabulary is not None
            else "Unknown"
        )

        missing_allocations = pd.DataFrame([
            {
                "activity_identifier": activity_identifier,
                "vocabulary": fallback_vocabulary,
                "sector_code": "",
                "sector_name": "Unallocated sector",
                "allocation_percentage": 100.0,
            }
            for activity_identifier in missing_activity_ids
        ])

        sectors = pd.concat(
            [sectors, missing_allocations],
            ignore_index=True,
        )
    if sectors.empty:
        return h.empty_result(
            "No sector allocations were found for the requested filters.",
            source_url=xml_source(),
        )

    merged = transactions.merge(
        sectors,
        on="activity_identifier",
        how="left",
    )
    merged["allocation_percentage"] = pd.to_numeric(
        merged["allocation_percentage"],
        errors="coerce",
    )
    merged = merged[merged["allocation_percentage"].notna()].copy()
    merged["allocated_value"] = (
        merged["value"] * merged["allocation_percentage"] / 100
    )

    grouped = (
        merged.groupby(
            [
                "vocabulary",
                "sector_code",
                "sector_name",
                "transaction_type",
                "currency",
            ],
            dropna=False,
        )["allocated_value"]
        .sum()
        .reset_index()
    )
    grouped = grouped.sort_values(
        ["vocabulary", "currency", "allocated_value", "sector_name"],
        ascending=[True, True, False, True],
        kind="mergesort",
    )
    total = len(grouped)
    shown = (
        grouped.groupby(
            ["vocabulary", "currency"],
            sort=False,
            group_keys=False,
        )
        .head(limit)
    )

    rows = []
    for _, row in shown.iterrows():
        rows.append(
            {
                "vocabulary": row["vocabulary"],
                "sector_code": row["sector_code"],
                "sector_name": row["sector_name"],
                "transaction_type": row["transaction_type"],
                "currency": row["currency"],
                "total": row["allocated_value"],
            }
        )

    table = h.build_table(
        rows,
        [
            ("vocabulary", "Vocabulary"),
            ("sector_code", "Sector code"),
            ("sector_name", "Sector"),
            ("transaction_type", "Transaction type"),
            ("currency", "Currency"),
            ("total", "Allocated total"),
        ],
        formatters={
            "transaction_type": h.transaction_type_label,
            "total": h.format_amount,
        },
    )

    summary = (
        "Transaction amounts are allocated using the published sector "
        "percentages. Currencies and sector vocabularies are reported "
        "separately."
    )
    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total,
        shown=len(rows),
        filters={
            "transaction_type": transaction_type_code,
            "currency": selected_currency or None,
            "vocabulary": vocabulary,
        },
        limit=limit,
        charts=_sector_totals_charts(grouped, transaction_type_code),
    )


def top_activities_by_amount(
    transaction_type: str = "2",
    currency: str | None = None,
    limit: int = 10,
):
    """Return activities with the highest transaction totals.

    Rankings are calculated independently for each currency. Only commitments
    and disbursements are supported.
    """
    tool_name = "top_activities_by_amount"
    if limit < 1:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    transaction_type_code = _transaction_type_code(transaction_type)
    if transaction_type_code is None:
        return h.empty_result(
            "Unsupported transaction type. Use commitment, disbursement, "
            "2 or 3.",
            source_url=xml_source(),
        )

    selected_currency = ""
    if currency is not None:
        selected_currency = str(currency).strip().upper()
        if not selected_currency:
            return h.empty_result(
                "Currency cannot be empty when provided.",
                source_url=xml_source(),
            )

    transactions = transactions_df().copy()
    transactions["transaction_type"] = (
        transactions["transaction_type"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["value"] = pd.to_numeric(transactions["value"], errors="coerce")
    transactions = transactions[
        (transactions["transaction_type"] == transaction_type_code)
        & transactions["value"].notna()
    ].copy()

    if transactions.empty:
        return h.empty_result(
            "No matching transactions were found in the loaded IATI data.",
            source_url=xml_source(),
        )

    activity_columns = [
        "activity_identifier",
        "title",
        "reporting_org_name",
        "reporting_org_ref",
        "recipient_country_code",
        "recipient_country_name",
        "default_currency",
    ]
    activities = (
        activities_df()[activity_columns]
        .drop_duplicates(subset=["activity_identifier"])
        .copy()
    )
    for column in activity_columns:
        activities[column] = (
            activities[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    transactions = transactions.merge(
        activities,
        on="activity_identifier",
        how="left",
    )

    transactions["currency"] = (
        transactions["currency"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    transactions["default_currency"] = (
        transactions["default_currency"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    transactions["currency"] = transactions["currency"].where(
        transactions["currency"] != "",
        transactions["default_currency"],
    )
    transactions["currency"] = transactions["currency"].fillna("")
    transactions["currency"] = transactions["currency"].astype(str).str.strip()
    transactions["currency"] = transactions["currency"].where(
        transactions["currency"] != "",
        "Unknown",
    )

    if selected_currency:
        transactions = transactions[transactions["currency"] == selected_currency]

    if transactions.empty:
        return h.empty_result(
            f"No transactions were found for currency '{selected_currency}'.",
            source_url=xml_source(),
        )

    transactions["reporting_org_name"] = (
        transactions["reporting_org_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["reporting_org_ref"] = (
        transactions["reporting_org_ref"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["display_org_name"] = transactions["reporting_org_name"].where(
        transactions["reporting_org_name"] != "",
        transactions["reporting_org_ref"],
    )
    transactions["display_org_name"] = transactions["display_org_name"].where(
        transactions["display_org_name"] != "",
        "Unknown reporting organisation",
    )

    transactions["recipient_country_name"] = (
        transactions["recipient_country_name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )
    transactions["recipient_country_code"] = (
        transactions["recipient_country_code"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )
    transactions["display_country"] = transactions["recipient_country_name"].where(
        transactions["recipient_country_name"] != "",
        transactions["recipient_country_code"],
    )
    transactions["display_country"] = transactions["display_country"].where(
        transactions["display_country"] != "",
        "Unknown",
    )

    grouped = (
        transactions.groupby(
            [
                "activity_identifier",
                "title",
                "display_org_name",
                "display_country",
                "currency",
            ],
            dropna=False,
        )["value"]
        .sum()
        .reset_index()
    )
    grouped = grouped.sort_values(
        ["currency", "value", "activity_identifier"],
        ascending=[True, False, True],
        kind="mergesort",
    )
    total_results = len(grouped)
    grouped = grouped.groupby("currency", group_keys=False).head(limit)

    rows = []
    for _, row in grouped.iterrows():
        rows.append(
            {
                "activity_identifier": row["activity_identifier"],
                "title": row["title"],
                "organisation": row["display_org_name"],
                "country": row["display_country"],
                "transaction_type": transaction_type_code,
                "currency": row["currency"],
                "total": row["value"],
            }
        )

    table = h.build_table(
        rows,
        [
            ("activity_identifier", "IATI identifier"),
            ("title", "Title"),
            ("organisation", "Organisation"),
            ("country", "Country"),
            ("transaction_type", "Transaction type"),
            ("currency", "Currency"),
            ("total", "Total"),
        ],
        formatters={
            "transaction_type": h.transaction_type_label,
            "total": h.format_amount,
        },
    )

    filters = {
        "transaction_type": transaction_type_code,
    }
    if selected_currency:
        filters["currency"] = selected_currency

    summary = f"Found {total_results} top activity amount(s)."
    if transaction_type_code == "2":
        interpretation = (
            "Commitments do not necessarily represent payments made."
        )
    else:
        interpretation = (
            "Disbursements represent funds transferred to finance an activity."
        )
    return h.text_result(
        f"{summary}\n\n{interpretation}",
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total_results,
        shown=len(rows),
        filters=filters,
        limit=limit,
        charts=_top_activity_charts(grouped, transaction_type_code),
    )


def activity_transactions(
    iati_identifier: str,
    limit: int = 50,
):
    """List transactions associated with one IATI activity."""
    tool_name = "activity_transactions"
    iati_identifier = iati_identifier.strip()

    if not iati_identifier:
        return h.empty_result(
            "An IATI activity identifier is required.",
            source_url=xml_source(),
        )

    if limit < 1:
        return h.empty_result(
            "The result limit must be greater than zero.",
            source_url=xml_source(),
        )

    activities = activities_df()
    activity = activities[
        activities["activity_identifier"] == iati_identifier
    ]

    if activity.empty:
        return h.empty_result(
            f"No IATI activity found with identifier "
            f"'{iati_identifier}'.",
            source_url=xml_source(),
        )

    transactions = transactions_df()
    matches = transactions[
        transactions["activity_identifier"] == iati_identifier
    ].copy()

    if matches.empty:
        return h.empty_result(
            f"No transactions were found for IATI activity "
            f"'{iati_identifier}'.",
            source_url=xml_source(),
        )

    matches["transaction_date"] = (
        matches["transaction_date"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    matches = matches.sort_values(
        ["transaction_date", "transaction_type"],
        na_position="last",
    )

    total = len(matches)
    shown = matches.head(limit).copy()

    rows = shown[
        [
            "transaction_date",
            "transaction_type",
            "value",
            "currency",
            "description",
        ]
    ].copy()

    rows["currency"] = rows["currency"].fillna("")
    rows["description"] = rows["description"].fillna("")

    table = h.build_table(
        rows.to_dict("records"),
        [
            ("transaction_date", "Date"),
            ("transaction_type", "Transaction type"),
            ("value", "Value"),
            ("currency", "Currency"),
            ("description", "Description"),
        ],
        formatters={
            "transaction_type": h.transaction_type_label,
            "value": lambda value: (
                ""
                if value is None or str(value) == "nan"
                else h.format_amount(value)
            ),
        },
    )

    title = activity.iloc[0]["title"]

    summary = (
        f"Found {total} transaction(s) for {title} "
        f"({iati_identifier})."
    )

    return h.text_result(
        summary,
        source_url=xml_source(),
        table=table,
        tool_name=tool_name,
        total=total,
        shown=len(shown),
        filters={"iati_identifier": iati_identifier},
        limit=limit,
        charts=_activity_transaction_charts(shown, iati_identifier),
    )
