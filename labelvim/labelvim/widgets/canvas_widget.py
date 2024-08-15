from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtCore
from labelvim.widgets.label_pupop import LabelPopup
from labelvim.utils.config import ANNOTATION_MODE
from enum import Enum

class CanvasWidget(QLabel):
    """A custom QLabel widget to display images and draw rectangles on them."""
    update_label_list_slot_transmitter = pyqtSignal(list) # Signal to update the label list
    update_label_list_slot_receiver = pyqtSignal(list) # Signal to update the label list
    annotation_data_slot_transmitter = pyqtSignal(list) # Signal to transmit the annotation data
    annotation_data_slot_receiver = pyqtSignal(list) # Signal to receive the annotation data
    btn_action_slot = pyqtSignal(Enum) # Signal to transmit the button action
    def __init__(self, parent=None):
        super(CanvasWidget, self).__init__(parent)
        self.setGeometry(70, 0, 1321, 801)
        self.setFrameShape(QLabel.WinPanel)
        self.setFrameShadow(QLabel.Raised)
        self.setLineWidth(9)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        
        # set scroll area
        # self.scroll_area = QScrollArea(parent)
        # self.scroll_area.setWidget(self)
        # self.scroll_area.setWidgetResizable(True)
        # self.scroll_area.setAlignment(Qt.AlignCenter)
        # self.scroll_area.setGeometry(70, 0, 1321, 801)
        # self.scroll_area.setFrameShape(QFrame.Box | QFrame.Plain)
        # self.scroll_area.setFrameShadow(QFrame.Sunken)
        
        self.start_point = None
        self.end_point = None
        self.rectangles = []  # List to store drawn rectangles
        self.selected_rectangle = None  # The rectangle currently selected for deletion
        self.pixmap = None  # To store the loaded pixmap
        self.label_list = []
        self.update_label_list_slot_receiver.connect(self.update_label_list)
        self.annotation_data_slot_receiver.connect(self.update_annotation_from_json)
        self.btn_action_slot.connect(self.set_annotation_mode)
        self.__reset_scale_factor()
        self.annotation_mode = ANNOTATION_MODE.NONE

    def update_pixmap(self, file_name):
        """Update the displayed image in the widget.

        Args:
            file_name (str): Path to the image file.
        """
        self.clear_painter()
        self.pixmap = QPixmap(file_name)
        self.__reset_scale_factor()
        # print(f"Scale Factor W: {self.scale_factor_w}")
        # print(f"Scale Factor H: {self.scale_factor_h}")
        if not self.pixmap.isNull():
            self.setPixmap(self.pixmap)
            self.scale_factor_w, self.scale_factor_h = self.__scale_factor()
            # print(f"Scale Factor W: {self.scale_factor_w}")
            # print(f"Scale Factor H: {self.scale_factor_h}")
        else:
            print(f"Failed to load image: {file_name}")
        self.update()  # Trigger a repaint to show the new image
    

    def clear_pixmap(self):
        """Clear the displayed image from the widget."""
        self.clear()
        self.pixmap = None
        self.rectangles.clear()
        self.update()

    def mousePressEvent(self, event):
        if self.pixmap is not None:
            if event.button() == Qt.LeftButton:
                self.start_point = event.pos()
                # self.selected_rectangle = self.get_rectangle_at(self.start_point)

    def mouseMoveEvent(self, event):
        if self.pixmap is not None and self.start_point and self.annotation_mode == ANNOTATION_MODE.CREATE:
            self.end_point = event.pos()
            self.update()  # Trigger a repaint to show the rectangle being drawn

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_point and self.annotation_mode == ANNOTATION_MODE.CREATE:
            self.end_point = event.pos()
            # self.img_pos(self.end_point)
            rect = QRect(self.start_point, self.end_point).normalized()
            if self.distance(self.start_point, self.end_point) > 50:
                label_selected = self.select_label_from_label_list()
                print(f"Selected Label: {label_selected}")
                if label_selected:
                    try:
                        index = self.label_list.index(label_selected)
                        self.rectangles.append({"label": index, "rect": [rect.x(), rect.y(), rect.width(), rect.height()]})
                    except ValueError:
                        print("Label not found in the label list")
            self.start_point = None
            self.end_point = None
            self.update()  # Trigger a repaint to show the new rectangle
            # print(f"list of available labels: {self.LabelWidget.get_labels()}")
    
    def paintEvent(self, event):
        super().paintEvent(event)  # Ensure the QLabel's paintEvent is called

        if self.pixmap is not None:
            painter = QPainter(self)
            painter.setPen(QPen(QColor(0, 0, 255), 2, Qt.SolidLine))
            painter.setBrush(QBrush(QColor(0, 0, 255, 50)))

            # Draw the rectangle being dragged (if any)
            if self.start_point and self.end_point:
                current_rect = QRect(self.start_point, self.end_point).normalized()
                # print(f"Current Rect: {current_rect}")
                # print(f"NOrmalized: {current_rect.normalized()}")
                painter.drawEllipse(current_rect.topLeft(), 5, 5)
                painter.drawEllipse(current_rect.topRight(), 5, 5)
                painter.drawEllipse(current_rect.bottomLeft(), 5, 5)
                painter.drawEllipse(current_rect.bottomRight(), 5, 5)
                painter.drawRect(current_rect)
            # print(f"Rectangles in paint: {self.rectangles}")
            # Draw existing rectangles
            for rectangle in self.rectangles:
                # print(f"Rectangle: {rectangle}")
                painter.setPen(QPen(QColor(0, 0, 255), 2, Qt.SolidLine))
                rect, index = rectangle['rect'], rectangle["label"]
                rect = QRect(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3]))
                text_label = self.label_list[index]
                # print(f"Text Label: {text_label}")
                painter.drawEllipse(rect.topLeft(), 5, 5)
                painter.drawEllipse(rect.topRight(), 5, 5)
                painter.drawEllipse(rect.bottomLeft(), 5, 5)
                painter.drawEllipse(rect.bottomRight(), 5, 5)
                painter.drawRect(rect)
                # draw rectangle box around the label and fill it with color
                painter.setPen(QPen(QColor(0, 255, 255), 2, Qt.SolidLine))
                painter.drawRect(rect.topLeft().x(), rect.topLeft().y() - 20, rect.width(), 20)
                painter.drawText(rect.topLeft().x(), rect.topLeft().y() - 5, text_label)
            self.update()  # Trigger a repaint to show the new rectangle
    
    def clear_painter(self):
        """Clear the drawn rectangles from the widget."""
        self.rectangles.clear()
        self.update()
    
    def distance(self, p1, p2):
        return ((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2)**0.5
    
    def select_label_from_label_list(self):
        """Generate a label selection popup dialog."""
        dialog = LabelPopup(self.label_list,self.update_label_list_slot_transmitter, self)
        if dialog.exec_():
            selected_label, _ = dialog.get_selected_item()
            print(f"label list: {self.label_list}")
            return selected_label
        return None

    # def get_rectangle_at(self, point):
    #     """Check if a point is within any rectangle and return the rectangle if found.

    #     Args:
    #         point (QPoint): The point to check.

    #     Returns:
    #         QRect: The rectangle that contains the point or None if no rectangle is found.
    #     """
    #     for rect in reversed(self.rectangles):  # Check from the topmost rectangle
    #         if rect[1].contains(point):
    #             return rect
    #     return None

    def update_label_list(self, label_list):
        self.label_list = label_list
        print(f"Label List: {self.label_list}")

    def __fit_to_window(self):
        """Fit the image to the window size."""
        self.setScaledContents(True)

    def __scale_factor(self):
        """Calculate the scale factor for the image."""
        original_image_size = self.pixmap.size()
        scaled_image_size = self.size()
        print(f"Original Image Size: {original_image_size}")
        print(f"Scaled Image Size: {scaled_image_size}")
        scale_factor_w = original_image_size.width() / scaled_image_size.width()
        scale_factor_h = original_image_size.height() / scaled_image_size.height()
        return scale_factor_w, scale_factor_h
    
    def __reset_scale_factor(self):
        """Reset the scale factor to 1."""
        self.scale_factor_w, self.scale_factor_h = 1, 1

    def __mouse_pos_to_img_pos(self, x, y):
        """Convert the mouse position to image coordinates."""
        return x * self.scale_factor_w, y* self.scale_factor_h
    
    def __img_pos_to_mouse_pos(self, x, y):
        """Convert the image position to mouse coordinates."""
        return x / self.scale_factor_w, y / self.scale_factor_h
    
    def __bbox_img_pos_to_mouse_pos(self, bbox: list):
        """Convert the bounding box image position to mouse position."""
        x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
        x, y = self.__img_pos_to_mouse_pos(x, y)
        w, h = self.__img_pos_to_mouse_pos(w, h)
        return [x, y, w, h]
    
    def __bbox_mouse_pos_to_img_pos(self, bbox: list):
        """Convert the bounding box mouse position to image position."""
        x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
        x, y = self.__mouse_pos_to_img_pos(x, y)
        w, h = self.__mouse_pos_to_img_pos(w, h)
        return [x, y, w, h]
    
    def update_annotation_from_json(self, annotation: list):
        """
        Update the drawn rectangles from the annotation data.
        
        Args:
            annotation (list): A list of annotations containing the label and rectangle data.
            annotation = [{
            ...     "id": 1,
            ...     "category_id": 1,
            ...     "bbox": [10, 20, 100, 200],
            ...     "area": 1000,
            ...     "segmentation": [[10, 20, 100, 20, 100, 200, 10, 200]],
            ...     "iscrowd": 0
            ... }]
        """
        # self.clear_painter()
        # print(annotation)
        self.rectangles.clear()
        for anno in annotation:
            label = anno['category_id']
            bbox = self.__bbox_img_pos_to_mouse_pos(anno['bbox'])
            self.rectangles.append({"label": label, "rect": bbox})
        print(f"Rectangles: {len(self.rectangles)}")
        # print(f"Rectangles: {self.rectangles}")
        # self.rectangles
        self.update()
    
    def update_annotation_to_json(self):
        """
        Update the annotation data from the drawn rectangles.
        
        Returns:
            list: A list of annotations containing the label and rectangle data.
        """
        annotations = []
        print(f"to json rectangles: {len(self.rectangles)}")
        for rect in self.rectangles:
            label = rect['label']
            x, y, w, h = rect['rect'][0], rect['rect'][1], rect['rect'][2], rect['rect'][3]
            bbox = self.__bbox_mouse_pos_to_img_pos([x, y, w, h])
            area = w * h
            segmentation = [[x, y, x + w, y, x + w, y + h, x, y + h]]
            iscrowd = 0
            annotations.append({
                "category_id": label,
                "bbox": bbox,
                "area": area,
                "segmentation": segmentation,
                "iscrowd": iscrowd
            })
        return annotations
    
    def set_annotation_mode(self, mode):
        """Set the annotation mode."""
        self.annotation_mode = mode
        print(f"Annotation Mode: {self.annotation_mode}")
        if self.annotation_mode == ANNOTATION_MODE.CLEAR:
            self.clear_painter()
            self.annotation_mode = ANNOTATION_MODE.NONE
        self.update()
    
