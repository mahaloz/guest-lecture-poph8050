"""Frozen-snapshot observational HPAI investigation. Run from any directory."""
from pathlib import Path
import csv, json, hashlib, platform
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import geopandas as gpd
from matplotlib.colors import Normalize

ROOT=Path(__file__).resolve().parents[1]
SEASONS=['Summer','Autumn','Winter','Spring']
COLORS=['#159895','#bb5a24','#5667a5','#a94376']
CUTOFF=pd.Timestamp('2026-11-01') # retrieval month excluded from inference

def save_json(name,value):
    (ROOT/'results'/name).write_text(json.dumps(value,indent=2,default=lambda x: x.item() if hasattr(x,'item') else str(x),allow_nan=False)+'\n')

def verify_sources():
    manifests=json.loads((ROOT/'sources/download_manifest.json').read_text())
    manifests.append(json.loads((ROOT/'sources/poultry_manifest.json').read_text()))
    for m in manifests:
        assert hashlib.sha256((ROOT/m['path']).read_bytes()).hexdigest()==m['sha256'],m['path']
    return manifests

def season(month):
    return {12:'Winter',1:'Winter',2:'Winter',3:'Spring',4:'Spring',5:'Spring',6:'Summer',7:'Summer',8:'Summer',9:'Autumn',10:'Autumn',11:'Autumn'}[month]

def clean():
    verify_sources()
    raw=ROOT/'data/raw/A Table by Confirmation Date.csv'
    lines=list(csv.reader(raw.open(encoding='utf-16',newline=''),delimiter='\t'))
    assert lines[1][:5]==['Confirmed Diagnosis','State','County Name','Special ID','Production']
    records=[]; populated=[];previous=[None]*4
    for line in lines[2:]:
        if not any(line):continue
        assert len(line)==len(lines[1])
        # Tableau crosstab omits repeated row headings. Fill only heading fields.
        for j in range(4):
            if line[j].strip(): previous[j]=line[j].strip()
        date,state,county,pid=previous
        values=[(j,x.strip()) for j,x in enumerate(line[5:],5) if x.strip()]
        assert len(values)==1,('Expected one birds-affected cell per event',date,pid,values)
        j,value=values[0]; populated.append(j)
        birds=float(value.replace(',',''))
        assert birds>=0 and birds.is_integer()
        records.append([date,state,county,pid,line[4].strip(),int(birds),lines[1][j]])
    p=pd.DataFrame(records,columns=['date','state','county','premises_label','production','birds_affected','control_area_release_heading'])
    p['date']=pd.to_datetime(p.date,format='%d-%b-%Y',errors='raise')
    assert p[['state','county','premises_label','production']].notna().all().all()
    assert (p.date>=pd.Timestamp('2022-01-01')).all() and (p.date<=pd.Timestamp('2026-11-06')).all()
    p['group']=np.select([p.production.str.startswith('Commercial')|p.production.eq('Primary Broiler Breeder Pedigree Farm'),p.production.eq('WOAH Poultry'),p.production.eq('WOAH Non-Poultry')],['Commercial','Backyard poultry proxy','WOAH Non-Poultry'],default='Market / sales')
    assert set(p.loc[p.group.eq('Market / sales'),'production'])<= {'Live Bird Market','Live Bird Sales  (non-slaughter)'}
    p['year']=p.date.dt.year;p['month']=p.date.dt.month;p['season']=p.month.map(season)
    p['period']=p.date.dt.to_period('M').astype(str)
    p['is_poultry']=~p.production.eq('WOAH Non-Poultry')
    states=gpd.read_file(ROOT/'data/raw/states.zip')
    assert set(p.state)<=set(states.NAME),set(p.state)-set(states.NAME)
    w=pd.read_csv(ROOT/'data/raw/wild_birds.csv')
    for c in w.select_dtypes('object'):w[c]=w[c].str.strip()
    for old,new in [('Collection Date','collection_date'),('Date Detected','date')]:
        w[new]=pd.to_datetime(w[old],format='%m/%d/%Y',errors='coerce')
    assert w.date.notna().all()
    w['method']=w['Sampling Method'].str.lower();w['classification']=w['WOAH Classification'].str.lower()
    w['period']=w.date.dt.to_period('M').astype(str)
    w['delay_days']=(w.date-w.collection_date).dt.days
    # No unique specimen identifier: preserve identical signatures, which may be separate birds.
    validation={'poultry_rows':len(p),'wild_rows':len(w),'poultry_date_min':str(p.date.min().date()),'poultry_date_max':str(p.date.max().date()),'wild_date_min':str(w.date.min().date()),'wild_date_max':str(w.date.max().date()),'poultry_exact_signatures_repeated':int(p.duplicated(['date','state','county','production','birds_affected']).sum()),'poultry_repeated_event_labels':int(p.duplicated(['date','state','county','premises_label']).sum()),'poultry_repeated_premises_labels_across_dates':int(p.duplicated(['state','county','premises_label']).sum()),'wild_exact_signatures_repeated':int(w.iloc[:,:9].duplicated().sum()),'wild_missing_collection_dates':int(w.collection_date.isna().sum()),'wild_negative_delay':int(w.delay_days.lt(0).sum()),'wild_delay_quantiles_days':w.delay_days.quantile([.5,.9,.95,.99]).to_dict(),'wild_delay_over_30_days':int(w.delay_days.gt(30).sum()),'wild_missing_by_column':w.iloc[:,:9].isna().sum().to_dict(),'wild_invalid_collection_tokens':w.loc[w.collection_date.isna(),'Collection Date'].value_counts().to_dict(),'groups':p.group.value_counts().to_dict(),'birds_total':int(p.birds_affected.sum()),'birds_poultry':int(p.loc[p.is_poultry,'birds_affected'].sum()),'states_all':int(p.state.nunique()),'states_poultry':int(p.loc[p.is_poultry,'state'].nunique())}
    p.to_csv(ROOT/'data/processed/poultry.csv',index=False);w.to_csv(ROOT/'data/processed/wild_birds.csv',index=False)
    save_json('validation.json',validation)
    return p,w,validation

