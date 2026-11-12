import pandas as pd, numpy as np, json, warnings
warnings.filterwarnings('ignore')
import statsmodels.api as sm, statsmodels.formula.api as smf
A=pd.read_csv('results/clean.csv'); A['grp']=A.Site+'_'+A.day.astype(str); S=['AM','AV','JM','TL']; P=['CO','SO2','VOC','PM25','PM10']
rows=[]; pred={}; site_pred={}
def fit(formula,d):
    return smf.glm(formula,d,family=sm.families.Poisson()).fit(cov_type='cluster',cov_kwds={'groups':d['grp']},maxiter=200)
def wald(m,key):
    idx=[i for i,n in enumerate(m.params.index) if n.startswith(key)]
    R=np.zeros((len(idx),len(m.params)))
    for k,i in enumerate(idx): R[k,i]=1
    w=m.wald_test(R,use_f=False,scalar=True); return float(w.statistic),len(idx),float(w.pvalue)
for v in P:
    d=A.dropna(subset=[v,'AT','RH']).copy()
    m=fit(f'{v} ~ C(Site) + bs(AT,df=3) + bs(RH,df=3)',d)
    for term,key in (('AT','bs(AT'),('RH','bs(RH')):
        c,df,p=wald(m,key); rows.append(dict(Pollutant=v,Term=term,df=df,chi2=c,p=p,N=len(d),Days=d.grp.nunique(),converged=m.converged))
    out={}
    for term,other in (('AT','RH'),('RH','AT')):
        g=np.linspace(d[term].quantile(.01),d[term].quantile(.99),80)
        ys=[m.predict(pd.DataFrame({term:g,other:d[other].median(),'Site':s})).values for s in S]
        out[term]=(g.tolist(),np.mean(ys,axis=0).tolist())
    pred[v]=out
    sp={}
    for s in S:
        ds=d[d.Site==s]
        try:
            ms=fit(f'{v} ~ bs(AT,df=3) + bs(RH,df=3)',ds); o={}
            for term,other in (('AT','RH'),('RH','AT')):
                g=np.linspace(ds[term].quantile(.02),ds[term].quantile(.98),60)
                pr=ms.get_prediction(pd.DataFrame({term:g,other:ds[other].median()})).summary_frame()
                o[term]=(g.tolist(),pr['mean'].tolist(),pr['mean_ci_lower'].tolist(),pr['mean_ci_upper'].tolist())
            sp[s]=dict(n=len(ds),curves=o)
        except Exception as ex: print('site fit failed',v,s,type(ex).__name__,ex); sp[s]=None
    site_pred[v]=sp
R=pd.DataFrame(rows); R.to_csv('results/spline.csv',index=False); print(R.round(4).to_string(index=False))
json.dump(pred,open('results/splinepred.json','w')); json.dump(site_pred,open('results/splinesite.json','w'))
for v in P:
    for t in ('AT','RH'):
        x,y=pred[v][t]; k=[0,13,26,40,53,66,79]; print(v,t,[(round(x[i],1),round(y[i],2)) for i in k],'peak at %.1f'%x[int(np.argmax(y))])
