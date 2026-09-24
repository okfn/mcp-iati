"""Loads a real IATI activities XML into flat pandas DataFrames.

Genericity note: this module works with ANY IATI 2.x activities XML, not just
the default sample - the columns it reads (activity_identifier,
transaction_type, value, ...) come straight from the IATI standard, produced
by okfn_iati's `IatiMultiCsvConverter.xml_to_csv_folder()`.

The XML files are NOT stored in this repo: on first use the configured file
is downloaded from the IADB's official IATI hosting
(https://webimages.iadb.org/iati/, the same URLs the IATI Dashboard indexes;
the bank refreshes them monthly) into a per-user data directory. Pick a
different country file with MCP_IATI_SAMPLE (e.g. `iadb-Argentina.xml`), set
MCP_IATI_XML_URL for any other publisher's XML, set MCP_IATI_DATASET to a
dataset short name from the IATI Dashboard (the XML URL is then resolved
through its API, so publishers that rename their files on every release keep
working), or set MCP_IATI_XML_PATH to use a local file with no download at
all.
"""
import hashlib
import json
import os
import shutil
import tempfile
import time
import urllib.error
import urllib.request
import warnings
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
from okfn_iati import IatiMultiCsvConverter

from mcp_iati.config import get_settings

# Official IADB IATI files (a few MB each), hosted by the publisher itself
# and downloaded on demand. These are the URLs the IATI registry indexes.
_SAMPLES_BASE_URL = "https://webimages.iadb.org/iati"
_cache: dict = {}

# These CSVs are required for the tools to work; if they are missing, the
# conversion failed or the XML is not a valid IATI activities file.
REQUIRED_TOOL_CSVS = (
    "activities.csv",
    "transactions.csv",
    "sectors.csv",
)


DATAFRAME_SPECS = {
    "activities": {
        "filename": "activities.csv",
        "required_columns": (
            "activity_identifier",
            "title",
            "activity_status",
            "reporting_org_name",
            "reporting_org_ref",
            "default_currency",
            "recipient_country_code",
            "recipient_country_name",
        ),
        "numeric_columns": (),
    },
    "transactions": {
        "filename": "transactions.csv",
        "required_columns": (
            "activity_identifier",
            "transaction_type",
            "transaction_date",
            "value",
            "currency",
            "description",
        ),
        "numeric_columns": ("value",),
    },
    "sectors": {
        "filename": "sectors.csv",
        "required_columns": (
            "activity_identifier",
            "sector_code",
            "sector_name",
            "vocabulary",
            "percentage",
        ),
        "numeric_columns": ("percentage",),
    },
    # Optional: activity-date elements land here (some publishers report
    # dates only this way, leaving the activities.csv date columns empty).
    "activity_dates": {
        "filename": "activity_date.csv",
        "required_columns": (
            "activity_identifier",
            "type",
            "iso_date",
        ),
        "numeric_columns": (),
        "optional": True,
    },
    # Optional: participating-org elements are not guaranteed in every IATI
    # file, so a missing CSV yields an empty table instead of an error.
    "participating_orgs": {
        "filename": "participating_orgs.csv",
        "required_columns": (
            "activity_identifier",
            "org_ref",
            "org_name",
            "org_type",
            "role",
        ),
        "numeric_columns": (),
        "optional": True,
    },
}


TABLE_RELATIONSHIPS = {
    "transactions.activity_identifier": (
        "activities.activity_identifier"
    ),
    "sectors.activity_identifier": (
        "activities.activity_identifier"
    ),
}


def _cache_is_fresh(path: Path) -> bool:
    """Return whether a cached file is still inside the configured TTL."""
    if not path.exists():
        return False
    age_seconds = max(0, time.time() - path.stat().st_mtime)
    return age_seconds < get_settings().cache_ttl_seconds


