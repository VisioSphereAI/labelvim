from PyQt5.QtWidgets import QLabel, QApplication, QVBoxLayout, QWidget, QPushButton, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPoint

class ImageLabel(QLabel):
    def __init__(self, image_path):
        super().__init__()
        self.original_pixmap = QPixmap(image_path)
        self.current_pixmap = self.original_pixmap
        self.scale_factor = 1.0
        self.setPixmap(self.original_pixmap)
        self.setAlignment(Qt.AlignCenter)  # Center the image in the label

    def scale_image(self, factor):
        self.scale_factor *= factor
        new_size = self.scale_factor * self.original_pixmap.size()
        self.current_pixmap = self.original_pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setPixmap(self.current_pixmap)
        self.adjustSize()  # Adjust the label size to fit the new pixmap size

    def mousePressEvent(self, event):
        # Get the position of the click relative to the QLabel
        click_pos = event.pos()

        # Get the size of the displayed (scaled) pixmap
        displayed_image_size = self.current_pixmap.size()

        # Calculate the offsets due to alignment
        x_offset = (self.width() - displayed_image_size.width()) // 2
        y_offset = (self.height() - displayed_image_size.height()) // 2

        # Calculate the click position relative to the pixmap
        relative_x = click_pos.x() - x_offset
        relative_y = click_pos.y() - y_offset

        # Only proceed if the click is within the image boundaries
        if 0 <= relative_x < displayed_image_size.width() and 0 <= relative_y < displayed_image_size.height():
            # Scale the click position back to the original image coordinates
            original_x = relative_x / self.scale_factor
            original_y = relative_y / self.scale_factor

            print(f"Click position on original image: {original_x}, {original_y}")

    def zoom_in(self):
        self.scale_image(1.25)  # Zoom in by 25%

    def zoom_out(self):
        self.scale_image(0.8)  # Zoom out by 20%

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.label = ImageLabel('icon/AI.jpg')

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)  # Center the label within the scroll area

        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.label.zoom_in)

        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.label.zoom_out)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.zoom_in_button)
        layout.addWidget(self.zoom_out_button)

        self.setLayout(layout)

# Usage example
app = QApplication([])
window = MainWindow()
window.resize(800, 600)
window.show()
app.exec_()
