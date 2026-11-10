# HW3 Task 3 - Analytical CM, stiffness and CR

Status: provisional common-geometry baseline; formal Task 2 promotion remains pending. This is an agent-generated analytical calculation, not claimed as handwritten student work.

## Assumptions and mass

The floor reuses the retained HW1 dimension-chain rectangles including balconies. O1/O2 are voids. S1 is deducted from ordinary slab and added separately as an equivalent-horizontal mass zone, with the inherited 8.75 kN/m2 service intensity. No vertical-member self-weight is added to this prescribed uniform floor mass. Full G+Q mass is an exercise convention, not a code seismic combination.

Net equivalent mass area = 184.615000 m2. CM = (4.963771, 8.326083) m. One-storey mass = 164.666794 t; five-storey sum = 823.333970 t. The assignment's factor n=5 produces a total, not a per-storey mass. Polar mass moment about CM = 6416.764916 t m2.

See [signed rectangle calculation](outputs/Plan3/task3/Mass_Rectangles.csv). Positive body/balcony rectangles, negative void rectangles and a separately added S1 make the accounting explicit.

## Wall stiffness and matrix derivation

E=30e6 kN/m2, nu=0.2, G=12.5e6 kN/m2, H=3 m, Av=(5/6)Lt. Walls are cantilevers: k_b=3EI/H^3 and k_bs=1/[H^3/(3EI)+H/(GAv)]. Strong I=tL^3/12; weak I=Lt^3/12. The matched rectangular-wall baseline retains both bending directions, excludes intrinsic vertical wall torsion, columns, approximate short returns and cracking. The brief's strong-direction-only construction is reported separately as a sensitivity case.

About CM, q=(u,v,phi), a_x=(1,0,-dy), a_y=(0,1,dx). Assemble K=sum[kx outer(a_x,a_x)+ky outer(a_y,a_y)]. Thus Kxphi=-sum(kx*dy), Kyphi=sum(ky*dx). For orthogonal walls, xr=xm+Kyphi/Kyy and yr=ym-Kxphi/Kxx. From F=inv(K), xr=xm-Fphiy/Fphiphi and yr=ym+Fphix/Fphiphi. The two routes must agree.

The brief's stiffness ratio Kphix/Kphiphi has units 1/m, so it cannot be added to a coordinate. The flexibility ratios above have units m. K uses mixed translational/rotational units: its 2x2 translational block is kN/m, translation-rotation entries kN and the rotational entry kN m. Angles are radians.

[Per-wall stiffness table](outputs/Plan3/task3/Wall_Stiffnesses.csv) includes bending-only and shear-inclusive values and the shear fraction of strong-axis flexibility.

| Assumption | CR x (m) | CR y (m) | Eccentricity (m) |
|---|---:|---:|---:|
| matched_rectangular_shear | 5.563280 | 9.694116 | 1.493628 |
| matched_rectangular_bending_only | 5.756626 | 9.893719 | 1.756731 |
| brief_strong_direction_only_shear | 5.566963 | 9.714323 | 1.513623 |
| brief_strong_direction_only_bending | 5.761623 | 9.909434 | 1.773012 |

### Matched baseline K about CM

```text
[[ 3.812103e+06  0.000000e+00 -5.215082e+06]
 [ 0.000000e+00  3.045466e+06  1.825785e+06]
 [-5.215082e+06  1.825785e+06  1.714294e+08]]
```

### Matched baseline flexibility F about CM

```text
[[ 2.737900100832e-07 -5.025404745675e-09  8.382531457602e-09]
 [-5.025404745675e-09  3.305592905931e-07 -3.673452953916e-09]
 [ 8.382531457602e-09 -3.673452953916e-09  6.127433809332e-09]]
```

## Demonstration force shares

A separately declared demonstration force Fy=100.0 kN acts at CM. It is an assumed linear-analysis test, not a code design demand. Torque about CR is (xm-xr)*Fy=-59.950920 kN m. In general Tz=(xm-xr)*Fy-(ym-yr)*Fx; e*F is a maximum lever-arm envelope, not the torque for every force direction.

At CR, direct y force share is ky/sum(ky), torsional y coefficient is ky*dx/J, and torsional x coefficient is -kx*dy/J. [Force-share table](outputs/Plan3/task3/Wall_Force_Shares.csv) records direct and torsional components separately. Unit-torque coefficients have units 1/m, not dimensionless percentages.

## Reproduction and verification

Run python HW3/scripts/task03_centres.py, then python HW3/scripts/verify_task03.py. The independent checker uses polygon boundary integrals, direct weighted CR and separately assembled equilibrium equations. OpenSees matching is a later stage, not asserted by this analytical report.

The [pre-solve briefing](records/Task_03_PreSolve_Briefing.md) and params_mechanics.json were committed before this calculation. Input hashes and all intermediate matrices are retained in [Analytical_Result.json](outputs/Plan3/task3/Analytical_Result.json).
