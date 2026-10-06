"""HW2 geometry definitions and preserved legacy all-matched implementation.

The command-line entry point delegates to hw2_mixed_supports.main. The historical
main below is retained for audit only; it is not the current analysis.

The geometry extends the reviewed HW1 coordinate system. Beam and wall axes are
image-derived from the detailed structural drawing. Each slab panel is classified
before load allocation. Two-way panels use nearest finite support-edge assignment
(45-degree divisions for matched orthogonal supports); one-way panels are assigned
only to the two edges perpendicular to their span. Cantilevers load their root edge.
"""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
GRID = 0.01
SLAB_DEAD = 3.75  # kN/m2
LIVE = 5.00  # kN/m2
CONCRETE = 25.0  # kN/m3
SLAB_THICKNESS = 0.150  # m
TARGET_ORDINARY_SLAB_AREA = 179.250  # m2, retained from HW1


@dataclass(frozen=True)
class Segment:
    support_id: str
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def length(self) -> float:
        return math.hypot(self.x2 - self.x1, self.y2 - self.y1)

    @property
    def horizontal(self) -> bool:
        return math.isclose(self.y1, self.y2)


def beam(beam_id: str, x1: float, y1: float, x2: float, y2: float, depth_mm: int,
         panels: str, role: str) -> dict[str, object]:
    return {
        "beam_id": beam_id,
        "x1_m": x1,
        "y1_m": y1,
        "x2_m": x2,
        "y2_m": y2,
        "width_mm": 250,
        "depth_mm": depth_mm,
        "panels": panels,
        "role": role,
    }


BEAMS = [
    beam("D01", 2.45, 19.20, 5.75, 19.20, 700, "P1, P10", "perimeter/root; two-sided including cantilever"),
    beam("D02", 2.45, 15.20, 2.45, 17.20, 700, "P1", "perimeter; one-sided"),
    beam("D03", 7.75, 15.20, 7.75, 19.20, 700, "P1, P12", "perimeter/root; two-sided including cantilever"),
    beam("D04", 0.00, 15.20, 2.45, 15.20, 700, "P2, P11", "perimeter/root; two-sided including cantilever"),
    beam("D05", 0.00, 12.10, 0.00, 15.20, 700, "P2", "perimeter; one-sided; Beam A segment"),
    beam("D06", 3.60, 12.10, 3.60, 15.20, 600, "P1, P2", "interior; two-sided"),
    beam("D07", 7.75, 12.10, 7.75, 15.20, 600, "P1, P12", "perimeter/root; two-sided including cantilever"),
    beam("D08", 0.00, 12.10, 3.60, 12.10, 600, "P2, P3", "interior; two-sided"),
    beam("D09", 3.60, 12.10, 4.70, 12.10, 600, "P1, P4", "core-side; two-sided"),
    beam("D10", 7.75, 12.10, 10.20, 12.10, 700, "P5, P13", "perimeter/root; two-sided including cantilever"),
    beam("D11", 0.00, 6.05, 0.00, 12.10, 700, "P3", "perimeter; one-sided; Beam A segment"),
    beam("D12", 3.60, 6.05, 3.60, 12.10, 600, "P3, P4", "interior; two-sided"),
    beam("D13", 6.60, 10.60, 6.60, 12.10, 600, "P5", "core-side; one-sided"),
    beam("D14", 6.60, 6.05, 6.60, 7.20, 600, "P5, P6", "core-side; one slab-bearing side adopted"),
    beam("D15", 10.20, 6.05, 10.20, 12.10, 700, "P5", "perimeter; one-sided"),
    beam("D16", 0.00, 6.05, 3.60, 6.05, 600, "P3, P7", "interior; two-sided; Beam B span 1"),
    beam("D17", 3.60, 6.05, 6.60, 6.05, 600, "P6, P8", "interior; P8 is one-way to vertical beams; Beam B span 2"),
    beam("D18", 6.60, 6.05, 10.20, 6.05, 600, "P5, P9", "interior; two-sided; Beam B span 3"),
    beam("D19", 0.00, 0.00, 0.00, 6.05, 700, "P7", "perimeter; one-sided; Beam A segment"),
    beam("D20", 3.60, 0.00, 3.60, 6.05, 600, "P7, P8", "interior; two-sided"),
    beam("D21", 6.60, 0.00, 6.60, 6.05, 600, "P8, P9", "interior; two-sided"),
    beam("D22", 10.20, 0.00, 10.20, 6.05, 700, "P9", "perimeter; one-sided"),
    beam("D23", 0.00, 0.00, 3.60, 0.00, 700, "P7, P14", "perimeter/root; two-sided including cantilever"),
    beam("D24", 3.60, 0.00, 6.60, 0.00, 700, "P8, P14", "perimeter/root; cantilever load only from P14"),
    beam("D25", 6.60, 0.00, 10.20, 0.00, 700, "P9, P14", "perimeter/root; two-sided including cantilever"),
]

