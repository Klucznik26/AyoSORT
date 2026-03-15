import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .drop_area import DropArea
from .image_fan import ImageFan


def build_ui(window):
    central_widget = QWidget()
    central_widget.setObjectName("main_widget")
    window.setCentralWidget(central_widget)

    window.main_layout = QHBoxLayout(central_widget)
    window.main_layout.setContentsMargins(10, 10, 10, 10)
    window.main_layout.setSpacing(10)

    _build_narrow_panel(window)
    _build_sidebar_panel(window)
    _build_workspace_panel(window)

    window.main_layout.addWidget(window.narrow_panel)
    window.main_layout.addWidget(window.left_panel)
    window.main_layout.addWidget(window.right_panel, 1)

    window.key_map = {
        Qt.Key.Key_1: "good",
        Qt.Key.Key_2: "mid",
        Qt.Key.Key_3: "bad",
    }


def _add_shadow(widget):
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(30)
    shadow.setOffset(0, 6)
    widget.setGraphicsEffect(shadow)


def _build_narrow_panel(window):
    window.narrow_panel = QFrame()
    window.narrow_panel.setObjectName("narrowPanel")
    window.narrow_panel.setFixedWidth(60)
    _add_shadow(window.narrow_panel)

    layout = QVBoxLayout(window.narrow_panel)
    layout.setContentsMargins(0, 20, 0, 20)
    layout.setSpacing(20)

    window.btn_narrow_logo = QPushButton()
    window.btn_narrow_logo.setObjectName("iconButton")
    window.btn_narrow_logo.setCursor(Qt.CursorShape.PointingHandCursor)

    assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    logo_path = os.path.join(assets_dir, "ASORT.png")
    if os.path.exists(logo_path):
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            window.btn_narrow_logo.setIcon(QIcon(pixmap))
            window.btn_narrow_logo.setIconSize(QSize(40, 40))
    else:
        window.btn_narrow_logo.setText("ⓘ")

    window.btn_narrow_logo.clicked.connect(window.show_info_window)
    layout.addWidget(window.btn_narrow_logo)

    layout.addStretch()

    window.btn_narrow_lang = QPushButton("🌐\uFE0E")
    window.btn_narrow_lang.setObjectName("iconButton")
    window.btn_narrow_lang.setCursor(Qt.CursorShape.PointingHandCursor)
    window.btn_narrow_lang.clicked.connect(window.show_language_window)
    layout.addWidget(window.btn_narrow_lang)

    window.btn_narrow_settings = QPushButton("⚙")
    window.btn_narrow_settings.setObjectName("iconButton")
    window.btn_narrow_settings.setCursor(Qt.CursorShape.PointingHandCursor)
    window.btn_narrow_settings.clicked.connect(window.show_theme_window)
    layout.addWidget(window.btn_narrow_settings)

    window.btn_narrow_close = QPushButton("⏻")
    window.btn_narrow_close.setObjectName("iconButton")
    window.btn_narrow_close.setProperty("danger", True)
    window.btn_narrow_close.setCursor(Qt.CursorShape.PointingHandCursor)
    window.btn_narrow_close.clicked.connect(window.close)
    layout.addWidget(window.btn_narrow_close)

    for btn in (
        window.btn_narrow_logo,
        window.btn_narrow_lang,
        window.btn_narrow_settings,
        window.btn_narrow_close,
    ):
        btn.setFixedSize(44, 44)


def _build_sidebar_panel(window):
    window.left_panel = QFrame()
    window.left_panel.setObjectName("leftPanel")
    window.left_panel.setFixedWidth(220)
    _add_shadow(window.left_panel)

    left_layout = QVBoxLayout(window.left_panel)
    left_layout.setContentsMargins(10, 15, 10, 10)
    left_layout.setSpacing(8)

    window.btn_create_catalog = QPushButton(window.tr("btn_create_catalog"))
    window.btn_create_catalog.setObjectName("runButton")
    window.btn_create_catalog.setFixedHeight(52)
    window.btn_create_catalog.clicked.connect(window.create_sorting_catalog)
    left_layout.addWidget(window.btn_create_catalog)

    window.btn_select_folder = QPushButton(window.tr("btn_select_folder"))
    window.btn_select_folder.setObjectName("runButton")
    window.btn_select_folder.setFixedHeight(52)
    window.btn_select_folder.clicked.connect(window.select_folder_to_sort)
    left_layout.addWidget(window.btn_select_folder)

    sort_btns_layout = QHBoxLayout()
    sort_btns_layout.setSpacing(6)

    window.btn_good = QPushButton("✓")
    window.btn_good.setToolTip(window.tr("tooltip_good"))
    window.btn_good.clicked.connect(lambda: window.sort_current("good"))
    sort_btns_layout.addWidget(window.btn_good)

    window.btn_mid = QPushButton("◐")
    window.btn_mid.setToolTip(window.tr("tooltip_mid"))
    window.btn_mid.clicked.connect(lambda: window.sort_current("mid"))
    sort_btns_layout.addWidget(window.btn_mid)

    window.btn_bad = QPushButton("✕")
    window.btn_bad.setToolTip(window.tr("tooltip_bad"))
    window.btn_bad.clicked.connect(lambda: window.sort_current("bad"))
    sort_btns_layout.addWidget(window.btn_bad)

    for btn in (window.btn_good, window.btn_mid, window.btn_bad):
        f = btn.font()
        f.setPointSize(18)
        btn.setFont(f)

    left_layout.addLayout(sort_btns_layout)

    window.label_info_create = QLabel(window.tr("label_info_create"))
    window.label_info_create.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.label_info_create.setFixedHeight(48)
    window.label_info_create.setProperty("secondary", "true")
    left_layout.addWidget(window.label_info_create)

    window.label_info_select = QLabel(window.tr("label_info_select"))
    window.label_info_select.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.label_info_select.setFixedHeight(48)
    window.label_info_select.setProperty("secondary", "true")
    left_layout.addWidget(window.label_info_select)

    left_layout.addStretch()


def _build_workspace_panel(window):
    window.right_panel = QFrame()
    window.right_panel.setObjectName("rightPanel")
    _add_shadow(window.right_panel)

    content_layout = QHBoxLayout(window.right_panel)
    content_layout.setContentsMargins(10, 10, 10, 10)
    content_layout.setSpacing(10)

    window.drop_area = DropArea(on_drop_callback=window.handle_drop)
    window.drop_area.setObjectName("dropArea")
    window.drop_area.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
    content_layout.addWidget(window.drop_area, 1)

    side_layout = QVBoxLayout()
    side_layout.setContentsMargins(0, 0, 0, 0)
    side_layout.setSpacing(8)
    side_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

    side_layout.addSpacing(20)
    window.image_fan = ImageFan()
    side_layout.addWidget(window.image_fan, alignment=Qt.AlignmentFlag.AlignHCenter)

    window.file_count_label = QLabel("")
    window.file_count_label.setObjectName("fileCountLabel")
    window.file_count_label.setFixedSize(122, 30)
    window.file_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.file_count_label.setVisible(False)
    side_layout.addWidget(window.file_count_label, alignment=Qt.AlignmentFlag.AlignHCenter)

    side_layout.addStretch()

    window.mini_logo = QLabel()
    window.mini_logo.setObjectName("cornerLogo")
    window.mini_logo.setFixedSize(150, 150)
    window.mini_logo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
    window.load_logo()
    side_layout.addWidget(window.mini_logo)

    content_layout.addLayout(side_layout)
