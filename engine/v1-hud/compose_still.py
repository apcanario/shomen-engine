import sys
FX_GLITCH=False   # OFF by default. ON only when Pedro asks (spec §7.1). Graphics + photo only — never text, logo or face.
src_=open('vid.py').read()
head,rest=src_.split('# ---------------- background pieces (1x)')
layers=rest.split('# ---------------- layers ----------------')[1].split('mono1=')[0]
# full-res layers (no 1x downscale)
head=head.replace("im=s.img.resize((W1,H1),Image.LANCZOS); bb=im.getbbox()","im=s.img; bb=im.getbbox()")
if FX_GLITCH:   # Light reads weak under grain/scanlines -> Regular for first name + location
    head=head.replace("FX_VHS=False","FX_VHS=True"); layers=layers.replace("T('Light',28)","T('Regular',28)")
exec(head); exec(layers)
def put(fr,L,dx=0,dy=0,alpha=1.0):
    a=L['a']*alpha; x=int(round(L['x']+dx)); y=int(round(L['y']+dy)); h,w=a.shape
    x0,y0=max(0,x),max(0,y); x1,y1=min(W,x+w),min(H,y+h)
    sa=a[y0-y:y1-y,x0-x:x1-x,None]; reg=fr[y0:y1,x0:x1]; reg[:]=reg*(1-sa)+L['rgb'][y0-y:y1-y,x0-x:x1-x]*sa
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
def glow(cx,cy,r,col):
    dd=np.sqrt((xx-cx)**2+(yy-cy)**2)/r; return (np.clip(1-dd,0,1)**2)[...,None]*np.array(col,np.float32)/255.
