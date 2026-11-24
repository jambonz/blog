"""Draw the STT and TTS vendor-support dot charts from data.py.

Usage: python chart.py [output_dir]   (default: the bring-your-own-everything post)
"""
import os, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from data import P, stt, tts
out=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'..','..','src','content','blog','bring-your-own-everything-voice-ai')
plt.rcParams['font.family']=['Helvetica Neue','Helvetica','Arial','DejaVu Sans']
PURPLE='#5046b8'; GREY='#8a8a86'; ORANGE='#de5a2b'; EMPTY='#c9c9c4'; SHADE='#f0f0f6'; INK='#1a1a1a'; MUTED='#8a8a86'
def draw(d, title, fn):
    for p in P: assert len(set(d[p]))==len(d[p]), p
    allv=set().union(*d.values())
    n=lambda v: sum(v in d[p] for p in P)
    key=lambda v:(-n(v), v.lower())
    shared=sorted([v for v in allv if v in d['jambonz'] and n(v)>1], key=key)
    only=sorted([v for v in allv if v in d['jambonz'] and n(v)==1], key=key)
    gap=sorted([v for v in allv if v not in d['jambonz']], key=key)
    groups=[(f'Supported by jambonz and others ({len(shared)})',shared),(f'Only jambonz ({len(only)})',only),(f'Not yet in jambonz ({len(gap)})',gap)]
    rows=[]
    for g,vs in groups:
        if vs: rows.append(('H',g)); rows+=[('V',v) for v in vs]
    RH=0.41; top=1.75; H=top+len(rows)*RH+0.25
    W=15.0; x0=1.95; dx=1.28
    fig=plt.figure(figsize=(W,H),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(0,W); ax.set_ylim(H,0); ax.axis('off')
    ax.text(0.22,0.35,title,fontsize=24,fontweight='bold',color=INK,va='center')
    cx=lambda i: x0+2.6+i*dx
    ax.add_patch(plt.Rectangle((cx(0)-0.51,top-0.05),1.02,len(rows)*RH+0.1,color=SHADE,zorder=0))
    for i,p in enumerate(P):
        ax.text(cx(i),top-0.62,p,ha='center',fontsize=17,color=INK,fontweight='bold' if i==0 else 'normal')
        ax.text(cx(i),top-0.36,str(len(d[p])),ha='center',fontsize=14,color=MUTED)
    ax.plot([x0,cx(len(P)-1)+0.8],[top-0.12,top-0.12],color='#bdbdb8',lw=1)
    y=top-0.25
    for kind,label in rows:
        y+=RH
        if kind=='H':
            ax.text(x0,y,label,fontsize=14.5,style='italic',color=MUTED,va='center'); continue
        ax.text(x0,y,label,fontsize=17,color=INK,va='center')
        for i,p in enumerate(P):
            if label in d[p]:
                c=PURPLE if i==0 else (ORANGE if label not in d['jambonz'] else GREY)
                ax.scatter(cx(i),y,s=220,color=c,zorder=3,linewidths=0)
            else:
                ax.scatter(cx(i),y,s=22,color=EMPTY,zorder=3,linewidths=0)
    fig.savefig(fn,dpi=100,facecolor='white'); plt.close(fig)
    print(fn, len(rows))
draw(stt,'Speech-to-text (STT): vendor support by platform',out+'/stt-vendor-matrix.png')
draw(tts,'Text-to-speech (TTS): vendor support by platform',out+'/tts-vendor-matrix.png')
