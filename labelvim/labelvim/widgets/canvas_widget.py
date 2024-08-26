from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QImage
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtWidgets, QtCore
from labelvim.labelvim.widgets.label_pupop import LabelPopup
from labelvim.labelvim.utils.config import ANNOTATION_MODE, OBJECT_LIST_ACTION, ANNOTATION_TYPE
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
        self.polygon_points = []
        self.polygon_move_point = None
        self.rectangles = []  # List to store drawn rectangles
        self.original_pixmap = None
        self.current_pixmap = None
        self.brush_color = QColor(0, 0, 255, 50)
        self.polygon_brush_color = QColor(255, 0, 0, 50)
        self.pen_color = QColor(0, 255, 255)
        self.title_pen_color = QColor(0, 255, 255)
        self.selected_rectangle_brush_color = QColor(255, 0, 255, 50)
        self.selected_polygon_brush_color = QColor(255, 255, 0, 50)
        self.selected_object = None  # List to store selected rectangles
        self.selected_object_subset = None
        self.selected_vertex = None
        self.line_segment = None
        self.moving_object = False
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
        self.annotation_type = ANNOTATION_TYPE.NONE
        self.scale_factor_w, self.scale_factor_h = 1, 1
        self.zoom_in_scale_factor = 1.25
        self.zoom_out_scale_factor = 0.8
        self.max_scale_factor = 6
        self.point_click_radious = 5 # The radious of the point click

    def update_annotation_type(self, annotation_type):
        print(f"Annotation Type: {annotation_type}")
        print(f"OLD Annotation Type: {self.annotation_type}")
        self.annotation_type = annotation_type
        print(f"UPDATED Annotation Type: {self.annotation_type}")

    def load_image(self, file_name):
        self.clear_annotation()
        self.selected_object = None
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
        self.start_point = None
        self.end_point = None
        self.polygon_points.clear()
        self.polygon_move_point = None
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
                if self.annotation_type == ANNOTATION_TYPE.BBOX:
                    if self.annotation_mode == ANNOTATION_MODE.CREATE:
                        start_point = self.map_to_original_image(click_pos)
                        if start_point:
                            self.start_point = start_point
                    if self.annotation_mode == ANNOTATION_MODE.EDIT:
                        self.selected_object, self.selected_vertex = self.find_object_to_edit(click_pos)
                        print(f"Selected Rectangle: {self.selected_object}, Selected Vertex: {self.selected_vertex}")
                        if self.selected_vertex is None and self.selected_object is None:
                            # Start moving the rectangle if no vertex is selected
                            self.moving_object = True
                            self.last_mouse_position = self.map_to_original_image(click_pos)
                            if self.last_mouse_position is None:
                                self.moving_object = False
                            else:
                                self.select_rectangle(self.last_mouse_position)
                            print(f"Selected Rectangle: {self.selected_object}")
                elif self.annotation_type == ANNOTATION_TYPE.POLYGON:
                    new_map = self.map_to_original_image(click_pos)
                    self.polygon_move_point = None
                    if self.annotation_mode == ANNOTATION_MODE.CREATE:
                        if len(self.polygon_points) == 0:
                            # print("First Point")
                            self.polygon_points.append(new_map)
                        elif len(self.polygon_points) == 1:
                            if self.distance(self.polygon_points[0], new_map) > 10:
                                # print("Second Point")
                                self.polygon_points.append(new_map)
                        elif len(self.polygon_points) >=2:
                            # print("More than 2 points")
                            if self.distance(self.polygon_points[0], new_map) < 10:
                                # print("Last Point")
                                self.polygon_move_point = None
                                self.update_rectangle(poly = self.polygon_points)
                                self.polygon_points.clear()
                            else:
                                # print("More than 2 points")
                                self.polygon_points.append(new_map)
                    elif self.annotation_mode == ANNOTATION_MODE.EDIT:
                        self.selected_object, self.selected_object_subset,self.selected_vertex, self.line_segment = self.find_polygon_to_edit(new_map)
                        print(f"Selected Rectangle: {self.selected_object}, Selected Rectangle subset: {self.selected_object_subset} Selected Vertex: {self.selected_vertex}, Line Segment: {self.line_segment}")

                        if self.selected_vertex is None and self.selected_object is None and self.line_segment is None:
                            print("Moving Polygon")
                            print(f"Selected Rectangle: {self.selected_object}")
                            self.moving_object = True
                            self.last_mouse_position = new_map
                            print(f"Last Mouse Position: {self.last_mouse_position}")
                            if self.last_mouse_position is None:
                                self.moving_object = False
                            else:
                                self.select_polygon(new_map)
                            print(f"Selected Rectangle: {self.selected_object}")
                        # self.selected_object = self.select_polygon(new_map)
                        # if self.selected_object is not None:
                        #     self.polygon_move_point = new_map
        self.update()

    def mouseMoveEvent(self, event):
        if self.original_pixmap:
            click_pos = event.pos()
            if self.annotation_type == ANNOTATION_TYPE.BBOX:
                if self.start_point and self.annotation_mode == ANNOTATION_MODE.CREATE:
                    end_point = self.map_to_original_image(click_pos)
                    if end_point:
                        self.end_point = end_point
                
                elif self.selected_vertex is not None and self.annotation_mode == ANNOTATION_MODE.EDIT:
                    # Resize the selected rectangle
                    new_pos = self.map_to_original_image(click_pos)
                    if new_pos:
                        self.move_vertex(self.selected_vertex, new_pos)
                elif self.moving_object and self.annotation_mode == ANNOTATION_MODE.EDIT:
                    # Move the selected rectangle
                    new_pos = self.map_to_original_image(click_pos) # origional image dimension
                    if new_pos:
                        self.move_rectangle(new_pos)
                        self.last_mouse_position = new_pos # in repect to origional image dimension
            elif self.annotation_type == ANNOTATION_TYPE.POLYGON:
                new_map = self.map_to_original_image(click_pos)
                if self.annotation_mode == ANNOTATION_MODE.EDIT:
                    if self.selected_object is not None and self.selected_vertex is not None:
                        # new_map = self.map_to_original_image(click_pos)
                        if new_map:
                            self.move_polygon_vertex(new_map)
                    elif self.selected_object is not None and self.line_segment is not None:
                        new_map = self.map_to_original_image(click_pos)
                        self.last_mouse_position = new_map
                        if new_map:
                            self.add_point_to_polygon(new_map)
                            self.selected_vertex = self.line_segment[1]
                            self.line_segment = None
                    elif self.moving_object and self.selected_object is not None:
                        # print("Moving Polygon")
                        new_map = self.map_to_original_image(click_pos)
                        if new_map:
                            self.move_polygon(new_map)
                            self.last_mouse_position = new_map
        self.update()
    
    def mouseReleaseEvent(self, event):
        if self.original_pixmap and event.button() == Qt.LeftButton:
            click_pos = event.pos()
            if self.annotation_type == ANNOTATION_TYPE.BBOX:
                if self.start_point and self.annotation_mode == ANNOTATION_MODE.CREATE:
                    end_point = self.map_to_original_image(click_pos)
                    if end_point:
                        self.end_point = end_point
                        rect = QRect(self.start_point, self.end_point).normalized()
                        if self.distance(self.start_point, self.end_point) > 20:
                            self.update_rectangle(bbox = rect)
                elif self.selected_vertex is not None and self.annotation_mode == ANNOTATION_MODE.EDIT:
                    self.selected_vertex = None
                elif self.moving_object and self.annotation_mode == ANNOTATION_MODE.EDIT:
                    self.moving_object = False
                self.start_point = None
                self.end_point = None
            elif self.annotation_type == ANNOTATION_TYPE.POLYGON:
                if self.selected_vertex is not None and self.annotation_mode == ANNOTATION_MODE.EDIT:
                    self.selected_vertex = None
                elif self.moving_object and self.annotation_mode == ANNOTATION_MODE.EDIT:
                    self.moving_object = False
                self.last_mouse_position = None
        self.selected_object = None
        self.selected_object_subset = None
        self.update()
    
    # def keyPressEvent(self, event):
    #     # Capture the key press event and display the key information
    #     key = event.key()

    #     if self.annotation_type == ANNOTATION_TYPE.POLYGON:
    #         print("Delete Key Pressed")
    #         if key == Qt.Key_Delete:
                
    #             if self.selected_object is not None and self.selected_vertex is None:
    #                 self.rectangles.pop(self.selected_object)
    #                 # emit signal to remove object from the object list
    #                 self.object_list_action_slot.emit([self.selected_object], OBJECT_LIST_ACTION.REMOVE)
    #                 self.selected_object = None
    #             elif self.selected_object is not None and self.selected_vertex is not None:
    #                 self.remove_point_from_polygon(self.selected_vertex)
    #                 self.selected_vertex = None

        # Optional: If you want to handle the key press and not propagate it further, you can skip calling the base class implementation.
        # If you want the key press to be handled by the parent class as well, call the superclass's method:
        # super().keyPressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        # print("self.rectangles: ", self.rectangles)
        if self.current_pixmap:
            painter = QPainter(self)
            offset_x = (self.width() - self.current_pixmap.width()) // 2
            offset_y = (self.height() - self.current_pixmap.height()) // 2
            painter.drawPixmap(offset_x, offset_y, self.current_pixmap)
            # print(f"offset_x: {offset_x}, offset_y: {offset_y}")
            painter.setPen(QPen(self.pen_color, 2, Qt.SolidLine))
            painter.setBrush(QBrush(self.brush_color))
            # print(f"Annotation Type: {self.annotation_type}")
            if self.annotation_type == ANNOTATION_TYPE.BBOX:
                # print(f"self.rectangles: {self.rectangles}")
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
                    if self.selected_object is not None and self.selected_object == rectangle["id"]:
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
            elif self.annotation_type == ANNOTATION_TYPE.POLYGON:
                # print(f"self.rectangles: {self.rectangles}")
                if self.polygon_points:
                    polygon_points = [QPoint(offset_x+int(point.x() * self.scale_factor), offset_y+int(point.y() * self.scale_factor)) for point in self.polygon_points]
                    polgon = QPolygon(polygon_points)
                    painter.setPen(QPen(self.pen_color, 2, Qt.SolidLine))
                    painter.setBrush(QBrush(self.polygon_brush_color))
                    painter.drawPolygon(polgon)
                    for point in polygon_points:
                        painter.drawEllipse(point, 5, 5)
                for rectangle in self.rectangles:
                    rect, index, polgons = rectangle['bbox'], rectangle["category_id"], rectangle["polygon"]
                    # print(f"Polygon: {polgon}")
                    painter.setPen(QPen(self.pen_color, 2, Qt.SolidLine))
                    painter.setBrush(QBrush(self.brush_color))
                    if self.selected_object is not None and self.selected_object == rectangle["id"]:
                        painter.setBrush(QBrush(self.selected_rectangle_brush_color))
                    rect = QRect(offset_x+int(rect[0] * self.scale_factor), offset_y+int(rect[1] * self.scale_factor), int(rect[2] * self.scale_factor), int(rect[3] * self.scale_factor))
                    painter.drawRect(rect)
                    painter.setPen(QPen(self.pen_color, 2, Qt.SolidLine))
                    painter.setBrush(QBrush(self.polygon_brush_color))
                    if self.selected_object is not None and self.selected_object == rectangle["id"]:
                        painter.setBrush(QBrush(self.selected_polygon_brush_color))
                    for polgon in polgons: # modified as per polygon list
                        # print(f"Polygon: {polgon}")
                        painter.drawPolygon(QPolygon([QPoint(offset_x+int(point.x() * self.scale_factor), offset_y+int(point.y() * self.scale_factor)) for point in polgon]))
                        for point in polgon:
                            painter.drawEllipse(QPoint(offset_x+int(point.x() * self.scale_factor), offset_y+int(point.y() * self.scale_factor)), 5, 5)
                    text_label = self.label_list[index]
                    painter.setPen(QPen(self.title_pen_color, 2, Qt.SolidLine))
                    painter.setBrush(QBrush(QColor(255, 255, 255, 75)))
                    painter.drawRect(rect.topLeft().x(), rect.topLeft().y() - 20, rect.width(), 20)
                    painter.setPen(QPen(QColor(0,0,0), 2, Qt.SolidLine))
                    painter.drawText(rect.topLeft().x(), rect.topLeft().y() - 5, text_label)
                    
        self.update()
    
    def update_rectangle(self, **kwargs): # need to rename later
        bbox = kwargs.get('bbox')
        poly = kwargs.get('poly')
        if bbox:
            label_selected, selected_id = self.select_label_from_label_list()
            print(f"Selected Label: {label_selected}")
            if label_selected:
                try:
                    index = self.label_list.index(label_selected)
                    self.rectangles.append({"category_id": index, "bbox": [bbox.x(), bbox.y(), bbox.width(), bbox.height()], "id": len(self.rectangles), "polygon": []})
                    # emit signal to add object to the object list
                    self.object_list_action_slot.emit([self.rectangles[-1]], OBJECT_LIST_ACTION.ADD)
                except ValueError:
                    print("Label not found in the label list")
        if poly:
            label_selected, selected_id = self.select_label_from_label_list()
            print(f"Selected Label: {label_selected}")
            if label_selected:
                try:
                    if selected_id == -1:
                        index = self.label_list.index(label_selected)
                        polygon = QPolygon(poly)
                        # print(f"Polygon: {poly}")
                        # print(f"Polygon: {polygon}")
                        bbox = polygon.boundingRect()
                        # print(f"Bounding Box: {bbox}")
                        self.rectangles.append({"category_id": index, "bbox": [bbox.x(), bbox.y(), bbox.width(), bbox.height()], "id": len(self.rectangles), "polygon": [poly.copy()]})
                        # emit signal to add object to the object list
                        self.object_list_action_slot.emit([self.rectangles[-1]], OBJECT_LIST_ACTION.ADD)
                    else:
                        # print(f"Selected ID: {selected_id}")
                        # print(f"rectangles: {self.rectangles[selected_id]}")
                        rectanlge = self.rectangles[selected_id]
                        bbox_c = rectanlge["bbox"]
                        # print(f"Bounding Box: {bbox_c}")
                        bbox = QRect(bbox_c[0], bbox_c[1], bbox_c[2], bbox_c[3])
                        # poly_prev = self.rectangles[selected_id]["polygon"]
                        self.rectangles[selected_id]["polygon"].append(poly.copy())
                        # print(f"Polygons: {len(self.rectangles[selected_id]['polygon'])}")
                        # print(f"Polygons: {self.rectangles[selected_id]['polygon']}")
                        polygon = QPolygon(poly.copy())
                        bbox_1 = polygon.boundingRect()
                        bbox = bbox.united(bbox_1)
                        self.rectangles[selected_id]["bbox"] = [bbox.x(), bbox.y(), bbox.width(), bbox.height()]

                except ValueError:
                    print("Label not found in the label list")
    @staticmethod
    def distance(p1, p2):
        """
        Calculate the distance between two points.
        
        Args:
        
            p1 (QPoint): The first point.
            p2 (QPoint): The second point.
            
            Returns:
            
                float: The distance between the two points.
                
        """
        return ((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2)**0.5
    
    @staticmethod
    def distance_to_line_segment(p, v, w):
        """Calculate the distance from point p to the line segment vw."""
        l2 = CanvasWidget.distance(v, w) ** 2
        if l2 == 0.0:
            return CanvasWidget.distance(p, v)
        t = max(0, min(1, ((p.x() - v.x()) * (w.x() - v.x()) + (p.y() - v.y()) * (w.y() - v.y())) / l2))
        projection = QPoint(int(v.x() + t * (w.x() - v.x())), int(v.y() + t * (w.y() - v.y())))
        return CanvasWidget.distance(p, projection)

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
            self.selected_object = closest_rect["id"]

    @staticmethod
    def distance_to_center(pos, bbox):
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


    def get_selected_object(self):
        """
        Get the selected rectangle.
        
        Returns:
        
            dict: The selected rectangle.
        """
        for rect in self.rectangles:
            if rect["id"] == self.selected_object:
                return rect
        return None
    
    def move_vertex(self, vertex_index, new_pos):
        if self.selected_object is not None:
            for rectangle in self.rectangles:
                if rectangle['id'] == self.selected_object:
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
        if self.selected_object is not None:
            rect = self.get_selected_object()
            if rect is not None:
                dx = new_pos.x() - self.last_mouse_position.x()
                dy = new_pos.y() - self.last_mouse_position.y()
                rect["bbox"][0] += int(dx)
                rect["bbox"][1] += int(dy)
                
    
    
    def select_polygon(self, pos):
        selected_polygon = []
        selected_polygon_id = []
        selected_polygon_id_subset = []
        for polygons in self.rectangles:
            for poly_idx, polygon in enumerate(polygons['polygon']):
                poly = polygon.copy()
                # polygon_points = [QPoint(point.x(), point.y()) for point in poly]
                # polygon_points = [QPoint(point[0] * self.scale_factor, point[1] * self.scale_factor) for point in polygon_points]
                polygon_obj = QPolygon(poly)
                if polygon_obj.containsPoint(pos, Qt.OddEvenFill):
                    selected_polygon.append(polygon)
                    selected_polygon_id.append(polygons['id'])
                    selected_polygon_id_subset.append(poly_idx)
        if selected_polygon:
            closest_polygon = min(selected_polygon, key=lambda polygon: self.calculate_polygon_area(polygon))
            self.selected_object = selected_polygon_id[selected_polygon.index(closest_polygon)]
            self.selected_object_subset = selected_polygon_id_subset[selected_polygon.index(closest_polygon)]
            
            # print(f"Selected Polygon: {selected_polygon}")
            # closest_polygon = min(selected_polygon, key=lambda polygon: self.calculate_polygon_area(polygon))
            # print(f"Selected Polygon: {closest_polygon}")
            # print(f"Selected Polygon: {closest_polygon['id']}")
            # self.selected_object = closest_polygon["id"]
    
    @staticmethod
    def calculate_polygon_area(polygon):
        area = 0
        # polygon = QPolygon(polygon['polygon'])
        polygon = QPolygon(polygon)
        for i in range(polygon.count()):
            j = (i + 1) % polygon.count()
            area += polygon.point(i).x() * polygon.point(j).y()
            area -= polygon.point(j).x() * polygon.point(i).y()
        return abs(area) / 2

    def move_polygon(self, new_pos):
        if self.selected_object is not None:
            poly = self.get_selected_object()
            dx = new_pos.x() - self.last_mouse_position.x()
            dy = new_pos.y() - self.last_mouse_position.y()

            for i, point in enumerate(poly['polygon'][self.selected_object_subset]):
                poly['polygon'][self.selected_object_subset][i] = QPoint(point.x() + dx, point.y() + dy)
            for poly_idx, polygon in enumerate(poly['polygon']):
                if poly_idx == 0:
                    bbox = QPolygon(polygon).boundingRect()
                else:
                    bbox = bbox.united(QPolygon(polygon).boundingRect())
            # bbox = QPolygon(poly['polygon'][self.selected_object_subset]).boundingRect()
            poly['bbox'] = [bbox.x(), bbox.y(), bbox.width(), bbox.height()]
            self.last_mouse_position = new_pos
    
    def move_polygon_vertex(self, new_pos):
        if self.selected_object is not None:
            poly = self.get_selected_object()
            if poly is not None:
                poly['polygon'][self.selected_object_subset][self.selected_vertex] = new_pos
                
                for poly_idx, polygon in enumerate(poly['polygon']):
                    if poly_idx == 0:
                        bbox = QPolygon(polygon).boundingRect()
                    else:
                        bbox = bbox.united(QPolygon(polygon).boundingRect())
                    # bbox = QPolygon(poly['polygon'][self.selected_object_subset]).boundingRect()
                    poly['bbox'] = [bbox.x(), bbox.y(), bbox.width(), bbox.height()]
                
                # bbox = QPolygon(poly['polygon']).boundingRect()
                # print(f"Bounding Box in mover polygon vertex: {bbox}")
                # poly['bbox'] = [bbox.x(), bbox.y(), bbox.width(), bbox.height()]
                # print(f"Bounding Box in mover polygon vertex: {poly['bbox']}")
    
    def add_point_to_polygon(self, new_pos):
        if self.selected_object is not None:
            poly = self.get_selected_object()
            if poly is not None:
                poly['polygon'][self.selected_object_subset].insert(self.line_segment[1], new_pos)
                for poly_idx, polygon in enumerate(poly['polygon']):
                    if poly_idx == 0:
                        bbox = QPolygon(polygon).boundingRect()
                    else:
                        bbox = bbox.united(QPolygon(polygon).boundingRect())
                    # bbox = QPolygon(poly['polygon'][self.selected_object_subset]).boundingRect()
                    poly['bbox'] = [bbox.x(), bbox.y(), bbox.width(), bbox.height()]
                # bbox = QPolygon(poly['polygon']).boundingRect()
                # poly['bbox'] = [bbox.x(), bbox.y(), bbox.width(), bbox.height()]
    
    # def remove_point_from_polygon(self, point_index):
    #     if self.selected_object is not None:
    #         poly = self.get_selected_object()
    #         if poly is not None:
    #             poly['polygon'].pop(point_index)
    #             bbox = QPolygon(poly['polygon']).boundingRect()
    #             poly['bbox'] = [bbox.x(), bbox.y(), bbox.width(), bbox.height()]
    
    def find_polygon_to_edit(self, click_pos):
        for polygons in reversed(self.rectangles):
            polygon = polygons['polygon']
            # polygon_obj = QPolygon(poly)
            
            # Check if click_pos is near any vertex of the polygon
            for poly_idx, poly in enumerate(polygon):
                for i, point in enumerate(poly):
                    if CanvasWidget.distance(QPoint(point.x(), point.y()), click_pos) <= 10:
                        return polygons['id'], poly_idx, i, None
                
                # Check if click_pos is on any line segment of the polygon
                for i, point in enumerate(poly):
                    v = QPoint(point.x(), point.y())
                    w = QPoint(poly[(i + 1) % len(poly)].x(), poly[(i + 1) % len(poly)].y())
                    # print(f"V: {v}, W: {w}")
                    # print(f"Click Pos: {click_pos}")
                    if CanvasWidget.distance_to_line_segment(click_pos, v, w) <= 10:
                        return polygons['id'], poly_idx, None, (i, (i + 1) % len(poly))

        return None, None, None, None

    def select_label_from_label_list(self):
        """Generate a label selection popup dialog."""
        dialog = LabelPopup(self.label_list, self.rectangles, self.annotation_type, self.update_label_list_slot_transmitter, self)
        if dialog.exec_():
            selected_label, _, selected_id = dialog.get_selected_item()
            print(f"label list: {self.label_list}")
            print(f"Selected Label: {selected_label}")
            print(f"Selected ID: {selected_id}")
            return selected_label, selected_id
        return None, None

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
            poly = anno['segmentation']
            polygons = []
            for polygon in poly:
                polygons.append([QPoint(polygon[i], polygon[i+1]) for i in range(0, len(polygon), 2)])
            # polygon = QPolygon([QPoint(poly[i], poly[i+1]) for i in range(0, len(poly), 2)])
            self.rectangles.append({"category_id": category_id, "bbox": bbox, "id": id, "polygon": polygons.copy()})
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
            polygons = []
            for polygon in rect['polygon']:
                poly = []
                for point in polygon:
                    poly.append(point.x())
                    poly.append(point.y())
                polygons.append(poly)
            # for point in rect['polygon']:
            #     polygon.append(point.x())
            #     polygon.append(point.y())
            segmentation = polygons
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
            if self.selected_object is not None:
                for idx, rect in enumerate(self.rectangles):
                    if rect["id"] == self.selected_object:
                        self.rectangles.pop(idx)
                        self.selected_object = None
                        break
                # update the new object id
                for idx, rect in enumerate(self.rectangles):
                    rect["id"] = idx
                self.object_list_action_slot.emit([self.rectangles], OBJECT_LIST_ACTION.REMOVE)
                self.selected_object = None
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
            self.selected_object = None
        else:
            self.selected_object = object_id