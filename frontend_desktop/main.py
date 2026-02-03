import sys
import requests
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QMessageBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QScrollArea, QSizePolicy,
                             QGraphicsOpacityEffect, QProgressBar)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/api/upload/"

# --- Styling (QSS) ---
STYLESHEET = """
QMainWindow {
    background-color: #f8fafc;
}

/* --- SCROLL AREA FIX --- */
QScrollArea {
    border: none;
    background-color: #f8fafc;
}
/* IMPORTANT: This must be solid, not transparent, to fix the scroll glitch */
QWidget#ScrollContent {
    background-color: #f8fafc; 
}

/* --- Loading Overlay --- */
QFrame#LoadingOverlay {
    background-color: #f8fafc;
    border: none;
}
QLabel#LoadingText {
    color: #4f46e5;
    font-size: 18px;
    font-weight: bold;
}
QProgressBar {
    border: none;
    background-color: #e2e8f0;
    border-radius: 4px;
    height: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #4f46e5;
    border-radius: 4px;
}

/* --- Header --- */
QLabel#HeaderTitle {
    font-size: 28px;
    font-weight: 800;
    color: #1e293b;
    font-family: 'Segoe UI', sans-serif;
    background-color: transparent;
}
QLabel#HeaderSubtitle {
    font-size: 14px;
    color: #64748b;
    font-family: 'Segoe UI', sans-serif;
    background-color: transparent;
}

/* --- Cards --- */
QFrame#Card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
}

/* --- Buttons --- */
QPushButton {
    background-color: #4f46e5;
    color: white;
    font-size: 15px;
    font-weight: bold;
    padding: 15px 30px;
    border-radius: 10px;
    border: none;
}
QPushButton:hover {
    background-color: #4338ca;
}
QPushButton:pressed {
    background-color: #3730a3;
    padding-top: 17px;
}

/* --- Stats --- */
QFrame#StatBox {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
QLabel#StatTitle { 
    color: #64748b; 
    font-size: 11px; 
    font-weight: bold; 
    text-transform: uppercase;
    background-color: transparent;
}
QLabel#StatValue { 
    color: #4f46e5; 
    font-size: 32px; 
    font-weight: 800; 
    background-color: transparent;
}

/* --- Table --- */
QTableWidget {
    background-color: white;
    gridline-color: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    font-size: 13px;
    color: #334155;
    padding: 10px;
}
QHeaderView::section {
    background-color: white;
    color: #64748b;
    padding: 12px;
    border: none;
    border-bottom: 2px solid #e2e8f0;
    font-weight: bold;
    text-transform: uppercase;
    font-size: 11px;
}
"""

