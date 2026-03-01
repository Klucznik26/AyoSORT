"""
Motyw Jasny (Beige & Brown)
"""

_MAIN_STYLE = """
/* =========================
   MOTYW JASNY
   ========================= */

QMainWindow {
    background-color: #EFE6D6;
}

QDialog {
    background-color: #EFE6D6;
}

/* =========================
   RAMKI / PANELE
   ========================= */
QFrame {
    background-color: #F6F0E6;
    border: 1px solid #B8A890;
}

/* =========================
   TEKST
   ========================= */
QLabel {
    color: #3A2E24;
}

QLabel[secondary="true"] {
    color: #9C8F80;
}

QLabel#scaleLabel {
    color: #3A2E24;
}

QLabel#statusLabel {
    color: #000000;
    font-weight: bold;
    font-size: 13px;
}

/* =========================
   PRZYCISKI
   ========================= */
QPushButton {
    padding: 8px 14px;
    background-color: #E3D8C6;
    border: 1px solid #B8A890;
    border-radius: 6px;
    color: #3A2E24;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #D6C9B5;
}

QPushButton:pressed {
    background-color: #CBBDA7;
}

QPushButton:disabled {
    background-color: #E0D6C8;
    color: #9C8F80;
    border: 1px solid #C4B8A5;
}

/* =========================
   PRZYCISK WYKONAJ (AKCENT)
   ========================= */
QPushButton#runButton {
    background-color: #3A2E24;
    border: none;
    color: #EFE6D6;
}

QPushButton#runButton:hover {
    background-color: #4E3D30;
}

QPushButton#runButton:pressed {
    background-color: #2B221B;
}

/* =========================
   SUWAK SKALI
   ========================= */
QSlider::groove:horizontal {
    height: 6px;
    background: #B8A890;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #3A2E24;
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
}

QSlider::sub-page:horizontal {
    background: #3A2E24;
    border-radius: 3px;
}

QSlider::add-page:horizontal {
    background: #B8A890;
    border-radius: 3px;
}

/* =========================
   KONTROLKI FORMULARZY
   ========================= */
QComboBox {
    background-color: #E3D8C6;
    color: #3A2E24;
    border: 1px solid #B8A890;
    padding: 4px;
}

QComboBox::drop-down {
    border: none;
}

QListView, QTreeView {
    background-color: #F6F0E6;
    color: #3A2E24;
    border: 1px solid #B8A890;
}
"""

_DROP_ZONE_STYLE = """
    QLabel#dropArea {
        background-color: #F6F0E6;
        border: 2px dashed #B8A890;
        border-radius: 10px;
        color: #3A2E24;
        font-size: 18px;
    }
"""

theme = _MAIN_STYLE + "\n" + _DROP_ZONE_STYLE