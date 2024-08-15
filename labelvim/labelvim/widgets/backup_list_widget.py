from PyQt5.QtCore import pyqtSignal, QRect, QStringListModel, Qt
from PyQt5.QtWidgets import QListView, QInputDialog, QMessageBox, QMenu, QAction

class CustomLabelListWidget(QListView):
    """
    A custom QListView widget for displaying and managing a list of labels. 
    Allows adding new labels by double-clicking and supports updating the list 
    based on an annotation type.

    Attributes:
        model (QStringListModel): The data model for storing label names.
        label_list (list): A list to store label names displayed in the list view.
        annotation_type (str): The type of annotation currently being handled.
    """
    update_label_list_slot_transmitter = pyqtSignal(list)  # Signal to update the label list
    update_label_list_slot_receiver = pyqtSignal(list)  # Signal to update the label list

    def __init__(self, parent=None):
        """
        Initializes the CustomLabelListWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super(CustomLabelListWidget, self).__init__(parent)
        self.model = QStringListModel()
        self.label_list = []
        self.annotation_type = "Rectangle"
        self.set_geometry()
        self.set_model()
        self.set_label_list()
        self.update_label_list_slot_receiver.connect(self.set_label_list)
        self.model.dataChanged.connect(self.on_data_changed)  # Connect the dataChanged signal

    def set_geometry(self):
        """
        Sets the geometry of the list view widget.
        """
        self.setGeometry(QRect(1390, 30, 450, 192))

    def set_model(self):
        """
        Sets the data model for the list view and enables updates.
        """
        self.setModel(self.model)
        self.setUpdatesEnabled(True)
        self.setEditTriggers(QListView.NoEditTriggers)  # Disable inline editing by default

    def set_label_list(self, label_list=[]):
        """
        Updates the list view with a new list of labels.

        Args:
            label_list (list, optional): A list of label names to display. Defaults to an empty list.
        """
        if isinstance(label_list, list) and len(label_list) > 0:
            self.label_list = label_list
            self.model.setStringList(self.label_list)

    def clear_list(self):
        """
        Clears all items from the list view.
        """
        self.model.setStringList([])

    def __update_list(self, annotation_type):
        """
        Updates the list of labels based on the provided annotation type.

        Args:
            annotation_type (str): The type of annotation to use for updating the list.
        """
        if annotation_type in label_list_reader.label_list:
            self.set_label_list(label_list_reader.label_list[annotation_type])

    def update_annotation_type(self, annotation_type):
        """
        Updates the annotation type currently being used.

        Args:
            annotation_type (str): The new annotation type to use.
        """
        if annotation_type == "Object Detection":
            self.annotation_type = "Rectangle"
        elif annotation_type == "Segmentation":
            self.annotation_type = "Polygon"
        else:
            self.annotation_type = "None"
        self.__update_list(self.annotation_type)

    def mouseDoubleClickEvent(self, event):
        """
        Handles mouse double-click events on the list view. Prompts the user to 
        add a new label if the left mouse button is double-clicked.

        Args:
            event (QMouseEvent): The mouse event object.
        """
        if self.annotation_type != "None" and event.button() == Qt.LeftButton:
            new_label, ok = QInputDialog.getText(self, 'Add New Label', 'Enter a new label:')
            if ok and new_label.strip():
                self.add_label(new_label)

        super(CustomLabelListWidget, self).mousePressEvent(event)

    def add_label(self, new_label):
        """
        Adds a new label to the list view.

        Args:
            new_label (str): The label to add to the list.
        """
        if new_label not in self.label_list:
            self.label_list.append(new_label)
            self.model.setStringList(self.label_list)
            self.update_label_list_slot_transmitter.emit(self.label_list)  # Emit signal to update the list
            label_list_reader.label_list[self.annotation_type] = self.label_list
            label_list_reader.update(label_list_reader.label_list)
        else:
            QMessageBox.warning(self, 'Warning', 'This label already exists.')

    def remove_label(self, label):
        """
        Removes a label from the list view.

        Args:
            label (str): The label to remove from the list.
        """
        if label in self.label_list:
            self.label_list.remove(label)
            self.model.setStringList(self.label_list)

    def contextMenuEvent(self, event):
        """
        Handles the context menu event, providing an option to edit the selected item.

        Args:
            event (QContextMenuEvent): The context menu event object.
        """
        index = self.indexAt(event.pos())
        if index.isValid():
            menu = QMenu(self)
            edit_action = QAction('Edit', self)
            edit_action.triggered.connect(lambda: self.edit_label(index))
            menu.addAction(edit_action)
            menu.exec_(event.globalPos())

    def edit_label(self, index):
        """
        Triggers inline editing for the selected item.

        Args:
            index (QModelIndex): The index of the item to be edited.
        """
        self.edit(index)

    def on_data_changed(self, topLeft, bottomRight, roles):
        """
        Slot that is triggered when the data in the model is changed.

        Args:
            topLeft (QModelIndex): The top-left index of the changed data.
            bottomRight (QModelIndex): The bottom-right index of the changed data.
            roles (list): The roles that have changed.
        """
        self.label_list = self.model.stringList()
        self.update_label_list_slot_transmitter.emit(self.label_list)  # Emit signal to update the list
