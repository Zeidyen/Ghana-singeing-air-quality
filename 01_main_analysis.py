import pandas as pd, numpy as np, sys, json, warnings, itertools
warnings.filterwarnings('ignore')
from scipy import stats
import statsmodels.formula.api as smf
import patsy
pd.set_option('display.width',250); pd.set_option('display.max_columns',40)
x=pd.read_excel((sys.argv[1] if len(sys.argv)>1 else 'data/pollution_data_raw.xlsx'),sheet_name=None)
code={'AM':'AM','TL':'TL','JM':'JM','AV':'AV'}
ren={'CO(ppm)':'CO','SO2(ppm)':'SO2','VOCH(ppm)':'VOC','PM 2.5':'PM25','PM10':'PM10'}
fr=[]; log={}
for k,d in x.items():
    d.columns=[str(c).strip() for c in d.columns]; d=d.rename(columns=ren); s=code[k]
    n0=len(d); d=d[d['Hour'].notna()].copy(); log[s]={'rows_in_sheet':n0,'unlabelled_rows_dropped':n0-len(d)}
    d['Site']=s
    _sw=(d['PM10']<d['PM25']); log[s]['pm_rows_swapped']=int(_sw.sum())   # data-entry correction (author): values entered in the wrong column
    _lo=np.minimum(d['PM25'].values,d['PM10'].values); _hi=np.maximum(d['PM25'].values,d['PM10'].values); d['PM25']=_lo; d['PM10']=_hi
    d['PM25']/=1000; d['PM10']/=1000; d['day']=((d['Hour']-1)//12).astype(int)+1
    fr.append(d[['Hour','Site','day','CO','SO2','VOC','PM25','PM10','AT','RH']])
A=pd.concat(fr,ignore_index=True)
# --- cleaning rules
gas=['CO','SO2','VOC']
imp=(A.Site=='AV')&(((A.CO*1000).round(6)%1!=0)|((A.SO2*1000).round(6)%1!=0)|((A.VOC*1000).round(6)%1!=0))
A.loc[imp,gas]=np.nan; log['AV']['interpolated_gas_rows_set_missing']=int(imp.sum())
bt=A.AT>45; A.loc[bt,'AT']=np.nan
br=A.RH<50; A.loc[br,'RH']=np.nan
for s in code.values():
    log[s]['AT_gt45_set_missing']=int((bt&(A.Site==s)).sum()); log[s]['RH_lt50_set_missing']=int((br&(A.Site==s)).sum()); log[s]['rows_analysed']=int((A.Site==s).sum())
A.to_csv('results/clean.csv',index=False)
S=['AM','AV','JM','TL']; P=['CO','SO2','VOC','PM25','PM10']; V=P+['AT','RH']
R={'cleaning':log}
# --- descriptives
desc=[]
for s in S:
    for v in V:
        a=A.loc[A.Site==s,v].dropna()
        desc.append(dict(Site=s,Var=v,N=len(a),Mean=a.mean(),SD=a.std(),Median=a.median(),Q1=a.quantile(.25),Q3=a.quantile(.75),Min=a.min(),Max=a.max()))
D=pd.DataFrame(desc); D.to_csv('results/desc.csv',index=False); 
# --- Mann-Whitney
mw=[]
for v in P:
    for a,b in itertools.combinations(S,2):
        xa=A.loc[A.Site==a,v].dropna(); xb=A.loc[A.Site==b,v].dropna()
        u,p=stats.mannwhitneyu(xa,xb,alternative='two-sided')
        mw.append(dict(Var=v,A=a,B=b,nA=len(xa),nB=len(xb),U=u,p=p,PS=u/(len(xa)*len(xb)),medA=xa.median(),medB=xb.median()))
M=pd.DataFrame(mw); M.to_csv('results/mw.csv',index=False); 
# --- Spearman
sp={}
for s in S:
    r=A.loc[A.Site==s,V].corr(method='spearman'); sp[s]=r; r.to_csv(f'results/spearman_{s}.csv'); 
# --- models
B=A.copy(); B['ATz']=(B.AT-B.AT.mean())/B.AT.std(); B['RHz']=(B.RH-B.RH.mean())/B.RH.std(); B['grp']=B.Site+'_'+B.day.astype(str)
R['z']={'AT_mean':B.AT.mean(),'AT_sd':B.AT.std(),'RH_mean':B.RH.mean(),'RH_sd':B.RH.std()}
f='~ C(Site,Treatment("AM"))*ATz + C(Site,Treatment("AM"))*RHz'
coef=[]; fit=[]
def clean(n): return n.replace('C(Site, Treatment("AM"))[T.','Site[').replace(']',']')
for v in P:
    d=B.dropna(subset=[v,'ATz','RHz'])
    if v!='VOC':
        m=None
        for meth in ('powell','nm','bfgs','lbfgs','cg'):
            try:
                m=smf.mixedlm(v+f,d,groups=d['grp']).fit(reml=True,method=meth,maxiter=2000)
                if m.converged and np.isfinite(m.bse).all(): print(v,'fitted with',meth); break
            except Exception as e: print(v,meth,'failed',type(e).__name__)
        fe=m.fe_params; ci=m.conf_int().loc[fe.index]
        for n in fe.index: coef.append(dict(Pollutant=v,Model='LME',Term=clean(n),Beta=fe[n],SE=m.bse[n],CI_low=ci.loc[n,0],CI_high=ci.loc[n,1],p=m.pvalues[n]))
        X=patsy.dmatrix(f[1:],d,return_type='dataframe'); vf=np.var(X.values@fe.values,ddof=0); vr=float(m.cov_re.iloc[0,0]); ve=m.scale
        fit.append(dict(Pollutant=v,Model='LME',N=len(d),Groups=d.grp.nunique(),R2_marginal=vf/(vf+vr+ve),R2_conditional=(vf+vr)/(vf+vr+ve),Var_fixed=vf,Var_day=vr,Var_resid=ve,converged=m.converged))
    else:
        m=smf.ols(v+f,d).fit(cov_type='cluster',cov_kwds={'groups':d['grp']}); ci=m.conf_int()
        for n in m.params.index: coef.append(dict(Pollutant=v,Model='OLS (cluster-robust)',Term=clean(n),Beta=m.params[n],SE=m.bse[n],CI_low=ci.loc[n,0],CI_high=ci.loc[n,1],p=m.pvalues[n]))
        fit.append(dict(Pollutant=v,Model='OLS',N=len(d),Groups=d.grp.nunique(),R2_marginal=m.rsquared,R2_conditional=np.nan,Var_fixed=np.nan,Var_day=np.nan,Var_resid=m.mse_resid,converged=True))
CF=pd.DataFrame(coef); CF.to_csv('results/coef.csv',index=False); F=pd.DataFrame(fit); F.to_csv('results/fit.csv',index=False)
print(F.round(4).to_string())
# --- spline regressions
spl=[]; pred={}
for v in P:
    d=B.dropna(subset=[v,'AT','RH'])
    full=smf.ols(f'{v} ~ C(Site) + bs(AT,df=3) + bs(RH,df=3)',d).fit()
    for term,red in [('AT',f'{v} ~ C(Site) + bs(RH,df=3)'),('RH',f'{v} ~ C(Site) + bs(AT,df=3)')]:
        r=smf.ols(red,d).fit(); ft=full.compare_f_test(r)
        spl.append(dict(Pollutant=v,Term=term,df=int(ft[2]),F=ft[0],p=ft[1],N=len(d),R2=full.rsquared))
    # predictions: site = AM reference averaged over sites (mean of site predictions), other var at median
    out={}
    for term,other in [('AT','RH'),('RH','AT')]:
        g=np.linspace(d[term].quantile(.01),d[term].quantile(.99),80); ys=[]
        for s in S:
            nd=pd.DataFrame({term:g,other:d[other].median(),'Site':s}); ys.append(full.predict(nd).values)
        out[term]=(g.tolist(),np.mean(ys,axis=0).tolist())
    pred[v]=out
SP=pd.DataFrame(spl); SP.to_csv('results/spline.csv',index=False); print(SP.round(5).to_string())
json.dump(pred,open('results/splinepred.json','w')); json.dump(R,open('results/meta.json','w'),indent=1); print(json.dumps(R,indent=1))
# --- hypothesis: period tests in the paper used only the first 13 rows per site
print('first-13-rows hypothesis: KW H (6 morning / 4 afternoon / 3 evening)')
for s in S:
    g=A[A.Site==s].head(13); per=np.array(['m']*6+['a']*4+['e']*3); o=[]
    for v in V:
        try: h,p=stats.kruskal(*[g[v].values[per==q] for q in 'mae']); o.append('%s %.2f'%(v,h))
        except Exception: o.append(v+' NA')
    print(s,' '.join(o),'| AT means',[round(g.AT.values[per==q].mean(),1) for q in 'mae'],'CO means',[round(g.CO.values[per==q].mean(),2) for q in 'mae'])