fr=np.zeros((H,W,3),np.float32)+np.array(BG,np.float32)/255.
fr+=glow(W*0.95,H*0.06,W*0.95,RED)*0.30+glow(W*0.02,H*0.97,W*1.0,BLUE)*0.22
del yy,xx
# athlete at 2x
ph=cv2.cvtColor(cv2.imread(PHOTO),cv2.COLOR_BGR2RGB).astype(np.float32); mk_=cv2.imread(MASK,0).astype(np.float32)/255
y0,y1,x0,x1=PHOTO_CROP; ph=ph[y0:y1,x0:x1]; mk_=mk_[y0:y1,x0:x1]
sc=0.90*1.03*S; nw,nh=int(ph.shape[1]*sc),int(ph.shape[0]*sc)
ph=cv2.resize(ph,(nw,nh),interpolation=cv2.INTER_LANCZOS4); mk_=cv2.resize(mk_,(nw,nh),interpolation=cv2.INTER_CUBIC).clip(0,1)
a_=np.clip((ph/255.-0.5)*1.10+0.52,0,1); a_[...,0]*=0.97; a_[...,2]*=1.04; a_=np.clip(a_,0,1)
halo=cv2.GaussianBlur(mk_,(0,0),26)
ax=P(540)-nw//2; ay=P(505)-int(nh*0.03*0.15)
fade=(1-sm(P(990),P(1175),np.arange(H,dtype=np.float32)))
ye=min(H,ay+nh); fy=fade[ay:ye,None]
al=mk_[:ye-ay]*fy; ha=halo[:ye-ay]*fy
reg=fr[ay:ye,ax:ax+nw]; reg+=ha[...,None]*np.array(RED,np.float32)/255.*0.10; reg[:]=reg*(1-al[...,None])+a_[:ye-ay]*al[...,None]
full=np.zeros((H,W),np.float32); full[ay:ye,ax:ax+nw]=al
# grid
g=Image.new('L',(W,H),0); gd=ImageDraw.Draw(g)
for x in range(0,W,P(54)): gd.line([(x,0),(x,H)],fill=255,width=S)
for y in range(0,H,P(54)): gd.line([(0,y),(W,y)],fill=255,width=S)
G=np.array(g,np.float32)/255.*0.045*(1-full); fr=fr*(1-G[...,None])+G[...,None]
sd=np.array([k60,-1.0])*(-30*S)
for n in ('sl1','sl2','sl3','sl4'): put(fr,Ls[n],sd[0],sd[1])
GFX=['hdr','brA','brB','hojeline','dot','cross','ul','card','cbr','hbar','tab','foot']
TXT=['hd1','hd2','hd3','logo','hoje','dia','t1','t2','desc','ev','loc','tabt','kum','cat','hash','forca','foott']
for n in GFX: put(fr,Ls[n])
im=Image.fromarray((np.clip(fr,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(im,'RGBA')
for k in range(27):
    h=12 if k%5==0 else 6; d.line([(P(1004),P(620+k*10)),(P(1004+h),P(620+k*10))],fill=(255,255,255,70),width=S)
fr=np.array(im).astype(np.float32)/255.
clean=fr.copy()
# ================= GLITCH PASS (opt-in) =================
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 7)
if FX_GLITCH:
  def band(y,h,xa,xb,shift,split):
      """slice y..y+h, x-range xa..xb (1x px): displace by shift, split R/B by +-split"""
      Y0,Y1,XA,XB=P(y),P(y+h),P(xa),P(xb); sh=P(shift); sp=P(split)
      src=np.roll(clean[Y0:Y1],sh,axis=1)
      out=src.copy(); out[...,0]=np.roll(src[...,0],sp,axis=1); out[...,2]=np.roll(src[...,2],-sp,axis=1)
      fr[Y0:Y1,XA:XB]=out[:,XA:XB]
  # (y,h,xa,xb,shift,split) — logo (x<370,y260-520) and face (x400-690,y490-830) untouched
  B=[(40,10,0,1080,46,5),(66,4,0,1080,-70,8),(212,14,0,1080,-38,6),
   
     (560,6,700,1080,60,8),(598,18,0,390,-30,6),(772,5,0,390,44,7),
     (884,14,0,1080,-24,6),(930,5,0,1080,52,9),(968,20,0,1080,14,4),
   
     (1369,4,0,1080,64,8),
   
     (1648,16,0,1080,-56,7),(1752,5,0,1080,80,10),(1790,24,0,1080,30,6),(1880,8,0,780,-44,8),
     (852,6,0,1080,-34,7),(700,10,690,1080,28,6),(640,5,300,400,-20,6),(1010,8,0,1080,40,8)]
  for b in B: band(*b)
  # data-corruption bars: short solid key-colour / white ticks
  for _ in range(16):
      y=int(rng.choice([rng.integers(20,250),rng.integers(540,1000),rng.integers(1610,1900)])); x=int(rng.integers(0,1000))
      wd_=220
      if 400<x+60 and x<690 and 490<y<830: continue
      if x<370 and 260<y<520: continue
      if x<420 and 80<y<210: continue
      if x<220 and 670<y<740: continue
      if x+wd_>680 and 1690<y<1750: continue
      if x+wd_>780 and 1850<y<1895: continue
      wd=int(rng.integers(30,220)); ht=int(rng.choice([2,3,4,8])); col=[RED,BLUE,WHITE][int(rng.integers(0,3))]; a=float(rng.uniform(0.35,0.85))
      reg=fr[P(y):P(y+ht),P(x):P(min(1080,x+wd))]; reg[:]=reg*(1-a)+np.array(col,np.float32)/255.*a
  # pixel-sort style smear off the right shoulder
  ys,ye_=P(905),P(925); xs=P(760); row=clean[ys:ye_,xs-4:xs].mean(axis=1,keepdims=True); ln=P(180)
  fall=np.linspace(0.8,0,ln,dtype=np.float32)[None,:,None]; reg=fr[ys:ye_,xs:xs+ln]; reg[:]=reg*(1-fall)+row*fall
  # scanlines
  sl=np.ones(H,np.float32); sl[::4]=0.93; sl[1::4]=0.965; fr*=sl[:,None,None]
# ---------- text + logo: composited AFTER the FX pass, always clean ----------
for n in TXT: put(fr,Ls[n])
im=Image.fromarray((np.clip(fr,0,1)*255).astype(np.uint8)); d=ImageDraw.Draw(im,'RGBA'); mono=F('GeistMono-Regular',15)
d.text((P(64),P(690)),f'X {COORD[0]:.4f}',font=mono,fill=GREY); d.text((P(64),P(714)),f'Y {COORD[1]:.4f}',font=mono,fill=GREY)
fr=np.array(im).astype(np.float32)/255.
fr+=rng.normal(0,5.5/255,(H,W,1)).astype(np.float32)
out=Image.fromarray((np.clip(fr,0,1)*255).astype(np.uint8))
out.save('/mnt/user-data/outputs/shomen-still.png',optimize=True)
pv=out.resize((540,960),Image.LANCZOS).convert('RGBA'); ov=Image.new('RGBA',pv.size,(0,0,0,0)); od=ImageDraw.Draw(ov)
od.rectangle([0,0,540,125],fill=(255,230,0,40)); od.rectangle([0,800,540,960],fill=(255,230,0,40)); Image.alpha_composite(pv,ov).convert('RGB').save('qa.png')
