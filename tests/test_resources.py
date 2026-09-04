"""Reference resources exposed by the IATI plugin."""

from mcp_iati import register_resources
from mcp_iati.terms import IATI_STANDARD_URL


def test_register_resources_adds_iati_standard_link(fake_mcp):
    register_resources(fake_mcp)

    resource = fake_mcp.resources["iati_standard"]
    assert resource["uri"] == "references/iati-standard"
    assert resource["name"] == "IATI Standard"
    assert resource["mime_type"] == "text/uri-list"
    assert resource["annotations"] == {
        "publisher": "IATI",
        "language": "en",
        "showcase_url": IATI_STANDARD_URL,
    }
    assert resource["handler"]() == IATI_STANDARD_URL + "\n"
