"""
Optional country / sector / organisation / status filters on the
aggregation tools, and the generic count_activities_by group-by (uses the
synthetic data from `seed_cache`: IATI-001 is AR, Transport, implementation,
with 1500 USD committed; IATI-002 is BR, Basic health care, completion).
"""

import pytest

from mcp_iati.activities import queries


def _text(result):
    return result.content[0].text


def _table(result):
    return result.structuredContent["table"]


def _is_empty(result):
    return "table" not in result.structuredContent


def test_top_activities_by_amount_filters_by_country(seed_cache):
    result = queries.top_activities_by_amount(country="Argentina", limit=5)

    rows = _table(result)[1:]
    assert [row[0] for row in rows] == ["IATI-001"]
    text = _text(result)
    assert "for recipient country 'Argentina'" in text
    assert "resolved to AR" in text
    assert "recipient_country=Argentina" in text


def test_top_activities_by_amount_unknown_country_lists_available(seed_cache):
    result = queries.top_activities_by_amount(country="Narnia")

    assert _is_empty(result)
    assert "Available recipient countries: AR (Argentina); BR (Brazil)" in _text(result)


def test_top_activities_by_amount_without_filters_is_unchanged(seed_cache):
    result = queries.top_activities_by_amount()

    text = _text(result)
    assert "Found 1 top activity amount(s)." in text
    assert "recipient_country" not in text


def test_list_sectors_filters_by_country(seed_cache):
    result = queries.list_sectors(country="AR")

    assert _table(result) == [
        ["Vocabulary", "Sector code", "Sector", "Activities"],
        ["99", "TR", "Transport", 1],
    ]
    assert "Found 1 sector value(s) for recipient country 'AR'." in _text(result)


def test_list_sectors_empty_scope_is_reported(seed_cache):
    result = queries.list_sectors(country="BR", status="implementation")

    assert _is_empty(result)
    assert "for recipient country 'BR' and for activity status 'implementation'" in _text(result)


def test_transaction_totals_by_year_filters_by_organisation(seed_cache):
    result = queries.transaction_totals_by_year(organisation="Ministry of Transport")

    rows = _table(result)[1:]
    assert rows and all(row[1] in ("Out Commitment", "Disbursement") for row in rows)
    assert "participating_org=Ministry of Transport" in _text(result)


def test_transaction_totals_by_sector_filters_by_status(seed_cache):
    result = queries.transaction_totals_by_sector(status="implementation")

    cells = {cell for row in _table(result)[1:] for cell in row}
    assert "Transport" in cells
    assert "Basic health care" not in cells


def test_transaction_totals_by_country_filters_by_sector(seed_cache):
    result = queries.transaction_totals_by_country(sector="Transport")

    codes = [row[0] for row in _table(result)[1:]]
    assert codes == ["AR"]
    assert "for sector 'Transport'" in _text(result)


@pytest.mark.parametrize("group_by", ["sector", "sectors", "Sectors"])
def test_count_activities_by_sector_inside_a_country(seed_cache, group_by):
    result = queries.count_activities_by(group_by, country="Argentina")

    assert _table(result) == [
        ["Vocabulary", "Sector code", "Sector", "Activities"],
        ["99", "TR", "Transport", 1],
    ]
    text = _text(result)
    assert "Counted 1 IATI activity(ies) for recipient country 'Argentina' across 1 sector value(s)." in text
    assert "group_by=sector" in text
    assert "can add up to more than the number of activities" in text


def test_count_activities_by_country_uses_names_and_charts(seed_cache):
    result = queries.count_activities_by("countries")

    assert _table(result) == [
        ["Country code", "Recipient country", "Activities"],
        ["AR", "Argentina", 1],
        ["BR", "Brazil", 1],
    ]
    charts = result.structuredContent["charts"]
    assert len(charts) == 1
    assert charts[0]["labels"] == ["Argentina", "Brazil"]


def test_count_activities_by_status_labels_codes(seed_cache):
    result = queries.count_activities_by("status")

    assert _table(result) == [
        ["Status code", "Activity status", "Activities"],
        ["3", "Completion", 1],
        ["2", "Implementation", 1],
    ]


def test_count_activities_by_organisation_inside_a_sector(seed_cache):
    result = queries.count_activities_by("organisation", sector="TR", limit=1)

    header, first = _table(result)[:2]
    assert header == ["Organisation reference", "Participating organisation", "Activities"]
    assert first[2] == 1
    assert "Records shown: 1" in _text(result)


def test_count_activities_by_rejects_unknown_dimension(seed_cache):
    result = queries.count_activities_by("year")

    assert _is_empty(result)
    assert "Use one of: country, sector, organisation, status." in _text(result)


def test_count_activities_by_reports_unresolved_filter(seed_cache):
    result = queries.count_activities_by("country", sector="nope")

    assert _is_empty(result)
    assert "No sector matches" in _text(result) or "sector" in _text(result).lower()
