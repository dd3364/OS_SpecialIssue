import glob, random, statistics as st, json, csv, sys, itertools
import os; S=os.path.dirname(os.path.abspath(__file__))+'/'
papers=[]
for f in sorted(glob.glob(S+'coding/p*.py')):
    g={}; exec(open(f).read(),g); P=g['P']; P['num']=int(f.split('/p')[-1][:2]); papers.append(P)
papers.sort(key=lambda p:p['num'])
mean=lambda xs: sum(xs)/len(xs) if xs else float('nan')
def raised(pts):  # issues a report raises (same)
    return set(i for p in pts for i in p[6])
def raised_rel(pts):
    return set(i for p in pts for i in p[6]+p[7])
def ai_pts(P,k=None):
    a=[(x[0],)+tuple(x[1:8]) for x in P['ai']]
    return a if k is None else a[:k]
def refs(P, drop_returning=False):
    return {r:v for r,v in P['human'].items() if v and not (drop_returning and r in P['returning'])}
def documented_by_others(P, r):
    return set(i for i,d in P['issues'].items() if (not d['by']) or any(b!=r for b in d['by']))
def boot(vals, n=4000, seed=1):
    rnd=random.Random(seed); vals=[v for v in vals if v==v]
    if len(vals)<2: return (float('nan'),float('nan'))
    ms=sorted(mean([rnd.choice(vals) for _ in vals]) for _ in range(n))
    return (ms[int(.025*n)], ms[int(.975*n)-1])
KEYS=['crit','spec','constr','tone']
def rq1(P, dr=False):
    H=refs(P,dr); A=ai_pts(P)
    out={}
    for j,k in enumerate(KEYS,2):
        h=mean([mean([p[j] for p in v]) for v in H.values()])
        out[k]=(mean([p[j] for p in A]), h)
    core={'theory','data','methods','claims'}
    out['core_share']=(mean([p[1] in core for p in A]), mean([mean([p[1] in core for p in v]) for v in H.values()]))
    out['pres_share']=(mean([p[1]=='presentation' for p in A]), mean([mean([p[1]=='presentation' for p in v]) for v in H.values()]))
    out['n_points']=(len(A), mean([len(v) for v in H.values()]))
    return out
def subset(P, kind):
    I=P['issues']
    f={'all':lambda d:True,'substantive':lambda d:d['rev']=='substantive','presentation':lambda d:d['rev']=='presentation',
       'editor':lambda d:'ED' in d['by'],'emph':lambda d:d.get('emph',False),'unasked':lambda d:not d['by']}[kind]
    return set(i for i,d in I.items() if f(d))
def rq2(P, dr=False, kind='all', loose=False, length=False):
    """per referee: fair coverage of referee vs AI on issues documented by others; alignment"""
    H=refs(P,dr); rows=[]
    R=raised_rel if loose else raised
    for r,v in H.items():
        D=documented_by_others(P,r) & subset(P,kind)
        if not D: continue
        A=ai_pts(P, len(v) if length else None)
        rows.append(dict(ref=r, nD=len(D), human=len(R(v)&D)/len(D), ai=len(R(A)&D)/len(D)))
    return rows
def align(pts, loose=False):
    return mean([bool(p[6] or (loose and p[7])) for p in pts])
def rq3(P, dr=False, length=False):
    H=refs(P,dr); out=[]
    for ri,rj in itertools.permutations(H,2):
        Sset=set(i for i,d in P['issues'].items() if ri not in d['by'] and ((not d['by']) or any(b!=rj for b in d['by'])))
        A=ai_pts(P, len(H[rj]) if length else None)
        out.append(dict(ri=ri,rj=rj,nS=len(Sset),g_h=len(raised(H[rj])&Sset),g_ai=len(raised(A)&Sset)))
    return out
def overlap(a,b):
    ra,rb=raised(a),raised(b)
    return (sum(bool(set(p[6])&rb) for p in a)+sum(bool(set(p[6])&ra) for p in b))/(len(a)+len(b))