class StatCard(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setObjectName("StatBox")
        self.setFixedHeight(120)
        # Force background paint
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        t_label = QLabel(title)
        t_label.setObjectName("StatTitle")
        t_label.setAlignment(Qt.AlignCenter)
        
        v_label = QLabel(str(value))
        v_label.setObjectName("StatValue")
        v_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(t_label)
        layout.addWidget(v_label)

class ChemicalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.resize(1200, 900)
        self.setStyleSheet(STYLESHEET)

        # 1. Main Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Disable horizontal scroll
        self.setCentralWidget(self.scroll_area)

        # 2. Scroll Content Widget (THE FIX: Solid Background)
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("ScrollContent")
        self.scroll_content.setAutoFillBackground(True) # Force paint
        self.scroll_area.setWidget(self.scroll_content)

        # 3. Root Layout
        self.root_layout = QVBoxLayout(self.scroll_content)
        self.root_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.root_layout.setContentsMargins(0, 40, 0, 40)

        # 4. Main Container
        self.container = QWidget()
        self.container.setObjectName("MainContainer")
        self.container.setFixedWidth(1000)
        self.root_layout.addWidget(self.container)

        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(25)

        # --- UI ELEMENTS ---
        self.init_header()
        self.init_upload_hero()
        
        self.stats_container = QWidget()
        self.stats_layout = QHBoxLayout(self.stats_container)
        self.stats_layout.setSpacing(20)
        self.layout.addWidget(self.stats_container)
        self.stats_container.hide()

        self.chart_frame = QFrame()
        self.chart_frame.setObjectName("Card")
        self.chart_frame.setFixedHeight(450)
        self.chart_layout = QVBoxLayout(self.chart_frame)
        self.chart_layout.setContentsMargins(20, 20, 20, 20)
        
        self.figure, self.ax = plt.subplots(1, 2, figsize=(10, 4))
        self.figure.patch.set_facecolor('white')
        self.canvas = FigureCanvas(self.figure)
        self.chart_layout.addWidget(self.canvas)
        self.layout.addWidget(self.chart_frame)
        self.chart_frame.hide()

        self.table_label = QLabel("Raw Data Preview")
        self.table_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #334155; margin-top: 10px; background-color: transparent;")
        self.layout.addWidget(self.table_label)
        self.table_label.hide()

        self.table = QTableWidget()
        self.table.setMinimumHeight(600)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.layout.addWidget(self.table)
        self.table.hide()

        # --- LOADING OVERLAY (Added Feature) ---
        self.init_loading_overlay()

        # Simulate "Boot Up" (Manages painting time)
        QTimer.singleShot(500, self.finish_loading)

    def init_loading_overlay(self):
        """Creates a white screen that covers everything while the app paints."""
        self.loading_overlay = QFrame(self)
        self.loading_overlay.setObjectName("LoadingOverlay")
        self.loading_overlay.resize(1200, 900) # Full size
        
        l = QVBoxLayout(self.loading_overlay)
        l.setAlignment(Qt.AlignCenter)
        
        # Text
        self.loading_text = QLabel("Initializing Dashboard...")
        self.loading_text.setObjectName("LoadingText")
        self.loading_text.setAlignment(Qt.AlignCenter)
        
        # Bar
        self.progress = QProgressBar()
        self.progress.setFixedWidth(200)
        self.progress.setRange(0, 0) # Infinite loading animation
        
        l.addWidget(self.loading_text)
        l.addSpacing(15)
        l.addWidget(self.progress)
        
        self.loading_overlay.show()

    def finish_loading(self):
        """Fade out the loading screen once app is ready."""
        # 1. Force a repaint of the main window behind the scene
        self.scroll_content.repaint()
        
        # 2. Fade out animation
        self.anim = QPropertyAnimation(self.loading_overlay, b"windowOpacity")
        self.anim.setDuration(500)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.finished.connect(self.loading_overlay.hide)
        self.anim.start()

    # --- Standard App Logic ---
    def init_header(self):
        header_widget = QWidget()
        l = QVBoxLayout(header_widget)
        l.setAlignment(Qt.AlignCenter)
        title = QLabel("Chemical Analytics Dashboard")
        title.setObjectName("HeaderTitle")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Upload your CSV dataset to generate insights and visualizations")
        subtitle.setObjectName("HeaderSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        l.addWidget(title)
        l.addWidget(subtitle)
        self.layout.addWidget(header_widget)

    def init_upload_hero(self):
        self.upload_frame = QFrame()
        self.upload_frame.setObjectName("Card")
        l = QVBoxLayout(self.upload_frame)
        l.setAlignment(Qt.AlignCenter)
        l.setContentsMargins(40, 40, 40, 40)
        l.setSpacing(20)
        icon_label = QLabel("📂")
        icon_label.setStyleSheet("font-size: 48px; background-color: transparent;")
        icon_label.setAlignment(Qt.AlignCenter)
        self.upload_btn = QPushButton("Import CSV Dataset")
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setFixedWidth(250)
        self.upload_btn.clicked.connect(self.upload_file)
        l.addWidget(icon_label)
        l.addWidget(self.upload_btn)
        self.layout.addWidget(self.upload_frame)

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '.', "CSV Files (*.csv)")
        if fname:
            self.upload_btn.setText("Processing...")
            self.upload_btn.setEnabled(False)
            QApplication.processEvents()
            try:
                files = {'file': open(fname, 'rb')}
                response = requests.post(API_URL, files=files)
                if response.status_code == 200:
                    data = response.json()['data']
                    self.render_dashboard(data)
                    self.upload_btn.setText("Import New Dataset")
                else:
                    QMessageBox.critical(self, "Error", response.text)
                    self.upload_btn.setText("Import CSV Dataset")
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", str(e))
                self.upload_btn.setText("Import CSV Dataset")
            self.upload_btn.setEnabled(True)

    def render_dashboard(self, data):
        # Stats
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)
        stats = [
            ("Total Units", data['total_count']),
            ("Avg Flowrate", data['averages']['avg_flowrate']),
            ("Avg Pressure", data['averages']['avg_pressure']),
            ("Avg Temperature", data['averages']['avg_temperature'])
        ]
        for title, value in stats:
            card = StatCard(title, value)
            self.stats_layout.addWidget(card)

        # Charts
        self.ax[0].clear()
        self.ax[1].clear()
        
        dist = data['distribution']
        wedges, _, _ = self.ax[0].pie(
            dist.values(), autopct='%1.1f%%', 
            colors=['#6366f1', '#ec4899', '#eab308', '#22c55e', '#3b82f6'],
            startangle=90, textprops={'fontsize': 8, 'color': 'white'}
        )
        self.ax[0].legend(wedges, dist.keys(), loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), frameon=False)
        self.ax[0].set_title("Equipment Types", fontsize=10, fontweight='bold')

        metrics = ['Flowrate', 'Pressure', 'Temp']
        values = [data['averages']['avg_flowrate'], data['averages']['avg_pressure'], data['averages']['avg_temperature']]
        self.ax[1].bar(metrics, values, color=['#6366f1', '#ec4899', '#eab308'], width=0.5)
        self.ax[1].set_title("Average Metrics", fontsize=10, fontweight='bold')
        self.ax[1].grid(axis='y', linestyle='--', alpha=0.3)
        self.ax[1].spines['top'].set_visible(False)
        self.ax[1].spines['right'].set_visible(False)
        
        self.figure.subplots_adjust(wspace=1, left=0.05, right=0.95, top=0.9, bottom=0.1)
        self.canvas.draw()

        # Table
        rows = data['preview']
        if rows:
            columns = list(rows[0].keys())
            self.table.setColumnCount(len(columns))
            self.table.setRowCount(len(rows))
            self.table.setHorizontalHeaderLabels([c.upper() for c in columns])
            header = self.table.horizontalHeader()
            for i in range(len(columns)):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
            for i, row in enumerate(rows):
                for j, col in enumerate(columns):
                    item = QTableWidgetItem(str(row[col]))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)

        self.stats_container.show()
        self.chart_frame.show()
        self.table_label.show()
        self.table.show()

    def resizeEvent(self, event):
        """Keep loading overlay full size when resizing"""
        if hasattr(self, 'loading_overlay') and self.loading_overlay.isVisible():
            self.loading_overlay.resize(self.width(), self.height())
        super().resizeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    basedir = os.path.dirname(__file__)
    icon_path = os.path.join(basedir, 'assets', 'icon.jpeg')
    app.setWindowIcon(QIcon(icon_path))
    window = ChemicalApp()
    window.show()
    sys.exit(app.exec_())