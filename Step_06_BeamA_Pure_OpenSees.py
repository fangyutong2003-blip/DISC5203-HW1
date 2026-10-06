"""OpenSees input entry point for the standalone Beam A model."""

from step06_opensees_core import run_model


if __name__ == "__main__":
    result = run_model("Beam A", "pure")
    print(f"Beam A pure model complete: |M|max = {result['peak_abs_moment_kNm']:.3f} kN m")
