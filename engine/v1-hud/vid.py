import numpy as np, cv2, subprocess, sys, math
from PIL import Image, ImageDraw, ImageFont
S=2; W1,H1=1080,1920; W,H=W1*S,H1*S
# ================= CONFIG (edit per post) =================
PHOTO='leo-000.png'; MASK='leo_mask.png'          # outputs of the cut-out step
PHOTO_CROP=(544,1800,255,950)                      # y0,y1,x0,x1 athlete bbox in the source photo
LOGO='/mnt/user-data/uploads/1000123820.png'
T_FIRST,T_LAST='LEONOR ','GONÇALVES'
T_WHEN='HOJE'; T_WHEN_SUB='DIA DE COMPETIÇÃO'
T_EVENT='WKF YOUTH LEAGUE'; T_LOC='GUADALAJARA 2026'; T_CAT='JUNIOR -53 KG'; T_DISC='KUMITE'
T_CHEER="LET'S GO!"; T_HASH='#TEAMSHOMEN'
T_L1,T_L2,T_L3='SHM // MATCH DAY','REF. YL-GDL-26 / KUMITE','LIVE — TEAM SHOMEN'
T_DESC='ATLETA // TEAM SHOMEN'; T_STANDBY='ON TATAMI // GUADALAJARA MX'; T_FOOT='SHOMEN © 2026'
COORD=(20.6597,-103.3496)
OUT_PREFIX='seg'
# --- FX: OFF by default. Turn on ONLY when Pedro asks (spec §8.4). Never touch text or logo. ---
FX_VHS=False     # glitch bursts + chroma bleed + scanlines + streak grain + tracking band + head-switch noise
FX_RAIN=False    # matrix-style code rain behind the athlete (palette blue, never green)
# ================= FONTS =================
import os
TOMORROW_DIR='/home/claude/fonts'                  # Tomorrow-<Weight>.ttf, see shomen-glitch-post.md §3.2
FD='/mnt/skills/examples/canvas-design/canvas-fonts/'
_warned=set()
def T(weight,sz,s=None):
    """Tomorrow by weight name (Light, Regular, Medium, SemiBold, Bold, ExtraBold, Black); Work Sans fallback."""
    assert weight not in ('Thin','ExtraLight'), 'weight floor is Light (300) — see shomen-glitch-post.md §3.2'
    s=S if s is None else s
    p=f'{TOMORROW_DIR}/Tomorrow-{weight}.ttf'
    if not os.path.exists(p):
        if weight not in _warned: print('FALLBACK Work Sans for',weight,file=sys.stderr); _warned.add(weight)
        p=FD+('WorkSans-Bold.ttf' if weight in('SemiBold','Bold','ExtraBold','Black') else 'WorkSans-Regular.ttf')
    return ImageFont.truetype(p,int(sz*s))
def F(n,sz,s=S): return ImageFont.truetype(FD+n+'.ttf',int(sz*s))
M=lambda s:F('GeistMono-Regular',s); MB=lambda s:F('GeistMono-Bold',s)   # numeric readouts only
def fit(weight,text,start,maxw,tr=0):
    """largest size <= start whose tracked width fits maxw (1x px)"""
    sz=start
    while sz>10:
        f=T(weight,sz); w=sum(f.getlength(c)+tr*S for c in text)-tr*S
        if w<=P(maxw): return f,sz
        sz-=1
    return T(weight,sz),sz
