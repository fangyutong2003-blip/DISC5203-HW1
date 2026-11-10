"""Display unchanged input images and the fixed-rule masks for the portability report."""
import json
from pathlib import Path
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    freeze = json.loads((ROOT/'records/Task_08_Input_Freeze.json').read_text())
    fig,axes = plt.subplots(2,2,figsize=(12,10))
    for row,item in enumerate(freeze['inputs']):
        plan=item['plan']
        image=cv2.imread(str(ROOT/item['file']),0)
        mask=cv2.imread(str(ROOT/'outputs'/plan/'stage01/04_Open21.png'),0)
        record=json.loads((ROOT/'outputs'/plan/'stage01/Classical_Components.json').read_text())
        axes[row,0].imshow(image,cmap='gray',vmin=0,vmax=255)
        axes[row,1].imshow(mask,cmap='gray',vmin=0,vmax=255)
        axes[row,0].set_title(plan+' - frozen input')
        axes[row,1].set_title(f"{plan} - unchanged rules: {len(record['components'])} raw components")
        for ax in axes[row]:
            ax.axis('off')
    fig.suptitle('Task 8: retained portability failures, not accepted structural geometry')
    fig.text(.5,.015,'NIST Figure 2: Elsibaie et al. (2025), NIST TN 2351. Republished courtesy of NIST.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.035,1,.94),h_pad=3,w_pad=1.5)
    output=ROOT/'outputs/Task08'
    output.mkdir(parents=True,exist_ok=True)
    fig.savefig(output/'Unchanged_Classical_Comparison.png',dpi=160)
    plt.close(fig)


if __name__=='__main__':
    main()
