# Task 3 pre-solve analytical briefing

Date: 10 November 2026 (Asia/Singapore). Author: coding agent. This is an analytical plan recorded before the new mechanics solve, not a signed student prediction or a handwritten student calculation.

## Input and selection status

Use the saved Plan 3 labelled rectangles and the retained dimension-chain floor. The two received readers agree on all five queried fields and resolve all five against the frozen alternative reference. No winner is established. Run an explicitly provisional engineering baseline on their common geometry; do not claim formal Task 2 promotion. The context-exposure and execution-harness limits remain open.

## Mass and geometry

Use metres, kN, seconds and tonnes; gravity g=9.81 m/s2. Preserve O1/O2 as voids. Include balconies. Keep S1 as a separate equivalent-horizontal-area mass zone with the inherited service intensity, rather than silently merging it into ordinary flat slab. For this exercise use the specified full G+Q=8.75 kN/m2 equivalent mass intensity, not a code seismic mass combination. Compute one-storey mass as w*A/g and report five-storey total separately. Do not multiply a one-storey diaphragm mass by five.

Calculate signed rectangular areas, first moments and polar mass moment about CM. Gross outline is 186.615 m2, voids 2.000 m2, ordinary slab 179.250 m2, separate S1 5.365 m2. Net equivalent mass area is 184.615 m2. Uniform intensity permits area-weighted CM.

## Walls and stiffness assumptions

Use 12 main-wall rectangles only, E=30e6 kN/m2, nu=0.20, G=E/[2(1+nu)], H=3 m and Av=(5/6)*L*t. Columns and approximate short returns are excluded from the baseline lateral system. No cracking or shell/diaphragm flexibility is introduced.

For every wall report k_b=3EI/H^3 and k_bs=1/[H^3/(3EI)+H/(G*Av)], with I_strong=t*L^3/12. Also report the physically present weak-axis stiffness of a rectangular Timoshenko cantilever using I_weak=L*t^3/12. The matched analytical/model baseline retains both principal bending directions. A separate strong-direction-only matrix reproduces the simplified scalar-wall construction in the brief. These are explicitly different assumptions, not a numerical discrepancy to hide.

Exclude intrinsic wall torsion about the vertical axis (J_element=0 in the planned beam model); floor torsional stiffness still arises from the lateral resisting walls' lever arms. Bases fixed, wall-top bending rotations free, and the floor ties horizontal translations and vertical-axis rotation. These match cantilever rather than fixed-fixed wall bending.

## Derivation to freeze before solving

Let q=(u,v,phi) at CM, dx=x_i-x_m and dy=y_i-y_m. Wall-top translations are u_i=u-dy*phi and v_i=v+dx*phi. Assemble K=sum[kx*a_x*a_x^T + ky*a_y*a_y^T] with a_x=(1,0,-dy), a_y=(0,1,dx). Consequently Kxphi=-sum(kx*dy), Kyphi=sum(ky*dx), and Kphiphi=sum(kx*dy^2+ky*dx^2).

For this orthogonal system CR is xr=xm+Kyphi/Kyy, yr=ym-Kxphi/Kxx. Equivalently, with F=K^-1, xr=xm-Fphiy/Fphiphi, yr=ym+Fphix/Fphiphi. Derive these from zero rotation under an offset load rather than copying the inconsistent stiffness-denominator formula in the assignment.

The brief's Kphix/Kphiphi ratio has units 1/m and cannot be added to a coordinate. The flexibility ratios above have units m. All K coordinates must refer to the same reference point. The sum is of outer products of 3-component column vectors; treating a displayed row vector literally would otherwise produce a scalar.

## Expected checks

- Signed areas and first moments agree with an independent polygon integration.
- K is symmetric positive definite; shear-inclusive stiffness is below bending-only stiffness.
- CR from weighted positions and from F agrees to 1e-8 m analytically.
- Moving the matrix origin to CR removes translation/rotation coupling.
- Unit force through CR gives near-zero rotation; unit force through CM rotates when the perpendicular eccentricity is nonzero.
- A later OpenSees model must reproduce the same assumptions before its output is compared. Target hand/model CR agreement 1e-5 m and relative flexibility error 1e-6; image-coordinate accuracy is a separate issue.

No analytical result is asserted before the script is run. Preserve this briefing in Git before the solve.
