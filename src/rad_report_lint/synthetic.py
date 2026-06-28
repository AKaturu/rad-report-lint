from __future__ import annotations

import random
from typing import Any


def _pick(seq: list[Any]) -> Any:
    return random.choice(seq)


_MODALITIES = ["CT", "MRI", "XR", "US"]
_BODY_PARTS = [
    "liver", "kidney", "lung", "brain", "spleen", "pancreas",
    "thyroid", "aorta", "spine", "breast", "prostate", "bladder",
]
_LATERALITY = ["right", "left", ""]

_NORMAL_STATEMENTS = [
    "The {laterality} {body} is normal in size and appearance.",
    "Normal {laterality} {body} without focal lesion.",
    "The {laterality} {body} demonstrates normal signal intensity.",
]
_ABNORMAL_STATEMENTS = [
    "There is a {size} {body} in the {laterality} {body} measuring {measurement}.",
    "{size} nodule in the {laterality} {body}.",
    "Focal {finding_type} in the {laterality} {body}.",
]
_IMPRESSION_NORMAL = [
    "No significant abnormality identified.",
    "Normal examination.",
]
_IMPRESSION_ABNORMAL = [
    "{finding} as described above, recommend follow-up.",
    "{finding} in the {body}. Recommend further evaluation.",
]
_MEASUREMENTS = [
    "8 mm", "12 mm", "15 mm", "6 mm", "22 mm", "10 mm", "5 mm",
    "1.2 cm", "2.5 cm", "3.0 cm",
]
_FINDING_TYPES = [
    "nodule", "cyst", "lesion", "mass", "calcification",
    "effusion", "thickening", "dilation",
]
_HEDGE_WORDS = [
    "may", "could", "possibly", "likely", "suggestive of",
]
_COMPARISON = [
    "",
    "Compared to prior exam from",
    "When compared with previous study dated",
    "No prior studies available for comparison.",
]
_PRIOR_DATES = [
    "2025-01-15",
    "2025-03-20",
    "2024-11-01",
    "2024-06-15",
]


def _build_report(
    modality: str,
    body: str,
    laterality: str,
    normal: bool,
    include_comparison: bool,
    include_interval: bool,
    critical_omitted: bool,
    hedging: int,
    use_placeholder: bool,
    contradictory_lat: bool,
    conflict: bool,
    duplicated_text: bool,
) -> str:
    lat = f"{laterality} " if laterality else ""
    lat_for_body = f"{_pick(['right', 'left'])} " if contradictory_lat else lat

    parts: list[str] = []
    parts.append(f"EXAMINATION: {modality} {body.replace('_', ' ').title()}")

    comp = _pick(_COMPARISON)
    if comp and include_comparison:
        parts.append(f"COMPARISON: {comp} {_pick(_PRIOR_DATES)}.")
    elif comp and not include_comparison:
        parts.append("COMPARISON: Compared to prior examination.")
    else:
        parts.append("COMPARISON: None.")

    parts.append("TECHNIQUE: Standard protocol.")
    parts.append("")

    findings: list[str] = []
    if duplicated_text:
        dup = f"The {lat}{body} demonstrates a {_pick(_MEASUREMENTS)} {_pick(_FINDING_TYPES)}."
        findings.extend([dup, dup])
    elif normal and not conflict:
        findings.append(_pick(_NORMAL_STATEMENTS).format(laterality=lat, body=body))
    elif not normal and not conflict:
        finding_text = _pick(_ABNORMAL_STATEMENTS)
        if "{size}" in finding_text:
            finding_text = finding_text.replace(
                "{size}", _pick(["small", "a 12 mm", "an 8 mm"])
            )
        findings.append(
            finding_text.format(
                laterality=lat_for_body if contradictory_lat else lat,
                body=body,
                size=f"a {_pick(_MEASUREMENTS)}" if "{size}" not in finding_text else "",
                measurement=_pick(_MEASUREMENTS),
                finding_type=_pick(_FINDING_TYPES),
            )
        )
    elif conflict:
        findings.extend([
            _pick(_NORMAL_STATEMENTS).format(laterality=lat, body=body),
            _pick(_ABNORMAL_STATEMENTS).format(
                laterality=lat, body=body,
                size=f"a {_pick(_MEASUREMENTS)}",
                measurement=_pick(_MEASUREMENTS),
                finding_type=_pick(_FINDING_TYPES),
            ),
        ])

    hedge = ""
    if hedging > 0:
        hedge_words = " ".join(_pick(_HEDGE_WORDS) for _ in range(hedging))
        hedge = f" This {hedge_words} represents a {_pick(_FINDING_TYPES)}."

    rec = ""
    if include_interval:
        rec = f" Recommend follow-up in {_pick(['3', '6', '12'])} months."
    elif not include_interval and not normal:
        rec = " Recommend follow-up."

    if use_placeholder:
        findings.append("[___]")

    parts.append("FINDINGS:")
    for f_text in findings:
        parts.append(f_text + hedge)
    parts.append(rec)
    parts.append("")

    if critical_omitted:
        parts.append("IMPRESSION:")
        parts.append("No significant findings.")
    elif contradictory_lat:
        lat_opposite = "left" if laterality == "right" else "right"
        parts.append("IMPRESSION:")
        parts.append(
            f"There is a {_pick(_MEASUREMENTS)} {_pick(_FINDING_TYPES)} "
            f"in the {lat_opposite} {body}."
        )
    elif normal:
        parts.append("IMPRESSION:")
        parts.append(_pick(_IMPRESSION_NORMAL))
    else:
        parts.append("IMPRESSION:")
        parts.append(
            _pick(_IMPRESSION_ABNORMAL).format(
                finding=_pick(_FINDING_TYPES).title(),
                body=body,
            )
        )

    return "\n".join(parts)


