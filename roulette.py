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
        return max(0,float(self.cfg.get("cooldown_hours",24))*3600-(time.time()-float(self.state.get("last_spin",0))))

    def mousePressEvent(self,e):
        if e.button()==Qt.LeftButton and self.button.contains(e.position()): self.spin()

    def spin(self):
        if self.busy:return
        left=self.remaining()
        if left:
            h=int(left//3600); m=int(left%3600//60); s=int(left%60)
            QMessageBox.information(self,"Крутка недоступна",f"Следующая крутка через {h:02d}:{m:02d}:{s:02d}")
            return
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
        cx=self.width()*.66; cy=self.height()*.46; r=min(self.height()*.39,self.width()*.34)
        self.info(p)
        self.wheel(p,QPointF(cx,cy),r)
        self.pointer(p,cx,cy-r-8)
        bw=min(460,self.width()*.31); self.button=QRectF(cx-bw/2,cy+r*.82,bw,82); self.draw_button(p,self.button)
        left=self.remaining()
        txt="КРУТКА ДОСТУПНА" if not left else f"СЛЕДУЮЩАЯ КРУТКА  {int(left//3600):02d}:{int(left%3600//60):02d}:{int(left%60):02d}"
        p.setPen(QColor("#ffd9ff")); p.setFont(QFont("Arial",14,QFont.Bold))
        p.drawText(QRectF(cx-280,cy+r*.99,560,30),Qt.AlignCenter,txt); p.end()

    def background(self,p):
        g=QLinearGradient(0,0,self.width(),self.height()); g.setColorAt(0,QColor("#100020")); g.setColorAt(.5,QColor("#28004f")); g.setColorAt(1,QColor("#07000f")); p.fillRect(self.rect(),QBrush(g))
        for i in range(34):
            x=(i*137)%self.width(); y=(i*83)%self.height(); p.setPen(Qt.NoPen); p.setBrush(QColor(220,70,255,45)); p.drawEllipse(QPointF(x,y),3+(i%5),3+(i%5))
        p.setPen(QPen(QColor(185,52,255,90),2))
        for x in range(0,self.width(),140):
            p.drawLine(x,self.height(),x-120,self.height()*.65)
        # title
        p.setPen(QColor("#ffffff")); p.setFont(QFont("Arial",34,QFont.Bold))
        p.drawText(48,72,"РОЗЫГРЫШ")
        p.setPen(QColor("#df59ff")); p.setFont(QFont("Arial",18,QFont.Bold))
        p.drawText(51,102,"КОЛЕСО ФОРТУНЫ  •  PERFECT WORLD")

    def info(self,p):
        x,y,w,h=38,150,370,415; r=QRectF(x,y,w,h)
        p.setBrush(QColor(8,2,24,220)); p.setPen(QPen(QColor("#cf4cff"),2)); p.drawRoundedRect(r,18,18)
        p.setPen(QColor("#f0baff")); p.setFont(QFont("Arial",19,QFont.Bold)); p.drawText(x+24,y+38,"КАК УЧАСТВОВАТЬ?")
        lines=["▶  Подпишись на канал","💬  Напиши комментарий","❤  Поставь лайк","","🎁  Одна крутка каждые 24 часа","✨  Приз определяется случайно"]
        p.setPen(QColor("#fff")); p.setFont(QFont("Arial",14))
        yy=y+82
        for s in lines: p.drawText(x+25,yy,s); yy+=43
        p.setPen(QColor("#e99aff")); p.setFont(QFont("Arial",13,QFont.Bold)); p.drawText(x+24,y+h-42,"ПРИЗОВ: "+str(len(self.prizes)))

    def wheel(self,p,c,r):
        n=len(self.prizes)
        if not n:return
        for i in range(12,0,-1):
            p.setPen(QPen(QColor(235,45,255,max(8,50-i*3)),i*3)); p.setBrush(Qt.NoBrush); p.drawEllipse(c,r+i*3,r+i*3)
        p.setPen(QPen(QColor("#f1a8ff"),6)); p.setBrush(QColor("#130321")); p.drawEllipse(c,r+6,r+6)
        span=360/n; rect=QRectF(c.x()-r,c.y()-r,2*r,2*r)
        for i,item in enumerate(self.prizes):
            start=i*span+self.model.angle; col=QColor(item.get("color","#7a1cff"))
            p.setBrush(col); p.setPen(QPen(QColor("#ffb8ff"),3)); p.drawPie(rect,int((90-start-span)*16),int(span*16))
            a=math.radians(-(start+span/2)+90); tx=c.x()+math.cos(a)*r*.63; ty=c.y()-math.sin(a)*r*.63
            p.save(); p.translate(tx,ty); p.rotate(-(start+span/2)); p.setPen(QColor("#fff")); p.setFont(QFont("Arial",max(11,int(r*.045)),QFont.Bold))
            p.drawText(QRectF(-r*.22,-r*.12,r*.44,r*.24),Qt.AlignCenter|Qt.TextWordWrap,item["name"]); p.restore()
        grad=QRadialGradient(c,r*.23); grad.setColorAt(0,QColor("#ff8cff")); grad.setColorAt(.4,QColor("#8b13ff")); grad.setColorAt(1,QColor("#150024"))
        p.setBrush(grad); p.setPen(QPen(QColor("#ffd0ff"),5)); p.drawEllipse(c,r*.21,r*.21)
        p.setPen(QColor("#fff")); p.setFont(QFont("Arial",int(r*.10),QFont.Bold)); p.drawText(QRectF(c.x()-r*.18,c.y()-r*.13,r*.36,r*.26),Qt.AlignCenter,"?")

    def pointer(self,p,x,y):
        pts=[QPointF(x,y-16),QPointF(x-24,y+40),QPointF(x,y+28),QPointF(x+24,y+40)]
        p.setBrush(QColor("#ff39ff")); p.setPen(QPen(QColor("#fff"),3)); p.drawPolygon(pts)

    def draw_button(self,p,r):
        for i in range(10,0,-1): p.setPen(QPen(QColor(225,35,255,45),i*2)); p.setBrush(Qt.NoBrush); p.drawRoundedRect(r.adjusted(-i,-i,i,i),20,20)
        g=QLinearGradient(r.topLeft(),r.bottomRight()); g.setColorAt(0,QColor("#e841ff")); g.setColorAt(.5,QColor("#8c18ff")); g.setColorAt(1,QColor("#30005f"))
        p.setBrush(g); p.setPen(QPen(QColor("#ffd4ff"),4)); p.drawRoundedRect(r,20,20)
        p.setPen(QColor("#fff")); p.setFont(QFont("Arial",29,QFont.Bold)); p.drawText(r,Qt.AlignCenter,"К Р У Т И Т Ь")

if __name__=="__main__":
    app=QApplication(sys.argv); app.setStyle("Fusion"); w=Roulette(); w.show(); sys.exit(app.exec())
