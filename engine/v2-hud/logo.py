import cv2, numpy as np
from PIL import Image, ImageDraw
_m=cv2.imread('/home/claude/logo_mask_raw.png',0)
_m=cv2.GaussianBlur(_m,(0,0),0.8); _m=(_m>127).astype(np.uint8)*255
ys,xs=np.where(_m>0); X0,X1,Y0,Y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
_m=_m[Y0:Y1,X0:X1]; LW,LH=_m.shape[1],_m.shape[0]
cs,hier=cv2.findContours(_m,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
POLYS=[]
for i,c in enumerate(cs):
    ap=cv2.approxPolyDP(c,1.1,True)[:,0,:].astype(float)
    POLYS.append((ap,hier[0][i][3]<0))   # (points, is_outer)
def logo_rgba(width,color=(255,255,255)):
    """vector-rendered Shomen logo, RGBA, white on transparent, given target width (px)"""
    SS=4; sc=width*SS/LW; w,h=int(round(LW*sc)),int(round(LH*sc))
    im=Image.new('L',(w,h),0); d=ImageDraw.Draw(im)
    for pts,outer in POLYS:
        if outer: d.polygon([(x*sc,y*sc) for x,y in pts],fill=255)
    for pts,outer in POLYS:
        if not outer: d.polygon([(x*sc,y*sc) for x,y in pts],fill=0)
    im=im.resize((max(1,w//SS),max(1,h//SS)),Image.LANCZOS)
    a=np.array(im); out=np.zeros((a.shape[0],a.shape[1],4),np.uint8); out[...,:3]=color; out[...,3]=a
    return Image.fromarray(out)
if __name__=='__main__':
    lg=logo_rgba(600); bg=Image.new('RGBA',lg.size,(9,10,14,255)); bg.alpha_composite(lg); bg.convert('RGB').save('logo_vec_test.png'); print(lg.size, len(POLYS))
