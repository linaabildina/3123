import sys, random
from pathlib import Path
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, Property, QPointF
from PySide6.QtGui import QPainter, QPixmap, QTransform, QColor, QPolygonF
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox

ROOT = Path(sys._MEIPASS) if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS") else Path(__file__).resolve().parent

BG = ROOT / "roulette_background.jpg"
WHEEL = ROOT / "wheel_layer.webp"

PRIZES = [
    "10 000 000 юаней",
    "Игровой предмет",
    "Заказать музыку",
    "Секретный приз",
]


class Roulette(QWidget):
    angleChanged = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Perfect World — Розыгрыш | Колесо Фортуны")
        self.setMinimumSize(1200, 675)
        self.resize(1672, 941)
        self.bg = QPixmap(str(BG))
        self.wheel = QPixmap(str(WHEEL))
        self.angle = 0.0
        self.anim = None
        self.busy = False
        self.button_rect = None
        self.setStyleSheet("background:#090012;")

    def fit_background(self, pixmap):
        if pixmap.isNull():
            return QPixmap()
        return pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        bg = self.fit_background(self.bg)
        if not bg.isNull():
            p.drawPixmap((self.width() - bg.width()) // 2, (self.height() - bg.height()) // 2, bg)
        else:
            p.fillRect(self.rect(), QColor("#12001f"))

        if not self.wheel.isNull():
            size = int(min(self.height() * 0.61, self.width() * 0.40))
            wheel = self.wheel.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            rotated = wheel.transformed(QTransform().rotate(self.angle), Qt.SmoothTransformation)
            cx = self.width() * 0.494
            cy = self.height() * 0.505
            p.drawPixmap(int(cx - rotated.width() / 2), int(cy - rotated.height() / 2), rotated)

            # Fixed pointer: it stays at the top while the wheel rotates underneath it.
            pointer_x = int(cx)
            pointer_y = int(cy - size / 2 - 8)
            glow = QPolygonF([
                QPointF(pointer_x, pointer_y - 8),
                QPointF(pointer_x - 22, pointer_y - 42),
                QPointF(pointer_x + 22, pointer_y - 42),
            ])
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 70, 235, 80))
            p.drawPolygon(glow)
            pointer = QPolygonF([
                QPointF(pointer_x, pointer_y + 10),
                QPointF(pointer_x - 14, pointer_y - 18),
                QPointF(pointer_x + 14, pointer_y - 18),
            ])
            p.setBrush(QColor("#ff4de8"))
            p.drawPolygon(pointer)
            p.setPen(QColor("#fff0ff"))
            p.drawPolyline(QPolygonF([
                (pointer_x, pointer_y + 10),
                (pointer_x - 14, pointer_y - 18),
                (pointer_x + 14, pointer_y - 18),
                (pointer_x, pointer_y + 10),
            ]))

        bw = self.width() * 0.30
        bh = self.height() * 0.10
        cx = self.width() * 0.495
        cy = self.height() * 0.865
        self.button_rect = (cx - bw / 2, cy - bh / 2, bw, bh)
        p.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or not self.button_rect:
            return
        x, y, w, h = self.button_rect
        pos = event.position()
        if x <= pos.x() <= x + w and y <= pos.y() <= y + h:
            self.spin()

    def spin(self):
        if self.busy:
            return

        self.busy = True
        winner = random.randrange(len(PRIZES))
        sector = 360.0 / len(PRIZES)
        current = self.angle % 360
        target = (270.0 - (winner + 0.5) * sector) % 360
        delta = (target - current) % 360
        end = self.angle + random.randint(7, 10) * 360 + delta

        self.anim = QPropertyAnimation(self, b"roulette_angle")
        self.anim.setDuration(5600)
        self.anim.setStartValue(self.angle)
        self.anim.setEndValue(end)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.finished.connect(lambda: self.finish(winner))
        self.anim.start()

    def get_angle(self):
        return self.angle

    def set_angle(self, value):
        self.angle = float(value)
        self.angleChanged.emit()
        self.update()

    roulette_angle = Property(float, get_angle, set_angle, notify=angleChanged)

    def finish(self, winner):
        self.busy = False
        QMessageBox.information(self, "🎉 ПОЗДРАВЛЯЕМ!", f"Вам выпало:\n\n{PRIZES[winner]}")
        self.update()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Roulette()
    window.show()
    sys.exit(app.exec())