def monthly(p,w):
    idx=pd.date_range('2022-02-01',CUTOFF,freq='MS')
    m=pd.DataFrame(index=idx);m.index.name='date'
    for key,frame in [('all_domestic',p),('poultry',p[p.is_poultry])]:
        m[key]=frame.set_index('date').resample('MS').size().reindex(idx,fill_value=0)
    m['birds']=p[p.is_poultry].set_index('date').birds_affected.resample('MS').sum().reindex(idx,fill_value=0)
    for group in p.group.unique():
        m[group]=p[p.group.eq(group)].set_index('date').resample('MS').size().reindex(idx,fill_value=0)
    m['wild']=w[w.classification.eq('wild bird')].set_index('date').resample('MS').size().reindex(idx,fill_value=0)
    valid=w[w.classification.eq('wild bird')&w.collection_date.notna()&w.delay_days.ge(0)]
    m['wild_collection']=valid.set_index('collection_date').resample('MS').size().reindex(idx,fill_value=0)
    for meth in ['hunter harvest','morbidity/mortality','live bird']:
        m[meth]=w[w.classification.eq('wild bird')&w.method.eq(meth)].set_index('date').resample('MS').size().reindex(idx,fill_value=0)
    m['year']=m.index.year;m['month']=m.index.month;m['season']=pd.Categorical([season(i) for i in m.month],categories=SEASONS)
    m['days']=m.index.days_in_month
    m.to_csv(ROOT/'results/monthly.csv')
    return m

def poisson(m,response):
    return smf.glm(f'{response} ~ C(season, Treatment(reference="Summer")) + C(year)',data=m,family=sm.families.Poisson(),offset=np.log(m.days)).fit(cov_type='HAC',cov_kwds={'maxlags':3})

