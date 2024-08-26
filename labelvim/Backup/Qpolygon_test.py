from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtGui import QPainter, QPolygon, QColor
from PyQt5.QtCore import QPoint, Qt

class PolygonWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('QPolygon Example')
        self.setGeometry(100, 100, 400, 300)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Define the points of the polygon
        points = [
            QPoint(50, 50),
            QPoint(150, 50),
            QPoint(200, 100),
            QPoint(150, 150),
            QPoint(50, 150),
            QPoint(0, 100)
        ]
        
        # Create the polygon using the points
        polygon = QPolygon(points)
        print(f'Polygon:{polygon.boundingRect()}')
        print(f'Polygon:{polygon.boundingRect().width()}')
        print(f'Polygon:{polygon.boundingRect().height()}')
        print(f'Polygon:{polygon.boundingRect().x()}')
        print(f'Polygon:{polygon.boundingRect().y()}')
        points = [polygon.point(i) for i in range(polygon.count())]
        print(f"polygon points:{points}")
        # Set pen and brush colors
        painter.setPen(Qt.black)
        painter.setBrush(QColor(100, 100, 250, 50))

        
        painter.drawPolygon(polygon)
        print(f'Rectangle:{polygon.boundingRect()}')
        # Draw the polygon
        points = [
            QPoint(300, 100)
        ]
        polygon = QPolygon(points)
        polygon.append(QPoint(QPoint(200, 100)))
        polygon.append(QPoint(QPoint(150, 150)))

        painter.setPen(Qt.black)
        painter.setBrush(QColor(250, 100, 250, 50))

        # Draw the polygon
        painter.drawPolygon(polygon)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 400, 300)

        # Add the custom widget that draws the polygon
        self.polygon_widget = PolygonWidget()
        self.setCentralWidget(self.polygon_widget)

if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
