"""Country-name aliases for resolving user input to ISO 3166-1 alpha-2 codes.

IATI files publish the recipient country as an ISO code plus, optionally,
a narrative name in the publisher's language (the IADB files say
"Brazil"). Users and chat models ask in their own language ("Brasil",
"Brésil"), so matching by published name alone fails even when the
question is unambiguous.

The primary strategy is still the ISO code: the tool descriptions ask the
model to pass "BR" when it knows it, and codes are language-neutral. This
table is the second line: it maps common English, Spanish, Portuguese and
French names (accent- and case-insensitive, see `_fold_text` in
`queries.py`) to the code so the lookup is deterministic instead of relying
on fuzzy similarity ("brasil" vs "brazil" scores only 0.83 in difflib).

It covers the Americas (the default data comes from the IADB) plus the
countries that usually appear as donors or comparison points; extend it
when a new dataset needs more. It is not a full codelist.
"""

import unicodedata

# code -> names in English, Spanish, Portuguese and French, plus common
# short forms. The English name published by most IATI files is included so
# the alias path also works when the file omits the narrative name.
COUNTRY_ALIASES: dict[str, tuple[str, ...]] = {
    "AR": ("Argentina", "Argentine"),
    "BS": ("Bahamas", "The Bahamas"),
    "BB": ("Barbados", "Barbade"),
    "BZ": ("Belize", "Belice"),
    "BO": ("Bolivia", "Bolivie", "Estado Plurinacional de Bolivia"),
    "BR": ("Brazil", "Brasil", "Bresil", "Brésil"),
    "CA": ("Canada", "Canadá"),
    "CL": ("Chile", "Chili"),
    "CO": ("Colombia", "Colômbia", "Colombie"),
    "CR": ("Costa Rica",),
    "CU": ("Cuba",),
    "DO": (
        "Dominican Republic",
        "Republica Dominicana",
        "República Dominicana",
        "Republique Dominicaine",
    ),
    "EC": ("Ecuador", "Equador", "Equateur"),
    "SV": ("El Salvador", "Salvador"),
    "GT": ("Guatemala",),
    "GY": ("Guyana", "Guiana",),
    "HT": ("Haiti", "Haití", "Haïti"),
    "HN": ("Honduras",),
    "JM": ("Jamaica", "Jamaïque"),
    "MX": ("Mexico", "México", "Mexique"),
    "NI": ("Nicaragua", "Nicarágua"),
    "PA": ("Panama", "Panamá"),
    "PY": ("Paraguay", "Paraguai"),
    "PE": ("Peru", "Perú", "Pérou"),
    "PR": ("Puerto Rico", "Porto Rico"),
    "SR": ("Suriname", "Surinam"),
    "TT": ("Trinidad and Tobago", "Trinidad y Tobago", "Trinidad e Tobago"),
    "US": (
        "United States",
        "United States of America",
        "USA",
        "Estados Unidos",
        "Etats-Unis",
    ),
    "UY": ("Uruguay", "Uruguai"),
    "VE": ("Venezuela", "Republica Bolivariana de Venezuela"),
    "ES": ("Spain", "España", "Espanha", "Espagne"),
    "PT": ("Portugal",),
    "FR": ("France", "Francia", "França"),
    "DE": ("Germany", "Alemania", "Alemanha", "Allemagne"),
    "GB": ("United Kingdom", "Reino Unido", "Royaume-Uni", "Great Britain"),
    "IT": ("Italy", "Italia", "Itália", "Italie"),
    "JP": ("Japan", "Japon", "Japón", "Japão"),
    "CN": ("China", "Chine"),
    "KR": ("South Korea", "Korea", "Corea del Sur", "Coreia do Sul", "Corée du Sud"),
    "NL": ("Netherlands", "Paises Bajos", "Países Bajos", "Holanda", "Pays-Bas"),
    "CH": ("Switzerland", "Suiza", "Suíça", "Suisse"),
    "SE": ("Sweden", "Suecia", "Suécia", "Suède"),
    "NO": ("Norway", "Noruega", "Norvège"),
    "AO": ("Angola",),
    "MZ": ("Mozambique", "Moçambique"),
    "CV": ("Cape Verde", "Cabo Verde"),
    "TL": ("Timor-Leste", "East Timor", "Timor Leste"),
}


def _fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value))
    return "".join(
        char for char in normalized if not unicodedata.combining(char)
    ).casefold().strip()


# folded alias -> code, built once at import time.
_ALIAS_TO_CODE: dict[str, str] = {
    _fold(name): code
    for code, names in COUNTRY_ALIASES.items()
    for name in names
}


def country_code_for_name(name: str) -> str | None:
    """Return the ISO alpha-2 code for a country name in any listed language.

    The lookup ignores case and accents. Returns None when the name is not
    in the alias table, so callers fall through to their next strategy.
    """
    return _ALIAS_TO_CODE.get(_fold(name))