def contrasts(fit):
    rows=[]
    for s in ['Spring','Autumn','Winter']:
        key=f'C(season, Treatment(reference="Summer"))[T.{s}]';b=fit.params[key];se=fit.bse[key]
        rows.append({'season':s,'ratio':float(np.exp(b)),'ci_low':float(np.exp(b-1.96*se)),'ci_high':float(np.exp(b+1.96*se)),'p_two_sided':float(fit.pvalues[key])})
    return rows

def contingency(a,b,strata=None,nperm=4999):
    a=pd.Categorical(a);b=pd.Categorical(b);ac=a.codes.astype(np.int64);bc=b.codes.astype(np.int64)
    assert (ac>=0).all() and (bc>=0).all()
    shape=(len(a.categories),len(b.categories))
    def table(x):return np.bincount(ac*shape[1]+x,minlength=shape[0]*shape[1]).reshape(shape)
    obs=table(bc);expected=np.outer(obs.sum(1),obs.sum(0))/obs.sum()
    def stat(t):return float(((t-expected)**2/expected).sum())
    observed=stat(obs);rng=np.random.default_rng(8050);exceed=0
    groups=[np.arange(len(ac))] if strata is None else [np.flatnonzero(np.asarray(strata)==x) for x in np.unique(strata)]
    for _ in range(nperm):
        shuffled=bc.copy()
        for ix in groups:shuffled[ix]=rng.permutation(shuffled[ix])
        exceed+=stat(table(shuffled))>=observed-1e-10
    return {'chi2':observed,'cramers_v':float(np.sqrt(observed/(len(ac)*min(shape[0]-1,shape[1]-1)))),'permutation_p':(exceed+1)/(nperm+1),'n':len(ac),'minimum_expected':float(expected.min()),'cells_expected_under_5':int((expected<5).sum()),'permutations':nperm},pd.DataFrame(obs,index=a.categories,columns=b.categories)

