import sys, random
from pathlib import Path

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, Property, QPointF
from PySide6.QtGui import QPainter, QPixmap, QTransform, QColor, QPolygonF, QPen
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox

ROOT = Path(sys._MEIPASS) if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS") else Path(__file__).resolve().parent

# The artwork is the visual source of truth. Interactive elements are drawn over it.
BG = ROOT / "reference_design.webp"
FALLBACK_BG = ROOT / "roulette_background.jpg"
WHEEL = ROOT / "reference_wheel.webp"
FALLBACK_WHEEL = ROOT / "wheel_layer.webp"

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
        self.setMinimumSize(1000, 563)
        self.resize(1672, 941)
        self.setStyleSheet("background:#090012;")

        bg_path = BG if BG.exists() else FALLBACK_BG
        wheel_path = WHEEL if WHEEL.exists() else FALLBACK_WHEEL

        self.bg = QPixmap(str(bg_path))
        self.wheel = QPixmap(str(wheel_path))

        self.angle = 0.0
        self.anim = None
        self.busy = False
        self.button_rect = None

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        if not self.bg.isNull():
            # The reference artwork is 16:9, so stretch to the window without
            # adding artificial panels, gradients or replacement branding.
            p.drawPixmap(self.rect(), self.bg)

        # Exact reference geometry at the native 1672x941 design size.
        sx = self.width() / 1672.0
        sy = self.height() / 941.0
        cx = 836.0 * sx
        cy = 500.0 * sy
        wheel_size = min(675.0 * sx, 675.0 * sy)

        if not self.wheel.isNull():
            wheel = self.wheel.scaled(
                int(wheel_size),
                int(wheel_size),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            rotated = wheel.transformed(
                QTransform().rotate(self.angle),
                Qt.SmoothTransformation,
            )
            p.drawPixmap(
                int(cx - rotated.width() / 2),
                int(cy - rotated.height() / 2),
                rotated,
            )

            # Fixed pointer: it never rotates with the wheel.
            px = int(cx)
            py = int(cy - wheel_size / 2 + 2)
            glow = QPolygonF([
                QPointF(px, py - 3),
                QPointF(px - 17 * sx, py - 31 * sy),
                QPointF(px + 17 * sx, py - 31 * sy),
            ])
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(255, 45, 230, 75))
            p.drawPolygon(glow)

            pointer = QPolygonF([
                QPointF(px, py + 9 * sy),
                QPointF(px - 10 * sx, py - 14 * sy),
                QPointF(px + 10 * sx, py - 14 * sy),
            ])
            p.setBrush(QColor("#ff4de8"))
            p.drawPolygon(pointer)
            p.setPen(QPen(QColor("#fff2ff"), max(1, int(2 * sx))))
            p.drawPolyline(QPolygonF([
                QPointF(px, py + 9 * sy),
                QPointF(px - 10 * sx, py - 14 * sy),
                QPointF(px + 10 * sx, py - 14 * sy),
                QPointF(px, py + 9 * sy),
            ]))

        # The button is already part of the reference artwork.
        # We only make its existing visual area clickable.
        self.button_rect = (
            510.0 * sx,
            750.0 * sy,
            575.0 * sx,
            125.0 * sy,
        )

        p.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton or self.button_rect is None:
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
        current = self.angle % 360.0

        # Pointer is at 12 o'clock.
        target = (270.0 - (winner + 0.5) * sector) % 360.0
        delta = (target - current) % 360.0
        end = self.angle + random.randint(7, 10) * 360.0 + delta

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
        QMessageBox.information(
            self,
            "🎉 ПОЗДРАВЛЯЕМ!",
            f"Вам выпало:\n\n{PRIZES[winner]}",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Roulette()
    window.show()
    sys.exit(app.exec())