BEAM_MAP = {row["beam_id"]: row for row in BEAMS}
SEGMENTS = {
    row["beam_id"]: Segment(row["beam_id"], row["x1_m"], row["y1_m"], row["x2_m"], row["y2_m"])
    for row in BEAMS
}


def wall(support_id: str, x1: float, y1: float, x2: float, y2: float) -> Segment:
    return Segment(support_id, x1, y1, x2, y2)


SUPPORTS = dict(SEGMENTS)
SUPPORTS.update({
    "W_T1": wall("W_T1", 5.75, 19.20, 7.75, 19.20),
    "W_T2": wall("W_T2", 2.45, 17.20, 2.45, 19.20),
    "W_T3": wall("W_T3", 2.45, 15.20, 3.60, 15.20),
    "W_T4": wall("W_T4", 4.70, 12.10, 7.75, 12.10),
    "W_CORE_R": wall("W_CORE_R", 4.70, 6.05, 4.70, 12.10),
    "W_T7": wall("W_T7", 6.60, 7.20, 6.60, 10.60),
    "W_T8": wall("W_T8", 4.70, 7.325, 6.60, 7.325),
})


PANELS = [
    {
        "panel_id": "P1",
        "polygon": [(2.45, 15.20), (2.45, 19.20), (7.75, 19.20), (7.75, 12.10),
                    (3.60, 12.10), (3.60, 15.20)],
        "panel_type": "two-way, matched supports, L-shaped",
        "supports": ["D01", "W_T1", "D02", "W_T2", "W_T3", "D06", "D09", "W_T4", "D03", "D07"],
    },
    {
        "panel_id": "P2",
        "polygon": [(0.00, 12.10), (3.60, 12.10), (3.60, 15.20), (0.00, 15.20)],
        "panel_type": "two-way, matched supports",
        "supports": ["D04", "W_T3", "D05", "D06", "D08"],
    },
    {
        "panel_id": "P3",
        "polygon": [(0.00, 6.05), (3.60, 6.05), (3.60, 12.10), (0.00, 12.10)],
        "panel_type": "two-way, matched supports",
        "supports": ["D08", "D11", "D12", "D16"],
    },
    {
        "panel_id": "P4",
        "polygon": [(3.60, 6.05), (4.70, 6.05), (4.70, 12.10), (3.60, 12.10)],
        "panel_type": "one-way core-side strip",
        "supports": ["D12", "W_CORE_R"],
    },
    {
        "panel_id": "P5",
        "polygon": [(6.60, 6.05), (10.20, 6.05), (10.20, 12.10), (6.60, 12.10)],
        "panel_type": "two-way, matched supports",
        "supports": ["W_T4", "D10", "D13", "W_T7", "D14", "D15", "D18"],
    },
    {
        "panel_id": "P6",
        "polygon": [(4.70, 6.05), (6.60, 6.05), (6.60, 7.325), (4.70, 7.325)],
        "panel_type": "one-way between T8 and D17",
        "supports": ["W_T8", "D17"],
    },
    {
        "panel_id": "P7",
        "polygon": [(0.00, 0.00), (3.60, 0.00), (3.60, 6.05), (0.00, 6.05)],
        "panel_type": "two-way, matched supports",
        "supports": ["D16", "D19", "D20", "D23"],
    },
    {
        "panel_id": "P8",
        "polygon": [(3.60, 0.00), (6.60, 0.00), (6.60, 6.05), (3.60, 6.05)],
        "panel_type": "one-way; 6.05/3.00 > 2",
        "supports": ["D20", "D21"],
    },
    {
        "panel_id": "P9",
        "polygon": [(6.60, 0.00), (10.20, 0.00), (10.20, 6.05), (6.60, 6.05)],
        "panel_type": "two-way, matched supports",
        "supports": ["D18", "D21", "D22", "D25"],
    },
]


