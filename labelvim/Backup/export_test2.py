from PyQt5.QtWidgets import QApplication, QMainWindow, QRadioButton, QGroupBox, QVBoxLayout, QHBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Model Selection")
        self.setGeometry(300, 300, 400, 200)
        
        # Create the main layout
        main_layout = QVBoxLayout()

        # Create the first group box
        group1 = QGroupBox("Group 1")
        group1_layout = QVBoxLayout()

        self.object_detection = QRadioButton('Object Detection')
        self.object_detection.setChecked(True)
        self.segmentation = QRadioButton('Segmentation')
        
        group1_layout.addWidget(self.object_detection)
        group1_layout.addWidget(self.segmentation)
        group1.setLayout(group1_layout)
        
        # Create the second group box
        group2 = QGroupBox("Group 2")
        group2_layout = QVBoxLayout()

        self.pose = QRadioButton('Pose')
        self.classification = QRadioButton('Classification')
        
        group2_layout.addWidget(self.pose)
        group2_layout.addWidget(self.classification)
        group2.setLayout(group2_layout)
        
        # Add both groups to the main layout
        main_layout.addWidget(group1)
        main_layout.addWidget(group2)

        # Set the main layout for the central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
