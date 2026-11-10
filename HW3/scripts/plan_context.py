"""Select source/output routing without changing image-processing parameters."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'Plan3': 'sources/assets/FloorPlan3.png',
    'NewPlan': 'sources/assets/NewPlan.png',
    'NIST': 'sources/third_plan_candidates/NIST_Figure_02_Plan.png',
}


def context():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', choices=SOURCES, default='Plan3')
    parser.add_argument('--output-plan', default=None,
                        help='Separate revision/regression directory; never an input image resize')
    args = parser.parse_args()
    output = args.output_plan or args.plan
    if not output.replace('_', '').replace('-', '').isalnum():
        parser.error('Output directory must be a single alphanumeric name')
    return args.plan, ROOT / SOURCES[args.plan], ROOT / 'outputs' / output
