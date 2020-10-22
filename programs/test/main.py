from PyQt5.QtWidgets import *

if __name__ == '__main__':
    app = QApplication([])
    button = QPushButton('Click')
    def on_button_clicked():
        alert = QMessageBox()
        alert.setText('You clicked the button!')
        alert.exec_()

    button.clicked.connect(on_button_clicked)
    button.show()
    app.exec_()
