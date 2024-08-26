from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtCore
from labelvim.widgets.label_pupop import LabelPopup
from labelvim.utils.config import ANNOTATION_MODE, OBJECT_LIST_ACTION
from enum import Enum

class CanvasWidget(QLabel):
    """A custom QLabel widget to display images and draw rectangles on them."""
    update_label_list_slot_transmitter = pyqtSignal(list) # Signal to update the label list
    update_label_list_slot_receiver = pyqtSignal(list) # Signal to update the label list
    annotation_data_slot_transmitter = pyqtSignal(list) # Signal to transmit the annotation data
    annotation_data_slot_receiver = pyqtSignal(list) # Signal to receive the annotation data
    object_list_action_slot = pyqtSignal(list, Enum) # Signal to transmit the object list action
    object_selection_notification_slot_receiver = pyqtSignal(int) # Signal to receive the object selection notification
    btn_action_slot = pyqtSignal(Enum) # Signal to transmit the button action
    scale_factor_slot = pyqtSignal(float) # Signal to transmit the scale factor
    def __init__(self, parent=None):
        super(CanvasWidget, self).__init__(parent)
        self.size_geometry = QRect(70, 0, 1310, 790)
        self.setGeometry(self.size_geometry)
        self.setFrameShape(QLabel.WinPanel)
        self.setFrameShadow(QLabel.Raised)
        self.setLineWidth(9)
        # self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        
        # set scroll area
        self.scroll_area = QScrollArea(parent)
        self.scroll_area.setWidget(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setGeometry(70, 0, 1321, 801)
        self.scroll_area.setFrameShape(QFrame.Box | QFrame.Plain)
        self.scroll_area.setFrameShadow(QFrame.Sunken)
        
        self.start_point = None
        self.end_point = None
        self.rectangles = []  # List to store drawn rectangles
        self.original_pixmap = None
        self.current_pixmap = None
        self.brush_color = QColor(0, 0, 255, 50)
        self.pen_color = QColor(0, 0, 255)
        self.title_pen_color = QColor(0, 255, 255)
        self.selected_rectangle_brush_color = QColor(255, 0, 0, 50)
        self.selected_rectangles = None  # List to store selected rectangles
        self.selected_vertex = None
        self.moving_rectangle = False
        self.last_mouse_position = QPoint()  # Store the last mouse position
        # self.pixmap = None  # To store the loaded pixmap
        self.label_list = []
        self.update_label_list_slot_receiver.connect(self.update_label_list)
        self.annotation_data_slot_receiver.connect(self.update_annotation_from_json)
        self.btn_action_slot.connect(self.set_annotation_mode)
        self.object_selection_notification_slot_receiver.connect(self.select_object)
        self.scale_factor = 1.0
        # self.__reset_scale_factor()
        self.annotation_mode = ANNOTATION_MODE.NONE
        self.scale_factor_w, self.scale_factor_h = 1, 1
        self.zoom_in_scale_factor = 1.25
        self.zoom_out_scale_factor = 0.8
        self.max_scale_factor = 6
        self.point_click_radious = 5 # The radious of the point click

    def load_image(self, file_name):
        self.clear_annotation()
        self.selected_rectangles = None
        # emit signal to clear the object list
        self.object_list_action_slot.emit([None], OBJECT_LIST_ACTION.CLEAR)
        self.annotation_mode = ANNOTATION_MODE.NONE
        self.scale_factor = 1.0
        # print(f"File Name: {file_name}")
        self.original_pixmap = QPixmap(file_name)
        self.current_pixmap = self.original_pixmap.copy()
        scale_factor = self.size_geometry.width() / self.current_pixmap.width()
        self.max_scale_factor = 4 * scale_factor
        self.min_scale_factor = 0.25 * scale_factor
        # print(f"Max Scale Factor: {self.max_scale_factor}, Min Scale Factor: {self.min_scale_factor}")
        self.scale_to_fit(self.size_geometry.size())
        # self.scale_to_fit(self.size_geometry.size())
        self.update()
    
    def scale_to_fit(self, available_size):
        if self.original_pixmap:
            self.current_pixmap = self.original_pixmap.scaled(
                available_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            self.scale_factor = self.current_pixmap.width() / self.original_pixmap.width()
            self.scale_factor_slot.emit(self.scale_factor)
            self.adjust_scroll_bars()
        self.update()
    

    def scale_image(self, factor):
        if self.original_pixmap:
            if self.scale_factor * factor < self.min_scale_factor or self.scale_factor * factor > self.max_scale_factor:
                return
                
            self.scale_factor *= factor
            self.scale_factor_slot.emit(self.scale_factor)
            new_size = self.scale_factor * self.original_pixmap.size()
            self.current_pixmap = self.original_pixmap.scaled(new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.adjust_scroll_bars()

    def adjust_scroll_bars(self):
        if self.current_pixmap:
            self.setFixedSize(self.current_pixmap.size())
    
    def reset(self):
        self.clear_annotation()
        self.annotation_mode = ANNOTATION_MODE.NONE
        self.scale_factor = 1.0
        self.current_pixmap = None
        self.original_pixmap = None
        self.update()

    def clear_annotation(self):
        """Clear the displayed image from the widget."""
        self.rectangles.clear()
        self.update()
    
    def zoom_in(self):
        self.scale_image(self.zoom_in_scale_factor)
        self.update()
    
    def zoom_out(self):
        self.scale_image(self.zoom_out_scale_factor)
        self.update()
    
    def fit_to_window(self):
        self.scale_to_fit(self.size_geometry.size())
        self.update()
    
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
    
    ## Start of mouse events

    def mousePressEvent(self, event):
        if self.original_pixmap:
            click_pos = event.pos()
            if event.button() == Qt.LeftButton:
                if self.annotation_mode == ANNOTATION_MODE.CREATE:
                    start_point = self.map_to_original_image(click_pos)
                    if start_point:
                        self.start_point = start_point
                if self.annotation_mode == ANNOTATION_MODE.EDIT:
                    self.selected_rectangles, self.selected_vertex = self.find_object_to_edit(click_pos)
                    print(f"Selected Rectangle: {self.selected_rectangles}, Selected Vertex: {self.selected_vertex}")
                    if self.selected_vertex is None and self.selected_rectangles is None:
                        # Start moving the rectangle if no vertex is selected
                        self.moving_rectangle = True
                        self.last_mouse_position = self.map_to_original_image(click_pos)
                        if self.last_mouse_position is None:
                            self.moving_rectangle = False
                        else:
                            self.select_rectangle(self.last_mouse_position)
                        print(f"Selected Rectangle: {self.selected_rectangles}")
                    # self.select_rectangle(click_pos)
                    # if self.selected_rectangles is not None:
                    #     self.start_drag_point = click_pos
                    #     self.dragging = True
                    # self.resizing = self.is_resizing(click_pos)

        self.update()

    def mouseMoveEvent(self, event):
        if self.original_pixmap:
            click_pos = event.pos()
            if self.start_point and self.annotation_mode == ANNOTATION_MODE.CREATE:
                end_point = self.map_to_original_image(click_pos)
                if end_point:
                    self.end_point = end_point
            
            elif self.selected_vertex is not None and self.annotation_mode == ANNOTATION_MODE.EDIT:
                # Resize the selected rectangle
                new_pos = self.map_to_original_image(click_pos)
                if new_pos:
                    self.move_vertex(self.selected_vertex, new_pos)
            elif self.moving_rectangle and self.annotation_mode == ANNOTATION_MODE.EDIT:
                # Move the selected rectangle
                new_pos = self.map_to_original_image(click_pos) # origional image dimension
                if new_pos:
                    self.move_rectangle(new_pos)
                    self.last_mouse_position = new_pos # in repect to origional image 

        self.update()
    
    def mouseReleaseEvent(self, event):
        if self.original_pixmap and event.button() == Qt.LeftButton:
            if self.start_point and self.annotation_mode == ANNOTATION_MODE.CREATE:
                click_pos = event.pos()
                end_point = self.map_to_original_image(click_pos)
                if end_point:
                    self.end_point = end_point
                    rect = QRect(self.start_point, self.end_point).normalized()
                    if self.distance(self.start_point, self.end_point) > 20:
                        label_selected = self.select_label_from_label_list()
                        print(f"Selected Label: {label_selected}")
                        if label_selected:
                            try:
                                index = self.label_list.index(label_selected)
                                self.rectangles.append({"category_id": index, "bbox": [rect.x(), rect.y(), rect.width(), rect.height()], "id": len(self.rectangles)})
                                # emit signal to add object to the object list
                                self.object_list_action_slot.emit([self.rectangles[-1]], OBJECT_LIST_ACTION.ADD)
                            except ValueError:
                                print("Label not found in the label list")
            elif self.selected_vertex is not None and self.annotation_mode == ANNOTATION_MODE.EDIT:
                self.selected_vertex = None
            elif self.moving_rectangle and self.annotation_mode == ANNOTATION_MODE.EDIT:
                self.moving_rectangle = False
        self.start_point = None
        self.end_point = None
        self.selected_rectangles = None
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.current_pixmap:
            painter = QPainter(self)
            offset_x = (self.width() - self.current_pixmap.width()) // 2
            offset_y = (self.height() - self.current_pixmap.height()) // 2
            painter.drawPixmap(offset_x, offset_y, self.current_pixmap)
            # print(f"offset_x: {offset_x}, offset_y: {offset_y}")
            painter.setPen(QPen(self.pen_color, 2, Qt.SolidLine))
            painter.setBrush(QBrush(self.brush_color))
            if self.start_point and self.end_point:
                # painter.setPen(QPen(QColor(0, 0, 255), 2, Qt.SolidLine))
                
                start_point = QPoint(offset_x+int(self.start_point.x() * self.scale_factor), offset_y+int(self.start_point.y() * self.scale_factor))
                end_point = QPoint(offset_x+int(self.end_point.x() * self.scale_factor), offset_y+int(self.end_point.y() * self.scale_factor))
                rect = QRect(start_point, end_point).normalized()
                painter.drawEllipse(rect.topLeft(), 5, 5)
                painter.drawEllipse(rect.topRight(), 5, 5)
                painter.drawEllipse(rect.bottomLeft(), 5, 5)
                painter.drawEllipse(rect.bottomRight(), 5, 5)
                painter.drawRect(rect)
            for rectangle in self.rectangles:
                rect, index = rectangle['bbox'], rectangle["category_id"]
                painter.setPen(QPen(self.pen_color, 2, Qt.SolidLine))
                painter.setBrush(QBrush(self.brush_color))
                if self.selected_rectangles is not None and self.selected_rectangles == rectangle["id"]:
                    painter.setBrush(QBrush(self.selected_rectangle_brush_color))
                rect = QRect(offset_x+int(rect[0] * self.scale_factor), offset_y+int(rect[1] * self.scale_factor), int(rect[2] * self.scale_factor), int(rect[3] * self.scale_factor))
                text_label = self.label_list[index]
                painter.drawEllipse(rect.topLeft(), 5, 5)
                painter.drawEllipse(rect.topRight(), 5, 5)
                painter.drawEllipse(rect.bottomLeft(), 5, 5)
                painter.drawEllipse(rect.bottomRight(), 5, 5)
                painter.drawRect(rect)
                painter.setPen(QPen(self.title_pen_color, 2, Qt.SolidLine))
                painter.setBrush(QBrush(QColor(255, 255, 255, 75)))
                painter.drawRect(rect.topLeft().x(), rect.topLeft().y() - 20, rect.width(), 20)
                painter.setPen(QPen(QColor(0,0,0), 2, Qt.SolidLine))
                painter.drawText(rect.topLeft().x(), rect.topLeft().y() - 5, text_label)
        self.update()
    
    def distance(self, p1, p2):
        """
        Calculate the distance between two points.
        
        Args:
        
            p1 (QPoint): The first point.
            p2 (QPoint): The second point.
            
            Returns:
            
                float: The distance between the two points.
                
        """
        return ((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2)**0.5
    
    def map_to_original_image(self, pos):
        """
        Map the position on the displayed image to the original image.
        
        Args:
        
            pos (QPoint): The position on the displayed image.
        
        Returns:
            
                QPoint: The position on the original image.
        """
        displayed_image_size = self.current_pixmap.size()
        offset_x = (self.width() - self.current_pixmap.width()) // 2
        offset_y = (self.height() - self.current_pixmap.height()) // 2
        relative_x = pos.x() - offset_x
        relative_y = pos.y() - offset_y
        if 0 <= relative_x < displayed_image_size.width() and 0 <= relative_y < displayed_image_size.height():
            return QPoint(int(relative_x / self.scale_factor), int(relative_y / self.scale_factor))
        return None
    
    def select_rectangle(self, pos):
        """
        Select the rectangle nearest to the selected point on the displayed image.
        
        Args:
            pos (QPoint): The position on the displayed image.
            
        Returns:
            dict: The selected rectangle dictionary with its attributes.
        """
        selected_rectangles = []
        selected_rectangles_id = []

        # Map the click position to the original image coordinates
        # mapped_pos = self.map_to_original_image(pos)

        # Iterate through all rectangles to find the ones containing the point
        for rect in self.rectangles:
            rect_obj = QRect(rect["bbox"][0], rect["bbox"][1], rect["bbox"][2], rect["bbox"][3])
            if rect_obj.contains(pos):
                selected_rectangles.append(rect)
                selected_rectangles_id.append(rect["id"])

        # If multiple rectangles contain the point, find the one closest to the point
        if selected_rectangles:
            closest_rect = min(
                selected_rectangles,
                key=lambda rect: self.distance_to_center(pos, rect["bbox"])
            )
            self.selected_rectangles = closest_rect["id"]


    def distance_to_center(self, pos, bbox):
        """
        Calculate the distance from a point to the center of a bounding box.
        
        Args:
            pos (QPoint): The position point.
            bbox (list): The bounding box coordinates [x, y, width, height].
            
        Returns:
            float: The distance from the point to the center of the bounding box.
        """
        center_x = bbox[0] + bbox[2] / 2
        center_y = bbox[1] + bbox[3] / 2
        return (pos.x() - center_x) ** 2 + (pos.y() - center_y) ** 2
    
    def find_object_to_edit(self, click_pos):
        # Iterate from top to bottom (reverse order) to find the topmost object
        for rectangle in reversed(self.rectangles):
            rect = rectangle['bbox']
            vertices = [QPoint(rect[0], rect[1]),  # top-left
                        QPoint(rect[0] + rect[2], rect[1]),  # top-right
                        QPoint(rect[0], rect[1] + rect[3]),  # bottom-left
                        QPoint(rect[0] + rect[2], rect[1] + rect[3])]  # bottom-right
            mapped_pos = self.map_to_original_image(click_pos)
            for i, vertex in enumerate(vertices):
                # scaled_vertex = self.scale_point(vertex)
                if self.distance(vertex, mapped_pos) <= 20:
                    return rectangle['id'], i
        return None, None


    def get_selected_rectangle(self):
        """
        Get the selected rectangle.
        
        Returns:
        
            dict: The selected rectangle.
        """
        for rect in self.rectangles:
            if rect["id"] == self.selected_rectangles:
                return rect
        return None
    
    def move_vertex(self, vertex_index, new_pos):
        if self.selected_rectangles is not None:
            for rectangle in self.rectangles:
                if rectangle['id'] == self.selected_rectangles:
                    rect = rectangle['bbox']
                    if vertex_index == 0:
                        delta_w = rect[0] - new_pos.x()
                        delta_h = rect[1] - new_pos.y()
                        rect[0] = new_pos.x()
                        rect[1] = new_pos.y()
                        rect[2] = rect[2] + delta_w
                        rect[3] = rect[3] + delta_h
                    elif vertex_index == 1:
                        delta_w = new_pos.x() - (rect[0] + rect[2])
                        delta_h = rect[1] - new_pos.y()
                        rect[1] = new_pos.y()
                        rect[2] = rect[2] + delta_w
                        rect[3] = rect[3] + delta_h
                        # rect[2] = new_pos.x() - rect[0]
                        # rect[1] = new_pos.y()
                    elif vertex_index == 2:
                        delta_w = rect[0] - new_pos.x()
                        delta_h = new_pos.y() - (rect[1] + rect[3])
                        rect[0] = new_pos.x()
                        rect[2] = rect[2] + delta_w
                        rect[3] = rect[3] + delta_h
                    elif vertex_index == 3:
                        delta_w = new_pos.x() - (rect[0] + rect[2])
                        delta_h = new_pos.y() - (rect[1] + rect[3])
                        rect[2] = rect[2] + delta_w
                        rect[3] = rect[3] + delta_h
                    break

    def move_rectangle(self, new_pos):
        if self.selected_rectangles is not None:
            rect = self.get_selected_rectangle()
            if rect is not None:
                dx = new_pos.x() - self.last_mouse_position.x()
                dy = new_pos.y() - self.last_mouse_position.y()
                rect["bbox"][0] += int(dx)
                rect["bbox"][1] += int(dy)
                # rect["bbox"][0] += int(dx / self.scale_factor)
                # rect["bbox"][1] += int(dy / self.scale_factor)
                # self.last_mouse_position = new_pos
    

    def select_label_from_label_list(self):
        """Generate a label selection popup dialog."""
        dialog = LabelPopup(self.label_list,self.update_label_list_slot_transmitter, self)
        if dialog.exec_():
            selected_label, _ = dialog.get_selected_item()
            print(f"label list: {self.label_list}")
            return selected_label
        return None

    def update_label_list(self, label_list):
        self.label_list = label_list
        print(f"Label List: {self.label_list}")
    
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
        self.rectangles.clear()
        for anno in annotation:
            category_id = anno['category_id']
            id = anno['id']
            bbox = anno['bbox']
            polygon = anno['segmentation']
            self.rectangles.append({"category_id": category_id, "bbox": bbox, "id": id, "polygon": polygon})
        if len(self.rectangles) > 0:
            self.object_list_action_slot.emit([self.rectangles], OBJECT_LIST_ACTION.UPDATE)
        print(f"Rectangles: {len(self.rectangles)}")
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
            category_id = rect['category_id']
            id = rect['id']
            x, y, w, h = rect['bbox'][0], rect['bbox'][1], rect['bbox'][2], rect['bbox'][3]
            area = w * h
            segmentation = [[]]
            iscrowd = 0
            annotations.append({
                "id": id,
                "category_id": category_id,
                "bbox": [x, y, w, h],
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
            self.clear_annotation()
            # if len(self.rectangles) > 0:
            self.object_list_action_slot.emit([None], OBJECT_LIST_ACTION.CLEAR)
            self.annotation_mode = ANNOTATION_MODE.NONE
        elif self.annotation_mode == ANNOTATION_MODE.DELETE:
            if self.selected_rectangles is not None:
                for idx, rect in enumerate(self.rectangles):
                    if rect["id"] == self.selected_rectangles:
                        self.rectangles.pop(idx)
                        self.object_list_action_slot.emit([self.rectangles], OBJECT_LIST_ACTION.REMOVE)
                        self.selected_rectangles = None
                        break
                self.selected_rectangles = None
            self.annotation_mode = ANNOTATION_MODE.CREATE
        elif self.annotation_mode == ANNOTATION_MODE.EDIT:
            pass
        elif self.annotation_mode == ANNOTATION_MODE.CREATE:
            pass
        else:
            pass
        self.update()

    def select_object(self, object_id):
        if object_id == -1:
            self.selected_rectangles = None
        else:
            self.selected_rectangles = object_id