RED=(255,42,80); BLUE=(84,200,255); WHITE=(245,246,248); GREY=(150,156,168); DIM=(70,76,90); BG=(9,10,14); PANEL=(14,16,22)
P=lambda v:int(round(v*S)); k60=1/math.tan(math.radians(60))
def sm(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
def ease(t,a,b):
    x=min(1,max(0,(t-a)/(b-a))); return 1-(1-x)**3
FPS=30; DUR=20; NF=FPS*DUR

class Ctx:
    def __init__(s): s.img=Image.new('RGBA',(W,H),(0,0,0,0)); s.d=ImageDraw.Draw(s.img,'RGBA')
    def text(s,xy,t,font,fill,tr=0,anchor='l'):
        x,y=xy; tr=tr*S; wt=sum(font.getlength(c)+tr for c in t)-tr
        if anchor=='r': x-=wt
        for c in t: s.d.text((x,y),c,font=font,fill=fill); x+=font.getlength(c)+tr
    def ruler(s,x,y,n,step=8,h1=6,h2=12,col=(255,255,255,90)):
        for i in range(n):
            h=h2 if i%5==0 else h1; s.d.line([(P(x+i*step),P(y)),(P(x+i*step),P(y+h))],fill=col,width=S)
    def bracket(s,x,y,sz,corner,col,w=3):
        x,y,sz=P(x),P(y),P(sz); w=int(w*S); sx=1 if 'l' in corner else -1; sy=1 if 't' in corner else -1
        s.d.line([(x,y),(x+sx*sz,y)],fill=col,width=w); s.d.line([(x,y),(x,y+sy*sz)],fill=col,width=w)
    def slash(s,xt,wd,ya,yb,col,yref=0):
        pts=[(xt-k60*(ya-yref),ya),(xt+wd-k60*(ya-yref),ya),(xt+wd-k60*(yb-yref),yb),(xt-k60*(yb-yref),yb)]
        s.d.polygon([(P(a),P(b)) for a,b in pts],fill=col)
    def layer(s):
        im=s.img.resize((W1,H1),Image.LANCZOS); bb=im.getbbox()
        a=np.array(im.crop(bb)).astype(np.float32)/255.
        return {'rgb':a[...,:3],'a':a[...,3],'x':bb[0],'y':bb[1]}

def comp(fr,L,dx=0,dy=0,alpha=1.0,clip=None,scale=None):
    """fr float32 HxWx3 0..1 ; clip=(fx0,fx1) fraction of layer width visible"""
    if alpha<=0.003: return
    rgb,a=L['rgb'],L['a']; x=L['x']; y=L['y']
    if scale is not None and abs(scale-1)>1e-3:
        h,w=a.shape; nw,nh=max(1,int(w*scale)),max(1,int(h*scale))
        rgb=cv2.resize(rgb,(nw,nh),interpolation=cv2.INTER_LINEAR); a=cv2.resize(a,(nw,nh),interpolation=cv2.INTER_LINEAR)
        ax,ay=L.get('anchor',(0.5,0.5)); x-= (nw-w)*ax; y-=(nh-h)*ay
    if clip is not None:
        h,w=a.shape; m=np.zeros(w,np.float32); c0,c1=int(w*clip[0]),int(w*clip[1]); m[c0:c1]=1; a=a*m[None,:]
    x=int(round(x+dx)); y=int(round(y+dy)); h,w=a.shape
    x0,y0=max(0,x),max(0,y); x1,y1=min(W1,x+w),min(H1,y+h)
    if x1<=x0 or y1<=y0: return
    sa=a[y0-y:y1-y,x0-x:x1-x,None]*alpha; sr=rgb[y0-y:y1-y,x0-x:x1-x]
    reg=fr[y0:y1,x0:x1]; reg[:]=reg*(1-sa)+sr*sa

# ---------------- background pieces (1x) ----------------
yy,xx=np.mgrid[0:H1,0:W1].astype(np.float32)
def glow(cx,cy,r,col):
    dd=np.sqrt((xx-cx)**2+(yy-cy)**2)/r; return (np.clip(1-dd,0,1)**2)[...,None]*np.array(col,np.float32)/255.
BASE=np.zeros((H1,W1,3),np.float32)+np.array(BG,np.float32)/255.
GR=glow(W1*0.95,H1*0.06,W1*0.95,RED); GB=glow(W1*0.02,H1*0.97,W1*1.0,BLUE)

# athlete
src=cv2.cvtColor(cv2.imread(PHOTO),cv2.COLOR_BGR2RGB).astype(np.float32)
msk=cv2.imread(MASK,0).astype(np.float32)/255
_y0,_y1,_x0,_x1=PHOTO_CROP; src=src[_y0:_y1,_x0:_x1]; msk=msk[_y0:_y1,_x0:_x1]
sc=0.90*1.06
nw,nh=int(src.shape[1]*sc),int(src.shape[0]*sc)
src=cv2.resize(src,(nw,nh),interpolation=cv2.INTER_LANCZOS4); msk=cv2.resize(msk,(nw,nh),interpolation=cv2.INTER_LINEAR)
pass
a_=src/255.; a_=np.clip((a_-0.5)*1.10+0.52,0,1); a_[...,0]*=0.97; a_[...,2]*=1.04; ATH=np.clip(a_,0,1)
HALO=cv2.GaussianBlur(msk,(0,0),13)
ATH_CX,ATH_TOP=540,505; F0,F1=990,1175
fadeY=(1-sm(F0,F1,np.arange(H1,dtype=np.float32)))

def draw_athlete(fr,t):
    ain=ease(t,1.0,2.2); 
    if ain<=0: return None
    z=(1.0+0.06*(t/DUR))/1.06
    w,h=int(nw*z),int(nh*z)
    rgb=cv2.resize(ATH,(w,h),interpolation=cv2.INTER_AREA); m=cv2.resize(msk,(w,h),interpolation=cv2.INTER_AREA); hl=cv2.resize(HALO,(w,h),interpolation=cv2.INTER_AREA)
    # anchor zoom at face (approx 0.5, 0.12 of layer)
    base_w,base_h=nw/1.06,nh/1.06
    x=ATH_CX-base_w/2-(w-base_w)*0.5; y=ATH_TOP-(h-base_h)*0.15+(1-ain)*50
    x=int(round(x)); y=int(round(y))
    y1=min(H1,y+h); x0=max(0,x); x1=min(W1,x+w)
    fy=fadeY[y:y1,None]
    al=m[:y1-y,x0-x:x1-x]*fy*ain; ha=hl[:y1-y,x0-x:x1-x]*fy*ain
    reg=fr[y:y1,x0:x1]
    reg+=ha[...,None]*np.array(RED,np.float32)/255.*0.10
    reg[:]=reg*(1-al[...,None])+rgb[:y1-y,x0-x:x1-x]*al[...,None]
    full=np.zeros((H1,W1),np.float32); full[y:y1,x0:x1]=al
    return full

# grid alpha (1x)
c=Ctx()
for x in range(0,W,P(54)): c.d.line([(x,0),(x,H)],fill=(255,255,255,255))
for y in range(0,H,P(54)): c.d.line([(0,y),(W,y)],fill=(255,255,255,255))
GRID=np.array(c.img.resize((W1,H1),Image.LANCZOS))[...,3].astype(np.float32)/255.*0.045

# ---------------- layers ----------------
Ls={}
def mk(name,fn,anchor=None):
    c=Ctx(); fn(c); L=c.layer(); 
    if anchor: L['anchor']=anchor
    Ls[name]=L
mk('sl1',lambda c:c.slash(1010,64,-200,250,RED))
mk('sl2',lambda c:c.slash(1110,44,-200,210,RED))
mk('sl3',lambda c:c.slash(962,5,-200,250,BLUE))
mk('sl4',lambda c:c.slash(940,1.5,-200,250,(255,255,255,200)))
mk('hd1',lambda c:c.text((P(64),P(96)),T_L1,T('Bold',15),WHITE,tr=3))
mk('hd2',lambda c:c.text((P(64),P(124)),T_L2,T('Medium',14),GREY,tr=2.5))
mk('hd3',lambda c:c.text((P(64),P(150)),T_L3,T('Medium',14),DIM,tr=2.5))
mk('hdr',lambda c:c.ruler(64,186,28))
lx,ly,lw=84,284,250
def _logo(c):
    lg=Image.open(LOGO).convert('RGBA'); w=P(lw); h=int(w*lg.height/lg.width)
    lg=lg.resize((w,h),Image.LANCZOS); la=np.array(lg); la[...,:3]=255; c.img.alpha_composite(Image.fromarray(la),(P(lx),P(ly)))
mk('logo',_logo,anchor=(0.5,0.5))
lh=lw*2496/2880
mk('brA',lambda c:c.bracket(lx-20,ly-20,32,'tl',RED)); mk('brB',lambda c:c.bracket(lx+lw+20,ly+lh+20,32,'br',BLUE))
fh_,_=fit('Black',T_WHEN,150,580); bbH=fh_.getbbox(T_WHEN); hy=292
mk('hoje',lambda c:c.text((P(1016),P(hy)-bbH[1]),T_WHEN,fh_,WHITE,anchor='r'))
hb_=(P(hy)+bbH[3]-bbH[1])/S; hw=fh_.getlength(T_WHEN)/S
mk('hojeline',lambda c:c.d.rectangle([P(1016-hw+6),P(hb_+20),P(1016),P(hb_+24)],fill=RED))
mk('dot',lambda c:c.d.ellipse([P(1016-hw+6),P(hb_+42),P(1016-hw+18),P(hb_+54)],fill=RED),anchor=(0.5,0.5))
mk('dia',lambda c:c.text((P(1016-hw+30),P(hb_+36)),T_WHEN_SUB,T('Medium',18),GREY,tr=3))
def _cross(c):
    cx,cy=104,640
    c.d.ellipse([P(cx-24),P(cy-24),P(cx+24),P(cy+24)],outline=(255,255,255,120),width=S)
    for dx,dy in((1,0),(-1,0),(0,1),(0,-1)): c.d.line([(P(cx+dx*12),P(cy+dy*12)),(P(cx+dx*36),P(cy+dy*36))],fill=(255,255,255,150),width=S)
    c.d.ellipse([P(cx-4),P(cy-4),P(cx+4),P(cy+4)],fill=RED)
mk('cross',_cross)
t1,t2=T_FIRST,T_LAST; sz=120
W_FIRST='Regular' if (FX_VHS or FX_RAIN) else 'Light'   # floor is Light; Regular under grain/VHS
while T(W_FIRST,sz).getlength(t1)+T('Black',sz).getlength(t2)>P(952): sz-=1
ft1,ft=T(W_FIRST,sz),T('Black',sz); TY=1122
mk('t1',lambda c:c.d.text((P(64),P(TY)),t1,font=ft1,fill=WHITE))
mk('t2',lambda c:c.d.text((P(64)+ft1.getlength(t1),P(TY)),t2,font=ft,fill=RED))
uy=TY+ft.getbbox('HEN')[3]/S+28   # diacritic/cedilla-free probe for the baseline
mk('ul',lambda c:c.d.rectangle([P(1016-430),P(uy),P(1016),P(uy+4)],fill=WHITE))
mk('desc',lambda c:c.text((P(1016-430-22),P(uy-11)),T_DESC,T('Medium',18),GREY,tr=3,anchor='r'))
X0,Y0,X1,Y1=64,uy+36,1016,uy+36+212
def _card(c):
    ch=28; poly=[(X0,Y0),(X1-ch,Y0),(X1,Y0+ch),(X1,Y1),(X0+ch,Y1),(X0,Y1-ch)]
    c.d.polygon([(P(a),P(b)) for a,b in poly],fill=PANEL+(217,)); c.d.line([(P(a),P(b)) for a,b in poly+[poly[0]]],fill=(255,255,255,38),width=S)
    mid=(Y0+Y1-28)/2
    c.d.rectangle([P(X0),P(Y0),P(X0+6),P(mid)],fill=RED); c.d.rectangle([P(X0),P(mid),P(X0+6),P(Y1-28)],fill=BLUE)
mk('card',_card)
mk('cbr',lambda c:c.bracket(X1+14,Y1+14,22,'br',(255,255,255,170),2))
ix=X0+40
_floc=T('Regular' if (FX_VHS or FX_RAIN) else 'Light',34); _locw=sum(_floc.getlength(ch)+2*S for ch in T_LOC)/S
_fev,_=fit('Bold',T_EVENT,46,(X1-36)-ix-_locw-36)
mk('ev',lambda c:c.text((P(ix),P(Y0+22)),T_EVENT,_fev,WHITE))
def _loc(c):
    c.text((P(X1-36),P(Y0+30)),T_LOC,_floc,GREY,tr=2,anchor='r'); c.text((P(X1-36),P(Y0+76)),'01 / 01',MB(14),DIM,tr=3,anchor='r')
mk('loc',_loc)
HX0,HY0,HX1,HY1=ix,Y0+112,X1-36,Y0+184; tabw=256
mk('hbar',lambda c:c.d.rectangle([P(HX0),P(HY0),P(HX1),P(HY1)],fill=BLUE+(26,),outline=BLUE+(255,),width=S))
def _tab(c):
    c.d.polygon([(P(HX0),P(HY0)),(P(HX0+tabw),P(HY0)),(P(HX0+tabw-34),P(HY1)),(P(HX0),P(HY1))],fill=BLUE+(255,))
mk('tab',_tab)
def _tabt(c):
    fm=T('Bold',22); bb=fm.getbbox('CATEGORIA'); c.text((P(HX0+22),P((HY0+HY1)/2)-(bb[1]+bb[3])/2),'CATEGORIA',fm,(9,10,14),tr=3)
mk('tabt',_tabt)
def _cat(c):
    fk,_=fit('Bold',T_CAT,46,(HX1-24)-(HX0+tabw+150)); bb=fk.getbbox(T_CAT); c.text((P(HX1-24),P((HY0+HY1)/2)-(bb[1]+bb[3])/2),T_CAT,fk,BLUE,anchor='r')
mk('cat',_cat)
mk('kum',lambda c:c.text((P(HX0+tabw+14),P((HY0+HY1)/2)-S*11),T_DISC,T('Medium',18),BLUE,tr=3))
fh=T('SemiBold',40); _hw=fh.getlength(T_HASH)/S
FY=Y1+36; ff,_=fit('Black',T_CHEER,88,952-_hw-40); bbF=ff.getbbox(T_CHEER); cb=ff.getbbox('HEN'); base=P(FY)-bbF[1]+cb[3]
mk('forca',lambda c:c.text((P(1016),P(FY)-bbF[1]),T_CHEER,ff,WHITE,anchor='r'),anchor=(1.0,0.8))
hb=fh.getbbox(T_HASH)
mk('hash',lambda c:c.text((P(64),base-hb[3]),T_HASH,fh,RED))
fy=1846
def _foot(c):
    c.d.line([(P(64),P(fy)),(P(1016),P(fy))],fill=(255,255,255,50),width=S)
    c.slash(92,16,fy+14,fy+44,BLUE,yref=fy); c.slash(122,16,fy+14,fy+44,RED,yref=fy)
    c.ruler(1016-39*8,1700,40,step=8)
mk('foot',_foot)
def _foott(c):
    c.text((P(1016),P(fy+20)),T_FOOT,T('Regular',14),GREY,tr=4,anchor='r'); c.text((P(1016),P(1726)),T_STANDBY,T('Medium',13),DIM,tr=3,anchor='r')
mk('foott',_foott)
print('event size',_fev.size/S,file=sys.stderr)
print('hero text ends at y=',base/S,'(must be <= 1600)',file=sys.stderr)

mono1=F('GeistMono-Regular',15,1)
rng=np.random.default_rng(3)
NOISE=[rng.normal(0,0.016,(H1,W1,1)).astype(np.float32) for _ in range(6)]
sdir=np.array([k60,-1.0])  # toward top-right along slash


# ================= MATRIX RAIN + VHS =================
CW,CH=18,26; NCOL=W1//CW; NROW=H1//CH+1
CHARS='0123456789ABCDEF<>/+=:*#'
_f=F('GeistMono-Bold',17,1); ATL=np.zeros((len(CHARS),CH,CW),np.float32)
for k,ch in enumerate(CHARS):
    im=Image.new('L',(CW,CH),0); ImageDraw.Draw(im).text((CW/2,CH/2),ch,font=_f,fill=255,anchor='mm'); ATL[k]=np.array(im,np.float32)/255.
rr=np.random.default_rng(11)
R_ON=rr.random(NCOL)<0.55; R_V=rr.uniform(5,15,NCOL); R_L=rr.integers(8,24,NCOL); R_P=rr.uniform(0,NROW+40,NCOL)
R_BASE=rr.integers(0,len(CHARS),(NROW,NCOL)); R_RATE=rr.choice([0.4,0.8,1.5,3,6],(NROW,NCOL))
rows_=np.arange(NROW,dtype=np.float32)[:,None]
_yv=np.arange(H1,dtype=np.float32)
RAIN_V=(1-0.85*sm(940,1120,_yv))+0.55*sm(1600,1720,_yv); RAIN_V=np.clip(RAIN_V,0,1)[:,None]
def rain(t):
    head=(R_P+R_V*t)%(NROW+R_L+12)
    d=head[None,:]-rows_; b=np.where((d>=0)&(d<R_L[None,:]),1-d/R_L[None,:],0)*R_ON[None,:]
    hd=((d>=0)&(d<1))*R_ON[None,:]
    idx=(R_BASE+(t*R_RATE).astype(int)*7)%len(CHARS)
    g=ATL[idx].transpose(0,2,1,3).reshape(NROW*CH,NCOL*CW)[:H1,:W1]
    B=np.repeat(np.repeat(b,CH,0),CW,1)[:H1,:W1]; Hd=np.repeat(np.repeat(hd,CH,0),CW,1)[:H1,:W1]
    return g*B, g*Hd
VN=[cv2.blur(rr.normal(0,0.10,(H1,W1)).astype(np.float32),(11,1))[...,None] for _ in range(6)]   # horizontal streak grain
SCAN=np.ones(H1,np.float32); SCAN[::2]=0.90; SCAN=SCAN[:,None,None]
_fy,_fx=np.mgrid[0:H1,0:W1].astype(np.float32)
FACE=np.clip(1.6-np.sqrt(((_fx-540)/170)**2+((_fy-655)/215)**2)*1.6,0,1)[...,None]; del _fy,_fx
BURSTS=[(0.35,1.0),(6.6,6.8),(8.0,8.2),(10.7,10.85),(13.5,13.7),(16.2,16.35),(18.0,18.2)]
def band(fr,src,y,h,shift,split):
    y0,y1=max(0,y),min(H1,y+h)
    if y1<=y0: return
    s_=np.roll(src[y0:y1],shift,axis=1); o=s_.copy(); o[...,0]=np.roll(s_[...,0],split,axis=1); o[...,2]=np.roll(s_[...,2],-split,axis=1); fr[y0:y1]=o
def vhs(fr,i,t):
    rg=np.random.default_rng(1000+i); clean=fr.copy(); hit=False
    inb=any(a<=t<b for a,b in BURSTS)
    n=int(rg.integers(3,8)) if inb else (1 if rg.random()<0.12 else 0)
    for _ in range(n):
        zone=rg.choice(4,p=[0.36,0.30,0.10,0.24]); lo,hi=[(0,470),(840,1010),(1250,1490),(1600,1900)][zone]
        h=int(rg.integers(3,50 if inb else 10)); y=int(rg.integers(lo,hi-h)); mx=24 if zone==2 else 90
        band(fr,clean,y,h,int(rg.integers(-mx,mx)),int(rg.integers(3,11))); hit=True
    # rolling tracking band (no displacement across the face rows)
    yb=int((t*170)%2700)-300
    for y in range(max(0,yb),min(H1,yb+46),3):
        amp=0 if 460<y<860 else 14
        if amp: fr[y:y+3]=np.roll(fr[y:y+3],int(rg.integers(-amp,amp+1)),axis=1)
        fr[y:y+3]+=rg.random((1,W1,1)).astype(np.float32)*0.10*(rg.random()<0.7)
    # head-switching noise at the bottom edge
    for k,y in enumerate(range(1884,H1,3)):
        fr[y:y+3]=np.roll(fr[y:y+3],int(k*4+rg.integers(-6,7)),axis=1); fr[y:y+3]+=rg.random((1,W1,1)).astype(np.float32)*0.14
    if hit: fr[:]=fr*(1-FACE)+clean*FACE
    # chroma bleed, scanlines, streak grain, slight luma wobble
    fr[...,0]=np.roll(fr[...,0],2,axis=1); fr[...,2]=np.roll(fr[...,2],-2,axis=1)
    fr*=SCAN*(1+0.02*math.sin(t*37))
    fr+=VN[i%6]*(1.6 if inb else 1.0)

def frame(i):
    t=i/FPS
    gin=ease(t,0.0,1.2)
    pr=0.30*(1+0.22*math.sin(2*math.pi*t/4.0)); pb=0.20*(1+0.25*math.sin(2*math.pi*t/5.0+1.3))
    fr=BASE+GR*(pr*gin)+GB*(pb*gin)
    # matrix rain behind everything (boot-strong, then settles)
    if FX_RAIN:
      ra=(0.80-0.42*ease(t,0.8,3.0))*ease(t,0.1,0.6); body,hd=rain(t)
      fr+=(body[...,None]*np.array(BLUE,np.float32)/255.*ra+hd[...,None]*0.75*ra)*RAIN_V[...,None]
    full=draw_athlete(fr,t)   # athlete covers the rain
    g=GRID*ease(t,0.2,1.4)
    if full is not None: g=g*(1-full)
    fr=fr*(1-g[...,None])+g[...,None]
    ph=((t-1.5)%5.0)/1.6
    if t>1.5 and ph<1:
        ys=int(ph*H1); bnd=np.exp(-((np.arange(H1)-ys)/18.0)**2).astype(np.float32)*0.06
        fr+=bnd[:,None,None]*np.array(BLUE,np.float32)/255.
    # ---------- PASS 1: graphics (get glitched) ----------
    for n,(nm,st) in enumerate((('sl1',0.3),('sl2',0.42),('sl3',0.55),('sl4',0.65))):
        e=ease(t,st,st+0.7); drift=math.sin(2*math.pi*t/6+n)*(10+6*n); off=sdir*((1-e)*520+drift-30)
        comp(fr,Ls[nm],off[0],off[1],alpha=min(1,e*1.5))
    comp(fr,Ls['hdr'],clip=(0,ease(t,1.0,1.6)))
    eb=ease(t,1.2,1.9); comp(fr,Ls['brA'],-(1-eb)*40,-(1-eb)*40,eb); comp(fr,Ls['brB'],(1-eb)*40,(1-eb)*40,eb)
    e=ease(t,2.0,2.6); comp(fr,Ls['hojeline'],clip=(1-e,1))
    if t>2.4:
        bl=0.5+0.5*math.cos(2*math.pi*(t-2.4)/1.0); comp(fr,Ls['dot'],alpha=0.25+0.75*bl,scale=1+0.35*bl)
    ec=ease(t,1.4,2.0); cdx=18*math.sin(2*math.pi*t/7.0); cdy=26*math.sin(2*math.pi*t/9.0+0.8)
    comp(fr,Ls['cross'],cdx,cdy,ec)
    e=ease(t,3.0,3.6); comp(fr,Ls['ul'],clip=(1-e,1))
    e=ease(t,3.3,4.0); comp(fr,Ls['card'],clip=(0,e)); comp(fr,Ls['cbr'],(1-e)*30,(1-e)*30,ease(t,3.8,4.3))
    e=ease(t,4.1,4.7); comp(fr,Ls['hbar'],clip=(0,e))
    et=ease(t,4.3,4.9); comp(fr,Ls['tab'],-(1-et)*60,0,et)
    if t>5.5:
        ph=((t-5.5)%4.0)/0.9
        if ph<1:
            xs=X0+ph*(X1-X0); xs_=np.arange(X0,X1); bnd=np.exp(-((xs_-xs)/40.0)**2).astype(np.float32)*0.10
            fr[int(Y0):int(Y1),X0:X1]+=bnd[None,:,None]
    comp(fr,Ls['foot'],alpha=ease(t,5.4,6.2))
    if FX_VHS: vhs(fr,i,t)
    # ---------- PASS 2: text + logo (always clean) ----------
    for nm,st in (('hd1',0.6),('hd2',0.75),('hd3',0.9)): comp(fr,Ls[nm],clip=(0,ease(t,st,st+0.6)))
    e=ease(t,0.8,1.6); comp(fr,Ls['logo'],alpha=e,scale=1.12-0.12*e)
    e=ease(t,1.6,2.3); comp(fr,Ls['hoje'],(1-e)*120,0,alpha=e,clip=(1-e,1))
    comp(fr,Ls['dia'],clip=(0,ease(t,2.3,2.9)))
    e=ease(t,2.4,3.1); comp(fr,Ls['t1'],-(1-e)*140,0,e)
    e=ease(t,2.6,3.3); comp(fr,Ls['t2'],(1-e)*140,0,e)
    comp(fr,Ls['desc'],alpha=ease(t,3.3,3.8))
    e=ease(t,3.7,4.3); comp(fr,Ls['ev'],-(1-e)*40,0,e)
    e=ease(t,3.9,4.5); comp(fr,Ls['loc'],(1-e)*40,0,e)
    comp(fr,Ls['tabt'],-(1-et)*60,0,et)
    comp(fr,Ls['kum'],alpha=ease(t,4.7,5.1))
    e=ease(t,4.6,5.2); comp(fr,Ls['cat'],(1-e)*60,0,e)
    e=ease(t,4.9,5.5); comp(fr,Ls['hash'],-(1-e)*80,0,e,clip=(0,e))
    e=ease(t,5.1,5.7); sc_=1.35-0.35*e
    for p0 in (9.0,13.0,17.0):
        if p0<=t<p0+0.6: sc_=1+0.07*math.sin(math.pi*(t-p0)/0.6)
    comp(fr,Ls['forca'],alpha=e,scale=sc_)
    comp(fr,Ls['foott'],alpha=ease(t,5.4,6.2))
    fr+=NOISE[i%6]*(0.6 if FX_VHS else 1.0)
    out=(np.clip(fr,0,1)*255).astype(np.uint8)
    if t>1.4:
        im=Image.fromarray(out); d=ImageDraw.Draw(im,'RGBA'); a=int(255*ec)
        jx=COORD[0]+cdx*0.0001+(math.sin(t*13)*0.00004); jy=COORD[1]+cdy*0.0001+(math.cos(t*11)*0.00004)
        d.text((64+cdx*0.3,690+cdy),f'X {jx:.4f}',font=mono1,fill=GREY+(a,)); d.text((64+cdx*0.3,714+cdy),f'Y {jy:.4f}',font=mono1,fill=GREY+(a,))
        off=(t*14)%50
        for k in range(-5,32):
            yk=620+k*10+off
            if 620<=yk<=880:
                idx=k-int((t*14)//50)*5; h=12 if idx%5==0 else 6
                d.line([(1004,yk),(1004+h,yk)],fill=(255,255,255,int(70*ec)),width=1)
        out=np.array(im)
    return out

if __name__=='__main__':
    if sys.argv[1]=='test':
        import time; t0=time.time()
        ims=[Image.fromarray(frame(int(s*FPS))) for s in (0.7,2.2,8.1,19.97)]
        print('s/frame',(time.time()-t0)/4,file=sys.stderr)
        sh=Image.new('RGB',(540*4,960)); [sh.paste(im.resize((540,960)),(540*k,0)) for k,im in enumerate(ims)]; sh.save('vid_test.png'); sys.exit()
    a0,a1=int(sys.argv[1]),int(sys.argv[2]); out=f'{OUT_PREFIX}_{a0:04d}.mp4'
    p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W1}x{H1}','-r',str(FPS),'-i','-',
        '-c:v','libx264','-preset','ultrafast','-crf','10','-pix_fmt','yuv420p','-r',str(FPS),out],stdin=subprocess.PIPE)
    for i in range(a0,a1): p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
