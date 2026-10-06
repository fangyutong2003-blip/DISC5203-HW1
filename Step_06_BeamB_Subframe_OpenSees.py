"""OpenSees input entry point for the one-storey Beam B subframe."""

from step06_opensees_core import run_model


if __name__ == "__main__":
    result = run_model("Beam B", "subframe")
    print(f"Beam B subframe complete: |M|max = {result['peak_abs_moment_kNm']:.3f} kN m")