def _download_xml(url: str, filename: str) -> Path:
    """Download an XML source unless a fresh cached copy exists."""
    target = get_settings().ensure_data_dir() / "xml" / filename
    if _cache_is_fresh(target):
        return target
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            content = resp.read()
    except (urllib.error.URLError, OSError) as exc:
        if target.exists():
            warnings.warn(
                f"Could not refresh IATI XML from {url}; using the stale "
                f"cached copy at {target}: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )
            return target
        raise FileNotFoundError(
            f"Could not download IATI XML from {url} ({exc}). Check "
            "MCP_IATI_XML_URL or MCP_IATI_SAMPLE, or set MCP_IATI_XML_PATH "
            "to a local file."
        ) from exc
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=target.parent,
            prefix=f".{target.name}-",
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)
        temporary_path.replace(target)
    finally:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
    return target


def _download_sample(name: str) -> Path:
    """Download a named IADB country file from the bank's IATI hosting."""
    if not name or Path(name).name != name or name in {".", ".."}:
        raise ValueError(
            "MCP_IATI_SAMPLE must be a filename without directory components."
        )
    url = f"{_SAMPLES_BASE_URL}/{name}"
    return _download_xml(url, name)


def _download_configured_url(url: str) -> Path:
    """Download a custom URL using a source-specific local filename."""
    source_name = Path(urlparse(url).path).name or "source.xml"
    source_hash = hashlib.sha256(url.encode()).hexdigest()[:12]
    return _download_xml(url, f"{source_hash}-{source_name}")


def _dataset_api_url(short_name: str) -> str:
    """Dashboard API endpoint describing one dataset (its current XML URL)."""
    return f"{get_settings().dashboard_api_url}/datasets/{short_name}/"


