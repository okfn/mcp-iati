"""Regression coverage for the investigative B-E tools."""

import inspect

import pandas as pd
from mcp_server import DataToolOutput

from mcp_iati.activities import advanced
from mcp_iati.activities import data as data_mod


PUBLIC_TOOLS = (
    advanced.totals_by_year,
    advanced.top_funders,
    advanced.top_receivers,
    advanced.top_activities,
    advanced.execution_gap,
    advanced.budget_vs_spend,
    advanced.funding_breakdown,
    advanced.funding_by_country,
    advanced.funding_by_sector,
    advanced.humanitarian_split,
    advanced.activity_full_record,
    advanced.activities_by_organisation,
    advanced.activity_results,
    advanced.activity_documents,
    advanced.activity_contacts,
)


def test_public_tools_declare_registry_return_type():
    for tool in PUBLIC_TOOLS:
        assert inspect.signature(tool).return_annotation is DataToolOutput


def _table(result):
    return result.structuredContent.get("table", [])


def _rows(result):
    table = _table(result)
    return [dict(zip(table[0], row)) for row in table[1:]]


def _seed_extended(seed_cache):
    transactions = seed_cache.transactions
    for column, values in {
        "provider_org_ref": ["F-1", "F-1", "F-2"],
        "provider_org_name": ["Fund A", "Fund A", "Fund B"],
        "provider_org_type": ["40", "40", "10"],
        "receiver_org_ref": ["R-1", "R-1", "R-2"],
        "receiver_org_name": ["Ministry", "Ministry", "NGO"],
        "receiver_org_type": ["10", "10", "22"],
        "finance_type": ["410", "410", "110"],
        "flow_type": ["10", "10", "10"],
        "aid_type": ["C01", "C01", "C01"],
        "tied_status": ["5", "5", "5"],
        "disbursement_channel": ["2", "2", "1"],
        "humanitarian": ["0", "0", "0"],
    }.items():
        transactions[column] = values
    seed_cache.activities["recipient_country_percentage"] = [100, 100]
    seed_cache.activities["humanitarian"] = ["0", "1"]
    seed_cache.activities["collaboration_type"] = ["1", "2"]
    seed_cache.activities["default_finance_type"] = ["410", "110"]
    seed_cache.activities["default_flow_type"] = ["10", "10"]
    seed_cache.activities["default_aid_type"] = ["C01", "B01"]
    seed_cache.activities["default_tied_status"] = ["5", "4"]
    data_mod._cache["dataframe:budgets"] = pd.DataFrame(
        [
            {
                "activity_identifier": "IATI-001",
                "budget_type": "1",
                "budget_status": "1",
                "period_start": "2024-01-01",
                "period_end": "2024-12-31",
                "value": 2000.0,
                "currency": "USD",
                "value_date": "2024-01-01",
            }
        ]
    )


def test_financial_rankings_and_execution(seed_cache):
    _seed_extended(seed_cache)
    assert _table(advanced.totals_by_year())
    assert _rows(advanced.top_funders())[0]["Organisation"] == "Fund A"
    assert _rows(advanced.top_receivers())[0]["Organisation"] == "Ministry"
    gap_result = advanced.execution_gap()
    assert _rows(gap_result)[0]["Execution ratio"] == "50.0%"
    assert "unpaid gap 750.00" in gap_result.content[0].text
    assert _table(advanced.top_activities("budget"))


def test_breakdowns_geography_and_humanitarian(seed_cache):
    _seed_extended(seed_cache)
    breakdown = _rows(advanced.funding_breakdown("finance_type"))
    assert breakdown
    assert "Finance Type code" in breakdown[0]
    assert "Finance Type" in breakdown[0]
    assert _table(advanced.funding_by_country())
    assert _table(advanced.funding_by_sector(vocabulary="99"))
    assert _table(advanced.humanitarian_split())


def test_budget_and_organisation_queries(seed_cache):
    _seed_extended(seed_cache)
    assert _table(advanced.budget_vs_spend("IATI-001", 2024))
    assert _table(advanced.activities_by_organisation("Ministry"))


def test_accountability_tables(seed_cache):
    _seed_extended(seed_cache)
    data_mod._cache["dataframe:documents"] = pd.DataFrame(
        [
            {
                "activity_identifier": "IATI-001",
                "url": "https://example.org/a.pdf",
                "format": "application/pdf",
                "title": "Contract",
                "description": "",
                "category_code": "A06",
                "language_code": "en",
                "document_date": "2024-01-01",
            }
        ]
    )
    data_mod._cache["dataframe:contact_info"] = pd.DataFrame(
        [
            {
                "activity_identifier": "IATI-001",
                "contact_type": "1",
                "organisation": "Bank",
                "department": "Projects",
                "person_name": "Jane",
                "job_title": "Lead",
                "telephone": "123",
                "email": "jane@example.org",
                "website": "https://example.org",
                "mailing_address": "Address",
            }
        ]
    )
    document = _rows(advanced.activity_documents("IATI-001"))[0]
    assert document["Category code"] == "A06"
    assert document["Category"] == "Summary information about contract"
    contact = _rows(advanced.activity_contacts("IATI-001"))[0]
    assert contact["Contact type code"] == "1"
    assert contact["Contact type"] == "General Enquiries"
    assert _table(advanced.activity_full_record("IATI-001", ["documents", "contacts"]))