def hypotheses(p,w,m):
    # Exclude first observed poultry month and retrieval month from all main tests.
    complete=m.loc['2022-03-01':'2026-10-01'].copy()
    fit=poisson(complete,'poultry');h1=contrasts(fit)
    (ROOT/'results/poisson_summary.txt').write_text(fit.summary().as_text())
    dispersion=float(np.sum(fit.resid_pearson**2)/fit.df_resid)
    nbfit=smf.negativebinomial('poultry ~ C(season, Treatment(reference="Summer")) + C(year)',data=complete,offset=np.log(complete.days)).fit(disp=False,cov_type='HAC',cov_kwds={'maxlags':3})
    nbcontrast=contrasts(nbfit)
    sens=contrasts(poisson(complete[complete.year.between(2023,2025)],'poultry'))
    broad=contrasts(poisson(complete,'all_domestic'))
    rows=p[p.date.ge('2022-03-01')&p.date.lt(CUTOFF)&p.is_poultry].copy()
    typed=rows[rows.group.isin(['Commercial','Backyard poultry proxy'])]
    h2,t2=contingency(typed.season,typed.group,typed.year);t2.to_csv(ROOT/'results/h2_season_type.csv')
    typedfull=typed[typed.year.between(2023,2025)]
    pd.crosstab([typed.year,typed.group],typed.season).to_csv(ROOT/'results/h2_by_year.csv')
    h2full,_=contingency(typedfull.season,typedfull.group,typedfull.year)
    broadtyped=p[p.date.ge('2022-03-01')&p.date.lt(CUTOFF)&~p.group.eq('Market / sales')].copy()
    broadtyped['type']=np.where(broadtyped.group.eq('Commercial'),'Commercial','Backyard poultry + non-poultry')
    h2b,_=contingency(broadtyped.season,broadtyped.type,broadtyped.year)
    h3,t3=contingency(rows.state,rows.year);t3.to_csv(ROOT/'results/h3_state_year.csv')
    sub=rows[rows.year.between(2023,2025)];h3s,_=contingency(sub.state,sub.year)
    h4data=complete.copy();h4data['lp']=np.log1p(h4data.poultry);h4data['lw']=np.log1p(h4data.wild)
    h4data['wild_lag1']=h4data.lw.shift(1)
    model=smf.ols('lp ~ wild_lag1 + C(month) + C(year)',data=h4data).fit(cov_type='HAC',cov_kwds={'maxlags':3})
    def result(f,key):
        ci=f.conf_int().loc[key];return {'beta':float(f.params[key]),'ci_low':float(ci.iloc[0]),'ci_high':float(ci.iloc[1]),'p':float(f.pvalues[key]),'n_months':int(f.nobs)}
    h4=result(model,'wild_lag1')
    diff=pd.DataFrame({'dp':h4data.lp.diff(),'dw_lag1':h4data.lw.diff().shift(1)})
    dfit=smf.ols('dp ~ dw_lag1',data=diff).fit(cov_type='HAC',cov_kwds={'maxlags':3})
    h4['first_difference']=result(dfit,'dw_lag1')
    residualp=smf.ols('lp ~ C(month)+C(year)',data=h4data).fit().resid
    residualw=smf.ols('lw ~ C(month)+C(year)',data=h4data).fit().resid
    lagcorr=[{'lag_months':lag,'raw_r':float(h4data.lp.corr(h4data.lw.shift(lag))),'adjusted_r':float(residualp.corr(residualw.shift(lag)))} for lag in range(-3,4)]
    # Date-of-collection sensitivity uses only observed specimens, not a claim of complete collection cohorts.
    h4data['wc_lag1']=np.log1p(h4data.wild_collection).shift(1)
    cf=smf.ols('lp ~ wc_lag1 + C(month)+C(year)',data=h4data).fit(cov_type='HAC',cov_kwds={'maxlags':3})
    h4['collection_date_sensitivity']=result(cf,'wc_lag1')
    (ROOT/'results/wild_lag_summary.txt').write_text(model.summary().as_text())
    # Two-sided tests are conservative for the prespecified positive H1 contrasts.
    pvals=[h1[0]['p_two_sided'],h1[1]['p_two_sided'],h2['permutation_p'],h3['permutation_p']]
    adjusted=multipletests(pvals,method='holm')[1]
    out={'H1':h1,'H1_dispersion':dispersion,'H1_negative_binomial':nbcontrast,'H1_nb_alpha':float(nbfit.params['alpha']),'H1_full_years':sens,'H1_including_nonpoultry':broad,'H2':h2,'H2_full_years':h2full,'H2_including_nonpoultry':h2b,'H3':h3,'H3_full_years':h3s,'H4_exploratory':h4,'lag_correlations':lagcorr,'holm_p':dict(zip(['H1_spring','H1_autumn','H2','H3'],adjusted)),'inferential_months':len(complete),'inferential_start':str(complete.index.min().date()),'inferential_end':str(complete.index.max().date())}
    save_json('hypotheses.json',out)
    annual=p.groupby(['year','group']).agg(events=('date','size'),birds=('birds_affected','sum'));annual.to_csv(ROOT/'results/annual_by_group.csv')
    seasonal=complete.groupby(['year','season'],observed=True).agg(events=('poultry','sum'),days=('days','sum'));seasonal['detections_per_day']=seasonal.events/seasonal.days;seasonal.to_csv(ROOT/'results/season_by_year.csv')
    states=p[p.is_poultry].groupby('state').agg(events=('date','size'),birds=('birds_affected','sum')).sort_values('events',ascending=False);states.to_csv(ROOT/'results/state_totals.csv')
    prod=p.groupby('production').agg(events=('date','size'),birds=('birds_affected','sum')).sort_values('birds',ascending=False);prod.to_csv(ROOT/'results/production_totals.csv')
    sizes=p[p.is_poultry].birds_affected.sort_values(ascending=False)
    save_json('descriptive.json',{'annual_poultry_events':p[p.is_poultry].groupby('year').size().to_dict(),'annual_all_events':p.groupby('year').size().to_dict(),'annual_poultry_birds':p[p.is_poultry].groupby('year').birds_affected.sum().to_dict(),'top10_events_bird_share':float(sizes.head(10).sum()/sizes.sum()),'top1pct_events_bird_share':float(sizes.head(int(np.ceil(len(sizes)*.01))).sum()/sizes.sum()),'top5_states_by_events':states.head().reset_index().to_dict('records'),'top5_states_by_birds':states.sort_values('birds',ascending=False).head().reset_index().to_dict('records'),'median_birds_by_group':p.groupby('group').birds_affected.median().to_dict()})
    return out

