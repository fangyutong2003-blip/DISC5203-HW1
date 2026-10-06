"""OpenSees input entry point for the one-storey Beam A subframe."""

from step06_opensees_core import run_model


if __name__ == "__main__":
    result = run_model("Beam A", "subframe")
    print(f"Beam A subframe complete: |M|max = {result['peak_abs_moment_kNm']:.3f} kN m")
