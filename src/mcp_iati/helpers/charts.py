"""Chart.js spec builders for IATI tool responses.

Tools pass the returned dicts through ``text_result(charts=[...])``; the base
server places them under ``structuredContent["charts"]`` and the chat
gateway renders each one with Chart.js (see ``static/chart/render.js`` in
mcp-chat-gateway). Supported shapes: ``pie`` (one dataset, one colour per
slice), ``bar`` (optionally ``stacked``) and ``line``.

The gateway only draws vertical bars, so long category labels are shortened
with ``short_label``; Chart.js tooltips still show the label as sent.

Mirrors the helper used by mcp-datos-uruguay-ben (``helpers/charts.py``),
without the per-dataset palette because IATI categories are open-ended.
"""

from collections.abc import Iterable, Sequence
from typing import Any

from okfn_iati.enums import Sector_Vocabulary

# Tableau-10, the same default palette as the Uruguay plugin.
PALETTE = [
    "#1f77b4", "#2ca02c", "#ff7f0e", "#8c564b", "#7f7f7f",
    "#9467bd", "#d62728", "#17becf", "#bcbd22", "#e377c2",
    "#aec7e8", "#98df8a", "#ffbb78", "#c49c94", "#c7c7c7",
]

# Slices/bars drawn before the rest is folded into "Other".
DEFAULT_TOP_N = 10

# Maximum characters kept on an axis label before adding an ellipsis.
LABEL_MAX_CHARS = 40

_VOCABULARY_LABELS = {
    str(member.value): member.name.replace("_", " ").title()
    for member in Sector_Vocabulary
}
_VOCABULARY_LABELS.update({
    "1": "OECD DAC purpose codes",
    "2": "OECD DAC sector categories",
    "98": "Reporting organisation vocabulary 2",
    "99": "Reporting organisation vocabulary",
})


def _color(index: int) -> str:
    return PALETTE[index % len(PALETTE)]


def _safe_float(value: Any) -> float:
    """Chart.js has no notion of gaps: None/NaN become 0."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number:  # NaN
        return 0.0
    return number


def short_label(text: Any, max_chars: int = LABEL_MAX_CHARS) -> str:
    """Trim a category label so it fits under a vertical bar."""
    label = str(text).strip()
    if len(label) <= max_chars:
        return label
    return label[: max_chars - 3].rstrip() + "..."


def vocabulary_label(code: Any) -> str:
    """Human-readable name of an IATI sector vocabulary code."""
    key = str(code).strip()
    if key == "":
        return "Unknown vocabulary"
    return _VOCABULARY_LABELS.get(key, f"Vocabulary {key}")


def top_n_with_other(
    items: Iterable[tuple[str, float]],
    top_n: int = DEFAULT_TOP_N,
    other_label: str = "Other",
) -> list[tuple[str, float]]:
    """Keep the ``top_n`` largest positive items and fold the rest into one.

    Non-positive values are dropped: they cannot be drawn as a share of a
    whole. ``items`` may arrive in any order; the result is sorted
    descending with the "Other" entry last.
    """
    positive = [
        (str(label), _safe_float(value))
        for label, value in items
        if _safe_float(value) > 0
    ]
    positive.sort(key=lambda item: item[1], reverse=True)
    head = positive[:top_n]
    tail = positive[top_n:]
    if tail:
        head.append((
            f"{other_label} ({len(tail)} more)",
            sum(value for _, value in tail),
        ))
    return head


def pie_chart(title: str, slices: Sequence[tuple[str, float]]) -> dict[str, Any]:
    """Pie chart. ``slices``: ``[(label, value)]`` in the desired order."""
    labels = [str(label) for label, _ in slices]
    values = [_safe_float(value) for _, value in slices]
    return {
        "type": "pie",
        "title": title,
        "labels": labels,
        "datasets": [{
            "data": values,
            "backgroundColor": [_color(i) for i in range(len(labels))],
        }],
    }


def bar_chart(
    title: str,
    labels: Sequence[Any],
    series: Sequence[tuple[str, Sequence[Any]]],
    stacked: bool = False,
) -> dict[str, Any]:
    """Vertical bars. ``series``: ``[(dataset label, values aligned to labels)]``."""
    chart: dict[str, Any] = {
        "type": "bar",
        "title": title,
        "labels": [str(label) for label in labels],
        "datasets": [
            {
                "label": label,
                "data": [_safe_float(v) for v in values],
                "backgroundColor": _color(i),
            }
            for i, (label, values) in enumerate(series)
        ],
    }
    if stacked:
        chart["stacked"] = True
    return chart


def line_chart(
    title: str,
    labels: Sequence[Any],
    series: Sequence[tuple[str, Sequence[Any]]],
) -> dict[str, Any]:
    """Lines (not stacked). Same input shape as ``bar_chart``."""
    return {
        "type": "line",
        "title": title,
        "labels": [str(label) for label in labels],
        "datasets": [
            {
                "label": label,
                "data": [_safe_float(v) for v in values],
                "borderColor": _color(i),
            }
            for i, (label, values) in enumerate(series)
        ],
    }
