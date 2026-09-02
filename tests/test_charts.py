"""
Charts in tool responses: the specs that the chat gateway renders with
Chart.js (structuredContent["charts"]) and the note that tells the AI a
chart is already on screen.

Rules covered here: chart values match the table, currencies and sector
vocabularies are never mixed in one chart, charts with fewer than two
points are skipped, and the reporting organisation stays out of the
participating-organisations chart.
"""

import math

import pandas as pd
import pytest

from mcp_iati import helpers as h
from mcp_iati.activities import data as data_mod
from mcp_iati.activities import queries
from mcp_iati.helpers import charts


def _text(res):
    return res.content[0].text


def _charts(res):
    return (res.structuredContent or {}).get("charts")


# --- text_result -----------------------------------------------------------

def test_text_result_forwards_charts_and_tells_the_ai():
    spec = charts.pie_chart("Shares", [("a", 1), ("b", 3)])
    res = h.text_result("summary", source_url="http://src", charts=[spec])
    assert res.structuredContent["charts"] == [spec]
    assert h.ALREADY_CHART in _text(res)


def test_text_result_without_charts_has_no_note():
    res = h.text_result("summary", source_url="http://src", charts=[])
    assert "charts" not in res.structuredContent
    assert h.ALREADY_CHART not in _text(res)


# --- builders --------------------------------------------------------------

def test_pie_chart_has_one_colour_per_slice():
    spec = charts.pie_chart("t", [("a", 1), ("b", None), ("c", float("nan"))])
    assert spec["type"] == "pie"
    assert spec["labels"] == ["a", "b", "c"]
    assert spec["datasets"][0]["data"] == [1.0, 0.0, 0.0]
    assert len(spec["datasets"][0]["backgroundColor"]) == 3


def test_bar_and_line_chart_shapes():
    bar = charts.bar_chart("t", [2023, 2024], [("x", [1, 2]), ("y", [3, 4])])
    assert bar["type"] == "bar" and "stacked" not in bar
    assert bar["labels"] == ["2023", "2024"]
    assert [d["label"] for d in bar["datasets"]] == ["x", "y"]
    assert charts.bar_chart("t", [1], [("x", [1])], stacked=True)["stacked"] is True
    line = charts.line_chart("t", ["2024-01-01"], [("x", [1.5])])
    assert line["type"] == "line"
    assert "borderColor" in line["datasets"][0]


def test_top_n_with_other_drops_non_positive_and_folds_tail():
    items = [("a", 5), ("b", -1), ("c", 0), ("d", 10), ("e", 1), ("f", math.nan)]
    assert charts.top_n_with_other(items, top_n=2) == [
        ("d", 10.0),
        ("a", 5.0),
        ("Other (1 more)", 1.0),
    ]
    assert charts.top_n_with_other(items, top_n=10) == [
        ("d", 10.0), ("a", 5.0), ("e", 1.0),
    ]


def test_short_label_and_vocabulary_label():
    assert charts.short_label("short") == "short"
    long = "x" * 60
    assert charts.short_label(long).endswith("...")
    assert len(charts.short_label(long)) == charts.LABEL_MAX_CHARS
    assert charts.vocabulary_label("1") == "OECD DAC purpose codes"
    assert charts.vocabulary_label("99") == "Reporting organisation vocabulary"
    assert charts.vocabulary_label("") == "Unknown vocabulary"
    assert charts.vocabulary_label("42") == "Vocabulary 42"


# --- queries over the synthetic fixture ------------------------------------

@pytest.fixture
def richer_cache(seed_cache):
    """Extend the shared fixture so aggregates have at least two points.

    Adds a commitment for IATI-002 (split 60/40 across two DAC sectors) and
    a third participating organisation.
    """
    cache = data_mod._cache
    cache["dataframe:transactions"] = pd.concat([
        cache["dataframe:transactions"],
        pd.DataFrame([{
            "activity_identifier": "IATI-002",
            "transaction_type": "2",
            "transaction_date": "2023-05-01",
            "value": 2000.0,
            "currency": "USD",
            "description": "Health commitment",
        }]),
    ], ignore_index=True)
    sectors = cache["dataframe:sectors"]
    sectors.loc[sectors["activity_identifier"] == "IATI-002", "percentage"] = 60.0
    cache["dataframe:sectors"] = pd.concat([
        sectors,
        pd.DataFrame([{
            "activity_identifier": "IATI-002",
            "sector_code": "12240",
            "sector_name": "Basic nutrition",
            "vocabulary": "1",
            "percentage": 40.0,
        }]),
    ], ignore_index=True)
    cache["dataframe:participating_orgs"] = pd.concat([
        cache["dataframe:participating_orgs"],
        pd.DataFrame([{
            "activity_identifier": "IATI-002",
            "org_ref": "ORG-020",
            "org_name": "Ministry of Health",
            "org_type": "10",
            "role": "4",
        }]),
    ], ignore_index=True)
    return seed_cache


