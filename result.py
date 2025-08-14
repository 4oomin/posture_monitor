import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QCalendarWidget, QLabel
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QColor,QFont
from PyQt5.QtCore import Qt

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import sqlite3
from datetime import datetime

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Result")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        layout.addWidget(self.calendar)

        # graph
        self.fig = Figure(figsize=(5,3))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.show()

        # handler
        self.calendar.clicked.connect(self.generate_graph)
    
    def generate_graph(self):
        #get records of the date from DB
        records=[]
        reference=0
        date =self.calendar.selectedDate().toString("yyyy/MM/dd") 
        
        conn = sqlite3.connect('_put your own path_')
        curs = conn.cursor()

        sql = """ SELECT ratio FROM references WHERE date = ?"""
        curs.execute(sql, (date,))
        reference= curs.fetchone()
        if reference is not None:
            reference= reference[0]
        else:
            return  # no records in selected date
        sql = """ SELECT substr(time,1,2) AS hour, AVG(ratio)
                  FROM monitors
                  WHERE date = ?
                  GROUP BY hour
                  ORDER BY hour"""
        curs.execute(sql, (date,))
        rows = curs.fetchall()
        if rows is not None:
            for row in rows:
                records.append(row)
        
        conn.close()
        
        #draw graph
        hours = [int(r[0]) for r in records]
        ratios = [round(float(r[1]),1) for r in records]

        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.plot(hours, ratios, marker='o', label="Ratio")
        ax.set_title(f"Bending degree in {date}")
        ax.set_xlabel("Hour")
        ax.set_ylabel("Degree")
        ax.grid(True)
        ax.legend()

        #degree map
        de0 = reference
        de30=round(reference/0.8,1)
        de60=round(reference/0.5,1)
        degree_text = (
            f"{de0} → 0°\n"
            f"{de30} → 30°\n"
            f"{de60} → 60°"
        )
        ax.text(
            1.02, 0.95, degree_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        self.canvas.draw()


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())