def _fetch_dataset_source_url(short_name: str) -> str:
    """Ask the IATI Dashboard which XML URL a dataset currently points at."""
    request = urllib.request.Request(
        _dataset_api_url(short_name),
        headers={
            "Accept": "application/json",
            "User-Agent": "mcp-iati (+https://github.com/okfn/mcp-iati)",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as resp:
        payload = json.load(resp)
    source_url = payload.get("source_url") if isinstance(payload, dict) else None
    if not source_url or urlparse(source_url).scheme not in {"http", "https"}:
        raise ValueError(
            f"Dashboard dataset {short_name!r} has no usable source_url: {payload!r}"
        )
    return source_url


def dataset_source_url(short_name: str) -> str:
    """Resolve a Dashboard dataset short name to its published XML URL.

    Publishers such as CAF rename the file on every release (the date is
    part of the filename), so the URL is looked up through the Dashboard
    API instead of being configured by hand. The resolved URL is cached on
    disk with the same TTL as the XML itself; when the Dashboard cannot be
    reached, the last resolved URL is reused so a running deployment keeps
    serving (the XML download has its own stale-copy fallback).
    """
    cached = _cache.get("dataset_source_url")
    if cached and cached[0] == short_name:
        return cached[1]
    target = get_settings().ensure_data_dir() / "xml" / f"{short_name}.source-url"
    if _cache_is_fresh(target):
        url = target.read_text().strip()
    else:
        try:
            url = _fetch_dataset_source_url(short_name)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            if not target.exists():
                raise FileNotFoundError(
                    f"Could not resolve IATI dataset {short_name!r} through "
                    f"{_dataset_api_url(short_name)} ({exc}). Check "
                    "MCP_IATI_DATASET, or set MCP_IATI_XML_URL / "
                    "MCP_IATI_XML_PATH instead."
                ) from exc
            url = target.read_text().strip()
            warnings.warn(
                f"Could not refresh the XML URL of IATI dataset {short_name!r}; "
                f"using the last resolved URL {url}: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(url + "\n")
    _cache["dataset_source_url"] = (short_name, url)
    return url


def xml_path() -> Path:
    """Path to the IATI XML file to load.

    MCP_IATI_XML_PATH points at a local file (no download). If it is absent,
    MCP_IATI_XML_URL can point at a remote XML, or MCP_IATI_DATASET at a
    dataset registered in the IATI Dashboard (its XML URL is resolved through
    the Dashboard API). Otherwise the sample named by MCP_IATI_SAMPLE is
    fetched from the IADB hosting on first use.
    """
    settings = get_settings()
    if settings.xml_path:
        return settings.xml_path
    if settings.xml_url:
        return _download_configured_url(settings.xml_url)
    if settings.dataset:
        return _download_configured_url(dataset_source_url(settings.dataset))
    return _download_sample(settings.sample)


def xml_source() -> str:
    """Return the original configured source used by tool responses."""
    settings = get_settings()
    if settings.xml_path:
        return str(settings.xml_path)
    if settings.xml_url:
        return settings.xml_url
    if settings.dataset:
        return dataset_source_url(settings.dataset)
    return f"{_SAMPLES_BASE_URL}/{settings.sample}"


def _source_cache_key() -> str:
    """Return a stable cache key for the configured XML origin."""
    settings = get_settings()
    if settings.xml_path:
        source = f"path:{settings.xml_path.resolve()}"
    elif settings.xml_url:
        source = f"url:{settings.xml_url}"
    elif settings.dataset:
        # Keyed by dataset, not by the resolved URL: a renamed release lands
        # as a newer XML file, which already invalidates the CSV cache.
        source = f"dataset:{settings.dataset}"
    else:
        source = f"sample:{settings.sample}"
    return hashlib.sha256(source.encode()).hexdigest()[:16]


def _csv_cache_is_complete(folder: Path) -> bool:
    """Return whether the CSV cache contains all files required by the tools."""
    required_files = (
        *(folder / filename for filename in REQUIRED_TOOL_CSVS),
        folder / ".complete",
    )
    return all(path.is_file() for path in required_files)


def _csv_cache_is_fresh(
    folder: Path,
    source_path: Path | None = None,
) -> bool:
    """Return whether a complete CSV cache is still valid."""
    marker = folder / ".complete"

    if not _csv_cache_is_complete(folder):
        return False
    if not _cache_is_fresh(marker):
        return False
    if source_path and not source_path.exists():
        return False

    return (
        source_path is None
        or marker.stat().st_mtime >= source_path.stat().st_mtime
    )


def _clear_expired_memory_cache() -> None:
    """Drop in-process data when their disk cache has expired."""
    if _cache.get("using_stale_csv"):
        # Stale mode pins the last complete cache so tool calls do not
        # retry an expensive conversion on every request. Retry once per
        # configured interval instead of never, so a transient failure
        # does not pin stale data until the process restarts.
        stale_since = _cache.get("stale_since", 0)
        retry_after = get_settings().stale_retry_seconds
        if time.time() - stale_since < retry_after:
            return
        _cache.clear()
        return

    cached_folder = _cache.get("csv_folder")
    local_source = get_settings().xml_path

    if cached_folder and not _csv_cache_is_fresh(
        Path(cached_folder),
        local_source,
    ):
        _cache.clear()


def _replace_csv_cache(tmp_dir: Path, cache_dir: Path) -> None:
    """Atomically replace a CSV cache while preserving rollback data."""
    backup_dir = cache_dir.with_name(f".{cache_dir.name}.previous")

    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    if cache_dir.exists():
        cache_dir.rename(backup_dir)

    try:
        tmp_dir.rename(cache_dir)
    except Exception:
        if backup_dir.exists() and not cache_dir.exists():
            backup_dir.rename(cache_dir)
        raise
    else:
        if backup_dir.exists():
            shutil.rmtree(backup_dir)


def _csv_folder() -> Path:
    """Return fresh, source-specific CSVs, converting the XML when needed."""
    _clear_expired_memory_cache()
    if "csv_folder" not in _cache:
        path = xml_path()
        if not path.exists():
            raise FileNotFoundError(
                f"IATI XML not found at {path}. "
                "Set MCP_IATI_XML_PATH to a valid file."
            )
        csv_parent = get_settings().ensure_data_dir() / "csv"
        csv_parent.mkdir(parents=True, exist_ok=True)
        cache_key = _source_cache_key()
        cache_dir = csv_parent / cache_key
        if _csv_cache_is_fresh(cache_dir, path):
            _cache["csv_folder"] = cache_dir
            return cache_dir

        tmp_dir = Path(
            tempfile.mkdtemp(prefix=f"{cache_key}-", dir=csv_parent)
        )

        try:
            converter = IatiMultiCsvConverter()

            if not converter.xml_to_csv_folder(path, tmp_dir):
                raise RuntimeError(
                    f"Failed to convert {path} to CSV: "
                    f"{converter.latest_errors}"
                )

            missing_files = [
                filename
                for filename in REQUIRED_TOOL_CSVS
                if not (tmp_dir / filename).is_file()
            ]
            if missing_files:
                missing = ", ".join(missing_files)
                raise RuntimeError(
                    "IATI conversion did not produce the required CSVs "
                    f"for {path}: {missing}"
                )

            (tmp_dir / ".complete").touch()
            _replace_csv_cache(tmp_dir, cache_dir)

        except Exception as error:
            if _csv_cache_is_complete(cache_dir):
                warnings.warn(
                    "Could not refresh IATI CSV cache from "
                    f"{xml_source()}; using the last complete cache "
                    f"at {cache_dir}: {error}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                _cache["csv_folder"] = cache_dir
                _cache["using_stale_csv"] = True
                _cache["stale_since"] = time.time()
                return cache_dir

            raise RuntimeError(
                "Could not create IATI CSV cache from "
                f"{xml_source()}: {error}"
            ) from error

        finally:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)

        _cache.pop("using_stale_csv", None)
        _cache.pop("stale_since", None)
        _cache["csv_folder"] = cache_dir
    return _cache["csv_folder"]


def prepare_data() -> Path:
    """Prepare and validate the configured IATI data before serving tools."""
    source = xml_source()

    try:
        folder = _csv_folder()
    except (FileNotFoundError, RuntimeError) as error:
        raise RuntimeError(
            f"Could not prepare IATI data from {source}: {error}"
        ) from error

    missing_files = [
        filename
        for filename in REQUIRED_TOOL_CSVS
        if not (folder / filename).exists()
    ]
    if missing_files:
        missing = ", ".join(missing_files)
        raise RuntimeError(
            f"IATI data from {source} is missing required CSV files: "
            f"{missing}"
        )

    generated_csvs = sorted(path.name for path in folder.glob("*.csv"))

    print(
        f"IATI data prepared from {source}: "
        f"{len(generated_csvs)} CSV files in {folder}"
    )

    return folder


def _dataframe(table_name: str) -> pd.DataFrame:
    """Load, validate and share a configured CSV as a pandas DataFrame."""
    try:
        spec = DATAFRAME_SPECS[table_name]
    except KeyError as error:
        raise ValueError(
            f"Unknown IATI CSV table: {table_name}"
        ) from error

    cache_key = f"dataframe:{table_name}"
    _clear_expired_memory_cache()

    if cache_key in _cache:
        return _cache[cache_key]

    csv_path = _csv_folder() / spec["filename"]
    if spec.get("optional") and not csv_path.is_file():
        dataframe = pd.DataFrame(
            columns=list(spec["required_columns"])
        )
        _cache[cache_key] = dataframe
        return dataframe
    dataframe = pd.read_csv(csv_path, dtype=str)

    missing_columns = [
        column
        for column in spec["required_columns"]
        if column not in dataframe.columns
    ]
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise RuntimeError(
            f"{spec['filename']} is missing required columns: "
            f"{missing}"
        )

    for column in spec["numeric_columns"]:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    _cache[cache_key] = dataframe
    return _cache[cache_key]


def activities_df() -> pd.DataFrame:
    """Return the shared activities DataFrame."""
    return _dataframe("activities")


def transactions_df() -> pd.DataFrame:
    """Return the shared transactions DataFrame."""
    return _dataframe("transactions")


def sectors_df() -> pd.DataFrame:
    """Return the shared sectors DataFrame."""
    return _dataframe("sectors")


def participating_orgs_df() -> pd.DataFrame:
    """Return the shared participating organisations DataFrame."""
    return _dataframe("participating_orgs")


def activity_dates_df() -> pd.DataFrame:
    """Return the shared activity dates DataFrame."""
    return _dataframe("activity_dates")
