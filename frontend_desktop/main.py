import sys
import requests
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QMessageBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QFrame, QScrollArea, QTabWidget, 
                             QCheckBox, QGridLayout, QSplitter)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor

# --- Configuration ---
# Pointing to Localhost Backend
API_BASE = "http://127.0.0.1:8000/api/"

# --- Styling (Light & Dark Themes) ---
THEME_LIGHT = """
QMainWindow { background-color: #f8fafc; }
QTabWidget::pane { border: none; background: #f8fafc; }
QTabBar::tab { background: transparent; color: #64748b; padding: 10px 20px; font-weight: bold; font-size: 14px; }
QTabBar::tab:selected { color: #4f46e5; border-bottom: 2px solid #4f46e5; }
QFrame#Card { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; }
QLabel { color: #1e293b; }
QLabel#StatTitle { color: #64748b; font-weight: bold; font-size: 11px; text-transform: uppercase; }
QLabel#StatValue { color: #4f46e5; font-weight: 800; font-size: 28px; }
QLabel#SubStat { color: #64748b; font-size: 10px; }
QPushButton { background-color: #4f46e5; color: white; border-radius: 8px; padding: 10px; font-weight: bold; }
QPushButton:hover { background-color: #4338ca; }
QTableWidget { background-color: white; border: 1px solid #e2e8f0; gridline-color: #f1f5f9; color: #334155; }
QHeaderView::section { background-color: #f1f5f9; color: #64748b; border: none; padding: 8px; font-weight: bold; }
"""

THEME_DARK = """
QMainWindow { background-color: #0f172a; }
QTabWidget::pane { border: none; background: #0f172a; }
QTabBar::tab { color: #94a3b8; }
QTabBar::tab:selected { color: #818cf8; border-bottom: 2px solid #818cf8; }
QFrame#Card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }
QLabel { color: #f8fafc; }
QLabel#StatTitle { color: #94a3b8; }
QLabel#StatValue { color: #818cf8; }
QLabel#SubStat { color: #94a3b8; }
QPushButton { background-color: #4f46e5; color: white; }
QTableWidget { background-color: #1e293b; border: 1px solid #334155; color: #e2e8f0; gridline-color: #334155; }
QHeaderView::section { background-color: #0f172a; color: #94a3b8; border: none; }
"""

# --- Custom Components ---
class ProfessionalStatCard(QFrame):
    def __init__(self, title, unit, stats):
        super().__init__()
        self.setObjectName("Card")
        self.setFixedHeight(140)
        
        layout = QVBoxLayout(self)
        
        # Header
        top_layout = QHBoxLayout()
        t_label = QLabel(f"{title} ({unit})")
        t_label.setObjectName("StatTitle")
        top_layout.addWidget(t_label)
        layout.addLayout(top_layout)
        
        # Main Value
        v_label = QLabel(str(stats['avg']))
        v_label.setObjectName("StatValue")
        v_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(v_label)
        
        # Footer (Min/Max/Median)
        bot_layout = QHBoxLayout()
        for label, val in [("Min", stats['min']), ("Max", stats['max']), ("Med", stats['median'])]:
            sub = QLabel(f"{label}: {val}")
            sub.setObjectName("SubStat")
            bot_layout.addWidget(sub)
        layout.addLayout(bot_layout)

class ChemicalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Visualizer Pro")
        self.resize(1200, 850)
        self.dark_mode = False
        self.apply_theme()

        # Main Tab Widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create Tabs
        self.dashboard_tab = QWidget()
        self.history_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.history_tab, "History")
        self.tabs.addTab(self.settings_tab, "Settings")

        # Initialize UI
        self.init_dashboard()
        self.init_history()
        self.init_settings()
        
        # Connect tab change to refresh history
        self.tabs.currentChanged.connect(self.on_tab_change)

    def apply_theme(self):
        self.setStyleSheet(THEME_DARK if self.dark_mode else THEME_LIGHT)

    # --- TAB 1: DASHBOARD ---
    def init_dashboard(self):
        layout = QVBoxLayout(self.dashboard_tab)
        
        # Scroll Area for Dashboard
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content = QWidget()
        self.dash_layout = QVBoxLayout(content)
        
        # 1. Upload Section
        self.upload_frame = QFrame()
        self.upload_frame.setObjectName("Card")
        ul = QHBoxLayout(self.upload_frame)
        self.upload_btn = QPushButton("Import CSV Dataset")
        self.upload_btn.clicked.connect(self.upload_file)
        self.upload_label = QLabel("No file loaded")
        ul.addWidget(self.upload_btn)
        ul.addWidget(self.upload_label)
        ul.addStretch()
        self.dash_layout.addWidget(self.upload_frame)

        # 2. Stats Row
        self.stats_container = QWidget()
        self.stats_layout = QHBoxLayout(self.stats_container)
        self.dash_layout.addWidget(self.stats_container)

        # 3. Charts Area (Grid)
        self.chart_container = QWidget()
        self.chart_grid = QGridLayout(self.chart_container)
        
        # We use Matplotlib Figures
        self.fig_line = Figure(figsize=(5, 4), facecolor='none')
        self.canvas_line = FigureCanvas(self.fig_line)
        self.fig_scatter = Figure(figsize=(5, 4), facecolor='none')
        self.canvas_scatter = FigureCanvas(self.fig_scatter)
        self.fig_pie = Figure(figsize=(5, 4), facecolor='none')
        self.canvas_pie = FigureCanvas(self.fig_pie)

        # Add to grid (Frame them for styling)
        for i, (canvas, title) in enumerate([
            (self.canvas_line, "Time Series Analysis"), 
            (self.canvas_scatter, "Correlation"), 
            (self.canvas_pie, "Equipment Distribution")
        ]):
            frame = QFrame()
            frame.setObjectName("Card")
            fl = QVBoxLayout(frame)
            lbl = QLabel(title)
            lbl.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
            fl.addWidget(lbl)
            fl.addWidget(canvas)
            # Row 0 for first two, Row 1 for Pie
            r, c = (0, i) if i < 2 else (1, 0)
            self.chart_grid.addWidget(frame, r, c)

        self.dash_layout.addWidget(self.chart_container)
        self.chart_container.hide()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '.', "CSV Files (*.csv)")
        if fname:
            self.upload_label.setText(f"Processing {os.path.basename(fname)}...")
            QApplication.processEvents()
            try:
                files = {'file': open(fname, 'rb')}
                # Call the new Upload Endpoint
                response = requests.post(API_BASE + "upload/", files=files)
                if response.status_code == 200:
                    data = response.json()['data']
                    self.render_data(data)
                    self.upload_label.setText("Analysis Complete")
                else:
                    QMessageBox.critical(self, "Error", "Upload failed. Check Backend.")
            except Exception as e:
                QMessageBox.critical(self, "Connection Error", f"Is backend running?\n{e}")

    def render_data(self, data):
        # 1. Update Stats
        # Clear old
        for i in reversed(range(self.stats_layout.count())): 
            self.stats_layout.itemAt(i).widget().setParent(None)
        
        # Add new Professional Cards
        stats = data.get('stats', {})
        if 'Flowrate' in stats:
            self.stats_layout.addWidget(ProfessionalStatCard("Flowrate", "L/min", stats['Flowrate']))
        if 'Pressure' in stats:
            self.stats_layout.addWidget(ProfessionalStatCard("Pressure", "PSI", stats['Pressure']))
        if 'Temperature' in stats:
            self.stats_layout.addWidget(ProfessionalStatCard("Temp", "°C", stats['Temperature']))

        # 2. Update Charts
        # Line Chart
        self.fig_line.clear()
        ax1 = self.fig_line.add_subplot(111)
        chart_data = data.get('chart_data', [])
        if chart_data:
            idx = range(len(chart_data))
            pressures = [d.get('Pressure', 0) for d in chart_data]
            temps = [d.get('Temperature', 0) for d in chart_data]
            ax1.plot(idx, pressures, label='Pressure', color='#f43f5e')
            ax1.plot(idx, temps, label='Temp', color='#3b82f6')
            ax1.legend()
            ax1.set_title("Process Stability")
        self.canvas_line.draw()

        # Scatter Chart
        self.fig_scatter.clear()
        ax2 = self.fig_scatter.add_subplot(111)
        if chart_data:
            p = [d.get('Pressure', 0) for d in chart_data]
            f = [d.get('Flowrate', 0) for d in chart_data]
            ax2.scatter(p, f, alpha=0.5, color='#6366f1')
            ax2.set_xlabel("Pressure")
            ax2.set_ylabel("Flowrate")
            ax2.set_title("P vs F Correlation")
        self.canvas_scatter.draw()

        # Pie Chart
        self.fig_pie.clear()
        ax3 = self.fig_pie.add_subplot(111)
        dist = data.get('distribution', {})
        if dist:
            ax3.pie(dist.values(), labels=dist.keys(), autopct='%1.1f%%', startangle=90)
        self.canvas_pie.draw()

        self.chart_container.show()

    # --- TAB 2: HISTORY ---
    def init_history(self):
        layout = QVBoxLayout(self.history_tab)
        
        header = QHBoxLayout()
        btn_refresh = QPushButton("Refresh List")
        btn_refresh.setFixedWidth(120)
        btn_refresh.clicked.connect(self.load_history)
        header.addWidget(QLabel("Past Analysis Records"))
        header.addStretch()
        header.addWidget(btn_refresh)
        layout.addLayout(header)

        self.hist_table = QTableWidget()
        self.hist_table.setColumnCount(4)
        self.hist_table.setHorizontalHeaderLabels(["Date", "File Name", "Avg Pressure", "Avg Temp"])
        self.hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.hist_table)

    def load_history(self):
        try:
            res = requests.get(API_BASE + "history/")
            if res.status_code == 200:
                records = res.json()
                self.hist_table.setRowCount(len(records))
                for i, r in enumerate(records):
                    # Parse date slightly for readability
                    date_str = r['upload_date'].split('T')[0]
                    self.hist_table.setItem(i, 0, QTableWidgetItem(date_str))
                    self.hist_table.setItem(i, 1, QTableWidgetItem(r['file_name']))
                    self.hist_table.setItem(i, 2, QTableWidgetItem(str(r['avg_pressure'])))
                    self.hist_table.setItem(i, 3, QTableWidgetItem(str(r['avg_temperature'])))
        except:
            print("Could not fetch history")

    def on_tab_change(self, index):
        if index == 1: # History Tab
            self.load_history()

    # --- TAB 3: SETTINGS ---
    def init_settings(self):
        layout = QVBoxLayout(self.settings_tab)
        layout.setAlignment(Qt.AlignTop)
        
        container = QFrame()
        container.setObjectName("Card")
        l = QVBoxLayout(container)
        
        l.addWidget(QLabel("Appearance"))
        
        self.cb_dark = QCheckBox("Enable Dark Mode")
        self.cb_dark.setStyleSheet("font-size: 16px; padding: 10px;")
        self.cb_dark.stateChanged.connect(self.toggle_dark_mode)
        l.addWidget(self.cb_dark)
        
        layout.addWidget(container)

    def toggle_dark_mode(self, state):
        self.dark_mode = (state == Qt.Checked)
        self.apply_theme()
        
        # Matplotlib figures need recoloring
        face = '#1e293b' if self.dark_mode else 'none'
        text = 'white' if self.dark_mode else 'black'
        
        for fig in [self.fig_line, self.fig_scatter, self.fig_pie]:
            fig.patch.set_facecolor('none') # Keep transparent to match card
            for ax in fig.axes:
                ax.tick_params(colors=text)
                ax.xaxis.label.set_color(text)
                ax.yaxis.label.set_color(text)
                ax.title.set_color(text)
                for spine in ax.spines.values():
                    spine.set_edgecolor(text)
        
        self.canvas_line.draw()
        self.canvas_scatter.draw()
        self.canvas_pie.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    # Try to load icon
    basedir = os.path.dirname(__file__)
    icon_path = os.path.join(basedir, 'assets', 'icon.jpeg')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        
    window = ChemicalApp()
    window.show()
    sys.exit(app.exec_())