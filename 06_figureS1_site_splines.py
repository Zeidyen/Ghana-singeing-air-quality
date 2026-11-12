import pandas as pd, numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=['AM','AV','JM','TL']
lab={'CO':'CO (ppm)','SO2':'SO₂ (ppm)','VOC':'VOCs (ppm)','PM25':'PM₂.₅ (µg/m³)','PM10':'PM₁₀ (µg/m³)','AT':'Air temperature (°C)','RH':'Relative humidity (%)'}
import json
SPJ=json.load(open('results/splinesite.json'))
for k,v in enumerate(['CO','PM25','PM10','SO2','VOC'],1):
    fig,axs=plt.subplots(2,4,figsize=(13,5.68),dpi=200)
    for j,s_ in enumerate(S):
        e_=SPJ[v][s_]
        for i,(t,c) in enumerate([('AT','#b2182b'),('RH','#2166ac')]):
            ax=axs[i,j]
            if e_ is not None:
                g,mu,lo,hi=e_['curves'][t]; ax.fill_between(g,lo,hi,color=c,alpha=.18,lw=0); ax.plot(g,mu,color=c,lw=1.8)
                ax.set_ylim(0,min(max(hi),4*max(mu))*1.05 if max(mu)>0 else 1)
            ax.set_title(f"{s_} (n = {e_['n'] if e_ else 0})",fontsize=10); ax.set_xlabel(lab[t],fontsize=9); ax.set_ylabel(lab[v] if j==0 else '',fontsize=9); ax.tick_params(labelsize=8)
            for sp in ('top','right'): ax.spines[sp].set_visible(False)
            ax.grid(alpha=.25,lw=.5)
    fig.tight_layout(); fig.savefig(f'fig/supp_image{k}.png'); plt.close(fig)