def summarize(ps, dr=False, label=''):
    res={'label':label,'n_papers':len(ps)}
    r1=[rq1(P,dr) for P in ps]
    for k in KEYS+['core_share','pres_share','n_points']:
        r1v=[x for x in r1 if x['crit'][1]==x['crit'][1]]; a=[x[k][0] for x in r1v]; h=[x[k][1] for x in r1v]; d=[x-y for x,y in zip(a,h)]
        res['RQ1_'+k]=dict(ai=mean(a), human=mean(h), diff=mean(d), ci=boot(d))
    res['RQ2_align_ai']=dict(same=mean([align(ai_pts(P)) for P in ps]), loose=mean([align(ai_pts(P),True) for P in ps]))
    res['RQ2_align_human']=dict(same=mean([mean([align(v) for v in refs(P,dr).values()]) for P in ps]))
    for kind in ['all','substantive','presentation','editor','emph','unasked']:
        for loose in (False,True):
            for length in (False,True):
                per=[]
                for P in ps:
                    rows=rq2(P,dr,kind,loose,length)
                    if rows: per.append((mean([x['human'] for x in rows]), mean([x['ai'] for x in rows]), sum(x['nD'] for x in rows)))
                if not per: continue
                d=[a-h for h,a,_ in per]
                res[f'RQ2_cov_{kind}{"_loose" if loose else ""}{"_lenmatch" if length else ""}']=dict(papers=len(per), human=mean([h for h,_,_ in per]), ai=mean([a for _,a,_ in per]), diff=mean(d), ci=boot(d))
    for length in (False,True):
        pp=[];tot_h=tot_ai=nS=0; npairs=0; ai_ge=0
        for P in ps:
            rows=rq3(P,dr,length)
            if not rows: continue
            pp.append(mean([x['g_ai']-x['g_h'] for x in rows]))
            for x in rows:
                tot_h+=x['g_h']; tot_ai+=x['g_ai']; nS+=x['nS']; npairs+=1; ai_ge+= x['g_ai']>=x['g_h']
        res['RQ3'+('_lenmatch' if length else '')]=dict(papers=len(pp),pairs=npairs,gain_human=tot_h/npairs,gain_ai=tot_ai/npairs,share_ai_ge=ai_ge/npairs,paper_diff=mean(pp),ci=boot(pp))
    hh=[];ah=[]
    for P in ps:
        H=refs(P,dr)
        if len(H)>=2: hh.append(mean([overlap(H[a],H[b]) for a,b in itertools.combinations(H,2)]))
        if H: ah.append(mean([overlap(ai_pts(P),v) for v in H.values()]))
    res['RQ4']=dict(hh=mean(hh), hh_papers=len(hh), ai_h=mean(ah))
    fc=[P['factcheck'] for P in ps]
    res['RQ5_factcheck']=dict(checked=sum(f['checked'] for f in fc), errors=sum(f['errors'] for f in fc))
    return res
def fmt(x): 
    return round(x,3) if isinstance(x,float) else ([fmt(y) for y in x] if isinstance(x,(list,tuple)) else ({k:fmt(v) for k,v in x.items()} if isinstance(x,dict) else x))
if __name__=='__main__':
    allp=papers
    out={'main':summarize(allp,label='all 10'),
         'no_p5':summarize([p for p in allp if not p.get('version_problem')],label='excl paper 5'),
         'no_returning':summarize(allp,dr=True,label='excl returning referees'),
         'not_transferred':summarize([p for p in allp if not p['transferred'] and not p.get('version_problem')],label='non-transferred, excl p5')}
    json.dump(fmt(out),open(S+'results/results.json','w'),indent=1)
    # per-paper table
    with open(S+'results/per_paper.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['num','id','field','study','transferred','returning','n_refs_with_points','human_points','ai_points','n_issues','n_substantive','n_unasked','ai_same_matches','ai_align_same','ai_align_loose','fair_cov_human','fair_cov_ai','fair_cov_ai_lenmatch','fc_checked','fc_errors'])
        for P in allp:
            H=refs(P); rows=rq2(P); rl=rq2(P,length=True)
            w.writerow([P['num'],P['id'],P['field'],P['study'],P['transferred'],'|'.join(P['returning']),len(H),sum(len(v) for v in H.values()),len(P['ai']),len(P['issues']),
                len(subset(P,'substantive')),len(subset(P,'unasked')),len(raised(ai_pts(P))),round(align(ai_pts(P)),3),round(align(ai_pts(P),True),3),
                round(mean([x['human'] for x in rows]),3) if rows else '',round(mean([x['ai'] for x in rows]),3) if rows else '',round(mean([x['ai'] for x in rl]),3) if rl else '',
                P['factcheck']['checked'],P['factcheck']['errors']])
    with open(S+'results/per_report.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(['num','ref','returning','n_points','crit','spec','constr','tone','issues_raised','fair_nD','fair_cov_ref','fair_cov_ai','fair_cov_ai_lenmatch'])
        for P in allp:
            rr={x['ref']:x for x in rq2(P)}; rl={x['ref']:x for x in rq2(P,length=True)}
            for r,v in list(refs(P).items())+[('AI',ai_pts(P))]:
                w.writerow([P['num'],r,r in P['returning'],len(v)]+[round(mean([p[j] for p in v]),2) for j in range(2,6)]+[len(raised(v)),
                    rr.get(r,{}).get('nD',''),round(rr[r]['human'],3) if r in rr else '',round(rr[r]['ai'],3) if r in rr else '',round(rl[r]['ai'],3) if r in rl else ''])
    print(json.dumps(fmt(out['main']),indent=0)[:6000])
