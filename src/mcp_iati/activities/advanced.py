"""Higher-level IATI investigations over the converter's pandas tables."""

from typing import Iterable

import pandas as pd
from mcp_server import DataToolOutput

from mcp_iati import helpers as h
from mcp_iati.activities.data import (
    activity_dates_df,
    activities_df,
    budgets_df,
    conditions_df,
    contact_info_df,
    documents_df,
    indicator_periods_df,
    indicators_df,
    locations_df,
    participating_orgs_df,
    results_df,
    sectors_df,
    transactions_df,
    xml_source,
)


TRANSACTION_TYPES = {
    "commitment": "2",
    "commitments": "2",
    "disbursement": "3",
    "disbursements": "3",
    "expenditure": "4",
    "expenditures": "4",
    "2": "2",
    "3": "3",
    "4": "4",
}
ROLE_CODES = {"funding": "1", "accountable": "2", "extending": "3", "implementing": "4"}
RESULT_TYPES = {"output": "1", "outcome": "2", "impact": "3", "other": "9"}


def _clean(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


def _type_code(value: str | None) -> str | None:
    if value is None:
        return None
    return TRANSACTION_TYPES.get(str(value).strip().casefold())


def _currency(transactions: pd.DataFrame) -> pd.DataFrame:
    defaults = activities_df()[["activity_identifier", "default_currency"]].drop_duplicates("activity_identifier")
    frame = transactions.merge(defaults, on="activity_identifier", how="left")
    frame["currency"] = _clean(frame["currency"]).str.upper()
    frame["default_currency"] = _clean(frame["default_currency"]).str.upper()
    frame["currency"] = frame["currency"].where(frame["currency"] != "", frame["default_currency"])
    frame["currency"] = frame["currency"].where(frame["currency"] != "", "Unknown")
    return frame


def _transactions(
    transaction_type: str | None = None, year_from: int | None = None, year_to: int | None = None
) -> tuple[pd.DataFrame, str | None]:
    if year_from is not None and year_to is not None and year_from > year_to:
        return pd.DataFrame(), "year_from cannot be greater than year_to."
    code = _type_code(transaction_type)
    if transaction_type is not None and code is None:
        return pd.DataFrame(), "Unsupported transaction type. Use commitment, disbursement, expenditure, 2, 3 or 4."
    frame = transactions_df().copy()
    frame["transaction_type"] = _clean(frame["transaction_type"])
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame["year"] = pd.to_datetime(frame["transaction_date"], errors="coerce", format="mixed").dt.year.astype("Int64")
    frame = frame[frame["value"].notna()]
    if code:
        frame = frame[frame["transaction_type"] == code]
    else:
        frame = frame[frame["transaction_type"].isin({"2", "3", "4"})]
    if year_from is not None:
        frame = frame[frame["year"] >= year_from]
    if year_to is not None:
        frame = frame[frame["year"] <= year_to]
    return _currency(frame), None


def _table_result(
    tool_name: str, summary: str, rows: Iterable[dict], columns: list[tuple[str, str]], *, filters=None, limit=None
):
    rows = list(rows)
    if not rows:
        return h.empty_result(summary, source_url=xml_source())
    return h.text_result(
        summary,
        source_url=xml_source(),
        table=h.build_table(rows, columns),
        tool_name=tool_name,
        total=len(rows),
        shown=len(rows),
        filters=filters or {},
        limit=limit,
    )


def totals_by_year(
    transaction_type: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> DataToolOutput:
    frame, error = _transactions(transaction_type, year_from, year_to)
    if error or frame.empty:
        return h.empty_result(error or "No matching transactions were found.", source_url=xml_source())
    grouped = frame.groupby(["year", "transaction_type", "currency"], dropna=False)["value"].sum().reset_index()
    grouped = grouped.sort_values(["year", "transaction_type", "currency"])
    rows = [
        {
            "year": int(r.year),
            "transaction_type": h.transaction_type_label(r.transaction_type),
            "currency": r.currency,
            "total": h.format_amount(r.value),
        }
        for r in grouped.itertuples()
    ]
    return _table_result(
        "totals_by_year",
        f"Found {len(rows)} annual financial total(s).",
        rows,
        [("year", "Year"), ("transaction_type", "Transaction type"), ("currency", "Currency"), ("total", "Total")],
        filters={"transaction_type": transaction_type, "year_from": year_from, "year_to": year_to},
    )


def _organisation_ranking(
    side: str, limit: int, transaction_type: str | None, year_from: int | None, year_to: int | None, org_type: str | None = None
):
    if limit < 1:
        return h.empty_result("The result limit must be greater than zero.", source_url=xml_source())
    frame, error = _transactions(transaction_type, year_from, year_to)
    if error:
        return h.empty_result(error, source_url=xml_source())
    prefix = "provider" if side == "funders" else "receiver"
    required = [f"{prefix}_org_ref", f"{prefix}_org_name", f"{prefix}_org_type"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        return h.empty_result(f"The source does not publish {prefix} organisation fields.", source_url=xml_source())
    if org_type is not None:
        frame = frame[_clean(frame[f"{prefix}_org_type"]) == str(org_type).strip()]
    frame["organisation_ref"] = _clean(frame[f"{prefix}_org_ref"])
    frame["organisation"] = _clean(frame[f"{prefix}_org_name"])
    frame["organisation"] = frame["organisation"].where(frame["organisation"] != "", frame["organisation_ref"])
    frame = frame[frame["organisation"] != ""]
    grouped = (
        frame.groupby(["organisation_ref", "organisation", f"{prefix}_org_type", "currency"], dropna=False)["value"]
        .sum()
        .reset_index()
    )
    grouped = (
        grouped.sort_values(["currency", "value"], ascending=[True, False]).groupby("currency", group_keys=False).head(limit)
    )
    rows = [
        {
            "organisation": r.organisation,
            "reference": r.organisation_ref,
            "organisation_type": h.category_value_label("organisation_type", getattr(r, f"{prefix}_org_type")),
            "currency": r.currency,
            "total": h.format_amount(r.value),
        }
        for r in grouped.itertuples()
    ]
    return _table_result(
        f"top_{side}",
        f"Found {len(rows)} ranked {side}.",
        rows,
        [
            ("organisation", "Organisation"),
            ("reference", "Reference"),
            ("organisation_type", "Organisation type"),
            ("currency", "Currency"),
            ("total", "Total"),
        ],
        filters={"transaction_type": transaction_type, "year_from": year_from, "year_to": year_to, "org_type": org_type},
        limit=limit,
    )


def top_funders(
    limit: int = 10,
    transaction_type: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> DataToolOutput:
    return _organisation_ranking("funders", limit, transaction_type, year_from, year_to)


def top_receivers(
    limit: int = 10,
    org_type: str | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> DataToolOutput:
    return _organisation_ranking("receivers", limit, None, year_from, year_to, org_type)


def top_activities(
    by: str = "commitment",
    limit: int = 10,
    status: str | None = None,
) -> DataToolOutput:
    by = by.strip().casefold()
    activities = activities_df().copy()
    if status is not None:
        activities = activities[_clean(activities["activity_status"]) == str(status).strip()]
    if by == "budget":
        values = budgets_df().copy()
        if values.empty:
            return h.empty_result("No budgets were published.", source_url=xml_source())
        values["value"] = pd.to_numeric(values["value"], errors="coerce")
    else:
        code = _type_code(by)
        if code not in {"2", "3"}:
            return h.empty_result("by must be commitment, disbursement or budget.", source_url=xml_source())
        values, _ = _transactions(by)
    values = values[values["activity_identifier"].isin(activities["activity_identifier"])]
    grouped = values.groupby(["activity_identifier", "currency"], dropna=False)["value"].sum().reset_index()
    grouped = grouped.merge(activities[["activity_identifier", "title", "activity_status"]], on="activity_identifier", how="left")
    grouped = (
        grouped.sort_values(["currency", "value"], ascending=[True, False]).groupby("currency", group_keys=False).head(limit)
    )
    rows = [
        {
            "iati_identifier": r.activity_identifier,
            "title": r.title,
            "status": h.activity_status_label(r.activity_status),
            "currency": r.currency,
            "total": h.format_amount(r.value),
        }
        for r in grouped.itertuples()
    ]
    return _table_result(
        "top_activities",
        f"Found {len(rows)} top activities by {by}.",
        rows,
        [
            ("iati_identifier", "IATI identifier"),
            ("title", "Title"),
            ("status", "Status"),
            ("currency", "Currency"),
            ("total", "Total"),
        ],
        filters={"by": by, "status": status},
        limit=limit,
    )


def execution_gap(
    iati_identifier: str | None = None, min_commitment: float = 0, only_underexecuted: bool = False, limit: int = 50
) -> DataToolOutput:
    frame, _ = _transactions()
    frame = frame[frame["transaction_type"].isin({"2", "3"})]
    if iati_identifier:
        frame = frame[frame["activity_identifier"] == iati_identifier.strip()]
    grouped = frame.pivot_table(
        index=["activity_identifier", "currency"], columns="transaction_type", values="value", aggfunc="sum", fill_value=0
    ).reset_index()
    for code in ("2", "3"):
        if code not in grouped:
            grouped[code] = 0.0
    grouped = grouped[grouped["2"] >= min_commitment]
    grouped["execution_ratio"] = grouped["3"].div(grouped["2"]).where(grouped["2"] != 0)
    if only_underexecuted:
        grouped = grouped[grouped["execution_ratio"] < 1]
    titles = activities_df()[["activity_identifier", "title"]].drop_duplicates("activity_identifier")
    grouped = (
        grouped.merge(titles, on="activity_identifier", how="left")
        .sort_values(["execution_ratio", "2"], ascending=[True, False])
        .head(limit)
    )
    rows = [
        {
            "iati_identifier": row["activity_identifier"],
            "title": row["title"],
            "currency": row["currency"],
            "commitment": h.format_amount(row["2"]),
            "disbursement": h.format_amount(row["3"]),
            "gap": h.format_amount(row["2"] - row["3"]),
            "execution_ratio": ("" if pd.isna(row["execution_ratio"]) else f"{row['execution_ratio']:.1%}"),
        }
        for _, row in grouped.iterrows()
    ]
    totals = (
        grouped.assign(unpaid_gap=grouped["2"] - grouped["3"])
        .groupby("currency", dropna=False)[["2", "3", "unpaid_gap"]]
        .sum()
        .reset_index()
    )
    totals_text = "; ".join(
        f"{row['currency']}: commitments {h.format_amount(row['2'])}, "
        f"disbursements {h.format_amount(row['3'])}, "
        f"unpaid gap {h.format_amount(row['unpaid_gap'])}"
        for _, row in totals.iterrows()
    )
    return _table_result(
        "execution_gap",
        f"Found {len(rows)} commitment/disbursement comparisons. "
        f"Totals for the displayed rows — {totals_text}.",
        rows,
        [
            ("iati_identifier", "IATI identifier"),
            ("title", "Title"),
            ("currency", "Currency"),
            ("commitment", "Commitment"),
            ("disbursement", "Disbursement"),
            ("gap", "Unpaid gap"),
            ("execution_ratio", "Execution ratio"),
        ],
        filters={"iati_identifier": iati_identifier, "min_commitment": min_commitment, "only_underexecuted": only_underexecuted},
        limit=limit,
    )


def budget_vs_spend(
    iati_identifier: str | None = None,
    year: int | None = None,
) -> DataToolOutput:
    budgets = budgets_df().copy()
    if budgets.empty:
        return h.empty_result("No budgets were published.", source_url=xml_source())
    budgets["year"] = pd.to_datetime(budgets["period_start"], errors="coerce", format="mixed").dt.year.astype("Int64")
    budgets["value"] = pd.to_numeric(budgets["value"], errors="coerce")
    spend, _ = _transactions("expenditure", year, year)
    if iati_identifier:
        budgets = budgets[budgets["activity_identifier"] == iati_identifier.strip()]
        spend = spend[spend["activity_identifier"] == iati_identifier.strip()]
    if year is not None:
        budgets = budgets[budgets["year"] == year]
    budget_group = budgets.groupby(["activity_identifier", "year", "currency"], dropna=False)["value"].sum().rename("budget")
    spend_group = spend.groupby(["activity_identifier", "year", "currency"], dropna=False)["value"].sum().rename("spend")
    grouped = pd.concat([budget_group, spend_group], axis=1).fillna(0).reset_index()
    grouped["variance"] = grouped["budget"] - grouped["spend"]
    rows = [
        {
            "iati_identifier": r.activity_identifier,
            "year": "" if pd.isna(r.year) else int(r.year),
            "currency": r.currency,
            "budget": h.format_amount(r.budget),
            "spend": h.format_amount(r.spend),
            "variance": h.format_amount(r.variance),
        }
        for r in grouped.itertuples()
    ]
    return _table_result(
        "budget_vs_spend",
        f"Found {len(rows)} budget versus expenditure comparisons.",
        rows,
        [
            ("iati_identifier", "IATI identifier"),
            ("year", "Year"),
            ("currency", "Currency"),
            ("budget", "Budget"),
            ("spend", "Expenditure"),
            ("variance", "Budget minus expenditure"),
        ],
        filters={"iati_identifier": iati_identifier, "year": year},
    )


def funding_breakdown(
    dimension: str,
    year_from: int | None = None,
    year_to: int | None = None,
) -> DataToolOutput:
    dimensions = {"finance_type", "flow_type", "aid_type", "tied_status", "collaboration_type", "disbursement_channel"}
    if dimension not in dimensions:
        return h.empty_result(f"Unsupported dimension. Use one of: {', '.join(sorted(dimensions))}.", source_url=xml_source())
    frame, error = _transactions(None, year_from, year_to)
    if error:
        return h.empty_result(error, source_url=xml_source())
    defaults = {
        "finance_type": "default_finance_type",
        "flow_type": "default_flow_type",
        "aid_type": "default_aid_type",
        "tied_status": "default_tied_status",
        "collaboration_type": "collaboration_type",
    }
    if dimension in defaults:
        default_column = defaults[dimension]
        activity_values = (
            activities_df()[["activity_identifier", default_column]]
            .drop_duplicates("activity_identifier")
            .rename(columns={default_column: "activity_default_value"})
        )
        frame = frame.merge(activity_values, on="activity_identifier", how="left")
        transaction_values = (
            _clean(frame[dimension])
            if dimension in frame.columns
            else pd.Series("", index=frame.index, dtype=str)
        )
        frame[dimension] = transaction_values.where(
            transaction_values != "", _clean(frame["activity_default_value"])
        )
    elif dimension not in frame.columns:
        frame[dimension] = ""
    frame[dimension] = _clean(frame[dimension]).where(_clean(frame[dimension]) != "", "Unknown")
    grouped = (
        frame.groupby([dimension, "transaction_type", "currency"], dropna=False)["value"]
        .sum()
        .reset_index()
        .sort_values("value", ascending=False)
    )
    rows = [
        {
            "code": getattr(r, dimension),
            "value": h.category_value_label(dimension, getattr(r, dimension)),
            "transaction_type": h.transaction_type_label(r.transaction_type),
            "currency": r.currency,
            "total": h.format_amount(r.value),
        }
        for r in grouped.itertuples()
    ]
    return _table_result(
        "funding_breakdown",
        f"Found {len(rows)} totals by {dimension}.",
        rows,
        [
            ("code", f"{dimension.replace('_', ' ').title()} code"),
            ("value", dimension.replace("_", " ").title()),
            ("transaction_type", "Transaction type"),
            ("currency", "Currency"),
            ("total", "Total"),
        ],
        filters={"dimension": dimension, "year_from": year_from, "year_to": year_to},
    )


def _allocated_funding(
    table: pd.DataFrame,
    keys: list[str],
    percentage: str,
    limit: int,
    year_from: int | None,
    year_to: int | None,
    transaction_type: str = "commitment",
):
    frame, error = _transactions(transaction_type, year_from, year_to)
    if error:
        return pd.DataFrame(), error
    allocations = table.copy()
    allocations[percentage] = pd.to_numeric(allocations[percentage], errors="coerce").fillna(100)
    merged = frame.merge(allocations[["activity_identifier", *keys, percentage]], on="activity_identifier", how="left")
    merged["allocated"] = merged["value"] * merged[percentage] / 100
    grouped = (
        merged.groupby([*keys, "currency"], dropna=False)["allocated"]
        .sum()
        .reset_index()
        .sort_values("allocated", ascending=False)
        .head(limit)
    )
    return grouped, None


def funding_by_country(
    limit: int = 20,
    year_from: int | None = None,
    year_to: int | None = None,
    region: str | None = None,
) -> DataToolOutput:
    activities = activities_df().copy()
    if region:
        if "recipient_region_code" not in activities:
            return h.empty_result("The source does not publish recipient regions.", source_url=xml_source())
        mask = _clean(activities["recipient_region_code"]).str.casefold().eq(region.strip().casefold()) | _clean(
            activities.get("recipient_region_name", pd.Series(index=activities.index, dtype=str))
        ).str.casefold().str.contains(region.strip().casefold(), regex=False)
        activities = activities[mask]
    grouped, error = _allocated_funding(
        activities,
        ["recipient_country_code", "recipient_country_name"],
        "recipient_country_percentage",
        limit,
        year_from,
        year_to,
    )
    if error or grouped.empty:
        return h.empty_result(error or "No matching country funding was found.", source_url=xml_source())
    rows = [
        {
            "country_code": r.recipient_country_code,
            "country": r.recipient_country_name,
            "currency": r.currency,
            "total": h.format_amount(r.allocated),
        }
        for r in grouped.itertuples()
    ]
    return _table_result(
        "funding_by_country",
        f"Found {len(rows)} recipient-country totals allocated by published percentages.",
        rows,
        [("country_code", "Country code"), ("country", "Country"), ("currency", "Currency"), ("total", "Allocated total")],
        filters={"year_from": year_from, "year_to": year_to, "region": region},
        limit=limit,
    )


def funding_by_sector(
    vocabulary: str = "1",
    limit: int = 20,
    year_from: int | None = None,
    year_to: int | None = None,
) -> DataToolOutput:
    sectors = sectors_df().copy()
    aliases = {"dac": "1", "sdg": "7", "sdg goals": "7", "sdg targets": "8"}
    selected = aliases.get(vocabulary.strip().casefold(), vocabulary.strip())
    sectors = sectors[_clean(sectors["vocabulary"]) == selected]
    grouped, error = _allocated_funding(
        sectors, ["vocabulary", "sector_code", "sector_name"], "percentage", limit, year_from, year_to
    )
    if error or grouped.empty:
        return h.empty_result(error or "No matching sector funding was found.", source_url=xml_source())
    rows = [
        {
            "vocabulary": r.vocabulary,
            "sector_code": r.sector_code,
            "sector": r.sector_name,
            "currency": r.currency,
            "total": h.format_amount(r.allocated),
        }
        for r in grouped.itertuples()
    ]
    return _table_result(
        "funding_by_sector",
        f"Found {len(rows)} sector totals allocated by published percentages.",
        rows,
        [
            ("vocabulary", "Vocabulary"),
            ("sector_code", "Sector code"),
            ("sector", "Sector"),
            ("currency", "Currency"),
            ("total", "Allocated total"),
        ],
        filters={"vocabulary": vocabulary, "year_from": year_from, "year_to": year_to},
        limit=limit,
    )


def humanitarian_split(
    year_from: int | None = None,
    year_to: int | None = None,
) -> DataToolOutput:
    frame, error = _transactions(None, year_from, year_to)
    if error:
        return h.empty_result(error, source_url=xml_source())
    activity_flags = activities_df()[["activity_identifier", "humanitarian"]].drop_duplicates("activity_identifier")
    frame = frame.merge(activity_flags, on="activity_identifier", how="left", suffixes=("_transaction", "_activity"))
    tx_flag = _clean(frame.get("humanitarian_transaction", pd.Series(index=frame.index, dtype=str)))
    activity_flag = _clean(frame["humanitarian_activity"])
    frame["humanitarian_group"] = (
        tx_flag.where(tx_flag != "", activity_flag).map({"1": "Humanitarian", "0": "Development"}).fillna("Unspecified")
    )
    grouped = frame.groupby(["humanitarian_group", "transaction_type", "currency"])["value"].sum().reset_index()
    rows = [
        {
            "classification": r.humanitarian_group,
            "transaction_type": h.transaction_type_label(r.transaction_type),
            "currency": r.currency,
            "total": h.format_amount(r.value),
        }
        for r in grouped.itertuples()
    ]
    return _table_result(
        "humanitarian_split",
        f"Found {len(rows)} humanitarian/development totals.",
        rows,
        [
            ("classification", "Classification"),
            ("transaction_type", "Transaction type"),
            ("currency", "Currency"),
            ("total", "Total"),
        ],
        filters={"year_from": year_from, "year_to": year_to},
    )


def activities_by_organisation(
    org: str,
    role: str | None = None,
    status: str | None = None,
    limit: int = 50,
) -> DataToolOutput:
    organisations = participating_orgs_df().copy()
    query = org.strip().casefold()
    organisations = organisations[
        _clean(organisations["org_name"]).str.casefold().str.contains(query, regex=False)
        | _clean(organisations["org_ref"]).str.casefold().eq(query)
    ]
    if role:
        code = ROLE_CODES.get(role.strip().casefold(), role.strip())
        organisations = organisations[_clean(organisations["role"]) == code]
    activities = activities_df().copy()
    if status:
        activities = activities[_clean(activities["activity_status"]) == status.strip()]
    matches = organisations.merge(
        activities[["activity_identifier", "title", "activity_status"]], on="activity_identifier", how="inner"
    ).head(limit)
    totals, _ = _transactions()
    amounts = totals.groupby(["activity_identifier", "currency"])["value"].sum().reset_index()
    matches = matches.merge(amounts, on="activity_identifier", how="left")
    rows = [
        {
            "iati_identifier": r.activity_identifier,
            "title": r.title,
            "role": h.organisation_role_label(r.role),
            "status": h.activity_status_label(r.activity_status),
            "currency": getattr(r, "currency", ""),
            "transaction_total": "" if pd.isna(getattr(r, "value", None)) else h.format_amount(r.value),
        }
        for r in matches.itertuples()
    ]
    return _table_result(
        "activities_by_organisation",
        f"Found {len(rows)} activities involving {org}.",
        rows,
        [
            ("iati_identifier", "IATI identifier"),
            ("title", "Title"),
            ("role", "Role"),
            ("status", "Status"),
            ("currency", "Currency"),
            ("transaction_total", "Transaction total"),
        ],
        filters={"org": org, "role": role, "status": status},
        limit=limit,
    )


def activity_results(
    iati_identifier: str | None = None,
    result_type: str | None = None,
    only_underachieving: bool = False,
) -> DataToolOutput:
    results = results_df().copy()
    indicators = indicators_df().copy()
    periods = indicator_periods_df().copy()
    if results.empty or indicators.empty or periods.empty:
        return h.empty_result("The source does not publish complete result indicators and periods.", source_url=xml_source())
    if iati_identifier:
        results = results[results["activity_identifier"] == iati_identifier.strip()]
    if result_type:
        code = RESULT_TYPES.get(result_type.strip().casefold(), result_type.strip())
        results = results[_clean(results["result_type"]) == code]
    merged = results.merge(indicators, on=["activity_identifier", "result_ref"], suffixes=("_result", "_indicator")).merge(
        periods, on=["activity_identifier", "result_ref", "indicator_ref"]
    )
    merged["target_value"] = pd.to_numeric(merged["target_value"], errors="coerce")
    merged["actual_value"] = pd.to_numeric(merged["actual_value"], errors="coerce")
    if only_underachieving:
        ascending = _clean(merged["ascending"]).isin({"1", "true", "True"})
        merged = merged[
            (ascending & (merged["actual_value"] < merged["target_value"]))
            | (~ascending & (merged["actual_value"] > merged["target_value"]))
        ]
    rows = [
        {
            "iati_identifier": r.activity_identifier,
            "result": r.title_result,
            "indicator": r.title_indicator,
            "baseline": r.baseline_value,
            "period_start": r.period_start,
            "period_end": r.period_end,
            "target": r.target_value,
            "actual": r.actual_value,
        }
        for r in merged.itertuples()
    ]
    return _table_result(
        "activity_results",
        f"Found {len(rows)} result indicator periods.",
        rows,
        [
            ("iati_identifier", "IATI identifier"),
            ("result", "Result"),
            ("indicator", "Indicator"),
            ("baseline", "Baseline"),
            ("period_start", "Period start"),
            ("period_end", "Period end"),
            ("target", "Target"),
            ("actual", "Actual"),
        ],
        filters={"iati_identifier": iati_identifier, "result_type": result_type, "only_underachieving": only_underachieving},
    )


def activity_documents(
    iati_identifier: str | None = None,
    category: str | None = None,
    limit: int = 50,
) -> DataToolOutput:
    frame = documents_df().copy()
    if iati_identifier:
        frame = frame[frame["activity_identifier"] == iati_identifier.strip()]
    if category:
        frame = frame[_clean(frame["category_code"]) == category.strip()]
    frame = frame.head(limit)
    rows = frame[
        ["activity_identifier", "category_code", "title", "format", "document_date", "url"]
    ].fillna("").to_dict("records")
    for row in rows:
        row["category"] = h.document_category_label(row["category_code"])
    return _table_result(
        "activity_documents",
        f"Found {len(rows)} supporting documents.",
        rows,
        [
            ("activity_identifier", "IATI identifier"),
            ("category_code", "Category code"),
            ("category", "Category"),
            ("title", "Title"),
            ("format", "Format"),
            ("document_date", "Date"),
            ("url", "URL"),
        ],
        filters={"iati_identifier": iati_identifier, "category": category},
        limit=limit,
    )


def activity_contacts(iati_identifier: str) -> DataToolOutput:
    frame = contact_info_df()
    frame = frame[frame["activity_identifier"] == iati_identifier.strip()]
    rows = (
        frame[
            [
                "contact_type",
                "organisation",
                "department",
                "person_name",
                "job_title",
                "telephone",
                "email",
                "website",
                "mailing_address",
            ]
        ]
        .fillna("")
        .to_dict("records")
    )
    for row in rows:
        row["contact_type_label"] = h.contact_type_label(row["contact_type"])
    return _table_result(
        "activity_contacts",
        f"Found {len(rows)} contacts for {iati_identifier}.",
        rows,
        [
            ("contact_type", "Contact type code"),
            ("contact_type_label", "Contact type"),
            ("organisation", "Organisation"),
            ("department", "Department"),
            ("person_name", "Person"),
            ("job_title", "Job title"),
            ("telephone", "Telephone"),
            ("email", "Email"),
            ("website", "Website"),
            ("mailing_address", "Address"),
        ],
        filters={"iati_identifier": iati_identifier},
    )


FULL_RECORD_TABLES = {
    "dates": activity_dates_df,
    "organisations": participating_orgs_df,
    "sectors": sectors_df,
    "transactions": transactions_df,
    "budgets": budgets_df,
    "locations": locations_df,
    "results": results_df,
    "indicators": indicators_df,
    "indicator_periods": indicator_periods_df,
    "documents": documents_df,
    "contacts": contact_info_df,
    "conditions": conditions_df,
}


def activity_full_record(
    iati_identifier: str,
    sections: list[str] | None = None,
) -> DataToolOutput:
    identifier = iati_identifier.strip()
    activity = activities_df()[activities_df()["activity_identifier"] == identifier]
    if activity.empty:
        return h.empty_result(f"No IATI activity found with identifier '{identifier}'.", source_url=xml_source())
    selected = list(FULL_RECORD_TABLES) if sections is None else sections
    unknown = sorted(set(selected) - set(FULL_RECORD_TABLES))
    if unknown:
        return h.empty_result(f"Unknown sections: {', '.join(unknown)}.", source_url=xml_source())
    rows = [{"section": "activity", "record": str({k: v for k, v in activity.iloc[0].fillna("").to_dict().items()})}]
    for section in selected:
        frame = FULL_RECORD_TABLES[section]()
        if not frame.empty:
            matches = frame[frame["activity_identifier"] == identifier].fillna("")
            rows.extend({"section": section, "record": str(record)} for record in matches.to_dict("records"))
    return _table_result(
        "activity_full_record",
        f"Found {len(rows)} records across the requested sections for {identifier}.",
        rows,
        [("section", "Section"), ("record", "Published record")],
        filters={"iati_identifier": identifier, "sections": selected},
    )
