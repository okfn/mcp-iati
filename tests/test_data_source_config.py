import os
import time
import urllib.error
from pathlib import Path
from types import SimpleNamespace

import pytest

from mcp_iati.activities import data


def test_local_path_keeps_priority_over_url_and_sample(monkeypatch):
    local_path = Path("/data/local.xml")
    settings = SimpleNamespace(
        xml_path=local_path,
        xml_url="https://example.org/remote.xml",
        dataset=None,
        sample="iadb-Argentina.xml",
    )
    monkeypatch.setattr(data, "get_settings", lambda: settings)

    assert data.xml_path() == local_path


def test_custom_url_has_priority_over_sample(monkeypatch):
    downloaded_path = Path("/data/downloaded.xml")
    settings = SimpleNamespace(
        xml_path=None,
        xml_url="https://example.org/remote.xml",
        dataset=None,
        sample="iadb-Argentina.xml",
    )
    monkeypatch.setattr(data, "get_settings", lambda: settings)
    monkeypatch.setattr(
        data,
        "_download_configured_url",
        lambda url: downloaded_path,
    )

    assert data.xml_path() == downloaded_path


def test_sample_download_is_preserved_as_fallback(monkeypatch):
    downloaded_path = Path("/data/iadb-Brazil.xml")
    settings = SimpleNamespace(
        xml_path=None,
        xml_url=None,
        dataset=None,
        sample="iadb-Brazil.xml",
    )
    monkeypatch.setattr(data, "get_settings", lambda: settings)
    monkeypatch.setattr(
        data,
        "_download_sample",
        lambda sample: downloaded_path,
    )

    assert data.xml_path() == downloaded_path


def test_custom_urls_generate_source_specific_names(monkeypatch):
    first_url = "https://one.example.org/activities.xml"
    second_url = "https://two.example.org/activities.xml"
    filenames = []
    monkeypatch.setattr(
        data,
        "_download_xml",
        lambda url, filename: filenames.append(filename) or Path(filename),
    )

    data._download_configured_url(first_url)
    data._download_configured_url(second_url)

    assert filenames[0] != filenames[1]
    assert filenames[0].endswith("-activities.xml")
    assert filenames[1].endswith("-activities.xml")


def _dataset_settings(tmp_path):
    return SimpleNamespace(
        xml_path=None,
        xml_url=None,
        dataset="caf-actfile-46008-2603",
        sample="iadb-Brazil.xml",
        dashboard_api_url="https://dashboard.example.org/api",
        data_dir=tmp_path,
        cache_ttl_seconds=3600,
        stale_retry_seconds=60,
        ensure_data_dir=lambda: tmp_path,
    )


def test_dataset_is_resolved_through_the_dashboard_api(monkeypatch, tmp_path):
    settings = _dataset_settings(tmp_path)
    monkeypatch.setattr(data, "get_settings", lambda: settings)
    data._cache.clear()
    requested = []

    def fake_fetch(short_name):
        requested.append(short_name)
        return "https://files.example.org/CAF-ActivityFile-2026-09-09v2.xml"

    monkeypatch.setattr(data, "_fetch_dataset_source_url", fake_fetch)
    downloaded = []
    monkeypatch.setattr(
        data,
        "_download_configured_url",
        lambda url: downloaded.append(url) or Path("/data/caf.xml"),
    )

    assert data.xml_path() == Path("/data/caf.xml")
    assert data.xml_source() == "https://files.example.org/CAF-ActivityFile-2026-09-09v2.xml"
    assert downloaded == ["https://files.example.org/CAF-ActivityFile-2026-09-09v2.xml"]
    # Resolved once, then served from memory and from the on-disk copy.
    assert requested == ["caf-actfile-46008-2603"]
    cached = tmp_path / "xml" / "caf-actfile-46008-2603.source-url"
    assert cached.read_text().strip() == "https://files.example.org/CAF-ActivityFile-2026-09-09v2.xml"
    data._cache.clear()
    assert data.xml_source() == "https://files.example.org/CAF-ActivityFile-2026-09-09v2.xml"
    assert requested == ["caf-actfile-46008-2603"]


def test_dataset_falls_back_to_last_resolved_url_when_dashboard_is_down(monkeypatch, tmp_path):
    settings = _dataset_settings(tmp_path)
    settings.cache_ttl_seconds = 1
    monkeypatch.setattr(data, "get_settings", lambda: settings)
    data._cache.clear()
    cached = tmp_path / "xml" / "caf-actfile-46008-2603.source-url"
    cached.parent.mkdir(parents=True)
    cached.write_text("https://files.example.org/old-release.xml\n")
    stale_time = time.time() - 10
    os.utime(cached, (stale_time, stale_time))

    def failing_fetch(short_name):
        raise urllib.error.URLError("dashboard unreachable")

    monkeypatch.setattr(data, "_fetch_dataset_source_url", failing_fetch)

    with pytest.warns(RuntimeWarning, match="last resolved URL"):
        assert data.xml_source() == "https://files.example.org/old-release.xml"


def test_unresolvable_dataset_without_cache_is_an_error(monkeypatch, tmp_path):
    settings = _dataset_settings(tmp_path)
    monkeypatch.setattr(data, "get_settings", lambda: settings)
    data._cache.clear()

    def failing_fetch(short_name):
        raise urllib.error.HTTPError(
            data._dataset_api_url(short_name), 404, "Not Found", {}, None
        )

    monkeypatch.setattr(data, "_fetch_dataset_source_url", failing_fetch)

    with pytest.raises(FileNotFoundError, match="MCP_IATI_DATASET"):
        data.xml_source()


def test_dataset_cache_key_ignores_the_resolved_url(monkeypatch, tmp_path):
    settings = _dataset_settings(tmp_path)
    monkeypatch.setattr(data, "get_settings", lambda: settings)

    assert data._source_cache_key() == data._source_cache_key()
    settings.dataset = "another-dataset"
    other_key = data._source_cache_key()
    settings.dataset = "caf-actfile-46008-2603"
    assert other_key != data._source_cache_key()
