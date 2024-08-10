from PyQt5 import QtWidgets
from PyQt5 import QtCore
class TaskSelectionDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(TaskSelectionDialog, self).__init__(parent)
        
        self.setWindowTitle("Task Selection")
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        self.label = QtWidgets.QLabel("Select a task to perform:", self)
        layout.addWidget(self.label)
        
        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.addItems(["Object Detection", "Segmentation"])
        layout.addWidget(self.comboBox)
        
        self.ok_button = QtWidgets.QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
    
    def selected_task(self):
        return self.comboBox.currentText()