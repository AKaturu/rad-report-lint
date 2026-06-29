from __future__ import annotations

import logging
import re

from rad_report_lint.models import (
    Finding,
    Laterality,
    Measurement,
    ParsedReport,
    ReportSection,
)

_SECTION_PATTERN = re.compile(
    r"^(?P<header>(?:TECHNIQUE|HISTORY|COMPARISON|FINDINGS|IMPRESSION)"
    r"(?:\s*:)?)\s*(?P<rest>.*)$",
    re.IGNORECASE | re.MULTILINE,
)

_BODY_PARTS = [
    "liver", "spleen", "kidney", "pancreas", "gallbladder", "adrenal",
    "lung", "heart", "aorta", "thyroid", "brain", "cerebellum",
    "bladder", "prostate", "uterus", "ovary", "breast", "lymph node",
    "bone", "spine", "vertebra", "disc", "colon", "bowel",
    "stomach", "esophagus", "muscle", "vessel", "artery", "vein",
    "pleura", "pericardium", "peritoneum", "pelvis", "hip", "shoulder",
    "knee", "ankle", "wrist", "elbow", "hand", "foot", "nodule",
    "lesion", "mass", "cyst",
]

_BODY_PART_PATTERN = re.compile(
    r"(?P<laterality>(?:right|left|bilateral|midline)\s)?"
    r"(?P<body>" + "|".join(
        p.replace(" ", r"\s+") for p in sorted(_BODY_PARTS, key=len, reverse=True)
    ) + r")s?\b",
    re.IGNORECASE,
)

_LATERALITY_MAP: dict[str, Laterality] = {
    "right": Laterality.right,
    "left": Laterality.left,
    "bilateral": Laterality.bilateral,
    "midline": Laterality.midline,
}

_MEASUREMENT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:x\s*(\d+(?:\.\d+)?)(?:\s*x\s*(\d+(?:\.\d+)?))?\s*)?"
    r"(?:mm|cm)\b",
    re.IGNORECASE,
)

_NORMAL_PATTERN = re.compile(
    r"\bnormal\s+(?:\w+\s+)?(?:size|appearance|signal|morphology|echogenicity|"
    r"attenuation|enhancement|contour|shape|cortex|medulla|parenchyma|"
    r"wall|lining|mucosa|caliber|course|finding)\b",
    re.IGNORECASE,
)

_ABNORMAL_PATTERN = re.compile(
    r"\b(?:abnormal|enlarged|atrophic|nodule|mass|lesion|tumor|cyst|"
    r"calcification|effusion|edema|hemorrhage|infarct|abscess|"
    r"thickening|dilation|stenosis|obstruction|fracture|erosion)\b",
    re.IGNORECASE,
)

_ABBREVIATION_PATTERN = re.compile(
    r"\b([A-Z]{2,})(?:\b|s\b)",
)

_COMMON_ABBREVIATIONS: dict[str, str] = {
    "CT": "computed tomography",
    "MRI": "magnetic resonance imaging",
    "MR": "magnetic resonance",
    "US": "ultrasound",
    "XR": "x-ray",
    "PET": "positron emission tomography",
    "IV": "intravenous",
    "PO": "by mouth",
    "STAT": "immediately",
    "LLL": "left lower lobe",
    "RLL": "right lower lobe",
    "LUL": "left upper lobe",
    "RUL": "right upper lobe",
    "RML": "right middle lobe",
    "RLQ": "right lower quadrant",
    "LLQ": "left lower quadrant",
    "RUQ": "right upper quadrant",
    "LUQ": "left upper quadrant",
    "MIP": "maximum intensity projection",
    "CPR": "cardiopulmonary resuscitation",
    "CC": "chief complaint",
    "HX": "history",
    "FU": "follow-up",
    "WNL": "within normal limits",
}

_MODALITY_TERMS = {
    "CT": ["ct scan", "computed tomography"],
    "MRI": ["mri", "magnetic resonance"],
    "US": ["ultrasound", "sonogram", "sonography"],
    "XR": ["x-ray", "radiograph", "plain film"],
    "PET": ["pet", "positron emission"],
}


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_section: ReportSection | None = None
    current_lines: list[str] = []

    for line in text.split("\n"):
        m = _SECTION_PATTERN.match(line)
        if m:
            if current_section is not None:
                sections[current_section] = " ".join(
                    line for line in current_lines if line.strip()
                )
            header = m.group("header").rstrip(":").strip().upper()
            try:
                current_section = ReportSection(header.lower())
            except ValueError:
                logging.warning("Unknown section header: %s", header)
                current_section = None
            current_lines = []
            rest = m.group("rest") or ""
            if rest.strip():
                current_lines.append(rest.strip())
        else:
            if current_section is not None:
                current_lines.append(line)

    if current_section is not None:
        sections[current_section] = " ".join(
            line for line in current_lines if line.strip()
        )

    return sections


def extract_findings(text: str) -> list[Finding]:
    findings: list[Finding] = []
    sentences = re.split(r"[.!?]\s+", text)

    for sentence in sentences:
        stripped = sentence.strip()
        if not stripped:
            continue

        matches = list(_BODY_PART_PATTERN.finditer(stripped))
        if not matches:
            continue

        is_normal = bool(_NORMAL_PATTERN.search(stripped))
        is_abnormal = bool(_ABNORMAL_PATTERN.search(stripped))

        for m in matches:
            lat_str = m.group("laterality")
            lat = Laterality.unspecified
            if lat_str:
                lat = _LATERALITY_MAP.get(lat_str.strip().lower(), Laterality.unspecified)

            findings.append(
                Finding(
                    body_part=m.group("body").lower(),
                    laterality=lat,
                    is_normal=is_normal and not is_abnormal,
                    text=stripped,
                )
            )

    return findings


def extract_measurements(text: str) -> list[Measurement]:
    measurements: list[Measurement] = []
    sentences = re.split(r"[.!?]\s+", text)

    for sentence in sentences:
        stripped = sentence.strip()
        if not stripped:
            continue

        for m in _MEASUREMENT_PATTERN.finditer(stripped):
            body_match = _BODY_PART_PATTERN.search(stripped)
            body = body_match.group("body").lower() if body_match else "structure"
            lat_str = body_match.group("laterality") if body_match else None
            lat = Laterality.unspecified
            if lat_str:
                lat = _LATERALITY_MAP.get(lat_str.strip().lower(), Laterality.unspecified)

            try:
                value_mm = float(m.group(1))
            except ValueError:
                logging.debug("Skipping malformed measurement value: %s", m.group(1))
                continue

            measurements.append(
                Measurement(
                    body_part=body,
                    laterality=lat,
                    value_mm=value_mm,
                    text=stripped,
                )
            )

    return measurements


def parse_report(text: str) -> ParsedReport:
    sections = split_sections(text)
    all_text = " ".join(sections.values()) if sections else text

    findings = extract_findings(all_text)
    measurements = extract_measurements(all_text)

    abbreviations: dict[str, str] = {}
    for m in _ABBREVIATION_PATTERN.finditer(all_text):
        abbr = m.group(0).rstrip("s")
        if abbr in _COMMON_ABBREVIATIONS:
            abbreviations[abbr] = _COMMON_ABBREVIATIONS[abbr]

    return ParsedReport(
        text=text,
        sections=sections,
        findings=findings,
        measurements=measurements,
        abbreviations=abbreviations,
    )
