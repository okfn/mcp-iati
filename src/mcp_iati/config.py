"""Environment-based configuration for MCP IATI data files."""

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from platformdirs import user_data_path


APP_NAME = "mcp-iati"
DEFAULT_SAMPLE = "iadb-Brazil.xml"
# Public API of the IATI Dashboard, which replaced the CKAN-based IATI
# Registry in December 2025 and is now the source of truth for publishers
# and their data files (https://dashboard.iatistandard.org/api/). Used to
# resolve MCP_IATI_DATASET (a dataset short name such as
# `caf-actfile-46008-2603`) to the XML URL currently published for it.
DEFAULT_DASHBOARD_API_URL = "https://dashboard.iatistandard.org/api"
# IATI publications are typically updated yearly (or at most quarterly),
# so a monthly refresh of the downloaded XML and its derived CSVs is
# plenty. Override with MCP_IATI_CACHE_TTL_SECONDS for livelier sources.
DEFAULT_CACHE_TTL_SECONDS = 30 * 24 * 60 * 60
DEFAULT_STALE_RETRY_SECONDS = 60 * 60


@dataclass(frozen=True)
class IatiSettings:
    """Configuration loaded once when the plugin process starts."""

    xml_path: Path | None
    xml_url: str | None
    dataset: str | None
    sample: str
    dashboard_api_url: str
    data_dir: Path
    cache_ttl_seconds: int
    stale_retry_seconds: int

    def ensure_data_dir(self) -> Path:
        """Create and return the configured data directory."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir


def _parse_positive_seconds(raw_value: str, variable_name: str) -> int:
    """Parse and validate a duration expressed in whole seconds."""
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValueError(
            f"{variable_name} must be an integer."
        ) from error

    if value <= 0:
        raise ValueError(
            f"{variable_name} must be greater than zero."
        )
    return value


def _parse_cache_ttl(raw_value: str) -> int:
    """Parse and validate the configured cache duration."""
    return _parse_positive_seconds(raw_value, "MCP_IATI_CACHE_TTL_SECONDS")


def _parse_dataset(raw_value: str | None) -> str | None:
    """Validate a Dashboard dataset short name (it becomes a cache filename)."""
    if raw_value is None:
        return None
    value = raw_value.strip()
    if not value:
        return None
    if not all(char.isalnum() or char in "._-" for char in value) or value in {".", ".."}:
        raise ValueError(
            "MCP_IATI_DATASET must be a Dashboard dataset short name "
            "(letters, digits, '.', '_' or '-'), e.g. caf-actfile-46008-2603."
        )
    return value


@lru_cache(maxsize=1)
def get_settings() -> IatiSettings:
    """Read settings once; environment changes apply after a restart."""
    raw_xml_path = os.environ.get("MCP_IATI_XML_PATH")
    raw_data_dir = os.environ.get("MCP_IATI_DATA_DIR")
    raw_cache_ttl = os.environ.get(
        "MCP_IATI_CACHE_TTL_SECONDS",
        str(DEFAULT_CACHE_TTL_SECONDS),
    )
    raw_stale_retry = os.environ.get(
        "MCP_IATI_STALE_RETRY_SECONDS",
        str(DEFAULT_STALE_RETRY_SECONDS),
    )

    return IatiSettings(
        xml_path=Path(raw_xml_path).expanduser() if raw_xml_path else None,
        xml_url=os.environ.get("MCP_IATI_XML_URL"),
        dataset=_parse_dataset(os.environ.get("MCP_IATI_DATASET")),
        sample=os.environ.get("MCP_IATI_SAMPLE", DEFAULT_SAMPLE),
        dashboard_api_url=os.environ.get(
            "MCP_IATI_DASHBOARD_API_URL",
            DEFAULT_DASHBOARD_API_URL,
        ).rstrip("/"),
        data_dir=(
            Path(raw_data_dir).expanduser()
            if raw_data_dir
            else user_data_path(APP_NAME)
        ),
        cache_ttl_seconds=_parse_cache_ttl(raw_cache_ttl),
        stale_retry_seconds=_parse_positive_seconds(
            raw_stale_retry,
            "MCP_IATI_STALE_RETRY_SECONDS",
        ),
    )
