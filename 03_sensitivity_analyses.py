import pandas as pd, numpy as np, json, itertools, warnings, patsy
warnings.filterwarnings('ignore')
from scipy import stats
import statsmodels.api as sm, statsmodels.formula.api as smf
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pd.set_option('display.width',220)
A=pd.read_csv('results/clean.csv'); A['grp']=A.Site+'_'+A.day.astype(str); S=['AM','AV','JM','TL']; P=['CO','SO2','VOC','PM25','PM10']
# 1 daily medians
DM=A.groupby(['Site','day'])[P].median().reset_index()
rows=[]
for v in P:
    for a,b in itertools.combinations(S,2):
        xa=DM.loc[DM.Site==a,v].dropna(); xb=DM.loc[DM.Site==b,v].dropna(); u,p=stats.mannwhitneyu(xa,xb)
        xh=A.loc[A.Site==a,v].dropna(); yh=A.loc[A.Site==b,v].dropna(); ph=stats.mannwhitneyu(xh,yh)[1]
        rows.append(dict(Var=v,A=a,B=b,nA=len(xa),nB=len(xb),medA=xa.median(),medB=xb.median(),U=u,p=p,PS=u/len(xa)/len(xb),p_hourly=ph))
DMT=pd.DataFrame(rows); DMT.to_csv('results/daily_mw.csv',index=False)
DMT['sig_d']=DMT.p<0.05; DMT['sig_h']=DMT.p_hourly<0.05
print(DMT[['Var','A','B','medA','medB','p','PS','p_hourly']].to_string(index=False,float_format=lambda x:'%.3g'%x))
print('agreement in significance:',(DMT.sig_d==DMT.sig_h).sum(),'of',len(DMT)); print(DMT[DMT.sig_d!=DMT.sig_h][['Var','A','B','p','p_hourly']].to_string(index=False))
# 2 residual autocorrelation of mixed models
B=A.copy(); B['ATz']=(B.AT-B.AT.mean())/B.AT.std(); B['RHz']=(B.RH-B.RH.mean())/B.RH.std()
f='~ C(Site,Treatment("AM"))*ATz + C(Site,Treatment("AM"))*RHz'; ac=[]
for v in ['CO','SO2','PM25','PM10']:
    d=B.dropna(subset=[v,'ATz','RHz']).copy(); m=None
    for meth in ('powell','nm','bfgs','lbfgs'):
        try:
            m=smf.mixedlm(v+f,d,groups=d['grp']).fit(reml=True,method=meth,maxiter=2000)
            if m.converged: break
        except Exception: pass
    d['res']=m.resid
    r1=np.mean([g.sort_values('Hour')['res'].autocorr(1) for _,g in d.groupby('grp') if len(g)>3])
    ac.append(dict(Pollutant=v,lag1_within_day=r1)); 
AC=pd.DataFrame(ac); AC.to_csv('results/resid_ac.csv',index=False); print(AC.round(2).to_string(index=False))
# 3 completeness
comp=[]
for s in S:
    g=A[A.Site==s]
    for v in P+['AT','RH']: comp.append(dict(Site=s,Var=v,Recorded=len(g),Analysed=int(g[v].notna().sum()),Pct=100*g[v].notna().mean()))
CP=pd.DataFrame(comp); CP.to_csv('results/completeness.csv',index=False); print(CP.pivot(index='Var',columns='Site',values='Analysed').to_string()); print('min pct %.1f'%CP.Pct.min())
# 4 spline: confidence bands at the average site effect, and trimmed sensitivity
def fit(formula,d): return smf.glm(formula,d,family=sm.families.Poisson()).fit(cov_type='cluster',cov_kwds={'groups':d['grp']},maxiter=200)
def wald(m,key):
    idx=[i for i,n in enumerate(m.params.index) if n.startswith(key)]; R=np.zeros((len(idx),len(m.params)))
    for k,i in enumerate(idx): R[k,i]=1
    w=m.wald_test(R,use_f=False,scalar=True); return float(w.statistic),float(w.pvalue)
lo_at,hi_at=A.AT.quantile(.05),A.AT.quantile(.95); lo_rh,hi_rh=A.RH.quantile(.05),A.RH.quantile(.95)
band={}; sens=[]
for v in P:
    d=A.dropna(subset=[v,'AT','RH']).copy(); form=f'{v} ~ C(Site) + bs(AT,df=3) + bs(RH,df=3)'
    m=fit(form,d); di=patsy.dmatrices(form,d,return_type='dataframe')[1].design_info; beta=m.params.values; V=m.cov_params().values; out={}
    for term,other in (('AT','RH'),('RH','AT')):
        g=np.linspace(d[term].quantile(.01),d[term].quantile(.99),80); Xs=[]
        for s in S:
            nd=pd.DataFrame({term:g,other:d[other].median(),'Site':s}); Xs.append(np.asarray(patsy.dmatrix(di,nd)))
        X=np.mean(Xs,axis=0); eta=X@beta; se=np.sqrt(np.einsum('ij,jk,ik->i',X,V,X))
        out[term]=dict(x=g.tolist(),y=np.exp(eta).tolist(),lo=np.exp(eta-1.96*se).tolist(),hi=np.exp(eta+1.96*se).tolist())
    band[v]=out
    dt=d[(d.AT>=lo_at)&(d.AT<=hi_at)&(d.RH>=lo_rh)&(d.RH<=hi_rh)]; mt=fit(form,dt)
    for term,key in (('AT','bs(AT'),('RH','bs(RH')):
        c0,p0=wald(m,key); c1,p1=wald(mt,key); sens.append(dict(Pollutant=v,Term=term,chi2=c0,p=p0,N=len(d),chi2_trim=c1,p_trim=p1,N_trim=len(dt)))
SN=pd.DataFrame(sens); SN.to_csv('results/spline_sens.csv',index=False); print(SN.round(4).to_string(index=False)); print('trim AT %.1f-%.1f RH %.1f-%.1f'%(lo_at,hi_at,lo_rh,hi_rh))
json.dump(band,open('results/splineband.json','w'))
lab={'CO':'CO (ppm)','SO2':'SO₂ (ppm)','VOC':'VOCs (ppm)','PM25':'PM₂.₅ (µg/m³)','PM10':'PM₁₀ (µg/m³)'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11})
fig,axs=plt.subplots(2,5,figsize=(15,6),dpi=220)
for j,v in enumerate(['PM10','PM25','CO','SO2','VOC']):
    for i,(t,xl,c) in enumerate([('AT','Air temperature (°C)','#b2182b'),('RH','Relative humidity (%)','#2166ac')]):
        ax=axs[i,j]; b=band[v][t]; ax.fill_between(b['x'],b['lo'],b['hi'],color=c,alpha=.18,lw=0); ax.plot(b['x'],b['y'],color=c,lw=2)
        ax.set_ylim(0,min(max(b['hi']),3.5*max(b['y']))*1.05)
        ax.set_xlabel(xl,fontsize=10); ax.set_ylabel(lab[v],fontsize=10); ax.tick_params(labelsize=9)
        for sp in ('top','right'): ax.spines[sp].set_visible(False)
        ax.grid(alpha=.25,lw=.5)
fig.tight_layout(); fig.savefig('fig/image20.png'); plt.close(fig)
for v in P:
    for t in ('AT','RH'):
        b=band[v][t]; k=int(np.argmax(b['y'])); print(v,t,'peak at %.1f'%b['x'][k],[(round(b['x'][i],1),round(b['y'][i],2)) for i in (0,26,53,79)])