def generate_demo_report(scenario: str | None = None) -> str | None:
    scenarios = {
        "normal": lambda: _build_report(
            modality=_pick(_MODALITIES), body=_pick(_BODY_PARTS),
            laterality=_pick(_LATERALITY).strip(), normal=True,
            include_comparison=True, include_interval=False,
            critical_omitted=False, hedging=0, use_placeholder=False,
            contradictory_lat=False, conflict=False, duplicated_text=False,
        ),
        "contradictory-laterality": lambda: _build_report(
            modality="CT", body="lung",
            laterality="right", normal=False,
            include_comparison=True, include_interval=False,
            critical_omitted=False, hedging=0, use_placeholder=False,
            contradictory_lat=True, conflict=False, duplicated_text=False,
        ),
        "normal-abnormal-conflict": lambda: _build_report(
            modality="MRI", body="liver",
            laterality="", normal=False,
            include_comparison=True, include_interval=False,
            critical_omitted=False, hedging=0, use_placeholder=False,
            contradictory_lat=False, conflict=True, duplicated_text=False,
        ),
        "missing-comparison-date": lambda: _build_report(
            modality="CT", body="brain",
            laterality="", normal=False,
            include_comparison=False, include_interval=False,
            critical_omitted=False, hedging=0, use_placeholder=False,
            contradictory_lat=False, conflict=False, duplicated_text=False,
        ),
        "empty-impression": lambda: "FINDINGS: Normal examination.\n\nIMPRESSION:\n",
        "recommendation-without-interval": lambda: _build_report(
            modality="XR", body="chest",
            laterality="", normal=False,
            include_comparison=True, include_interval=False,
            critical_omitted=False, hedging=0, use_placeholder=False,
            contradictory_lat=False, conflict=False, duplicated_text=False,
        ),
        "critical-omitted": lambda: _build_report(
            modality="CT", body="lung",
            laterality="right", normal=False,
            include_comparison=True, include_interval=True,
            critical_omitted=True, hedging=0, use_placeholder=False,
            contradictory_lat=False, conflict=False, duplicated_text=False,
        ),
        "hedging": lambda: _build_report(
            modality="CT", body="pancreas",
            laterality="", normal=False,
            include_comparison=True, include_interval=True,
            critical_omitted=False, hedging=3, use_placeholder=False,
            contradictory_lat=False, conflict=False, duplicated_text=False,
        ),
        "placeholder": lambda: _build_report(
            modality="MRI", body="spine",
            laterality="", normal=True,
            include_comparison=True, include_interval=False,
            critical_omitted=False, hedging=0, use_placeholder=True,
            contradictory_lat=False, conflict=False, duplicated_text=False,
        ),
        "findings-impression-contradiction": lambda: _build_report(
            modality="CT", body="lung",
            laterality="right", normal=False,
            include_comparison=True, include_interval=False,
            critical_omitted=False, hedging=0, use_placeholder=False,
            contradictory_lat=True, conflict=False, duplicated_text=False,
        ),
        "duplicated": lambda: _build_report(
            modality="CT", body="liver",
            laterality="", normal=False,
            include_comparison=True, include_interval=True,
            critical_omitted=False, hedging=0, use_placeholder=False,
            contradictory_lat=False, conflict=False, duplicated_text=True,
        ),
    }

    if scenario:
        if scenario in scenarios:
            return scenarios[scenario]()
        return None
    return scenarios[_pick(list(scenarios.keys()))]()


def generate_all_demo_reports() -> dict[str, str]:
    reports: dict[str, str | None] = {
        "01_normal": generate_demo_report("normal"),
        "02_contradictory_laterality": generate_demo_report("contradictory-laterality"),
        "03_normal_abnormal_conflict": generate_demo_report("normal-abnormal-conflict"),
        "04_missing_comparison": generate_demo_report("missing-comparison-date"),
        "05_empty_impression": generate_demo_report("empty-impression"),
        "06_recommendation_no_interval": generate_demo_report("recommendation-without-interval"),
        "07_critical_omitted": generate_demo_report("critical-omitted"),
        "08_hedging": generate_demo_report("hedging"),
        "09_placeholder": generate_demo_report("placeholder"),
        "10_findings_impression_contradiction": generate_demo_report("findings-impression-contradiction"),
        "11_duplicated": generate_demo_report("duplicated"),
    }
    return {k: v for k, v in reports.items() if v is not None}
