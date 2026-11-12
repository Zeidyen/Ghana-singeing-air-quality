import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from PIL import Image
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.edgecolor':'#52514e','axes.labelcolor':'#0b0b0b','xtick.color':'#52514e','ytick.color':'#52514e'})
A=pd.read_csv('results/clean.csv'); S=['AM','AV','JM','TL']; col={'AM':'#2a78d6','AV':'#2a78d6','JM':'#eb6834','TL':'#eb6834'}
lab={'CO':'CO (ppm)','SO2':'SO₂ (ppm)','VOC':'VOCs (ppm)','PM25':'PM₂.₅ (µg/m³)','PM10':'PM₁₀ (µg/m³)','AT':'Air temperature (°C)','RH':'Relative humidity (%)'}
rng=np.random.default_rng(1)
def panel(ax,v,log=False,legend=False):
    data=[A.loc[A.Site==s,v].dropna().values for s in S]
    for i,(s,d) in enumerate(zip(S,data)):
        ax.scatter(i+rng.uniform(-.22,.22,len(d)),d,s=5,color=col[s],alpha=.22,lw=0,zorder=1)
    bp=ax.boxplot(data,positions=range(4),widths=.5,showfliers=False,patch_artist=True,zorder=2,medianprops=dict(color='#0b0b0b',lw=1.6),whiskerprops=dict(color='#52514e',lw=1),capprops=dict(color='#52514e',lw=1))
    for b,s in zip(bp['boxes'],S): b.set(facecolor=matplotlib.colors.to_rgba(col[s],.30),edgecolor=col[s],lw=1.4)
    ax.set_xticks(range(4),S); ax.set_xlabel('Site'); ax.set_ylabel(lab[v])
    if log: ax.set_yscale('log')
    for sp in ('top','right'): ax.spines[sp].set_visible(False)
    ax.grid(axis='y',alpha=.25,lw=.5); ax.set_axisbelow(True)
    if legend: ax.legend(handles=[Patch(facecolor=matplotlib.colors.to_rgba('#2a78d6',.3),edgecolor='#2a78d6',label='LPG-fuel'),Patch(facecolor=matplotlib.colors.to_rgba('#eb6834',.3),edgecolor='#eb6834',label='Tyre-fuel')],frameon=False,fontsize=9,loc=('lower left' if v=='RH' else 'upper left'))
# in-document panels: (variable, file, top crop, visible aspect, log)
spec=[('PM10','image2.png',.12202,2663190/1781937,True),('PM25','image3.png',.10022,2588895/1652206,True),('SO2','image4.png',.11402,2628900/1652206,False),
      ('VOC','image5.png',.11402,2628900/1652206,False),('CO','image6.png',.11782,2642044/1652206,False),('RH','image7.png',.11082,2910840/1835785,False),('AT','image8.png',.06387,2625090/1871980,False)]
for v,fn,t,ar,log in spec:
    h=3.6; fig,ax=plt.subplots(figsize=(h*ar,h),dpi=300); panel(ax,v,log,legend=True); fig.tight_layout(); fig.savefig('fig/tmp.png'); plt.close(fig)
    im=Image.open('fig/tmp.png').convert('RGB'); H=round(im.height/(1-t)); full=Image.new('RGB',(im.width,H),'white'); full.paste(im,(0,H-im.height)); full.save('fig/'+fn)
# standalone composite figures for submission
import os; os.makedirs('figures',exist_ok=True)
fig,axs=plt.subplots(2,3,figsize=(13,7.6),dpi=300)
for k,(ax,(v,log)) in enumerate(zip(axs.flat,[('PM10',True),('PM25',True),('SO2',False),('VOC',False),('CO',False)])):
    panel(ax,v,log,legend=(k==0)); ax.set_title('ABCDE'[k],loc='left',fontweight='bold',fontsize=12)
axs.flat[5].axis('off'); fig.tight_layout(); fig.savefig('figures/Figure_2_pollutants_by_site.png'); plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(9.5,4),dpi=300)
for k,(ax,v) in enumerate(zip(axs,['RH','AT'])): panel(ax,v,legend=(k==0)); ax.set_title('AB'[k],loc='left',fontweight='bold',fontsize=12)
fig.tight_layout(); fig.savefig('figures/Figure_3_microclimate_by_site.png'); plt.close(fig)
# Figure 6 composite
lb=['CO','SO₂','VOCs','PM₂.₅','PM₁₀','AT','RH']
fig,axs=plt.subplots(2,2,figsize=(11.5,9.6),dpi=300,layout='constrained')
for k,(ax,s) in enumerate(zip(axs.flat,['AM','AV','JM','TL'])):
    r=pd.read_csv(f'results/spearman_{s}.csv',index_col=0).values; im=ax.imshow(r,cmap='RdBu_r',vmin=-1,vmax=1)
    ax.set_xticks(range(7),lb,rotation=45,ha='right'); ax.set_yticks(range(7),lb)
    for i in range(7):
        for j in range(7): ax.text(j,i,f'{r[i,j]:.2f}',ha='center',va='center',fontsize=9,color='white' if abs(r[i,j])>0.6 else '#222')
    ax.set_xticks(np.arange(-.5,7),minor=True); ax.set_yticks(np.arange(-.5,7),minor=True); ax.grid(which='minor',color='white',lw=1.5); ax.tick_params(which='both',length=0)
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_title(f'{"ABCD"[k]}   Site {s}',loc='left',fontweight='bold',fontsize=12)
cb=fig.colorbar(im,ax=axs,fraction=0.025,pad=0.02); cb.set_label('Spearman ρ'); cb.outline.set_visible(False)
fig.savefig('figures/Figure_4_spearman_heatmaps.png'); plt.close(fig)
import shutil; shutil.copy('fig/image1.png','figures/Figure_1_study_design_flowchart.png'); shutil.copy('fig/image20.png','figures/Figure_5_spline_associations.png')
for k,n in enumerate(['A_CO','B_PM2.5','C_PM10','D_SO2','E_VOCs'],1): shutil.copy(f'fig/supp_image{k}.png',f'figures/Figure_S1{n}.png')
print(os.listdir('figures'))
