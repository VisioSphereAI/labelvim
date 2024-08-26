import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QColorDialog, QLabel

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set the window title
        self.setWindowTitle("QColorDialog Example")
        
        # Create a menu bar
        menubar = self.menuBar()
        
        # Create a tools menu
        tools_menu = menubar.addMenu('Tools')
        
        # Create a QAction for selecting color
        color_action = QAction('Select Color', self)
        
        # Connect the action to the function that opens QColorDialog
        color_action.triggered.connect(self.open_color_dialog)
        
        # Add the action to the tools menu
        tools_menu.addAction(color_action)
        
        # Create a label to display the selected color
        self.label = QLabel("Selected Color", self)
        self.label.setGeometry(50, 100, 200, 50)
        
        # Show the window
        self.show()
    
    def open_color_dialog(self):
        # Open the QColorDialog and get the selected color
        color = QColorDialog.getColor()
        print(color)
        print(color.isValid())
        print(color.name())
        r = color.red()
        g = color.green()
        b = color.blue()
        alpha = color.alpha()
        print(f"R: {r}, G: {g}, B: {b}, Alpha: {alpha}")
        
        if color.isValid():
            # If a valid color is selected, set the label's background to that color
            self.label.setStyleSheet(f"background-color: {color.name()}")
            self.label.setText(f"Selected Color: {color.name()}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
