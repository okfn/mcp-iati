"""
Plugin registration: expected tools, glossary in the instructions and the
`no_tool_disponible` fallback message (uses `fake_mcp` from conftest.py).
"""

import pytest

from mcp_iati import register_tools
from mcp_iati.glossary import (
    TOOL_GLOSSARY_TERMS,
    tool_glossary_text,
)


def test_register_tools_adds_expected_tools(fake_mcp):
    register_tools(fake_mcp)

    assert list(fake_mcp.tools) == [
        "no_tool_disponible",
        "file_overview",
        "date_coverage",
        "list_category_values",
        "search_activities",
        "filter_activities",
        "list_activity_statuses",
        "list_reporting_organisations",
        "list_participating_organisations",
        "list_recipient_countries",
        "filter_activities_by_country",
        "list_sectors",
        "filter_activities_by_sector",
        "filter_activities_by_participating_org",
        "activity_summary",
        "activity_transactions",
        "transaction_totals_by_year",
        "transaction_totals_by_organisation",
        "transaction_totals_by_sector",
        "transaction_totals_by_country",
        "top_activities_by_amount",
        "define_term",
    ]


def test_plugin_info_has_user_facing_display_name(fake_mcp):
    register_tools(fake_mcp)

    assert fake_mcp.plugin_info["display_name"] == "Explore IATI Data"


def test_plugin_instructions_request_only_relevant_terms(fake_mcp):
    register_tools(fake_mcp)

    instructions = fake_mcp.plugin_info["instructions"]

    assert "only the IATI terms relevant" in instructions
    assert "do not add unrelated glossary entries" in instructions
    assert "call define_term" in instructions
    assert "IATI glossary:\n" not in instructions


def test_plugin_sample_questions_cover_main_use_cases(fake_mcp):
    register_tools(fake_mcp)

    questions = fake_mcp.plugin_info["sample_questions"]
    assert "What does this IATI file contain?" in questions


def test_no_tool_disponible_returns_clear_fallback_message(fake_mcp):
    register_tools(fake_mcp)

    result = fake_mcp.tools["no_tool_disponible"]("not a question about IATI activities")

    assert result.structuredContent == {"sources": []}
    text = result.content[0].text
    assert "only answers questions about the loaded IATI activities" in text
    assert "Reason: not a question about IATI activities." in text

@pytest.mark.parametrize(
    "tool_name",
    TOOL_GLOSSARY_TERMS,
)
def test_tool_descriptions_use_central_glossary(fake_mcp, tool_name):
    register_tools(fake_mcp)

    description = fake_mcp.tools[tool_name].__doc__
    expected = tool_glossary_text(tool_name)

    assert expected
    assert expected in description

def test_tool_description_excludes_unrelated_terms(fake_mcp):
    register_tools(fake_mcp)

    description = fake_mcp.tools["list_sectors"].__doc__

    assert "Sector:" in description
    assert "Vocabulary:" in description
    assert "Commitment:" not in description
    assert "Disbursement:" not in description
