import sys
from PyQt5.QtWidgets import QApplication, QWidget,QLabel, QVBoxLayout
from PyQt5.QtGui import QColor,QFont
from PyQt5.QtCore import Qt
import subprocess

class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.initHandler()

    def initUI(self):
        #window
        self.setGeometry(200, 200, 500, 400)
        self.setWindowTitle('Home')

        #set label
        self.box_colors = [(201, 241, 248), (201, 248, 215), (239, 223, 250)]
        labels_text = ['Start Monitoring', 'Set Reference', 'Show Result']
        self.labels = [QLabel(self) for _ in range(3)]
        for i, label in enumerate(self.labels):
            color = QColor(*self.box_colors[i])
            font = QFont("",12,QFont.Bold)
            label.setFont(font)
            label.setStyleSheet(f"QLabel {{ background-color: {color.name()}; }}")
            label.setAlignment(Qt.AlignCenter)
            label.setText(labels_text[i])

        # label vertical arrange 
        layout = QVBoxLayout(self)
        for label in self.labels:
            layout.addWidget(label)
        
        self.show()
    
    def initHandler(self):
        # add handler to label
        self.file_paths = ['monitor.py', 'reference.py', 'result.py']
        for i, label in enumerate(self.labels):
            label.mousePressEvent = lambda event, idx=i: subprocess.Popen(['python', self.file_paths[i]])
        

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())