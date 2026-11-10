# Task 4 OpenSees model briefing - frozen before solve

Author: coding agent, 10 November 2026. This is an implementation briefing, not a student-signed structural prediction.

Use the same Plan 3 walls, CM, mass and material in params_mechanics.json and Task 3. Build a three-dimensional, six-DOF one-storey model. Each wall is one vertical ElasticTimoshenkoBeam from z=0 to z=3 m, fixed at its base. Its local y axis follows the horizontal wall length; local x is vertical. Thus Iz=t*L^3/12 is the strong lateral inertia and Iy=L*t^3/12 is the weak inertia. Both shear areas equal (5/6)*L*t. Set intrinsic vertical wall torsion J=0 consistently with the frozen analytical model; floor torsional resistance comes from lateral wall lever arms. Do not silently introduce fixed-fixed wall behaviour.

Place the master node at CM, z=3 m. Fix only its z, rx and ry freedoms; retain u, v and rz. Constrain the wall tops with ops.rigidDiaphragm(3, master, *tops) and ops.constraints('Transformation'). Wall-top z is fixed; bending rotations remain free. No artificial very-stiff slab or penalty diaphragm is permitted.

Run three independent rebuilt models with unit Px, Py and Mz at the master; collect u, v and rz to form flexibility F. Invert F to K and calculate CR using the flexibility ratios from Task 3. Compare all entries and CR against the analytical rectangular-wall model. Extract base reactions and element forces. Positive table forces mean the wall resistance demand, equal to minus the base reaction in global x/y.

For an explicitly assumed 100 kN global-y demonstration force at CM, record master translation/rotation and each wall's horizontal force. Check horizontal equilibrium and base moment about CM, including fixed-base nodal moments. For diaphragm equilibrium, use each wall shear with its plan lever arm, since intrinsic vertical wall torsion is zero.

Task 5 tests rebuild the same model: push through CR in x and y and confirm zero rotation. Decompose the 100 kN CM force into a push through CR and signed torque T=(xm-xr)*Fy. Superpose displacements and all wall forces, and compare with direct loading. Include small analytical unit-cantilever tests for the strong and weak axes and an independently rebuilt bending-only beam case as limit checks.

Use the official OpenSeesPy command definitions:

- https://openseespydoc.readthedocs.io/en/latest/src/ElasticTimoshenkoBeam.html
- https://openseespydoc.readthedocs.io/en/latest/src/rigidDiaphragm.html

The Task 3 analytical result and this briefing must be committed before executing the OpenSees analysis. Task 2 identity/exposure/harness limits remain documented, and the mechanics baseline remains provisional.
