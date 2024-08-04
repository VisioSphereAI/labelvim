from PyQt5 import QtWidgets
from layout import Ui_MainWindow
import sys

class LabelVim(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(LabelVim, self).__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LabelVim()
    window.show()
    sys.exit(app.exec_())