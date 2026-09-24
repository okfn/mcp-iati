"""
Plugin registration: expected tools, glossary in the instructions and the
`no_tool_disponible` fallback message (uses `fake_mcp` from conftest.py).
"""

import pytest

from mcp_iati import register_tools
from mcp_iati.activities import queries
from mcp_iati.config import get_settings
from mcp_iati.glossary import (
    TOOL_GLOSSARY_TERMS,
    tool_glossary_text,
)


@pytest.fixture(autouse=True)
def reset_dataset_setting(monkeypatch):
    """Keep generic plugin-description tests independent of shell settings."""
    monkeypatch.delenv("MCP_IATI_DATASET", raising=False)
    monkeypatch.delenv("MCP_IATI_XML_PATH", raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


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
        "count_activities_by",
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


def test_plugin_sample_questions_quote_values_from_the_loaded_data(fake_mcp, seed_cache):
    register_tools(fake_mcp)

    questions = fake_mcp.plugin_info["sample_questions"]
    # IATI-001 is the only activity in implementation (Argentina, Transport)
    # and the one with the most transactions.
    assert (
        'Which activities in Argentina in the sector "Transport" are still in implementation?'
        in questions
    )
    assert "Give me a summary of activity IATI-001" in questions
    assert not any("XI-IATI-IADB-BR-L1231" in question for question in questions)


def test_plugin_sample_questions_are_specific_to_caf(fake_mcp, seed_cache, monkeypatch):
    monkeypatch.setenv("MCP_IATI_DATASET", "caf-actfile-46008-2603")
    get_settings.cache_clear()

    register_tools(fake_mcp)

    questions = fake_mcp.plugin_info["sample_questions"]
    assert "What does the CAF activity file contain?" in questions
    assert 'Which CAF activities in Argentina in the sector "Transport" are still in implementation?' in questions
    assert "Give me a summary of CAF activity IATI-001." in questions
    assert "What does this IATI file contain?" in questions


def test_plugin_sample_questions_detect_a_local_caf_file(fake_mcp, seed_cache, monkeypatch):
    monkeypatch.setenv("MCP_IATI_XML_PATH", "/data/CAF-ActivityFile.xml")
    get_settings.cache_clear()

    register_tools(fake_mcp)

    questions = fake_mcp.plugin_info["sample_questions"]
    assert "What does the CAF activity file contain?" in questions


def test_plugin_sample_questions_fall_back_when_no_data_is_loaded(fake_mcp, monkeypatch):
    # When the data cannot be read the defaults keep the plugin registering
    # normally (sample questions are cosmetic).
    def unavailable():
        raise FileNotFoundError("no IATI data")

    monkeypatch.setattr(queries, "activities_df", unavailable)

    register_tools(fake_mcp)

    questions = fake_mcp.plugin_info["sample_questions"]
    assert "Give me a summary of activity XI-IATI-IADB-BR-L1231" in questions
    assert 'Which activities in Brazil in the sector "health" are still in implementation?' in questions


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
