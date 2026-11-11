# Numerical area refinement before OpenSees

The retained 0.05 m area mesh closes both declared domains exactly. Against a 0.10 m mesh, the largest relative per-support change was 1.455% for NewPlan T4 and 2.210% for NIST NC18. The largest absolute changes were 0.400 m2 and 0.918 m2 respectively. Those observations are preserved; they are not source-reading accuracy scores.

Before running OpenSees, retain the 0.05 m outputs and run a separate 0.025 m partition checked against 0.05 m. No image mask, support location, source size or reference answer changes. This is numerical mesh refinement responding to a quantified integration concern, not retuning the frozen image extraction. The target is approximately 1% or better per-support area change; any remaining exception must be reported rather than hidden. The refined files use engineering_r1_refined; engineering_r1 remains the initial area/hand-calculation record.

The floor mass, analytical K/CR and mode calculations depend on declared geometry and uniform-area integrals, not the tributary raster. They should remain unchanged between the two meshes. Column-assumption and schematic-dimension uncertainties remain separate from this numerical convergence test.