def figure_save(fig,name):
    fig.savefig(ROOT/'figures'/f'{name}.png',dpi=300,bbox_inches='tight')
    fig.savefig(ROOT/'figures'/f'{name}.svg',bbox_inches='tight')
    plt.close(fig)

def figures(p,w,m,h):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','svg.fonttype':'none'})
    fig,axs=plt.subplots(2,1,figsize=(11,7),sharex=True,layout='constrained')
    groups=['Commercial','Backyard poultry proxy','Market / sales','WOAH Non-Poultry']
    axs[0].stackplot(m.index,*[m[g] for g in groups],labels=groups,colors=COLORS,alpha=.9)
    axs[0].set_ylabel('Reported flock detection records');axs[0].legend(loc='upper left',fontsize=8,ncol=2)
    axs[1].bar(m.index,m.birds/1e6,width=24,color=COLORS[0]);axs[1].set_ylabel('Reported affected birds\n(poultry only, millions)')
    for ax in axs:
        ax.axvspan(CUTOFF,pd.Timestamp('2026-12-01'),color='grey',alpha=.2)
        ax.grid(axis='y',alpha=.2);ax.set_xlim(pd.Timestamp('2022-02-01'),pd.Timestamp('2026-12-01'))
    axs[1].xaxis.set_major_locator(mdates.MonthLocator(interval=6));axs[1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    axs[0].set_title('1  |  Detection events and affected birds measure different burdens',loc='left')
    axs[1].set_xlabel('Confirmation month • grey: incomplete retrieval month (6 November 2026)')
    figure_save(fig,'01_timeline')
    comp=m.loc['2022-03-01':'2026-10-01'];mat=comp.pivot_table(index='year',columns='month',values='poultry').reindex(columns=range(1,13))
    fig,ax=plt.subplots(figsize=(11,4),layout='constrained');im=ax.imshow(np.ma.masked_invalid(mat.values),cmap='YlOrRd',aspect='auto')
    ax.set_xticks(range(12),['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']);ax.set_yticks(range(len(mat)),mat.index)
    for i in range(len(mat)):
        for j in range(12):
            if pd.notna(mat.iloc[i,j]):ax.text(j,i,str(int(mat.iloc[i,j])),ha='center',va='center',color='white' if mat.iloc[i,j]>mat.max().max()*.6 else '#222')
    fig.colorbar(im,ax=ax,label='Poultry flock detection records');ax.set_title('2  |  Seasonality varies across years; blank cells are excluded months',loc='left')
    figure_save(fig,'02_month_year_heatmap')
    fig,axs=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    for k,row in enumerate(h['H1']):
        axs[0].errorbar(row['ratio'],k,xerr=[[row['ratio']-row['ci_low']],[row['ci_high']-row['ratio']]],fmt='o',color=COLORS[k],capsize=4)
    axs[0].set_yticks(range(3),[r['season']+' / summer' for r in h['H1']]);axs[0].axvline(1,color='grey',linestyle='--');axs[0].set_xscale('log');axs[0].set_xlabel('Adjusted detection-count ratio (95% HAC CI)');axs[0].set_title('3a  |  Year-adjusted seasonal contrasts',loc='left')
    t=pd.read_csv(ROOT/'results/h2_season_type.csv',index_col=0).reindex(['Winter','Spring','Summer','Autumn']);shares=t/t.sum()
    shares.plot.bar(ax=axs[1],color={'Commercial':COLORS[0],'Backyard poultry proxy':COLORS[1]},rot=0);axs[1].set_ylabel('Fraction of records within production group');axs[1].set_xlabel('');axs[1].legend(fontsize=8);axs[1].set_title('3b  |  Production-group seasonal shares',loc='left')
    figure_save(fig,'03_seasonal_tests')
    geo=gpd.read_file(ROOT/'data/raw/states.zip');assert 'NAME' in geo.columns
    totals=p[p.is_poultry].groupby('state').agg(events=('date','size'),birds=('birds_affected','sum'))
    geo=geo.merge(totals,left_on='NAME',right_index=True,how='left');geo[['events','birds']]=geo[['events','birds']].fillna(0)
    excluded=geo[~geo.STUSPS.isin(['AK','HI','PR'])].copy().to_crs(5070)
    fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
    for ax,col,title in zip(axs,['events','birds'],['Poultry flock detection records','Affected poultry birds (millions)']):
        excluded.assign(value=excluded[col]/(1e6 if col=='birds' else 1)).plot(column='value',cmap='YlOrRd',ax=ax,legend=True,edgecolor='#777',linewidth=.35,legend_kwds={'shrink':.6})
        for ab,pos in [('AK',[.01,.0,.2,.24]),('HI',[.22,.0,.15,.20]),('PR',[.40,.0,.15,.20])]:
            inset=ax.inset_axes(pos);g=geo[geo.STUSPS.eq(ab)].to_crs(3338 if ab=='AK' else 4326)
            if len(g):g.assign(value=g[col]/(1e6 if col=='birds' else 1)).plot(column='value',ax=inset,cmap='YlOrRd',vmin=0,vmax=float((excluded[col]/(1e6 if col=='birds' else 1)).max()),edgecolor='#777',linewidth=.4)
            inset.set_title(ab,fontsize=8);inset.set_axis_off()
        ax.set_title(title,fontsize=11);ax.set_axis_off()
    fig.suptitle('4  |  Geographic counts reflect poultry distribution and surveillance, as well as exposure',fontweight='bold',fontsize=11)
    figure_save(fig,'04_geography')
    fig,axs=plt.subplots(2,1,figsize=(11,7),layout='constrained')
    for key,color in [('poultry',COLORS[0]),('wild',COLORS[1])]:
        v=np.log1p(comp[key]);axs[0].plot(comp.index,(v-v.mean())/v.std(),label=key+' (standardized log count)',color=color)
    axs[0].legend(fontsize=9);axs[0].set_ylabel('Standard deviations');axs[0].set_title('5a  |  Wild and poultry detections share broad temporal variation',loc='left');axs[0].grid(alpha=.2)
    lag=pd.DataFrame(h['lag_correlations']);axs[1].plot(lag.lag_months,lag.raw_r,'o-',label='Raw log counts',color=COLORS[1]);axs[1].plot(lag.lag_months,lag.adjusted_r,'o-',label='After month and year adjustment',color=COLORS[0]);axs[1].axhline(0,color='grey',lw=.7)
    axs[1].set_xticks(range(-3,4));axs[1].set_ylim(-1,1);axs[1].set_ylabel('Pearson correlation');axs[1].set_xlabel('Lag (months): positive = wild detections precede poultry');axs[1].legend(fontsize=9);axs[1].set_title('5b  |  Lag correlations are exploratory; no prediction validation',loc='left')
    figure_save(fig,'05_wild_poultry_lags')
    fig,axs=plt.subplots(1,2,figsize=(11,4.5),layout='constrained')
    prod=p[p.is_poultry].groupby('production').agg(events=('date','size'),birds=('birds_affected','sum')).sort_values('birds',ascending=False).head(7)
    y=np.arange(len(prod));labels=[x.replace('Commercial ','').replace('Production','').strip() for x in prod.index]
    axs[0].barh(y-.17,prod.events/prod.events.sum(),height=.32,color=COLORS[1],label='Share of top-seven events');axs[0].barh(y+.17,prod.birds/prod.birds.sum(),height=.32,color=COLORS[0],label='Share of top-seven birds');axs[0].set_yticks(y,labels,fontsize=8);axs[0].invert_yaxis();axs[0].legend(fontsize=7);axs[0].set_xlabel('Share within seven largest bird-count categories');axs[0].set_title('6a  |  Production mix changes the burden metric',loc='left')
    vals=np.sort(p[p.is_poultry].birds_affected.to_numpy());axs[1].plot(np.arange(len(vals)+1)/len(vals),np.r_[0,np.cumsum(vals)/vals.sum()],color=COLORS[0]);axs[1].plot([0,1],[0,1],color='grey',ls='--');axs[1].set_xlabel('Cumulative fraction of detection events\n(ordered by affected flock size)');axs[1].set_ylabel('Cumulative fraction of affected birds');axs[1].set_title('6b  |  Bird burden is concentrated in large flocks',loc='left')
    figure_save(fig,'06_burden_concentration')
    fig,axs=plt.subplots(2,1,figsize=(11,6.5),layout='constrained')
    meth=['hunter harvest','morbidity/mortality','live bird'];axs[0].stackplot(m.index,*[m[x] for x in meth],labels=meth,colors=COLORS[:3]);axs[0].legend(fontsize=8,loc='upper left');axs[0].set_ylabel('Wild-bird detection rows');axs[0].set_title('7  |  Surveillance method and confirmation delays complicate lead/lag inference',loc='left')
    valid=w[w.collection_date.notna()&w.delay_days.ge(0)].copy();valid['year']=valid.date.dt.year
    years=sorted(valid.year.unique());axs[1].boxplot([valid[valid.year.eq(y)].delay_days for y in years],tick_labels=years,showfliers=False);axs[1].set_ylabel('Collection-to-detection delay (days)');axs[1].set_xlabel('Confirmation year • boxes: IQR, whiskers: 1.5 × IQR; outliers hidden')
    figure_save(fig,'07_surveillance')
    table=pd.read_csv(ROOT/'results/h3_state_year.csv',index_col=0)
    top=table.sum(axis=1).nlargest(12).index
    shares=table.loc[top].divide(table.sum(axis=0),axis=1)*100
    fig,ax=plt.subplots(figsize=(8,6),layout='constrained')
    im=ax.imshow(shares.values,cmap='YlOrRd',aspect='auto')
    ax.set_xticks(range(len(shares.columns)),shares.columns);ax.set_yticks(range(len(top)),top)
    for i in range(len(top)):
        for j in range(len(shares.columns)):
            val=shares.iloc[i,j];ax.text(j,i,f'{val:.1f}',ha='center',va='center',color='white' if val>shares.max().max()*.6 else '#222')
    fig.colorbar(im,ax=ax,label='Percentage of year’s recorded poultry events')
    ax.set_xlabel('2022 starts March; 2026 ends October. Top 12 states overall shown.')
    ax.set_title('8  |  The geographic composition of detections changes over time',loc='left')
    figure_save(fig,'08_state_shares')

def main():
    p,w,v=clean();m=monthly(p,w);h=hypotheses(p,w,m);figures(p,w,m,h)
    save_json('execution.json',{'executed_at':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'input_manifest_sha256':hashlib.sha256((ROOT/'sources/poultry_manifest.json').read_bytes()).hexdigest(),'seed':8050,'analysis_cutoff_exclusive':str(CUTOFF.date()),'status':'success','figures_png':len(list((ROOT/'figures').glob('*.png'))),'poultry_rows':len(p),'wild_rows':len(w)})
    print(json.dumps({'validation':v,'hypotheses':h},indent=2))
    return p,w,m,h
if __name__=='__main__':main()
