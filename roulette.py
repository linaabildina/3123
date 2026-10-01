import sys, random
from pathlib import Path
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, Property, QPointF, QRectF
from PySide6.QtGui import QPainter, QPixmap, QTransform, QColor, QPolygonF, QFont, QLinearGradient, QPen
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

    def draw_panel(self, p, rect, title, lines):
        x, y, w, h = rect
        p.save()
        p.setPen(QPen(QColor(255, 174, 238, 185), 2))
        p.setBrush(QColor(20, 5, 45, 195))
        p.drawRoundedRect(QRectF(x, y, w, h), 18, 18)

        inner = QRectF(x + 3, y + 3, w - 6, h - 6)
        p.setPen(QPen(QColor(137, 65, 221, 150), 1))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(inner, 15, 15)

        p.setFont(QFont("Arial", 16, QFont.Bold))
        p.setPen(QColor("#ffd7fb"))
        p.drawText(QRectF(x + 18, y + 15, w - 36, 30), Qt.AlignCenter, title)

        p.setPen(QColor(255, 255, 255, 225))
        p.setFont(QFont("Arial", 12, QFont.Bold))
        yy = y + 58
        for line in lines:
            p.drawText(QRectF(x + 18, yy, w - 36, 25), Qt.AlignLeft | Qt.AlignVCenter, line)
            yy += 27
        p.restore()

    def paint_button(self, p, rect):
        x, y, w, h = rect
        p.save()
        # glow
        for pad, alpha in [(16, 25), (10, 40), (5, 65)]:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 55, 224, alpha))
            p.drawRoundedRect(QRectF(x - pad, y - pad / 2, w + pad * 2, h + pad), 18, 18)

        grad = QLinearGradient(x, y, x, y + h)
        grad.setColorAt(0.0, QColor("#ff68ed"))
        grad.setColorAt(0.5, QColor("#bd38e8"))
        grad.setColorAt(1.0, QColor("#7a1fc5"))
        p.setBrush(grad)
        p.setPen(QPen(QColor("#ffe8ff"), 2))
        p.drawRoundedRect(QRectF(x, y, w, h), 16, 16)

        p.setFont(QFont("Arial", 20, QFont.Bold))
        p.setPen(QColor("#ffffff"))
        p.drawText(QRectF(x, y, w, h), Qt.AlignCenter, "КРУТИТЬ")
        p.restore()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        bg = self.fit_background(self.bg)
        if not bg.isNull():
            p.drawPixmap((self.width() - bg.width()) // 2, (self.height() - bg.height()) // 2, bg)
        else:
            p.fillRect(self.rect(), QColor("#12001f"))

        # Dark vignette keeps the central wheel readable while preserving the fantasy artwork.
        vignette = QLinearGradient(0, 0, self.width(), 0)
        vignette.setColorAt(0.0, QColor(5, 0, 18, 165))
        vignette.setColorAt(0.22, QColor(5, 0, 18, 60))
        vignette.setColorAt(0.72, QColor(5, 0, 18, 25))
        vignette.setColorAt(1.0, QColor(5, 0, 18, 125))
        p.fillRect(self.rect(), vignette)

        # Left information cards from the reference layout.
        side_w = self.width() * 0.19
        self.draw_panel(
            p,
            (self.width() * 0.025, self.height() * 0.22, side_w, self.height() * 0.25),
            "КАК УЧАСТВОВАТЬ?",
            ["1. Нажми «КРУТИТЬ»", "2. Дождись остановки", "3. Забери свой приз!"],
        )
        self.draw_panel(
            p,
            (self.width() * 0.025, self.height() * 0.51, side_w, self.height() * 0.23),
            "ПРИЗОВОЙ ФОНД",
            ["💸 10 000 000 юаней", "🎁 Игровой предмет", "🎵 Заказать музыку", "🎁 Секретный приз"],
        )

        # Right-side branding.
        p.save()
        rx = self.width() * 0.80
        p.setPen(QColor(255, 222, 255, 235))
        p.setFont(QFont("Arial", 17, QFont.Bold))
        p.drawText(QRectF(rx, self.height() * 0.69, self.width() * 0.17, 30), Qt.AlignCenter, "PERFECT WORLD")
        p.setPen(QColor(255, 126, 235, 245))
        p.setFont(QFont("Arial", 23, QFont.Bold))
        p.drawText(QRectF(rx, self.height() * 0.73, self.width() * 0.17, 38), Qt.AlignCenter, "COMEBACK")
        p.setPen(QColor(255, 220, 255, 180))
        p.setFont(QFont("Arial", 10))
        p.drawText(QRectF(rx, self.height() * 0.78, self.width() * 0.17, 24), Qt.AlignCenter, "КОЛЕСО ФОРТУНЫ")
        p.restore()

        if not self.wheel.isNull():
            size = int(min(self.height() * 0.61, self.width() * 0.40))
            wheel = self.wheel.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            rotated = wheel.transformed(QTransform().rotate(self.angle), Qt.SmoothTransformation)
            cx = self.width() * 0.494
            cy = self.height() * 0.505
            p.drawPixmap(int(cx - rotated.width() / 2), int(cy - rotated.height() / 2), rotated)

            # Fixed pointer at the top.
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
            p.setPen(QPen(QColor("#fff0ff"), 2))
            p.drawPolyline(QPolygonF([
                QPointF(pointer_x, pointer_y + 10),
                QPointF(pointer_x - 14, pointer_y - 18),
                QPointF(pointer_x + 14, pointer_y - 18),
                QPointF(pointer_x, pointer_y + 10),
            ]))

        # Bottom central action button. No countdown/time is shown.
        bw = self.width() * 0.23
        bh = self.height() * 0.085
        cx = self.width() * 0.495
        cy = self.height() * 0.88
        self.button_rect = (cx - bw / 2, cy - bh / 2, bw, bh)
        self.paint_button(p, self.button_rect)

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
