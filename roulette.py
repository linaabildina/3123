import json, math, random, sys, time
from pathlib import Path
from PySide6.QtCore import Qt, QRectF, QPointF, QPropertyAnimation, QEasingCurve, QObject, Property, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QLinearGradient
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox

ROOT=Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
CFG=ROOT/"config.json"; STATE=ROOT/"state.json"

DEFAULT={"cooldown_hours":24,"prizes":[{"name":"Игровой предмет","color":"#1555ff","weight":1},{"name":"Заказать музыку","color":"#ef16ff","weight":1},{"name":"Секретный приз","color":"#7b16ff","weight":1},{"name":"Бонусный приз","color":"#ff246f","weight":1},{"name":"Игровая награда","color":"#3626ff","weight":1},{"name":"Сюрприз","color":"#d600ff","weight":1}]}


def load(path, default):
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        path.write_text(json.dumps(default,ensure_ascii=False,indent=2),encoding="utf-8"); return default

def save(path,data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")

class Model(QObject):
    changed=Signal()
    def __init__(self): super().__init__(); self._a=0
    def get(self): return self._a
    def set(self,v): self._a=v; self.changed.emit()
    angle=Property(float,get,set,notify=changed)

class Roulette(QWidget):
    def __init__(self):
        super().__init__()
        self.cfg=load(CFG,DEFAULT)
        self.prizes=self.cfg.get("prizes") or DEFAULT["prizes"]
        self.state=load(STATE,{"last_spin":0})
        self.model=Model(); self.model.changed.connect(self.update)
        self.anim=None; self.busy=False; self.selected=None
        self.setWindowTitle("Perfect World — Колесо Фортуны")
        self.resize(1600,900); self.setMinimumSize(1200,700)
        self.button=QRectF()

    def remaining(self):
        return 0

    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton and self.button.contains(e.position()): self.spin()

    def spin(self):
        if self.busy:return
        self.busy=True
        weights=[max(.001,float(x.get("weight",1))) for x in self.prizes]
        self.selected=random.choices(range(len(self.prizes)),weights=weights,k=1)[0]
        n=len(self.prizes); sector=360/n
        target=(270-(self.selected+.5)*sector)%360
        current=self.model.angle%360
        delta=(target-current)%360
        end=self.model.angle+random.randint(7,10)*360+delta
        self.anim=QPropertyAnimation(self.model,b"angle",self)
        self.anim.setDuration(6200); self.anim.setStartValue(self.model.angle); self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.OutCubic); self.anim.finished.connect(self.done); self.anim.start()

    def done(self):
        self.busy=False; self.state["last_spin"]=time.time(); save(STATE,self.state)
        p=self.prizes[self.selected]
        QMessageBox.information(self,"🎉 ПОЗДРАВЛЯЕМ!",f"Вам выпало:\n\n{p['name']}\n\nСледующая крутка доступна через 24 часа.")
        self.update()

    def paintEvent(self,e):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        self.background(p)
        cx=self.width()*.54; cy=self.height()*.53; r=min(self.height()*.36,self.width()*.27)
        self.info(p)
        self.wheel(p,QPointF(cx,cy),r)
        self.pointer(p,cx,cy-r-8)
        bw=min(470,self.width()*.30); self.button=QRectF(cx-bw/2,cy+r*.86,bw,82); self.draw_button(p,self.button)
        left=self.remaining()
        txt="КРУТКА ДОСТУПНА" if not left else f"СЛЕДУЮЩАЯ КРУТКА  {int(left//3600):02d}:{int(left%3600//60):02d}:{int(left%60):02d}"
        p.setPen(QColor("#ffd9ff")); p.setFont(QFont("Arial",14,QFont.Bold))
        p.drawText(QRectF(cx-280,cy+r*.99,560,30),Qt.AlignCenter,txt); p.end()

    def background(self,p):
        w,h=self.width(),self.height()
        # Deep fantasy night gradient
        g=QLinearGradient(0,0,0,h)
        g.setColorAt(0,QColor("#13002b")); g.setColorAt(.42,QColor("#26004d")); g.setColorAt(1,QColor("#080012"))
        p.fillRect(self.rect(),QBrush(g))
        # Large moon
        p.setPen(Qt.NoPen); p.setBrush(QColor(235,205,255,220))
        p.drawEllipse(QPointF(w*.64,h*.14),h*.105,h*.105)
        p.setBrush(QColor(100,25,160,70))
        for dx,dy,rr in [(-22,-10,12),(18,14,9),(30,-22,7),(-28,20,8)]:
            p.drawEllipse(QPointF(w*.64+dx,h*.14+dy),rr,rr)
        # distant mountains / waterfalls
        p.setBrush(QColor(34,9,65,230))
        p.drawPolygon([QPointF(0,h*.38),QPointF(w*.13,h*.18),QPointF(w*.25,h*.39),
                       QPointF(w*.39,h*.17),QPointF(w*.53,h*.38),QPointF(w*.67,h*.19),
                       QPointF(w*.83,h*.39),QPointF(w,h*.21),QPointF(w,h),QPointF(0,h)])
        p.setPen(QPen(QColor(177,73,255,75),4))
        for x in [w*.12,w*.27,w*.43,w*.73,w*.88]:
            p.drawLine(x,h*.33,x-8,h*.55)
            p.drawLine(x-8,h*.55,x+3,h*.69)
        # Pagodas across the horizon
        def pagoda(x,base,scale):
            p.setPen(QPen(QColor("#7d28bb"),2))
            p.setBrush(QColor(18,3,37,235))
            bw=48*scale
            p.drawRect(QRectF(x-bw*.16,base-70*scale,bw*.32,70*scale))
            for j in range(4):
                yy=base-(18+j*16)*scale
                ww=bw*(.72-.10*j)
                p.drawPolygon([QPointF(x-ww,yy),QPointF(x+ww,yy),
                               QPointF(x+ww*.55,yy-7*scale),QPointF(x-ww*.55,yy-7*scale)])
            p.drawLine(x,base-76*scale,x,base-95*scale)
        for x,sc in [(w*.08,.8),(w*.22,.55),(w*.38,.75),(w*.55,.55),(w*.73,.85),(w*.9,.65)]:
            pagoda(x,h*.50,sc)
        # Sakura branches
        p.setPen(QPen(QColor(95,26,94,220),9))
        p.drawLine(0,0,w*.22,h*.25); p.drawLine(w*.02,h*.08,w*.18,h*.03)
        p.setPen(Qt.NoPen)
        for i in range(115):
            x=(i*83+31)%w; y=(i*47+13)%(int(h*.72))
            r=2+(i%6)
            p.setBrush(QColor(255,60+(i%4)*30,230,80+(i%4)*35))
            p.drawEllipse(QPointF(x,y),r,r*.65)
        # Right-side fantasy character silhouette/hair glow
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(202,116,255,45))
        p.drawEllipse(QPointF(w*.86,h*.42),w*.16,h*.29)
        p.setBrush(QColor(245,178,255,95))
        p.drawEllipse(QPointF(w*.83,h*.27),w*.075,h*.105)
        p.setBrush(QColor(76,21,112,180))
        p.drawPolygon([QPointF(w*.78,h*.36),QPointF(w*.94,h*.36),QPointF(w*.98,h*.88),
                       QPointF(w*.75,h*.88)])
        # top-left branding
        p.setPen(QColor("#ff37ff")); p.setFont(QFont("Arial",30,QFont.Bold))
        p.drawText(48,50,"● LIVE")
        p.setPen(QColor("#f02cff")); p.setFont(QFont("Arial",42,QFont.Bold))
        p.drawText(52,100,"K4MUI")
        p.setPen(QColor("#ffffff")); p.setFont(QFont("Arial",42,QFont.Bold))
        p.drawText(238,100,"PLAY")
        p.setPen(QColor("#ffffff")); p.setFont(QFont("Arial",28,QFont.Bold))
        p.drawText(55,142,"РОЗЫГРЫШ")
        p.setPen(QColor("#f4a7ff")); p.setFont(QFont("Arial",17,QFont.Bold))
        p.drawText(58,169,"КОЛЕСО ФОРТУНЫ")
    def info(self,p):
        x,y,w,h=45,205,365,500; r=QRectF(x,y,w,h)
        p.setBrush(QColor(8,2,24,225)); p.setPen(QPen(QColor("#d33dff"),2)); p.drawRoundedRect(r,14,14)
        p.setPen(QColor("#f2b5ff")); p.setFont(QFont("Arial",18,QFont.Bold)); p.drawText(x+25,y+36,"КАК УЧАСТВОВАТЬ?")
        lines=[("▶","Подпишись на канал"),("●","Напиши комментарий"),("♥","Поставь лайк")]
        yy=y+83
        for icon,text in lines:
            p.setPen(QColor("#ff35ff")); p.setFont(QFont("Arial",22,QFont.Bold)); p.drawText(x+25,yy,icon)
            p.setPen(QColor("#ffffff")); p.setFont(QFont("Arial",15)); p.drawText(x+75,yy,text); yy+=48
        p.setPen(QColor("#d53cff")); p.drawLine(x+20,yy+5,x+w-20,yy+5)
        yy+=42
        p.setPen(QColor("#f3a8ff")); p.setFont(QFont("Arial",16,QFont.Bold)); p.drawText(x+25,yy,"УЧАСТНИКОВ:")
        p.setPen(QColor("#ffffff")); p.setFont(QFont("Arial",25,QFont.Bold)); p.drawText(x+205,yy,"247")
        yy+=52
        p.setPen(QColor("#f3a8ff")); p.setFont(QFont("Arial",18,QFont.Bold)); p.drawText(x+25,yy,"ПРИЗОВОЙ ФОНД")
        yy+=35
        items=["10 000 000 юаней","Игровой предмет","Заказать музыку","Секретный приз"]
        for t in items:
            p.setPen(QColor("#ffbcff")); p.setFont(QFont("Arial",15,QFont.Bold)); p.drawText(x+28,yy,t); yy+=42
    def wheel(self,p,c,r):
        n=4
        labels=["10 000 000\nЮАНЕЙ","ИГРОВОЙ\nПРЕДМЕТ","ЗАКАЗАТЬ\nМУЗЫКУ","СЕКРЕТНЫЙ\nПРИЗ"]
        cols=["#f01d1d","#1256ff","#f20cff","#8b1cff"]
        for i in range(14,0,-1):
            p.setPen(QPen(QColor(220,35,255,max(10,55-i*3)),i*3)); p.setBrush(Qt.NoBrush); p.drawEllipse(c,r+i*3,r+i*3)
        p.setPen(QPen(QColor("#eeb3ff"),7)); p.setBrush(QColor("#170321")); p.drawEllipse(c,r+7,r+7)
        span=90; rect=QRectF(c.x()-r,c.y()-r,2*r,2*r)
        for i in range(n):
            start=i*span+self.model.angle
            p.setBrush(QColor(cols[i])); p.setPen(QPen(QColor("#ffbaff"),4))
            p.drawPie(rect,int((90-start-span)*16),int(span*16))
            a=math.radians(90-(start+span/2)); tx=c.x()+math.cos(a)*r*.58; ty=c.y()-math.sin(a)*r*.58
            p.save(); p.translate(tx,ty); p.rotate(-(start+span/2))
            p.setPen(QColor("#ffffff")); p.setFont(QFont("Arial",max(13,int(r*.045)),QFont.Bold))
            p.drawText(QRectF(-r*.25,-r*.14,r*.50,r*.28),Qt.AlignCenter|Qt.TextWordWrap,labels[i])
            p.restore()
        p.setBrush(QColor("#ff42ff")); p.setPen(QPen(QColor("#fff"),2))
        for a in [45,135,225,315]:
            rad=math.radians(a); x=c.x()+math.cos(rad)*(r+17); y=c.y()+math.sin(rad)*(r+17)
            p.drawPolygon([QPointF(x,y-14),QPointF(x+14,y),QPointF(x,y+14),QPointF(x-14,y)])
        grad=QRadialGradient(c,r*.24); grad.setColorAt(0,QColor("#ff9cff")); grad.setColorAt(.45,QColor("#a314ff")); grad.setColorAt(1,QColor("#160022"))
        p.setBrush(QBrush(grad)); p.setPen(QPen(QColor("#ffd0ff"),6)); p.drawEllipse(c,r*.22,r*.22)
        p.setPen(QColor("#ffffff")); p.setFont(QFont("Arial",45,QFont.Bold))
        p.drawText(QRectF(c.x()-r*.18,c.y()-r*.14,r*.36,r*.28),Qt.AlignCenter,"?")
    def pointer(self,p,x,y):
        pts=[QPointF(x,y-16),QPointF(x-24,y+40),QPointF(x,y+28),QPointF(x+24,y+40)]
        p.setBrush(QColor("#ff35ff")); p.setPen(QPen(QColor("#ffffff"),4)); p.drawPolygon(pts)

    def draw_button(self,p,r):
        for i in range(10,0,-1): p.setPen(QPen(QColor(225,35,255,45),i*2)); p.setBrush(Qt.NoBrush); p.drawRoundedRect(r.adjusted(-i,-i,i,i),20,20)
        g=QLinearGradient(r.topLeft(),r.bottomRight()); g.setColorAt(0,QColor("#e841ff")); g.setColorAt(.5,QColor("#8c18ff")); g.setColorAt(1,QColor("#30005f"))
        p.setBrush(g); p.setPen(QPen(QColor("#ffd4ff"),4)); p.drawRoundedRect(r,20,20)
        p.setPen(QColor("#fff")); p.setFont(QFont("Arial",32,QFont.Bold)); p.drawText(r,Qt.AlignCenter,"К Р У Т И Т Ь")

if __name__=="__main__":
    app=QApplication(sys.argv); app.setStyle("Fusion"); w=Roulette(); w.show(); sys.exit(app.exec())