SHAPES = {
    "D01": "trapezoidal/truncated + partial cantilever UDL",
    "D02": "triangular/truncated, one-sided",
    "D03": "trapezoidal + cantilever UDL",
    "D04": "triangular/truncated + cantilever UDL",
    "D05": "triangular, one-sided",
    "D06": "two-sided triangular/trapezoidal",
    "D07": "trapezoidal/truncated + short cantilever UDL",
    "D08": "two-sided triangular",
    "D09": "truncated triangular, core-side",
    "D10": "truncated triangular + cantilever UDL",
    "D11": "trapezoidal, one-sided",
    "D12": "two-sided trapezoidal + one-way strip",
    "D13": "truncated triangular, one-sided",
    "D14": "truncated triangular, one-sided",
    "D15": "trapezoidal, one-sided",
    "D16": "two-sided triangular",
    "D17": "partial uniform one-way strip",
    "D18": "two-sided triangular",
    "D19": "trapezoidal, one-sided",
    "D20": "trapezoidal + one-way UDL, two-sided",
    "D21": "trapezoidal + one-way UDL, two-sided",
    "D22": "trapezoidal, one-sided",
    "D23": "triangular + partial cantilever UDL",
    "D24": "partial cantilever UDL only",
    "D25": "triangular + partial cantilever UDL",
}


def point_in_polygon(x: float, y: float, polygon: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(polygon) - 1
    for i in range(len(polygon)):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        intersects = ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        )
        if intersects:
            inside = not inside
        j = i
    return inside


def distance_l1(x: float, y: float, segment: Segment) -> float:
    if segment.horizontal:
        lo, hi = sorted((segment.x1, segment.x2))
        px = min(max(x, lo), hi)
        return abs(x - px) + abs(y - segment.y1)
    lo, hi = sorted((segment.y1, segment.y2))
    py = min(max(y, lo), hi)
    return abs(x - segment.x1) + abs(y - py)


def local_coordinate(x: float, y: float, segment: Segment) -> float:
    if segment.horizontal:
        lo = min(segment.x1, segment.x2)
        return min(max(x - lo, 0.0), segment.length - 1e-9)
    lo = min(segment.y1, segment.y2)
    return min(max(y - lo, 0.0), segment.length - 1e-9)


def panel_area(polygon: list[tuple[float, float]]) -> float:
    total = 0.0
    for i, (x1, y1) in enumerate(polygon):
        x2, y2 = polygon[(i + 1) % len(polygon)]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0


