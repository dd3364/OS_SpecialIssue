import json, csv, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os; S=os.path.join(os.path.dirname(os.path.abspath(__file__)),'')
R=json.load(open(S+'results/results.json'))['main']
HUM,AIF,AIM='#2a78d6','#eb6834','#1baf7a'
INK,INK2,GRID,SURF='#0b0b0b','#52514e','#e4e3df','#ffffff'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':GRID,'axes.labelcolor':INK2,
  'xtick.color':INK2,'ytick.color':INK2,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':SURF,'axes.facecolor':SURF})
def style(ax,grid='y'):
    ax.grid(axis=grid,color=GRID,lw=0.6); ax.set_axisbelow(True)
    ax.spines['left'].set_visible(grid!='y'); ax.tick_params(length=0)

# Fig 1: RQ1 small multiples
meas=[('Criticality','RQ1_crit',(1,3)),('Specificity','RQ1_spec',(1,3)),('Constructiveness','RQ1_constr',(0,2)),('Tone','RQ1_tone',(-1,1)),('Points per report','RQ1_n_points',(0,25))]
fig,axs=plt.subplots(1,5,figsize=(7.2,2.1))
for ax,(lab,k,lim) in zip(axs,meas):
    v=[R[k]['human'],R[k]['ai']]
    base=lim[0] if lim[0]>=0 else 0
    ax.bar([0,1],[x-base for x in v],bottom=base,color=[HUM,AIF],width=0.6)
    for xi,val in enumerate(v): ax.text(xi,val+(lim[1]-lim[0])*0.03 if val>=0 else val-(lim[1]-lim[0])*0.1,f'{val:.1f}' if k=='RQ1_n_points' else f'{val:.2f}',ha='center',fontsize=8.5,color=INK)
    ax.set_ylim(*lim); ax.set_xticks([0,1]); ax.set_xticklabels(['Human','AI']); ax.set_title(lab,fontsize=9,color=INK,loc='left',pad=12)
    if lim[0]<0: ax.axhline(0,color=INK2,lw=0.8)
    style(ax)
fig.tight_layout(w_pad=1.2); fig.savefig(S+'figures/f1_rq1.png',dpi=220); plt.close()

# Fig 2: coverage by issue type, 3 series
cats=[('All issues','all'),('Substantive','substantive'),('Presentation','presentation'),('Emphasized','emph'),('Unasked changes','unasked')]
import numpy as np
x=np.arange(len(cats)); w=0.26
hv=[R[f'RQ2_cov_{c}']['human']*100 for _,c in cats]
fv=[R[f'RQ2_cov_{c}']['ai']*100 for _,c in cats]
mv=[R[f'RQ2_cov_{c}_lenmatch']['ai']*100 for _,c in cats]
fig,ax=plt.subplots(figsize=(7.2,2.9))
for off,vals,col,lab in [(-w,hv,HUM,'Human referee'),(0,fv,AIF,'Full AI report'),(w,mv,AIM,'Length-matched AI report')]:
    b=ax.bar(x+off,vals,w-0.03,color=col,label=lab)
    for xi,v in zip(x+off,vals): ax.text(xi,v+1,f'{int(v+0.5)}',ha='center',fontsize=7.5,color=INK)
ax.set_xticks(x); ax.set_xticklabels([c for c,_ in cats]); ax.set_ylabel('Share of issues raised (%)'); ax.set_ylim(0,52)
ax.legend(frameon=False,ncol=3,loc='upper left',fontsize=8); style(ax)
fig.tight_layout(); fig.savefig(S+'figures/f2_cov.png',dpi=220); plt.close()

# Fig 3: per-paper dot plot
rows=list(csv.DictReader(open(S+'results/per_paper.csv')))
names={'1':'Partisan toxicity','2':'Cost of capital','3':'Forest finance','4':'Shopping data','5':'Aquatic foods','6':'Policing transparency','7':'Social influence','8':'Vaccine norms','9':'Nations','10':'Registered reports'}
fig,ax=plt.subplots(figsize=(7.2,4.0))
for i,r in enumerate(rows):
    y=len(rows)-1-i; h,f,m=[float(r[k])*100 for k in ('fair_cov_human','fair_cov_ai','fair_cov_ai_lenmatch')]
    ax.axhline(y,color=GRID,lw=0.6,zorder=0)
    ax.scatter([h],[y+0.27],s=36,color=HUM,zorder=3,edgecolor=SURF,lw=1.5,marker='o')
    ax.scatter([f],[y],s=36,color=AIF,zorder=3,edgecolor=SURF,lw=1.5,marker='s')
    ax.scatter([m],[y-0.27],s=40,color=AIM,zorder=3,edgecolor=SURF,lw=1.5,marker='D')
ax.set_yticks(range(len(rows))); ax.set_yticklabels([f"{r['num']}. {names[r['num']]}" for r in rows][::-1])
ax.set_xlabel('Share of documented issues raised (%)'); ax.set_xlim(-3,80)
ax.legend(handles=[plt.Line2D([],[],marker=mk,ls='',color=c,ms=7,label=l) for mk,c,l in [('o',HUM,'Average human referee'),('s',AIF,'Full AI report'),('D',AIM,'Length-matched AI report')]],frameon=False,ncol=3,loc='upper center',bbox_to_anchor=(0.4,1.13),fontsize=8)
style(ax,'x'); fig.tight_layout(); fig.savefig(S+'figures/f3_papers.png',dpi=220); plt.close()

# Fig 4: alignment stacked bar
same=R['RQ2_align_ai']['same']*100; loose=R['RQ2_align_ai']['loose']*100
parts=[('Same match',same,'#184f95'),('Related match',loose-same,'#6da7ec'),('No match in the issue record',100-loose,'#cde2fb')]
fig,ax=plt.subplots(figsize=(7.2,1.25)); left=0
for lab,v,c in parts:
    ax.barh(0,v,left=left,color=c,height=0.5,edgecolor=SURF,lw=2)
    ax.text(left+v/2,0,f'{v:.0f}%',ha='center',va='center',fontsize=9,color='white' if c=='#184f95' else INK)
    left+=v
ax.set_xlim(0,100); ax.set_yticks([]); ax.set_xticks([]); [s.set_visible(False) for s in ax.spines.values()]
ax.legend(handles=[Patch(color=c,label=l) for l,_,c in parts],frameon=False,ncol=3,loc='upper center',bbox_to_anchor=(0.5,1.35),fontsize=8)
fig.tight_layout(); fig.savefig(S+'figures/f4_align.png',dpi=220); plt.close()

# Fig 5: complementarity
lab=['Second human referee','Full AI report','Length-matched AI report']
vals=[R['RQ3']['gain_human'],R['RQ3']['gain_ai'],R['RQ3_lenmatch']['gain_ai']]
fig,ax=plt.subplots(figsize=(7.2,1.9))
ax.barh([2,1,0],vals,color=[HUM,AIF,AIM],height=0.55)
for y,v in zip([2,1,0],vals): ax.text(v+0.05,y,f'{v:.2f}',va='center',fontsize=8.5,color=INK)
ax.set_yticks([2,1,0]); ax.set_yticklabels(lab); ax.set_xlabel('New issues added to one referee\'s report (average per pair)'); ax.set_xlim(0,3.3)
style(ax,'x'); fig.tight_layout(); fig.savefig(S+'figures/f5_rq3.png',dpi=220); plt.close()
print('done')
