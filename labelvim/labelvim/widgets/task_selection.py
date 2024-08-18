import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from labelvim.utils.config import ANNOTATION_TYPE

class TaskSelectionDialog(QtWidgets.QDialog):
    """
    A custom dialog to prompt the user to select between 'Object Detection' and 'Segmentation' tasks.
    
    Attributes:
        label (QLabel): The label displaying the prompt message.
        comboBox (QComboBox): A dropdown menu allowing the user to select a task.
        ok_button (QPushButton): A button to confirm the selection and close the dialog.
    """
    def __init__(self, parent=None):
        """
        Initializes the TaskSelectionDialog with a title, layout, and components.
        
        Args:
            parent (QWidget, optional): The parent widget of the dialog. Defaults to None.
        """
        super(TaskSelectionDialog, self).__init__(parent)
        
        # Set dialog title and remove the close button
        self.setWindowTitle("Task Selection")
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.WindowTitleHint | QtCore.Qt.CustomizeWindowHint)
        
        # Set a fixed size for the dialog
        self.setFixedSize(300, 150)
        
        # Create the layout and set it
        layout = QtWidgets.QVBoxLayout(self)
        
        # Add a label with bold and larger font to make the prompt stand out
        self.label = QtWidgets.QLabel("Select a task to perform:", self)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)
        self.label.setFont(font)
        layout.addWidget(self.label)
        
        # Add a combo box with a dropdown list of tasks
        self.comboBox = QtWidgets.QComboBox(self)
        for task in ANNOTATION_TYPE:
            self.comboBox.addItem(task.name)
        # self.comboBox.addItems(["Object Detection", "Segmentation", "NONE"])
        layout.addWidget(self.comboBox)
        
        # Add an OK button with a custom style
        self.ok_button = QtWidgets.QPushButton("OK", self)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
    
    def selected_task(self):
        """
        Returns the task selected by the user from the combo box.
        
        Returns:
            str: The selected task, either 'Object Detection' or 'Segmentation'.
        """
        # index = self.comboBox.currentIndex()
        current_text = self.comboBox.currentText()
        if current_text == "BBOX":
            return ANNOTATION_TYPE.BBOX
        elif current_text == "POLYGON":
            return ANNOTATION_TYPE.POLYGON
        elif current_text == "NONE":
            return ANNOTATION_TYPE.NONE
        else:
            return ANNOTATION_TYPE.NONE
        # return self.comboBox.currentText()