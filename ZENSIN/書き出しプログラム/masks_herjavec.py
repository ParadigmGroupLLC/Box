import numpy as np, cv2
F=np.load('frames.npy'); n=len(F)
cuts=[0,18,40,56,86,91,120,137,172,194,235,253,287,298,334,n]
K=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41))
G=np.array([cv2.cvtColor(f,cv2.COLOR_RGB2GRAY) for f in F])
MED=np.median(G[18:334:2],axis=0).astype(np.int16)
H,W=G.shape[1:]
WM=np.zeros((H,W),np.uint8); WM[478:548,735:1005]=255
RIGHT=np.zeros((H,W),bool); RIGHT[60:300,540:1000]=True
BAND=np.zeros((H,W),bool); BAND[120:420,120:900]=True
M=np.zeros(G.shape,np.uint8); info=[]
for a,b in zip(cuts,cuts[1:]):
    s=a+int((b-a)*0.4); Mn=G[s:b].min(0)
    th=cv2.morphologyEx(Mn,cv2.MORPH_TOPHAT,K)
    m=((th>20)&(Mn>110)&((Mn.astype(np.int16)-MED)>22)).astype(np.uint8)
    r=(m.astype(bool)&RIGHT).sum(); c=(m.astype(bool)&BAND&~RIGHT).sum()
    if a<18 or a>=334: kind='none'; m[:]=0
    elif c>20000: kind='script'
    else: kind='right'
    if kind=='right': m=(m.astype(bool)&RIGHT).astype(np.uint8)
    if kind=='script':
        m=(m.astype(bool)&(BAND|RIGHT)).astype(np.uint8)
        blob=cv2.dilate(cv2.morphologyEx(m,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(29,29))),np.ones((5,5),np.uint8))
        keep=np.zeros_like(blob,bool); keep[120:340,700:1000]=True  # 文の終わりの「.」（丸い点）は戻す
        m=((m.astype(bool)&~blob.astype(bool))|(m.astype(bool)&keep)).astype(np.uint8)
    m=cv2.morphologyEx(m*255,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    m=cv2.dilate(m,np.ones((11,11),np.uint8))
    M[a:b]=np.maximum(m,WM) if kind!='none' else WM
    info.append((a,b,kind,int(r),int(c)))
print(info)
np.save('masks.npy',M)
outs=[]
for t in [2.2,2.8,4.6,5.5,10.2,10.8]:
    i=int(t*30); vis=F[i].copy(); sel=M[i]>0; vis[sel]=(vis[sel]*0.4+np.array([255,0,0])*0.6).astype(np.uint8)
    outs.append(np.concatenate([F[i],vis],1))
cv2.imwrite('masktest5.png',cv2.cvtColor(cv2.resize(np.concatenate(outs,0),None,fx=0.33,fy=0.33),cv2.COLOR_RGB2BGR))