def default_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def main() -> None:
    beam_area = defaultdict(float)
    direct_support_area = defaultdict(float)
    contributions = defaultdict(lambda: defaultdict(float))
    profiles: dict[str, list[float]] = {}
    for beam_id, seg in SEGMENTS.items():
        profiles[beam_id] = [0.0] * max(1, math.ceil(seg.length / GRID))

    assigned_points: list[tuple[float, float, str]] = []
    panel_checks = []

    for panel in PANELS:
        polygon = panel["polygon"]
        supports = [SUPPORTS[item] for item in panel["supports"]]
        min_x = min(x for x, _ in polygon)
        max_x = max(x for x, _ in polygon)
        min_y = min(y for _, y in polygon)
        max_y = max(y for _, y in polygon)
        nx = math.ceil((max_x - min_x) / GRID)
        ny = math.ceil((max_y - min_y) / GRID)
        assigned_area = 0.0
        for ix in range(nx):
            x = min_x + (ix + 0.5) * GRID
            if x >= max_x:
                continue
            for iy in range(ny):
                y = min_y + (iy + 0.5) * GRID
                if y >= max_y or not point_in_polygon(x, y, polygon):
                    continue
                chosen = min(supports, key=lambda seg: (distance_l1(x, y, seg), seg.support_id))
                area = GRID * GRID
                assigned_area += area
                contributions[chosen.support_id][panel["panel_id"]] += area
                if chosen.support_id in BEAM_MAP:
                    beam_area[chosen.support_id] += area
                    coord = local_coordinate(x, y, chosen)
                    index = min(int(coord / GRID), len(profiles[chosen.support_id]) - 1)
                    profiles[chosen.support_id][index] += area / GRID
                else:
                    direct_support_area[chosen.support_id] += area
                if (ix + iy) % 2 == 0:
                    assigned_points.append((x, y, chosen.support_id))
        exact = panel_area(polygon)
        panel_checks.append((panel["panel_id"], panel["panel_type"], exact, assigned_area))

    def add_uniform(beam_id: str, panel_id: str, start: float, length: float, width: float) -> None:
        area = length * width
        beam_area[beam_id] += area
        contributions[beam_id][panel_id] += area
        first = max(0, int(start / GRID))
        last = min(len(profiles[beam_id]), math.ceil((start + length) / GRID))
        for index in range(first, last):
            profiles[beam_id][index] += width

    # Cantilever/root-edge allocations. P10 is split between D01 and wall T1.
    add_uniform("D01", "P10", 1.35, 1.95, 0.50)
    direct_support_area["W_T1"] += 0.70 * 0.50
    contributions["W_T1"]["P10"] += 0.70 * 0.50
    add_uniform("D04", "P11", 0.00, 2.45, 1.00)
    add_uniform("D03", "P12", 0.00, 4.00, 0.50)
    add_uniform("D07", "P12", 2.80, 0.30, 0.50)
    add_uniform("D10", "P13", 0.00, 2.45, 0.90)
    add_uniform("D23", "P14", 1.00, 2.60, 1.20)
    add_uniform("D24", "P14", 0.00, 3.00, 1.20)
    add_uniform("D25", "P14", 0.00, 2.60, 1.20)

    explicit_panel_area = sum(item[2] for item in panel_checks) + 1.325 + 2.450 + 2.150 + 2.205 + 9.840
    # Close the model to the reviewed HW1 slab area using the actual sampled area,
    # not the exact polygon total. This prevents grid truncation from appearing as
    # a false load-path imbalance.
    residual = TARGET_ORDINARY_SLAB_AREA - (sum(beam_area.values()) + sum(direct_support_area.values()))
    direct_support_area["CORE_AND_SUPPORT_RESIDUAL"] += residual
    contributions["CORE_AND_SUPPORT_RESIDUAL"]["residual"] += residual

    summary_rows = []
    for row in BEAMS:
        beam_id = row["beam_id"]
        seg = SEGMENTS[beam_id]
        area = beam_area[beam_id]
        depth = row["depth_mm"] / 1000.0
        width = row["width_mm"] / 1000.0
        stem_dead = width * max(depth - SLAB_THICKNESS, 0.0) * CONCRETE
        slab_dead_udl = area * SLAB_DEAD / seg.length
        live_udl = area * LIVE / seg.length
        total_dead_udl = slab_dead_udl + stem_dead
        service_udl = total_dead_udl + live_udl

        m_mid_service_slab = 0.0
        for index, tributary_width in enumerate(profiles[beam_id]):
            x = min((index + 0.5) * GRID, seg.length)
            influence = 0.5 * min(x, seg.length - x)
            m_mid_service_slab += (SLAB_DEAD + LIVE) * tributary_width * GRID * influence
        q_moment_slab = 8.0 * m_mid_service_slab / (seg.length ** 2)
        q_moment_service = q_moment_slab + stem_dead
        summary_rows.append({
            **row,
            "span_m": seg.length,
            "tributary_area_m2": area,
            "mean_tributary_width_m": area / seg.length,
            "load_shape": SHAPES[beam_id],
            "slab_dead_udl_kN_m": slab_dead_udl,
            "beam_stem_dead_udl_kN_m": stem_dead,
            "total_dead_udl_kN_m": total_dead_udl,
            "live_udl_kN_m": live_udl,
            "service_udl_total_load_equiv_kN_m": service_udl,
            "service_udl_midspan_moment_equiv_kN_m": q_moment_service,
        })

    census_fields = [
        "beam_id", "x1_m", "y1_m", "x2_m", "y2_m", "span_m", "width_mm", "depth_mm", "panels", "role"
    ]
    with (ROOT / "Step_04_Beam_Census.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=census_fields, lineterminator="\n")
        writer.writeheader()
        for row in summary_rows:
            writer.writerow({field: f"{row[field]:.4f}" if isinstance(row[field], float) else row[field] for field in census_fields})

    contribution_fields = ["support_id", "panel_id", "tributary_area_m2", "support_type"]
    with (ROOT / "Step_04_Beam_Tributary_Area_Contributions.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=contribution_fields, lineterminator="\n")
        writer.writeheader()
        for support_id in sorted(contributions):
            for panel_id, area in sorted(contributions[support_id].items()):
                writer.writerow({
                    "support_id": support_id,
                    "panel_id": panel_id,
                    "tributary_area_m2": f"{area:.4f}",
                    "support_type": "beam" if support_id in BEAM_MAP else "wall/direct support",
                })

    load_fields = [
        "beam_id", "span_m", "depth_mm", "panels", "role", "tributary_area_m2",
        "mean_tributary_width_m", "load_shape",
        "slab_dead_udl_kN_m", "beam_stem_dead_udl_kN_m", "total_dead_udl_kN_m",
        "live_udl_kN_m", "service_udl_total_load_equiv_kN_m",
        "service_udl_midspan_moment_equiv_kN_m",
    ]
    with (ROOT / "Step_05_Beam_Line_Loads.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=load_fields, lineterminator="\n")
        writer.writeheader()
        for row in summary_rows:
            writer.writerow({
                field: f"{row[field]:.4f}" if isinstance(row[field], float) else row[field]
                for field in load_fields
            })

    # Diagram 1: beam census and Task 3 marked beam lines.
    scale = 70
    margin = 90
    width_px = int(10.8 * scale + 2 * margin)
    height_px = int(20.0 * scale + 2 * margin)
    def pt(x: float, y: float) -> tuple[int, int]:
        return int(margin + x * scale), int(height_px - margin - y * scale)

    img = Image.new("RGB", (width_px, height_px), "white")
    draw = ImageDraw.Draw(img)
    title_font = default_font(24, True)
    font = default_font(14, True)
    small = default_font(11)
    draw.text((margin, 20), "HW2 Plan 3 - Beam Census (image-derived axes)", font=title_font, fill="#172033")
    for panel in PANELS:
        draw.polygon([pt(x, y) for x, y in panel["polygon"]], fill="#f2f5f7", outline="#aab4bf")
    for support_id, seg in SUPPORTS.items():
        if support_id in BEAM_MAP:
            color = "#cf2f2f" if support_id in {"D05", "D11", "D19", "D16", "D17", "D18"} else "#175ea8"
            line_width = 6 if color == "#cf2f2f" else 3
            draw.line([pt(seg.x1, seg.y1), pt(seg.x2, seg.y2)], fill=color, width=line_width)
            mx, my = (seg.x1 + seg.x2) / 2, (seg.y1 + seg.y2) / 2
            draw.text(pt(mx, my), support_id.replace("D0", "D").replace("D", "Δ"), font=small, fill="#0b2948", anchor="mm")
        else:
            draw.line([pt(seg.x1, seg.y1), pt(seg.x2, seg.y2)], fill="#707981", width=5)
    for panel in PANELS:
        xs = [x for x, _ in panel["polygon"]]
        ys = [y for _, y in panel["polygon"]]
        draw.text(pt(sum(xs) / len(xs), sum(ys) / len(ys)), panel["panel_id"], font=font, fill="#5a6470", anchor="mm")
    draw.text((margin, height_px - 55), "Red: Beam A segments D05/D11/D19 and Beam B spans D16-D18. Blue: other beams. Grey: wall/direct supports.", font=small, fill="#333333")
    img.save(ROOT / "HW2_Beam_Census.png")

    # Diagram 2: sampled tributary regions. Colours identify the receiving beam; grey goes directly to walls.
    palette = [
        "#dceeff", "#ffe4cc", "#e1f3d8", "#f4dcea", "#fff1ad", "#dcd6f7",
        "#d7f0ef", "#f6d3d1", "#e6e6e6", "#cfe3b4", "#d8e5ff", "#ffd9a8",
    ]
    colours = {beam_id: palette[index % len(palette)] for index, beam_id in enumerate(BEAM_MAP)}
    reg = Image.new("RGB", (width_px, height_px), "white")
    rd = ImageDraw.Draw(reg)
    rd.text((margin, 20), "HW2 Beam Tributary Areas - 45-degree / midpoint allocation", font=title_font, fill="#172033")
    cell_px = max(1, int(GRID * scale * 2))
    for x, y, support_id in assigned_points:
        px, py = pt(x, y)
        colour = colours.get(support_id, "#d0d0d0")
        rd.rectangle((px, py, px + cell_px, py + cell_px), fill=colour)
    for support_id, seg in SUPPORTS.items():
        colour = "#111111" if support_id in BEAM_MAP else "#6f6f6f"
        rd.line([pt(seg.x1, seg.y1), pt(seg.x2, seg.y2)], fill=colour, width=3)
    for beam_id, seg in SEGMENTS.items():
        mx, my = (seg.x1 + seg.x2) / 2, (seg.y1 + seg.y2) / 2
        rd.text(pt(mx, my), beam_id.replace("D0", "D").replace("D", "Δ"), font=small, fill="#111111", anchor="mm")
    rd.text((margin, height_px - 55), "Coloured cells load beams. Grey cells load walls/core directly. P8 and P4/P6 use the stated one-way rules.", font=small, fill="#333333")
    reg.save(ROOT / "HW2_Beam_Tributary_Areas.png")

    # Worked load diagram for D18.
    worked_id = "D18"
    worked = next(row for row in summary_rows if row["beam_id"] == worked_id)
    profile = profiles[worked_id]
    plot_w, plot_h = 1300, 700
    chart = Image.new("RGB", (plot_w, plot_h), "white")
    cd = ImageDraw.Draw(chart)
    chart_title = default_font(28, True)
    axis_font = default_font(17)
    cd.text((70, 30), "Worked Example D18 - Service Line-Load Distribution", font=chart_title, fill="#172033")
    x0, y0, x1, y1 = 100, 600, 1220, 110
    cd.line((x0, y0, x1, y0), fill="#333333", width=3)
    cd.line((x0, y0, x0, y1), fill="#333333", width=3)
    stem = worked["beam_stem_dead_udl_kN_m"]
    total_values = [(SLAB_DEAD + LIVE) * value + stem for value in profile]
    dead_values = [SLAB_DEAD * value + stem for value in profile]
    live_values = [LIVE * value for value in profile]
    max_q = max(total_values) * 1.10
    def plot_line(values: list[float], colour: str, line_width: int) -> None:
        points = []
        for index, value in enumerate(values):
            x = x0 + (index / max(len(values) - 1, 1)) * (x1 - x0)
            y = y0 - (value / max_q) * (y0 - y1)
            points.append((int(x), int(y)))
        if len(points) > 1:
            cd.line(points, fill=colour, width=line_width)
    plot_line(total_values, "#c92828", 5)
    plot_line(dead_values, "#1f5ea8", 3)
    plot_line(live_values, "#2d8b57", 3)
    for tick in range(0, 5):
        x = x0 + tick * (x1 - x0) / 4
        cd.line((x, y0 - 5, x, y0 + 5), fill="#333333", width=2)
        cd.text((x, y0 + 14), f"{worked['span_m'] * tick / 4:.2f}", font=axis_font, fill="#333333", anchor="ma")
    for tick in range(0, 6):
        value = max_q * tick / 5
        y = y0 - tick * (y0 - y1) / 5
        cd.line((x0 - 5, y, x0 + 5, y), fill="#333333", width=2)
        cd.text((x0 - 12, y), f"{value:.1f}", font=axis_font, fill="#333333", anchor="rm")
    cd.text(((x0 + x1) / 2, 665), "Distance along D18 (m)", font=axis_font, fill="#333333", anchor="mm")
    cd.text((20, (y0 + y1) / 2), "q (kN/m)", font=axis_font, fill="#333333", anchor="mm")
    cd.line((820, 60, 870, 60), fill="#c92828", width=5); cd.text((880, 60), "Service", font=axis_font, fill="#333333", anchor="lm")
    cd.line((980, 60, 1030, 60), fill="#1f5ea8", width=3); cd.text((1040, 60), "Dead", font=axis_font, fill="#333333", anchor="lm")
    cd.line((1110, 60, 1160, 60), fill="#2d8b57", width=3); cd.text((1170, 60), "Live", font=axis_font, fill="#333333", anchor="lm")
    chart.save(ROOT / "HW2_D18_Worked_Line_Load.png")

    beam_total_area = sum(beam_area.values())
    direct_total_area = sum(direct_support_area.values())
    panel_max_error = max(abs(exact - assigned) for _, _, exact, assigned in panel_checks)

    # Markdown Task 1 report.
    task1 = [
        "# Step 04 - Beam Census and Beam Tributary Areas",
        "",
        "## 1. Scope and continuity from HW1",
        "",
        "This step extends the reviewed HW1 coordinate system. The floor outline, columns, walls, openings, and ordinary flat-slab area are reused; they are not re-derived. The detailed structural drawing identifies 25 beam segments, labelled D01-D25 here to represent drawing labels Δ1-Δ25 in machine-readable files.",
        "",
        "![HW2 marked plan](HW2_FloorPlan3_Marked_Beams.png)",
        "",
        "## 2. Beam identification",
        "",
        "Beam axes and endpoints are image-derived. D05, D11, and D19 form the marked left vertical peripheral line (Beam A). D16-D18 form the marked horizontal interior continuous line (Beam B).",
        "",
        "![Beam census](HW2_Beam_Census.png)",
        "",
        "| Beam | Start (m) | End (m) | Span (m) | Section (mm) | Bordering panels | Classification |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for row in summary_rows:
        task1.append(
            f"| {row['beam_id']} | ({row['x1_m']:.2f}, {row['y1_m']:.2f}) | "
            f"({row['x2_m']:.2f}, {row['y2_m']:.2f}) | {row['span_m']:.2f} | "
            f"{row['width_mm']}x{row['depth_mm']} | {row['panels']} | {row['role']} |"
        )
    task1 += [
        "",
        "## 3. Panel classification and allocation rule",
        "",
        "Each panel is classified before any load is assigned. Two-way panels with matched orthogonal supports are divided by nearest finite support-edge distance, producing midpoint and 45-degree boundaries. P8 is one-way because 6.05/3.00 > 2 and therefore loads only D20 and D21. The narrow P4 and P6 core-side strips are treated as one-way between their stated opposite supports. Cantilevers P10-P14 load their root supports.",
        "",
        "| Panel | Classification | Exact model area (m2) | Grid-assigned area (m2) |",
        "|---|---|---:|---:|",
    ]
    for panel_id, panel_type, exact, assigned in panel_checks:
        task1.append(f"| {panel_id} | {panel_type} | {exact:.4f} | {assigned:.4f} |")
    task1 += [
        "| P10 | cantilever, 0.50 m projection | 1.3250 | 1.3250 |",
        "| P11 | cantilever, 1.00 m projection | 2.4500 | 2.4500 |",
        "| P12 | cantilever, 0.50 m projection | 2.1500 | 2.1500 |",
        "| P13 | cantilever, 0.90 m projection | 2.2050 | 2.2050 |",
        "| P14 | cantilever, 1.20 m projection | 9.8400 | 9.8400 |",
        "",
        "Walls and core boundaries are retained as direct supports in the allocation. Grey regions in the following figure therefore do not load a beam; this prevents wall-supported slab load from being reassigned incorrectly to a nearby beam.",
        "",
        "![Beam tributary areas](HW2_Beam_Tributary_Areas.png)",
        "",
        "## 4. Beam tributary-area results",
        "",
        "| Beam | Tributary area (m2) | Mean width (m) | Load shape |",
        "|---|---:|---:|---|",
    ]
    for row in summary_rows:
        task1.append(
            f"| {row['beam_id']} | {row['tributary_area_m2']:.4f} | {row['mean_tributary_width_m']:.4f} | "
            f"{row['load_shape']} |"
        )
    task1 += [
        "",
        "## 5. Area checks and limitations",
        "",
        f"- Area assigned to beams: {beam_total_area:.4f} m2.",
        f"- Area assigned directly to walls/core/support residual: {direct_total_area:.4f} m2.",
        f"- Total reconciled ordinary slab area: {beam_total_area + direct_total_area:.4f} m2 = 179.2500 m2 from HW1.",
        f"- Maximum panel grid-area error at {GRID:.2f} m resolution: {panel_max_error:.6f} m2.",
        "- D01-D25 endpoints and panel support conditions are image-derived. Original CAD beam axes would supersede these values.",
        "- P4/P6 and the short core-side members are the most interpretation-sensitive regions and must be checked before the OpenSees model is frozen.",
        "- Equivalent beam areas exclude slab load assigned directly to structural walls. This is intentional and preserves the slab-to-support load path.",
        "",
        "The detailed contribution schedule is stored in `Step_04_Beam_Tributary_Area_Contributions.csv`.",
    ]
    (ROOT / "Step_04_Beam_Census_and_Tributary_Areas.md").write_text("\n".join(task1) + "\n", encoding="utf-8")

    # Markdown Task 2 report.
    task2 = [
        "# Step 05 - Beam Line Loads and Worked Example",
        "",
        "## 1. Load basis",
        "",
        "The adopted slab dead load is 3.75 kN/m2 and the live load is 5.00 kN/m2, consistent with HW1. No finishes value is shown, so no superimposed finish load is invented. Beam self-weight is added as the concrete stem below the 150 mm slab to avoid double-counting the slab thickness:",
        "",
        r"\[g_{beam}=0.25(d-0.15)(25)\]",
        "",
        "For each beam, the total-load-equivalent slab UDL is tributary area times area load divided by beam length. The separately reported moment-equivalent UDL reproduces the simply-supported midspan moment of the sampled triangular/trapezoidal service-load shape; it is not equivalent for local shear.",
        "",
        "## 2. Line-load summary",
        "",
        "| Beam | Span (m) | Area (m2) | Shape | Slab G (kN/m) | Beam stem G (kN/m) | Total G (kN/m) | Q (kN/m) | G+Q total-load UDL (kN/m) | G+Q midspan-moment UDL (kN/m) |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary_rows:
        task2.append(
            f"| {row['beam_id']} | {row['span_m']:.2f} | {row['tributary_area_m2']:.4f} | {row['load_shape']} | "
            f"{row['slab_dead_udl_kN_m']:.3f} | {row['beam_stem_dead_udl_kN_m']:.3f} | "
            f"{row['total_dead_udl_kN_m']:.3f} | {row['live_udl_kN_m']:.3f} | "
            f"{row['service_udl_total_load_equiv_kN_m']:.3f} | "
            f"{row['service_udl_midspan_moment_equiv_kN_m']:.3f} |"
        )
    task2 += [
        "",
        "## 3. Worked example - D18",
        "",
        "D18 is the right-hand span of marked Beam B. It is an interior beam between P5 and P9, so both slab sides contribute. The 45-degree construction produces a combined triangular/trapezoidal distribution rather than a uniform peak load.",
        "",
        f"- Span: L = {worked['span_m']:.2f} m.",
        f"- Tributary area: A = {worked['tributary_area_m2']:.4f} m2.",
        f"- Mean tributary width: A/L = {worked['mean_tributary_width_m']:.4f} m.",
        f"- Slab dead-load UDL by total load: 3.75A/L = {worked['slab_dead_udl_kN_m']:.3f} kN/m.",
        f"- Beam-stem self-weight: {worked['beam_stem_dead_udl_kN_m']:.3f} kN/m.",
        f"- Total dead-load UDL: {worked['total_dead_udl_kN_m']:.3f} kN/m.",
        f"- Live-load UDL by total load: 5.00A/L = {worked['live_udl_kN_m']:.3f} kN/m.",
        f"- Service UDL by total load: {worked['service_udl_total_load_equiv_kN_m']:.3f} kN/m.",
        f"- Service UDL reproducing simply-supported midspan moment: {worked['service_udl_midspan_moment_equiv_kN_m']:.3f} kN/m.",
        "",
        "![D18 worked line load](HW2_D18_Worked_Line_Load.png)",
        "",
        "The actual non-uniform load will be retained for the OpenSees discretised model. The total-load UDL is used for reaction checks, while the midspan-moment-equivalent UDL is used only for the stated hand moment comparison.",
        "",
        "## 4. Verification",
        "",
        "- Every D01-D25 beam has one census row and one line-load row.",
        "- The sum of beam and direct-wall tributary areas reconciles to the 179.250 m2 HW1 ordinary slab area.",
        "- Slab dead and live beam loads reconcile to beam tributary area multiplied by 3.75 and 5.00 kN/m2 respectively.",
        "- Beam-stem self-weight uses metres and kN consistently and excludes the slab thickness already counted in the area load.",
        "- Total-load and moment-equivalent UDLs are labelled separately because they answer different questions.",
        "",
        "## 5. Assumptions to freeze before Task 3",
        "",
        "1. Confirm D05/D11/D19 as Beam A and D16-D18 as Beam B.",
        "2. Confirm the image-derived 250x600 and 250x700 beam sections.",
        "3. Confirm the core-side P4/P6 support interpretation and whether D14 receives P6 edge-strip load.",
        "4. Confirm that no finishes load should be added.",
        "5. Freeze the non-uniform line-load profiles before generating the OpenSees briefing and model files.",
    ]
    (ROOT / "Step_05_Beam_Line_Loads_and_Worked_Example.md").write_text("\n".join(task2) + "\n", encoding="utf-8")

    print(f"Generated {len(summary_rows)} beam rows.")
    print(f"Beam tributary area: {beam_total_area:.4f} m2")
    print(f"Direct wall/core area: {direct_total_area:.4f} m2")
    print(f"Area closure: {beam_total_area + direct_total_area:.4f} m2")
    print(f"Maximum panel grid error: {panel_max_error:.6f} m2")


if __name__ == "__main__":
    # The former all-45-degree implementation remains above as audit evidence.
    from hw2_mixed_supports import main as revised_main
    revised_main()