def test_totals_by_year_chart_matches_table(richer_cache):
    res = queries.transaction_totals_by_year()
    (chart,) = _charts(res)
    assert chart["type"] == "bar"
    assert chart["labels"] == ["2023", "2024"]
    by_label = {d["label"]: d["data"] for d in chart["datasets"]}
    assert by_label["Out Commitment"] == [2000.0, 1500.0]
    assert by_label["Disbursement"] == [0.0, 750.0]
    assert "(USD)" in chart["title"]
    assert h.ALREADY_CHART in _text(res)


def test_totals_by_year_single_row_has_no_chart(seed_cache):
    res = queries.transaction_totals_by_year(year_from=2024, year_to=2024)
    # 2024 has both a commitment and a disbursement: two rows, chart drawn.
    assert len(_charts(res)) == 1
    # No transactions at all for 2020: empty result, no chart.
    res = queries.transaction_totals_by_year(year_from=2020, year_to=2020)
    assert _charts(res) is None


def test_totals_by_sector_pie_per_vocabulary(richer_cache):
    res = queries.transaction_totals_by_sector(transaction_type="2")
    found = _charts(res)
    # Vocabulary 99 has a single sector (one slice): skipped. Vocabulary 1
    # has two sectors: one pie, whose total is only that vocabulary's amount.
    assert len(found) == 1
    (pie,) = found
    assert pie["type"] == "pie"
    assert "OECD DAC purpose codes" in pie["title"]
    assert pie["labels"] == ["Basic health care", "Basic nutrition"]
    assert pie["datasets"][0]["data"] == [1200.0, 800.0]


def test_totals_by_sector_respects_vocabulary_filter(richer_cache):
    # With vocabulary 99 only, IATI-002 (DAC sectors only) is reported as
    # "Unallocated sector": two slices, and still a single vocabulary.
    res = queries.transaction_totals_by_sector(transaction_type="2", vocabulary="99")
    (pie,) = _charts(res)
    assert "Reporting organisation vocabulary" in pie["title"]
    assert pie["labels"] == ["Unallocated sector", "Transport"]
    assert pie["datasets"][0]["data"] == [2000.0, 1500.0]


def test_activity_statuses_pie(seed_cache):
    res = queries.list_activity_statuses()
    (pie,) = _charts(res)
    assert pie["labels"] == ["Implementation", "Completion"]
    assert pie["datasets"][0]["data"] == [1.0, 1.0]


def test_list_sectors_bars_per_vocabulary(richer_cache):
    res = queries.list_sectors()
    found = _charts(res)
    assert len(found) == 1
    (bar,) = found
    assert "OECD DAC purpose codes" in bar["title"]
    assert sorted(bar["labels"]) == ["Basic health care", "Basic nutrition"]
    assert bar["datasets"][0]["data"] == [1.0, 1.0]


def test_list_sectors_without_two_points_has_no_chart(seed_cache):
    assert _charts(queries.list_sectors()) is None


def test_participating_orgs_chart_excludes_reporting_org(richer_cache):
    res = queries.list_participating_organisations()
    (bar,) = _charts(res)
    assert "excluding the reporting organisation" in bar["title"]
    assert sorted(bar["labels"]) == ["Ministry of Health", "Ministry of Transport"]
    # The reporting organisation (ORG-001) is still in the table.
    assert any(row[0] == "ORG-001" for row in res.structuredContent["table"][1:])


def test_participating_orgs_single_other_org_has_no_chart(seed_cache):
    assert _charts(queries.list_participating_organisations()) is None


def test_top_activities_chart(richer_cache):
    res = queries.top_activities_by_amount(transaction_type="2")
    (bar,) = _charts(res)
    assert bar["labels"] == ["Health programme", "Sustainable transport programme"]
    assert bar["datasets"][0]["data"] == [2000.0, 1500.0]
    assert bar["datasets"][0]["label"] == "Out Commitment"


def test_activity_transactions_cumulative_lines(seed_cache):
    res = queries.activity_transactions("IATI-001")
    (line,) = _charts(res)
    assert line["type"] == "line"
    assert line["labels"] == ["2024-01-10", "2024-02-10", "2024-03-10"]
    by_label = {d["label"]: d["data"] for d in line["datasets"]}
    assert by_label["Out Commitment"] == [1000.0, 1500.0, 1500.0]
    assert by_label["Disbursement"] == [0.0, 0.0, 750.0]


def test_activity_transactions_few_rows_has_no_chart(seed_cache):
    res = queries.activity_transactions("IATI-001", limit=2)
    assert _charts(res) is None
