# # Basic window
# from PySide6.QtWidgets import QApplication, QWidget
# import sys

# app = QApplication(sys.argv)

# window = QWidget()
# window.setWindowTitle("My first window")
# window.resize(400,300)
# window.show()

# app.exec()



# # Basic window using MainWindow
# from PySide6.QtWidgets import QApplication, QMainWindow
# import sys

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Main Window Example")
#         self.resize(600, 400)

# app = QApplication(sys.argv)
# window = MainWindow()
# window.show()
# app.exec()



from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLabel, QVBoxLayout, QComboBox
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QLabel("Hello")
        button = QPushButton("Click me")
        button.clicked.connect(self.on_button_click)
        combo = QComboBox()
        combo.addItems(["Paris", "Rennes", "Brest"])
        combo.currentIndexChanged.connect(self.on_city_change)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(button)
        layout.addWidget(combo)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)
    
    def on_city_change(self):
        self.label.setText("Test")
    
    def on_button_click(self):
        global number
        number += 1
        self.label.setText(str(number))

        
number = 0
app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
