"""
Motyw Systemowy (Native Palette)
"""

_MAIN_STYLE = """
/* =========================
   MOTYW SYSTEMOWY
   ========================= */

QMainWindow {
    background-color: palette(window);
}

QDialog {
    background-color: palette(window);
}

/* =========================
   RAMKI / PANELE
   ========================= */
QFrame {
    background-color: palette(window);
    border: 1px solid palette(mid);
}

/* =========================
   TEKST
   ========================= */
QLabel {
    color: palette(windowText);
}

QLabel[secondary="true"] {
    color: palette(text);
}

QLabel#scaleLabel {
    color: palette(windowText);
}

QLabel#statusLabel {
    color: palette(text);
    font-weight: bold;
    font-size: 13px;
}

/* =========================
   PRZYCISKI
   ========================= */
QPushButton {
    padding: 8px 14px;
    background-color: palette(button);
    border: 1px solid palette(mid);
    border-radius: 6px;
    color: palette(buttonText);
    font-weight: bold;
}

QPushButton:hover {
    background-color: palette(light);
}

QPushButton:pressed {
    background-color: palette(midlight);
}

QPushButton:disabled {
    background-color: palette(window);
    color: palette(disabled:buttonText);
    border: 1px solid palette(mid);
}

/* =========================
   PRZYCISK WYKONAJ (AKCENT)
   ========================= */
QPushButton#runButton {
    background-color: palette(highlight);
    border: none;
    color: palette(highlightedText);
}

QPushButton#runButton:hover {
    background-color: palette(highlight);
}

QPushButton#runButton:pressed {
    background-color: palette(dark);
}

/* =========================
   SUWAK SKALI
   ========================= */
QSlider::groove:horizontal {
    height: 6px;
    background: palette(mid);
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: palette(button);
    width: 16px;
    margin: -5px 0;
    border-radius: 8px;
    border: 1px solid palette(mid);
}

QSlider::sub-page:horizontal {
    background: palette(highlight);
    border-radius: 3px;
}

QSlider::add-page:horizontal {
    background: palette(mid);
    border-radius: 3px;
}

/* =========================
   KONTROLKI FORMULARZY
   ========================= */
QComboBox {
    background-color: palette(button);
    color: palette(buttonText);
    border: 1px solid palette(mid);
    padding: 4px;
}

QComboBox::drop-down {
    border: none;
}

QListView, QTreeView {
    background-color: palette(base);
    color: palette(text);
    border: 1px solid palette(mid);
}
"""

_DROP_ZONE_STYLE = """
    QLabel#dropArea {
        background-color: palette(base);
        border: 2px dashed palette(mid);
        border-radius: 10px;
        color: palette(text);
        font-size: 18px;
    }
"""

theme = _MAIN_STYLE + "\n" + _DROP_ZONE_STYLE