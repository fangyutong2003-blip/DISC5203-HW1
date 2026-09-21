# Project Guidance for AI Agents

## Scope

This repository supports DISC 5203 Homework 1: image-based tributary-area and vertical-load analysis of Floor Plan 3.

## Project rules

- Keep all reports, code comments, filenames, tables, and Git commit messages in English.
- Preserve previous step files and Git history. Add a new step or revision rather than deleting audit evidence.
- Treat plan coordinates as image-derived unless original CAD coordinates are supplied.
- State all assumptions, units, exclusions, and numerical tolerances explicitly.
- Do not present an open direction line as a completed tributary boundary. Regions must close and pass area conservation.
- Keep O1/O2 as voids and S1 separate from the ordinary flat slab unless new source evidence changes the interpretation.
- Do not add unspecified structural loads without identifying them as assumptions.
- Verify generated calculations independently before reporting completion.

## Calculation sequence

1. Read and review the source drawing.
2. Establish the coordinate system, slab outline, openings, and special zones.
3. Identify support points and finite wall-axis segments.
4. Generate closed tributary regions and verify area conservation.
5. Calculate per-floor dead and live loads.
6. Add vertical-element self-weight and accumulate loads by storey.
7. Check totals, combinations, IDs, and representative elements independently.
8. Save intermediate outputs and commit each meaningful stage to Git.

## Required checks

- Tributary regions collectively equal the adopted ordinary slab area.
- Every vertical element appears consistently in geometry, area, and load files.
- Floor accumulation follows 1:2:3:4:5 for the five-storey building.
- The sum of element loads equals independently calculated whole-floor loads.
- Figures and Markdown links resolve from the repository root.

