# Tasks 6 and 7 - Design briefing before optimisation

Date: 10 November 2026, Asia/Singapore. Author: coding agent. This is a reviewable mathematical design proposal, not student signoff or a construction design.

## Frozen baseline

Use the analytical and OpenSees baseline already checked in Tasks 3-5. Keep the signed-rectangle floor mass, CM, polar mass moment, ordinary/stair separation, O1/O2 voids and all column positions fixed. Preserve baseline files and Git history. Formal Task 2 promotion remains pending; the two received readers agree on the queried geometry.

## Chosen modification and intent

Change only the thickness of existing walls T9 (left side) and T10 (bottom side). T9 should increase y-direction stiffness on the low-x side and move CR left; T10 should increase x-direction stiffness on the low-y side and move CR down. This avoids adding an entirely new wall through an opening or moving a column/grid line. Both strong and weak wall stiffness must be recalculated, since thickness changes weak inertia cubically.

Hold T9's exterior left face fixed and grow its thickness inward, so its centre x moves by half the thickness increase. Hold T10's exterior bottom face fixed and grow upward, so its centre y moves by half the increase. Preserve each wall's labelled main length and direction. This is a deterministic geometric change specified before optimisation, not a VLM coordinate edit.

Solve the two residuals (CRx-CMx, CRy-CMy) using thicknesses bounded from the original 0.25 m to 1.00 m, starting at 0.50 m each. Target ideal eccentricity <=1e-6 m. Preserve the actual optimisation trajectory and termination message. Failure to meet this criterion is a failed candidate, not a completed design. Also evaluate thicknesses rounded to a 5 mm grid as a practical sensitivity; report its residual eccentricity honestly.

Check all modified rectangles remain inside the adopted floor, avoid the void/stair interiors, do not overlap existing column footprints, and do not intersect other main walls except pre-existing junctions. Record width changes, centre changes, concrete volume and dead-weight increase per storey. Use the inherited concrete unit weight 25 kN/m3.

## Mass and scope limitation

The assignment explicitly keeps mass layout fixed. Therefore wall thickening does not update the prescribed equivalent floor mass in this exercise. Quantify the added concrete and mass-equivalent dead weight separately. A real redesign must revisit that added mass, gravity load, foundation/connection/reinforcement and architectural clearance; it is not legitimate to claim a fully designed building from the fixed-mass result.

## Numerical and mechanics checks

Recompute the analytical K and CR before rebuilding the matching OpenSees Timoshenko rigid diaphragm. Keep all baseline material, shear, weak-axis and wall-torsion assumptions. Compare new CR from hand and model, forces under assumed 100 kN x and y tests, and rotation at CM. Require hand/model CR difference <=1e-5 m and static force/moment closure <=1e-7 kN or kN m.

For Task 7 report both force directions. The signed torque is T=(xm-xr)Fy-(ym-yr)Fx; e*F is only the perpendicular envelope. For a y load, a wall's aligned-force factor is 1+(xm-xr)*(x_i-xr)/r_ty^2 with r_ty^2=J/Kyy. For an x load, the corresponding factor is 1+(ym-yr)*(y_i-yr)/r_tx^2 with r_tx^2=J/Kxx. The brief's radius-only denominator is dimensionally inconsistent; use the squared torsional radius and the wall stiffness in the force expression.

Use the same mass matrix diag(M,M,I_CM) before and after. Compute the actual coupled three-DOF modes and identify the mode with largest rotational mass fraction. Also report clearly labelled uncoupled characteristic period ratios. Attempt a matching OpenSees eigenanalysis with mass at the diaphragm master; preserve any failure rather than inventing a period.

Before solving, the only prediction is directional: the selected stiffness additions should move CR left/down and reduce CM-induced rotation. No final thickness, force reduction or period trend is assumed in advance. CM=CR does not guarantee torsion is no longer the first mode and does not remove height-dependent or nonuniform-ground-motion torsion.
