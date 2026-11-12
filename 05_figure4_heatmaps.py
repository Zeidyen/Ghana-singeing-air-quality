import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
lab=['CO','SO₂','VOCs','PM₂.₅','PM₁₀','AT','RH']
spec={'AM':('image16.png',.11632,.12681,.14552,0,2274570/1757680),'JM':('image17.png',.17969,.12571,.14767,.02101,2279015/1783080),
      'AV':('image18.png',.16483,.12681,.16107,0,2218690/1758315),'TL':('image19.png',.12210,.12196,.14093,0,2234565/1781175)}
for s,(fn,l,t,r_,b,ar) in spec.items():
    r=pd.read_csv(f'results/spearman_{s}.csv',index_col=0).values
    h=5.0; fig,ax=plt.subplots(figsize=(h*ar,h),dpi=260)
    im=ax.imshow(r,cmap='RdBu_r',vmin=-1,vmax=1)
    ax.set_xticks(range(7),lab,rotation=45,ha='right'); ax.set_yticks(range(7),lab)
    for i in range(7):
        for j in range(7): ax.text(j,i,f'{r[i,j]:.2f}',ha='center',va='center',fontsize=9,color='white' if abs(r[i,j])>0.6 else '#222')
    ax.set_xticks(np.arange(-.5,7),minor=True); ax.set_yticks(np.arange(-.5,7),minor=True); ax.grid(which='minor',color='white',lw=1.5); ax.tick_params(which='both',length=0)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_title(f'Site {s}',fontsize=12,pad=8)
    cb=fig.colorbar(im,ax=ax,fraction=0.046,pad=0.04); cb.set_label('Spearman ρ'); cb.outline.set_visible(False)
    fig.tight_layout(); fig.savefig('fig/tmp.png'); plt.close(fig)
    v=Image.open('fig/tmp.png').convert('RGB'); W=round(v.width/(1-l-r_)); H=round(v.height/(1-t-b))
    full=Image.new('RGB',(W,H),'white'); full.paste(v,(round(l*W),round(t*H))); full.save('fig/'+fn)
