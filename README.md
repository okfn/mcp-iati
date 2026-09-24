# MCP IATI

**Note:** Local proof of concept. Starting point for a future `mcp-server`
plugin that processes files following the
[IATI](https://iatistandard.org/) standard (activities and organisations):
documented Python tools, with `plugin_info`/`instructions`/`sample_questions`,
a `no_tool_disponible` fallback tool and a tools module separate from the
registration wiring.

It defines tools for exploring activities, organisations, recipient countries,
sectors and transactions from a configured IATI XML.

Available tools:

- `search_activities(text, limit=10)`: search activities by text in their
  title, description, sector names or participating organisation names,
  reporting where each match was found.
- `list_activity_statuses()`: list available activity statuses and counts.
- `list_reporting_organisations()`: list reporting organisations and their
  number of activities.
- `list_participating_organisations(limit=100)`: list all participating
  organisations with their roles, ordered by number of activities.
- `filter_activities(country, sector, organisation, status, text, limit=300)`:
  filter activities by any combination of recipient country, sector,
  participating organisation, activity status and title/description text
  (all optional, activities must satisfy every supplied one). Each value is
  resolved against the loaded data before filtering, and the response says
  how it matched and to which published value it resolved; when a value
  cannot be resolved, the response names the failing filter and lists the
  values available so the model can retry with an exact one. Country names
  in English, Spanish, Portuguese or French ("Brasil", "Bresil") are mapped
  to the ISO code (`activities/country_aliases.py`), so they match a file
  that only says "Brazil". The three `filter_activities_by_*` tools below
  are thin wrappers over this one.
- `list_recipient_countries()`: list recipient countries and activity counts.
- `filter_activities_by_country(country, limit=10)`: filter activities by
  recipient-country code or name.
- `list_sectors(limit=100, country=None, organisation=None, status=None)`:
  list sector codes, names and vocabularies with activity counts, optionally
  restricted to the activities matching the filters ("which sectors do the
  activities in Argentina cover?"). Missing names for OECD DAC codes
  (vocabulary 1) are filled in from the standard DAC codelist.
- `filter_activities_by_sector(sector, limit=10)`: filter activities by
  sector code or name (exact code first, then exact name, then name
  substring); on no match, the response lists the sectors available in the
  loaded data.
- `filter_activities_by_participating_org(organisation, limit=10)`: filter
  activities by participating organisation reference or name (exact
  reference first, then exact name, then a fallback combining name
  substrings with closely similar names, to cope with misspelled published
  names), reporting each organisation's role and which match kind applied;
  on no match, the response lists the organisations available in the
  loaded data.

Text matching in the search and filter tools ignores case and accents,
while responses always show the names exactly as published.
- `activity_summary(iati_identifier)`: show the main details of one activity:
  title, status, description, dates, recipient country, sectors, reporting
  and participating organisations (with their roles), default
  classifications and financial totals per transaction type.
- `activity_transactions(iati_identifier, limit=50)`: list an activity's
  transactions in chronological order.
- `transaction_totals_by_year(year_from=None, year_to=None, country=None, sector=None, organisation=None, status=None)`:
  group commitment and disbursement totals by year, transaction type and
  currency, while ignoring invalid dates/values and using the activity
  default currency when a transaction currency is missing.
- `transaction_totals_by_organisation(limit=50)`: group commitments and
  disbursements by reporting organisation, keeping transaction types and
  currencies separate and clarifying that the reporting organisation is the
  publisher of the activity data, not necessarily the funder or implementer.
- `transaction_totals_by_country(transaction_type="2", currency=None, limit=50, sector=None, organisation=None, status=None)`: group commitments and disbursements by recipient country, keeping transaction types and currencies separate and using a clear fallback label when country details are missing.
- `transaction_totals_by_sector(transaction_type="2", currency=None, vocabulary=None, limit=50, country=None, organisation=None, status=None)`: allocate commitment or disbursement totals across sectors using the published percentages, keeping vocabularies and currencies separate and adding an `Unallocated sector` bucket when percentages do not total 100%.
- `top_activities_by_amount(transaction_type="2", currency=None, limit=10, country=None, sector=None, organisation=None, status=None)`:
  list activities with the highest commitment or disbursement totals, ranked
  independently for each currency ("top 5 activities by commitment in
  Argentina" is `country="AR", limit=5`).
- `count_activities_by(group_by, country=None, sector=None, organisation=None, status=None, limit=50)`:
  the generic group-by: number of distinct activities per value of one
  dimension (`country`, `sector`, `organisation` or `status`), inside the
  optional filters on the other dimensions. "Sectors per country" is
  `count_activities_by("sector", country="AR")`; "countries where
  organisation X participates" is `count_activities_by("country",
  organisation="X")`. Returns a table and a bar chart.

The `country`, `sector`, `organisation` and `status` filters of the
aggregation tools above are resolved exactly like in `filter_activities`
(ISO code or name in several languages, sector code or name, organisation
reference or name, status code or label), and an unresolved value returns
the same "available values" message instead of an empty total.
- `define_term(term)`: explain an IATI term using the central glossary.

**Guiding principle:** these tools only use generic IATI standard fields
(identifiers, statuses, organisations, recipient countries, sectors and
transactions), never Brazil- or IADB-specific logic -
they must work just as well with any other IATI XML (see the configuration
variables below).

## Where the data comes from

The XML files are official IATI publications, **not versioned in this
repo**. By default they are the Inter-American Development Bank's, downloaded
on demand from the bank's own hosting at
[webimages.iadb.org/iati](https://webimages.iadb.org/iati/iadb-Brazil.xml)
(the same URLs the [IATI Dashboard](https://dashboard.iatistandard.org/publishers/iadb/)
indexes; the IADB refreshes them monthly) into the user data directory
(`~/.local/share/mcp-iati/xml/` on Linux, via `platformdirs`) and refreshed
when the configured TTL expires. The `.gitignore` excludes any `*.xml` just
in case.

Any other publisher works the same way. The public
[mcp.okfn.org/iati-caf/](https://mcp.okfn.org/iati-caf/) instance serves the
activity file of [CAF, Development Bank of Latin America and the
Caribbean](https://dashboard.iatistandard.org/publishers/caf/) through
`MCP_IATI_DATASET=caf-actfile-46008-2603` (see below).

### Finding a publisher's XML: the IATI Dashboard

The CKAN-based IATI Registry (`iatiregistry.org`) was replaced in December
2025 by [IATI Account](https://account.iatistandard.org/) (publishers manage
their files there) and the [IATI Dashboard](https://dashboard.iatistandard.org/)
(public, read-only metadata about every reporting organisation and dataset).
The Dashboard exposes a JSON API without authentication:

```bash
# one publisher and its dataset count
curl https://dashboard.iatistandard.org/api/reporting-orgs/caf/
# its datasets, each with the XML URL currently published (`source_url`)
curl "https://dashboard.iatistandard.org/api/datasets/?reporting_org__short_name=caf"
# one dataset
curl https://dashboard.iatistandard.org/api/datasets/caf-actfile-46008-2603/
```

Some publishers (CAF among them) put the release date in the XML filename,
so the URL changes with every update. `MCP_IATI_DATASET` takes the dataset
short name instead and resolves the current `source_url` through that API
on first use and whenever the cache TTL expires; the last resolved URL is
kept on disk so a Dashboard outage never stops a running server.

## How the XML is processed

1. `mcp_iati/activities/data.py` converts the configured XML to flat CSVs and
   reuses the source-specific cache until its TTL expires, using
   `okfn_iati.IatiMultiCsvConverter().xml_to_csv_folder(...)`
   (the same library `ckanext-iati-generator` uses in production, but in the
   XML -> CSV direction instead of CSV -> XML).
2. The tools (`mcp_iati/activities/queries.py`) query those CSVs with
   `pandas`, not the XML - this avoids reparsing a multi-MB file on every
   call.
3. It uses `iadb-Brazil.xml` by default. To use another official IADB
   country file, a dataset from the IATI Dashboard, a remote URL or a local
   file, without touching code:

   ```bash
   # another IADB country file from https://webimages.iadb.org/iati/
   export MCP_IATI_SAMPLE=iadb-Argentina.xml

   # or a dataset registered in the IATI Dashboard (CAF's activity file)
   export MCP_IATI_DATASET=caf-actfile-46008-2603

   # or any remote IATI XML
   export MCP_IATI_XML_URL=https://example.org/activities.xml

   # or any local file (downloads nothing)
   export MCP_IATI_XML_PATH=/path/to/another-iati-file.xml
   ```

   The plugin's sample questions quote a country, a sector and an activity
   taken from the loaded file, so they stay meaningful for any publisher.

## Configuration

Configuration is read once when the process starts. Restart the server after
changing the source, data directory or cache duration.

| Variable | Description | Default |
| --- | --- | --- |
| `MCP_IATI_XML_PATH` | Path to a local XML. It has priority and performs no download. | Not set. |
| `MCP_IATI_XML_URL` | HTTP(S) URL of a remote XML, used when no local path is configured. | Not set. |
| `MCP_IATI_DATASET` | Short name of a dataset in the IATI Dashboard (e.g. `caf-actfile-46008-2603`); its current XML URL is resolved through the Dashboard API. Used when neither a path nor a URL is configured. | Not set. |
| `MCP_IATI_DASHBOARD_API_URL` | Base URL of the IATI Dashboard API used to resolve `MCP_IATI_DATASET`. | `https://dashboard.iatistandard.org/api`. |
| `MCP_IATI_SAMPLE` | Name of an official IADB country file (from https://webimages.iadb.org/iati/), used when no path, URL or dataset is configured. | `iadb-Brazil.xml`. |
| `MCP_IATI_DATA_DIR` | Directory for downloaded XML files and generated CSV files. | User data directory provided by `platformdirs`. |
| `MCP_IATI_CACHE_TTL_SECONDS` | Configurable cache duration in seconds; must be greater than zero. | `2592000` (30 days; IATI files are typically updated yearly). |
| `MCP_IATI_STALE_RETRY_SECONDS` | How long to keep serving a stale CSV cache after a failed refresh before retrying the conversion; must be greater than zero. | `3600` (1 hour). |

Downloaded XML files and converted CSV folders are reused while they remain
inside this TTL. Once it expires, the XML is downloaded again and the CSVs
are regenerated. CSV caches use a key derived from the configured origin, so
Argentina, Brazil and custom URLs never share the same converted files.
If a remote refresh fails and a previous XML exists, that stale copy is used
with a runtime warning instead of making the tools unavailable.

The source precedence is:

1. `MCP_IATI_XML_PATH`.
2. `MCP_IATI_XML_URL`.
3. `MCP_IATI_DATASET`.
4. `MCP_IATI_SAMPLE`.
5. The default `iadb-Brazil.xml` sample.

Example:

```bash
export MCP_IATI_XML_URL=https://example.org/iadb-Argentina.xml
export MCP_IATI_DATA_DIR=/var/cache/mcp-iati
export MCP_IATI_CACHE_TTL_SECONDS=2592000
uv run mcp-server
```

### Local CAF chat with a private XML

The CAF chat runs as a **separate pair of processes** alongside the generic
IATI deployment. It reuses this plugin and the sibling `mcp-server` and
`mcp-chat-gateway` repositories; it does not require a code fork or changes
to the source-selection logic.

Keep the local XML outside Git in this repository under
`data-samples/caf/` (that directory and all XML files are ignored). Give CAF
its own cache directory so converted CSV tables can never be reused by another
deployment.

1. Copy `deploy/caf-mcp-server.env.example` to a private `deploy/caf-mcp-server.env`.
  Set `MCP_IATI_XML_PATH` to the actual CAF XML and use a CAF-only
  `MCP_IATI_DATA_DIR`.
2. In the sibling `mcp-server` repository, install this plugin in its virtual
  environment as described in [Adding this to a local mcp-server](#adding-this-to-a-local-mcp-server),
  then load the profile and start the HTTP server:

  ```bash
  set -a
  source ../mcp-iati/deploy/caf-mcp-server.env
  set +a
  uv run mcp-server
  ```

3. Copy `deploy/caf-chat-gateway.env.example` to a private
  `deploy/caf-chat-gateway.env`, set the AI provider credentials, and copy
  `deploy/gateway-overrides-caf.yaml` to
  `../mcp-chat-gateway/static/i18n/overrides.yaml`. Then start the separate
  gateway process from `mcp-chat-gateway`:

  ```bash
  set -a
  source ../mcp-iati/deploy/caf-chat-gateway.env
  set +a
  uv run python app.py
  ```

The example gateway profile uses port `8065`, leaving the generic chat's
default port `8064` untouched. For a production deployment, use externally
managed secrets and paths instead of committing either private `.env` file.

### CSV tables used by the plugin

| Table | Columns currently used | Relationship |
|---|---|---|
| `activities.csv` | `activity_identifier`, `title`, `activity_status`, `reporting_org_name`, `reporting_org_ref`, `default_currency`, `recipient_country_code`, `recipient_country_name` | `activity_identifier` identifies the activity |
| `transactions.csv` | `activity_identifier`, `transaction_type`, `transaction_date`, `value`, `currency`, `description` | `activity_identifier` references `activities.csv` |
| `sectors.csv` | `activity_identifier`, `sector_code`, `sector_name`, `vocabulary`, `percentage` | `activity_identifier` references `activities.csv` |
| `activity_date.csv` (optional) | `activity_identifier`, `type`, `iso_date` | `activity_identifier` references `activities.csv` |
| `participating_orgs.csv` (optional) | `activity_identifier`, `org_ref`, `org_name`, `org_type`, `role` | `activity_identifier` references `activities.csv` |

The CSV files are loaded as shared pandas DataFrames. Repeated tool
calls reuse the same instances and do not download the XML, run the
conversion or read the CSV files again. Optional tables yield an empty
DataFrame when their CSV is missing, instead of an error.

The data preparation and conversion logic is kept separate from the query
logic. Additional CSV tables can be added through `DATAFRAME_SPECS`.


## Development

```bash
# Install dependencies (mcp-server from git, okfn-iati from PyPI;
# the dev extra brings ruff and pytest)
uv sync --extra dev

# Lint
uv run ruff check src
```

## Adding this to a local mcp-server

From the `mcp-server/` folder, install this package into the same virtual
environment:

```bash
uv pip install -e ../mcp-iati
uv run mcp-server
```

The tools become available with the `mcp_iati_` prefix.

## Charts

Besides the table, some tools return Chart.js specs in
`structuredContent["charts"]`, which the chat gateway renders next to the
answer (same contract as the Uruguay energy-balance plugin):

| Tool | Chart |
|------|-------|
| `transaction_totals_by_year` | grouped bars, commitments vs disbursements per year, one chart per currency |
| `transaction_totals_by_sector` | pie of the top 10 sectors plus "Other", one chart per vocabulary and currency |
| `list_activity_statuses` | pie of activities by status |
| `list_sectors` | bars of activities per sector, one chart per vocabulary |
| `list_participating_organisations` | bars of activities per organisation (the reporting organisation is left out of the chart) |
| `top_activities_by_amount` | bars of the largest activities, one chart per currency |
| `count_activities_by` | bars of activities per group value (sectors: one chart per vocabulary) |
| `activity_transactions` | cumulative lines per transaction type over time |

Currencies and sector vocabularies are never mixed in one chart, charts
with fewer than two points are skipped and a response carries at most
three charts. The builders live in `src/mcp_iati/helpers/charts.py`.

## Chat gateway branding

The plugin describes itself to MCP clients through the standard channels
of `mcp-server`: `set_plugin_info(description, instructions,
sample_questions)` in `src/mcp_iati/__init__.py` (plugin card, sample
question chips and the system prompt) and `[project.urls]` in
`pyproject.toml` (link badges on the card and in the tools drawer).

The shell of the chat gateway (site title, hero, tagline, footer) is not
plugin-aware; it uses generic copy unless a `static/i18n/overrides.yaml`
is present. `deploy/gateway-overrides.yaml` in this repo is that file with
IATI terms. To use it locally:

```bash
cp deploy/gateway-overrides.yaml ../mcp-chat-gateway/static/i18n/overrides.yaml
```

The deployment image fetches the same file from this repository, so
editing it here is enough to change the deployed site.

## IATI glossary

The tool descriptions and the plugin instructions share a central glossary
defined in `src/mcp_iati/glossary.py`. Its goal is that the model interprets
the standard's terms consistently and explains the distinctions that tend to
be ambiguous, especially between reporting, funding and implementing
organisations, and between commitment, disbursement and expenditure. The
`define_term` tool exposes it directly, so questions like "what does
'disbursement' mean?" are answered from the glossary (with the IATI standard
as the cited source) instead of from the model's own knowledge.

The glossary covers the whole IATI 2.03 activity standard as modelled by the
[okfn/okfn_iati](https://github.com/okfn/okfn_iati) library (its enums mirror
the IATI codelists and its converter flattens each element to a CSV), grouped
in these areas:

| Area | Terms |
| --- | --- |
| Identification and lifecycle | IATI activity, IATI identifier, activity status, activity date, description, hierarchy, related activity, activity scope, humanitarian flag |
| Organisations | reporting organisation, participating organisation, organisation role, organisation type, provider organisation, receiver organisation, contact information |
| Financial data | transaction, transaction type, transaction value, commitment, disbursement, expenditure, budget, planned disbursement, default currency, country budget item |
| Aid classifications | aid type, finance type, flow type, tied status, collaboration type, disbursement channel, policy marker |
| Sectors and geography | sector, recipient country or region, location |
| Results and monitoring | result, indicator, indicator period |
| Documentation and cross-cutting | document link, condition, vocabulary, codelist, narrative |

When adding a new tool, reuse the definitions from the central module
instead of duplicating them in its docstring (via `glossary_text(...)` for
the relevant terms). When the underlying library starts exposing a new IATI
element, add its term to the glossary in the matching group.

## Tests

```bash
uv run pytest
```

The tests run offline: `tests/conftest.py` preloads the data cache with
synthetic DataFrames and sets `MCP_IATI_XML_PATH`, so nothing is downloaded.
They cover:

- that the glossary includes the minimum concepts and that the tool
  descriptions expose the relevant terms to the model;
- regression of the queries (tables, sources, empty cases);
- the **raw-data contract** (`test_raw_data_in_ai_response.py`): the gateway
  sends the AI only the text of the response, so every tool that returns a
  table must embed it verbatim in that text (done by `helpers.text_result`).
  When adding a new tool with a table, add it to the `DATA_TOOLS` list in
  that test.

On GitHub, `.github/workflows/python-lint.yml` runs ruff + pytest on every
push.
