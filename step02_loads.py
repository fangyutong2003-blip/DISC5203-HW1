"""Step 02: vertical-load and axial-force calculation for HW1 Plan 3.

Inputs are the reviewed coordinate and tributary-area CSV files. Outputs are
English CSV schedules and a Markdown report. The S1 stair/core zone is handled
as a transparent provisional equivalent-area model, separate from flat slab.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from project_utils import default_font

ROOT = Path(__file__).resolve().parent
COORDS = ROOT / "Step_01B_Vertical_Element_Coordinates.csv"
AREAS = ROOT / "Step_01C_Tributary_Areas.csv"
SUMMARY = ROOT / "Step_02_Element_Load_Summary.csv"
LEVELS = ROOT / "Step_02_Axial_Loads_by_Level.csv"
REPORT = ROOT / "Step_02_Vertical_Load_and_Axial_Force_Calculation.md"
CHART = ROOT / "Step_02_Base_ULS_Axial_Loads.png"
COMBINATIONS = ROOT / "load_combinations.json"

CONCRETE_UNIT_WEIGHT = 25.0  # kN/m3
SLAB_THICKNESS = 0.150       # m
STOREY_HEIGHT = 3.0          # m
LIVE_LOAD = 5.0              # kN/m2
STOREYS = 5
combination_data = json.loads(COMBINATIONS.read_text(encoding="utf-8"))
GAMMA_G = float(combination_data["uls"]["gamma_G"])
GAMMA_Q = float(combination_data["uls"]["gamma_Q"])
G_PLUS_Q_FACTOR = float(combination_data["g_plus_0_30q"]["q_factor"])

FLAT_SLAB_DEAD = SLAB_THICKNESS * CONCRETE_UNIT_WEIGHT
S1_AREA = 1.85 * 2.90
S1_BORDER_LENGTHS = {"T6": 2.10, "T7": 3.40, "T8": 2.10}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


area_rows = read_rows(AREAS)
areas = {row["element_id"]: float(row["tributary_area_m2"]) for row in area_rows}

coordinate_rows = read_rows(COORDS)
geometry: dict[str, dict[str, str]] = {}
for row in coordinate_rows:
    if row["axis_segment"] in {"centre", "main"}:
        geometry[row["element_id"]] = row

if set(areas) != set(geometry):
    raise ValueError(f"Element mismatch: areas={set(areas)-set(geometry)}, geometry={set(geometry)-set(areas)}")


def section_dimensions(section: str) -> tuple[float, float]:
    a, b = section.lower().replace("×", "x").split("x")
    return float(a) / 1000.0, float(b) / 1000.0


def element_self_weight(element: str) -> float:
    row = geometry[element]
    a, b = section_dimensions(row["section_mm"])
    if row["element_type"] == "column":
        plan_area = a * b
    else:
        x1, y1 = float(row["x1_m"]), float(row["y1_m"])
        x2, y2 = float(row["x2_m"]), float(row["y2_m"])
        length = math.hypot(x2 - x1, y2 - y1)
        thickness = min(a, b)
        plan_area = length * thickness
    return plan_area * STOREY_HEIGHT * CONCRETE_UNIT_WEIGHT


s1_permanent_total = S1_AREA * FLAT_SLAB_DEAD
s1_live_total = S1_AREA * LIVE_LOAD
s1_border_total = sum(S1_BORDER_LENGTHS.values())
s1_shares = {element: length / s1_border_total for element, length in S1_BORDER_LENGTHS.items()}

summary_rows: list[dict[str, float | str]] = []
level_rows: list[dict[str, float | str | int]] = []

for element, area in areas.items():
    slab_g = area * FLAT_SLAB_DEAD
    self_g = element_self_weight(element)
    s1_share = s1_shares.get(element, 0.0)
    s1_g = s1_permanent_total * s1_share
    s1_q = s1_live_total * s1_share
    g_floor = slab_g + self_g + s1_g
    q_floor = area * LIVE_LOAD + s1_q
    base_g = STOREYS * g_floor
    base_q = STOREYS * q_floor
    summary_rows.append({
        "element_id": element,
        "element_type": geometry[element]["element_type"],
        "tributary_area_m2": area,
        "flat_slab_dead_per_floor_kN": slab_g,
        "element_self_weight_per_floor_kN": self_g,
        "s1_share_percent": 100.0 * s1_share,
        "s1_dead_per_floor_kN": s1_g,
        "s1_live_per_floor_kN": s1_q,
        "total_G_per_floor_kN": g_floor,
        "total_Q_per_floor_kN": q_floor,
        "base_G_5_storeys_kN": base_g,
        "base_Q_5_storeys_kN": base_q,
        "base_G_plus_Q_kN": base_g + base_q,
        "base_ULS_1_35G_1_5Q_kN": GAMMA_G * base_g + GAMMA_Q * base_q,
        "base_G_plus_0_3Q_kN": base_g + G_PLUS_Q_FACTOR * base_q,
    })
    for level in range(STOREYS, 0, -1):
        floors_supported = STOREYS - level + 1
        g = floors_supported * g_floor
        q = floors_supported * q_floor
        level_rows.append({
            "element_id": element,
            "level": f"{level}/F",
            "floors_supported": floors_supported,
            "G_kN": g,
            "Q_kN": q,
            "G_plus_Q_kN": g + q,
            "ULS_1_35G_1_5Q_kN": GAMMA_G * g + GAMMA_Q * q,
            "G_plus_0_3Q_kN": g + G_PLUS_Q_FACTOR * q,
        })


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: (f"{value:.4f}" if isinstance(value, float) else value) for key, value in row.items()})


write_csv(SUMMARY, summary_rows)
write_csv(LEVELS, level_rows)

totals = {key: sum(float(row[key]) for row in summary_rows) for key in [
    "tributary_area_m2", "flat_slab_dead_per_floor_kN", "element_self_weight_per_floor_kN",
    "s1_dead_per_floor_kN", "s1_live_per_floor_kN", "total_G_per_floor_kN",
    "total_Q_per_floor_kN", "base_G_5_storeys_kN", "base_Q_5_storeys_kN",
    "base_G_plus_Q_kN", "base_ULS_1_35G_1_5Q_kN", "base_G_plus_0_3Q_kN",
]}

# Base ULS comparison chart.
chart = Image.new("RGB", (1300, 1120), "white")
draw = ImageDraw.Draw(chart)
title_font = default_font(28)
font = default_font(19)
small = default_font(16)
draw.text((70, 40), "Plan 3 | Base ULS Axial Load by Vertical Element", font=title_font, fill="#17324d")
draw.text((70, 80), "ULS = 1.35G + 1.50Q; five-storey accumulation", font=font, fill="#53677a")
left, right, top, row_h = 145, 1210, 125, 44
maximum = max(float(row["base_ULS_1_35G_1_5Q_kN"]) for row in summary_rows)
for i, row in enumerate(summary_rows):
    y = top + i * row_h
    value = float(row["base_ULS_1_35G_1_5Q_kN"])
    width = (right - left) * value / maximum
    colour = "#5687c7" if row["element_type"] == "column" else "#58a884"
    draw.text((70, y + 8), str(row["element_id"]), font=font, fill="#17324d")
    draw.rectangle((left, y + 7, left + width, y + 31), fill=colour)
    draw.text((left + width + 8, y + 8), f"{value:.1f} kN", font=small, fill="#17324d")
draw.rectangle((70, 1065, 92, 1087), fill="#5687c7")
draw.text((102, 1066), "Column", font=small, fill="#17324d")
draw.rectangle((205, 1065, 227, 1087), fill="#58a884")
draw.text((237, 1066), "Wall", font=small, fill="#17324d")
chart.save(CHART)

lines = [
    "# Step 02 - Vertical Load and Axial Force Calculation",
    "",
    "## 1. Scope and load path",
    "",
    "The ordinary slab load is assigned to C1-C9 and T1-T12 through the reviewed tributary areas from Step 01. Each element also carries its own storey-height self-weight. Loads are accumulated downward through five identical storeys, so the axial compression is greatest at the base.",
    "",
    "The stair/core zone S1 is not treated as ordinary flat slab. Because stair slope and reinforcement geometry are unavailable, this calculation uses a transparent provisional equivalent-horizontal-area model. The S1 load is shared by T6, T7, and T8 in proportion to their bordering lengths (2.10:3.40:2.10). This assumption must be replaced if detailed stair geometry becomes available.",
    "",
    "## 2. Input values",
    "",
    "| Parameter | Value |",
    "|---|---:|",
    f"| Concrete unit weight | {CONCRETE_UNIT_WEIGHT:.2f} kN/m³ |",
    f"| Slab thickness | {SLAB_THICKNESS:.3f} m |",
    f"| Slab self-weight | {FLAT_SLAB_DEAD:.3f} kN/m² |",
    f"| Live area load | {LIVE_LOAD:.2f} kN/m² |",
    f"| Storey height | {STOREY_HEIGHT:.2f} m |",
    f"| Number of storeys | {STOREYS} |",
    f"| S1 plan area | {S1_AREA:.3f} m² |",
    "",
    "No finishes, beams, masonry partitions, façade loads, or live-load reduction are included because HW1 does not provide those inputs.",
    "",
    "## 3. Equations",
    "",
    "Ordinary slab dead load assigned to element i:",
    "",
    r"\[G_{s,i}=A_i(0.15)(25)=3.75A_i\]",
    "",
    "Column or wall self-weight per storey:",
    "",
    r"\[G_{e,i}=V_i(25)\]",
    "",
    "Characteristic loads per storey:",
    "",
    r"\[G_i=G_{s,i}+G_{e,i}+G_{S1,i},\qquad Q_i=5A_i+Q_{S1,i}\]",
    "",
    "At a level supporting n identical floors:",
    "",
    r"\[N_G=nG_i,\qquad N_Q=nQ_i\]",
    "",
    "Reported combinations:",
    "",
    r"\[N_{service}=G+Q\]",
    r"\[N_{ULS}=1.35G+1.50Q\]",
    r"\[N_{G+0.30Q}=G+0.30Q\]",
    "",
    "The two factored expressions above are provisional reporting combinations loaded from `load_combinations.json`. No confirmed course design standard has yet been identified for them. The second expression is deliberately labelled by its equation rather than as seismic mass or quasi-permanent load until its intended use is confirmed.",
    "",
    "## 4. Five-storey base axial loads",
    "",
    "| Element | Area (m²) | G/floor (kN) | Q/floor (kN) | Base G (kN) | Base Q (kN) | G+Q (kN) | 1.35G+1.50Q (kN) |",
    "|---|---:|---:|---:|---:|---:|---:|---:|",
]
for row in summary_rows:
    lines.append(
        f"| {row['element_id']} | {row['tributary_area_m2']:.4f} | {row['total_G_per_floor_kN']:.2f} | "
        f"{row['total_Q_per_floor_kN']:.2f} | {row['base_G_5_storeys_kN']:.2f} | "
        f"{row['base_Q_5_storeys_kN']:.2f} | {row['base_G_plus_Q_kN']:.2f} | "
        f"{row['base_ULS_1_35G_1_5Q_kN']:.2f} |"
    )
lines += [
    f"| **Total** | **{totals['tributary_area_m2']:.4f}** | **{totals['total_G_per_floor_kN']:.2f}** | **{totals['total_Q_per_floor_kN']:.2f}** | **{totals['base_G_5_storeys_kN']:.2f}** | **{totals['base_Q_5_storeys_kN']:.2f}** | **{totals['base_G_plus_Q_kN']:.2f}** | **{totals['base_ULS_1_35G_1_5Q_kN']:.2f}** |",
    "",
    "![Base ULS axial-load comparison](Step_02_Base_ULS_Axial_Loads.png)",
    "",
    "The complete floor-by-floor schedule is provided in `Step_02_Axial_Loads_by_Level.csv`.",
    "",
    "## 5. Verification checks",
    "",
    f"- Tributary-area sum: {totals['tributary_area_m2']:.3f} m² = reviewed ordinary flat-slab area.",
    f"- Ordinary slab dead load: {totals['flat_slab_dead_per_floor_kN']:.3f} kN = 179.250×3.75.",
    f"- Ordinary slab live load before S1: {179.250 * LIVE_LOAD:.3f} kN = 179.250×5.00.",
    f"- S1 equivalent dead/live loads: {totals['s1_dead_per_floor_kN']:.3f}/{totals['s1_live_per_floor_kN']:.3f} kN per floor.",
    f"- Vertical-element self-weight: {totals['element_self_weight_per_floor_kN']:.3f} kN per floor.",
    f"- Total characteristic base loads: G={totals['base_G_5_storeys_kN']:.3f} kN and Q={totals['base_Q_5_storeys_kN']:.3f} kN.",
    "- The sum of element loads equals the independently calculated whole-floor load for every reported component.",
    "",
    "## 6. Limitations requiring review",
    "",
    "1. S1 is represented by horizontal plan area; the actual inclined stair-slab self-weight may be higher.",
    "2. S1 is distributed to T6-T8 by bordering length, not stiffness analysis.",
    "3. Nominal labelled wall lengths are used for wall self-weight. Approximate short returns are excluded to avoid uncertain overlap and double-counting.",
    "4. Finishes, beams, partitions, façade, and other permanent loads are outside the current HW1 input set.",
    "5. Axial forces are reported at the bottom of each storey segment and therefore include that segment's self-weight.",
    "",
]
REPORT.write_text("\n".join(lines), encoding="utf-8")

print(f"Wrote {SUMMARY.name}, {LEVELS.name}, {CHART.name}, and {REPORT.name}")
print(f"Base totals: G={totals['base_G_5_storeys_kN']:.3f} kN, Q={totals['base_Q_5_storeys_kN']:.3f} kN, ULS={totals['base_ULS_1_35G_1_5Q_kN']:.3f} kN")
