import math, wave, struct, sys
from pathlib import Path
SR=48000
DUR=138.0
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('sound-grammar-v3.wav')
buf=[0.0]*int(SR*DUR)

def burst(start,duration,freq,amp=0.04,decay=8.0):
    i0=int(start*SR); n=int(duration*SR)
    for i in range(n):
        t=i/SR
        env=math.exp(-decay*t)
        v=amp*env*math.sin(2*math.pi*freq*t)
        j=i0+i
        if 0<=j<len(buf): buf[j]+=v

def chord(start,duration,freqs,amp=0.03,decay=4.0):
    for k,f in enumerate(freqs):
        burst(start+k*0.018,duration,f,amp/max(1,len(freqs))*1.8,decay)

chord(0.18,0.42,[68,104],0.075,7.0)
for k,f in enumerate([920,850,780,710,650]):
    burst(3.35+k*0.52,0.075,f,0.035,28.0)
chord(7.10,0.30,[120,165],0.055,9.0)
chord(12.08,0.24,[300,430],0.035,10.0)
chord(19.72,0.09,[640,980],0.04,30.0)
for k in range(5):
    burst(20.28+k*0.36,0.055,1120+30*k,0.026,34.0)
chord(26.82,0.09,[640,980],0.038,30.0)
for k in range(5):
    burst(27.16+k*0.36,0.055,1120+30*k,0.025,34.0)
chord(36.32,0.42,[390,585],0.035,7.0)
burst(61.20,0.18,180,0.025,14.0)
chord(117.20,0.34,[260,390],0.028,8.0)
chord(130.25,0.90,[330,495,660],0.035,3.5)

peak=max(abs(x) for x in buf) or 1.0
scale=min(1.0,0.28/peak)
with wave.open(str(OUT),'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    frames=bytearray()
    for x in buf:
        y=max(-1.0,min(1.0,x*scale))
        frames += struct.pack('<h',int(y*32767))
    w.writeframes(frames)
print(f'SFX_PASS duration={DUR:.1f}s sr={SR} peak_pre={peak:.6f} scale={scale:.4f}')
print(f'OUTPUT={OUT}')
