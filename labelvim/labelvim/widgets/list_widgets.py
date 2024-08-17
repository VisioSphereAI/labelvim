from PyQt5 import QtWidgets
from PyQt5.QtCore import QStringListModel, Qt, QRect, pyqtSignal, QModelIndex, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QMenu, QAction

# External imports
from labelvim.utils.config import ANNOTATION_TYPE, OBJECT_LIST_ACTION
from labelvim.widgets.custom_delegets import CustomDelegate
from enum import Enum

class CustomListViewWidget(QtWidgets.QListView):
    """
    A custom QListView widget with added functionalities such as item selection, 
    item removal, list clearing, and handling mouse events to toggle checkbox states.

    Signals:
        update_list (list): Emitted to update the list of labels.
        notify_selected_item (str): Emitted when an item is selected, 
                                    containing the selected item's text.

    Attributes:
        model (QStandardItemModel): The data model for storing list items with checkboxes.
        label_list (list): A list to store label names displayed in the list view.
    """
    
    update_list = pyqtSignal(list)
    notify_selected_item = pyqtSignal(str, int)

    def __init__(self, parent=None):
        """
        Initializes the CustomListViewWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super(CustomListViewWidget, self).__init__(parent)
        self.model = QStandardItemModel()
        self.label_list = []
        self.set_geometry()
        self.set_model()
        self.set_label_list()
        self.selectionModel().currentChanged.connect(self.get_selected_item)
        self.update_list.connect(self.set_label_list)
        self.index = 0
    
    def set_geometry(self):
        """
        Sets the geometry of the list view widget.
        """
        self.setGeometry(QRect(1390, 531, 450, 271))

    def set_model(self):
        """
        Sets the data model for the list view and enables updates.
        """
        self.setModel(self.model)
        self.setUpdatesEnabled(True)

    def set_label_list(self, label_list=[]):
        """
        Updates the list view with a new list of labels.

        Args:
            label_list (list, optional): A list of label names to display. Defaults to an empty list.
        """
        # print(f"Label List in set label list: {label_list}")
        if isinstance(label_list, list) and len(label_list) > 0:
            self.model.clear()  # Clear the model before updating
            self.label_list = label_list
            for file_name in self.label_list:
                item = QStandardItem(file_name)
                item.setCheckable(True)
                item.setEditable(False)
                # Store the state in the item
                item.setData(False, Qt.UserRole + 1)  # False means unchecked
                self.model.appendRow(item)
            self.set_current_index(self.index)
    
    def get_selected_item(self, current, previous):
        """
        Emits the signal with the currently selected item's text.

        Args:
            current (QModelIndex): The index of the current item.
            previous (QModelIndex): The index of the previously selected item.
        """
        print(f"Current: {current.row()}")
        # if current.row() < 0:
        #     self.reset()
        #     return
        self.index = current.row() #self.selectedIndexes()[0].row()
        self.notify_selected_item.emit(self.model.data(current, Qt.DisplayRole), self.index)
    
    def remove_selected_item(self):
        """
        Removes the currently selected item from the list view.
        """
        if len(self.selectedIndexes()) > 0:
            self.model.removeRow(self.selectedIndexes()[0].row())
    
    def update_current_index(self, index):
        """
        Updates the current selection in the list view to the specified index.

        Args:
            index (QModelIndex): The index to set as the current selection.
        """
        self.setCurrentIndex(index)
    
    def next_index(self):
        """
        Moves the selection to the next item in the list view, if possible.
        """
        self.index = self.selectedIndexes()[0].row()
        if self.index < self.model.rowCount() - 1:
            self.setCurrentIndex(self.model.index(self.index + 1, 0))
            self.index = self.selectedIndexes()[0].row()
            # self.setCurrentIndex(self.model.index(self.selectedIndexes()[0].row() + 1, 0))
    
    def previous_index(self):
        """
        Moves the selection to the previous item in the list view, if possible.
        """
        index = self.selectedIndexes()[0].row()
        if index > 0:
            self.setCurrentIndex(self.model.index(index - 1, 0))
            self.index = self.selectedIndexes()[0].row()
            # self.setCurrentIndex(self.model.index(self.selectedIndexes()[0].row() - 1, 0))
        # return index
    
    def clear_list(self):
        """
        Clears all items from the list view.
        """
        self.model.removeRows(0, self.model.rowCount())
    
    def clear_selection(self):
        """
        Clears the current selection in the list view.
        """
        self.clearSelection()
    
    def get_label_list(self):
        """
        Returns the current list of labels.

        Returns:
            list: The list of label names.
        """
        return self.label_list
    
    def get_selected_index(self):
        """
        Returns the indexes of the selected items.

        Returns:
            list: A list of QModelIndex objects representing the selected items.
        """
        return self.selectedIndexes()
    
    def get_current_index(self):
        """
        Returns the index of the current selection.
        
        
        Returns:
            int: The index of the current selection.
        """
        return self.index
    
    def mousePressEvent(self, event):
        """
        Handles mouse press events on the list view. Toggles the checkbox state of 
        the item under the mouse cursor.

        Args:
            event (QMouseEvent): The mouse event object.
        """
        index = self.indexAt(event.pos())
        # print(f"Index: {index.row()}")
        # print(f"model row count {self.model.rowCount()}")
        if index.isValid():
            item = self.model.itemFromIndex(index)
            print(f"Item: {item.text()}")
            current_state = item.data(Qt.UserRole + 1)
            
            # Toggle the state
            new_state = not current_state
            item.setData(new_state, Qt.UserRole + 1)
            self.index = self.selectedIndexes()[0].row()

        # Call the parent class's mousePressEvent to handle other events
        super(CustomListViewWidget, self).mousePressEvent(event)
    
    def set_current_index(self, index):
        """
        Sets the current selection in the list view to the specified index.

        Args:
            index (int): The index to set as the current selection.
        """
        self.setCurrentIndex(self.model.index(index, 0))


class CustomLabelWidget(QtWidgets.QListView):
    """
    A custom QListView widget for displaying and managing a list of labels. 
    Allows adding new labels by double-clicking and supports updating the list 
    based on an annotation type.

    Attributes:
        model (QStringListModel): The data model for storing label names.
        label_list (list): A list to store label names displayed in the list view.
        annotation_type (str): The type of annotation currently being handled.
    """
    update_label_list_slot_transmitter = pyqtSignal(list) # Signal to update the label list
    update_label_list_slot_receiver = pyqtSignal(list) # Signal to update the label list

    def __init__(self, parent=None):
        """
        Initializes the CustomLabelWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super(CustomLabelWidget, self).__init__(parent)
        # Initialize the model and label list
        self.model = QStringListModel()
        # label list is empty
        self.label_list = []
        # Set the geometry, model
        self.set_geometry()
        self.set_model()
        self.delegate = CustomDelegate(self)
        self.setItemDelegate(self.delegate)
        # Set the annotation type to None
        self.annotation_type = "Rectangle"
        # Connect the signals
        self.update_label_list_slot_receiver.connect(self.__update_list) # Connect the signal to update the label list
        self.model.dataChanged.connect(self.on_data_changed)  # Connect the dataChanged signal

    def set_geometry(self):
        """
        Sets the geometry of the list view widget.
        """
        # Set the geometry of the list view widget
        self.setGeometry(QRect(1390, 30, 450, 192))
    
    def set_model(self):
        """
        Sets the data model for the list view and enables updates.
        """
        # set the model and enable updates
        self.setModel(self.model)
        self.setUpdatesEnabled(True)
        # Set the edit triggers to NoEditTriggers
        self.setEditTriggers(QtWidgets.QListView.NoEditTriggers)

    def set_label_list(self, label_list: list = []):
        """
        Updates the list view with a new list of labels.

        Args:
            label_list (list, optional): A list of label names to display. Defaults to an empty list.
        """
        # Check if the label list is a non-empty list
        if isinstance(label_list, list) and len(label_list) > 0:
            # Clear the model before updating
            self.clear_list()
            # Update the label list and model
            self.label_list = label_list
            # update the model
            print(f"Label List in set label list: {self.label_list}")
            self.model.setStringList(self.label_list)
    
    def clear_list(self):
        """
        Clears all items from the list view.
        """
        # Clear the list and update the model
        self.model.setStringList([])
    
    def __update_list(self, label_list: list):
        """
        Updates the list of labels based on the provided label list.

        Args:
            label_list (list): The list of labels to update.
        """
        # Get the label list based on the annotation type
        self.set_label_list(label_list)
    
    def update_annotation_type(self, annotation_type):
        """
        Updates the annotation type currently being used.

        Args:
            annotation_type (str): The new annotation type to use.
        """
        # Set the annotation type based on the provided value
        self.annotation_type = {
            "Object Detection": "Rectangle",
            "Segmentation": "Polygon"
        }.get(annotation_type, "None")
        # Print the annotation type
        print(f"Annotation Type: {self.annotation_type}")
    
    def mouseDoubleClickEvent(self, event):
        """
        Handles mouse double-click events on the list view. Prompts the user to 
        add a new label if the left mouse button is double-clicked.

        Args:
            event (QMouseEvent): The mouse event object.
        """
        # Check if the annotation type is set and the left mouse button is double-clicked
        if self.annotation_type != "None" and event.button() == Qt.LeftButton:
            # Show input dialog to add a new label
            new_label, ok = QInputDialog.getText(self, 'Add New Label', 'Enter a new label:')
            # Check if the user entered a label and clicked OK
            if ok and new_label.strip(): 
                # Add the new label
                self.add_label(new_label)
            # Call the parent class's mousePressEvent to handle other events
            super(CustomLabelWidget, self).mousePressEvent(event)
    
    def add_label(self, new_label):
        """
        Adds a new label to the list view.

        Args:
            new_label (str): The label to add.
        """
        # Check if the label already exists
        if new_label not in self.label_list:
            # Add the new label to the list
            self.label_list.append(new_label)
            # Update the model
            self.model.setStringList(self.label_list)
            # Emit signal to update the list
            self.update_label_list_slot_transmitter.emit(self.label_list)
        else:
            # Show a warning message if the label already exists
            QMessageBox.warning(self, 'Warning', 'This label already exists.')
            
    
    def remove_label(self, label):
        """
        Removes a label from the list view.

        Args:
            label (str): The label to remove.
        """
        # Check if the label exists in the list
        if label in self.label_list:
            # Remove the label from the list
            self.label_list.remove(label)
            # Update the model
            self.model.setStringList(self.label_list)

    def contextMenuEvent(self, event):
        """
        Handles the context menu event, providing an option to edit the selected item.

        Args:
            event (QContextMenuEvent): The context menu event object.
        """
        # Get the index at the mouse position
        index = self.indexAt(event.pos()) 
        # Check if the index is valid
        if index.isValid():
            # Create a context menu
            menu = QMenu(self) 
            # Create an action to edit the item
            edit_action = QAction('Edit', self)
            # Connect the action to the edit_label method
            edit_action.triggered.connect(lambda: self.edit_label(index)) 
            # Add the action to the menu
            menu.addAction(edit_action)
            # Show the context menu at the mouse position
            menu.exec_(event.globalPos())

    def edit_label(self, index):
        """
        Triggers inline editing for the selected item.

        Args:
            index (QModelIndex): The index of the item to be edited.
        """
        # Start editing the item at the specified index
        self.edit(index)
    
    
    def on_data_changed(self, topLeft, bottomRight, roles):
        """
        Slot that is triggered when the data in the model is changed.

        Args:
            topLeft (QModelIndex): The top-left index of the changed data.
            bottomRight (QModelIndex): The bottom-right index of the changed data.
            roles (list): The roles that have changed.
        """
        # Get the updated label list
        self.label_list = self.model.stringList()
        # Emit signal to update the list
        self.update_label_list_slot_transmitter.emit(self.label_list)

class CustomObjectListWidget(QtWidgets.QListView):
    """
    A custom QListView widget for displaying and managing a list of labels. 
    Allows adding new labels by double-clicking and supports updating the list 
    based on an annotation type.

    Attributes:
        model (QStringListModel): The data model for storing label names.
        label_list (list): A list to store label names displayed in the list view.
        annotation_type (str): The type of annotation currently being handled.
    """
    object_list_slot_receiver = pyqtSignal(list, Enum) # Signal to update the label list
    object_selection_notification_slot = pyqtSignal(int) # Signal to update the label list

    def __init__(self, parent=None):
        """
        Initializes the CustomLabelWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super(CustomObjectListWidget, self).__init__(parent)
        # Initialize the model and label list
        self.model = QStringListModel()
        # label list is empty
        self.label_list = [] # list of labels Updated by main.py
        self.category_id = [] # list of category id
        self.object_id = []
        self.object = dict()
        # Set the geometry, model
        self.set_geometry()
        self.set_model()
        # handel clicked event
        self.clicked.connect(self.on_item_clicked)
        self.set_label_list(self.label_list)
        # Connect the signals
        self.object_list_slot_receiver.connect(self.__receiver_action) # Connect the signal to update the label list
        # self.model.dataChanged.connect(self.handle_data_changed)  # Connect the dataChanged signal

    def set_geometry(self):
        """
        Sets the geometry of the list view widget.
        """
        # Set the geometry of the list view widget
        self.setGeometry(QRect(1390, 250, 450, 251))
    
    def set_model(self):
        """
        Sets the data model for the list view and enables updates.
        """
        # set the model and enable updates
        self.setModel(self.model)
        self.setUpdatesEnabled(True)
        # # Set the edit triggers to NoEditTriggers
        self.setEditTriggers(QtWidgets.QListView.NoEditTriggers)
    
    def __receiver_action(self, data: any, action: Enum):
        data = data[0]
        if action == OBJECT_LIST_ACTION.UPDATE:
            if isinstance(data, list):
                category_id = [label["category_id"] for label in data]
                object_id = [label['id'] for label in data]
                self.object = {label['id']: label["category_id"] for label in data}
                self.set_label_list(category_id=category_id, object_id=object_id)
        elif action == OBJECT_LIST_ACTION.ADD:
            if isinstance(data, dict):
                if data['id'] in self.object:
                    return
                self.object[data['id']] = data["category_id"]
                self.add_label(category_id = data["category_id"], object_id = data['id'])
        elif action == OBJECT_LIST_ACTION.CLEAR:
            self.clear_list()
        elif action == OBJECT_LIST_ACTION.REMOVE:
            # it will also remove the label from label_list and id from object_id_list
            # and update the new object_list, with new label_list and object_id_list
            if isinstance(data, list):
                self.remove_label(data)
        elif action == OBJECT_LIST_ACTION.EDIT:
            if isinstance(data, dict):
                self.edit_label(data['id'], data["category_id"])
        else:
            pass


    def set_label_list(self, category_id: list = [], object_id: list = []):
        """
        Updates the list view with a new list of labels.

        Args:
            label_list (list, optional): A list of label names to display. Defaults to an empty list.
        """
        # Check if the label list is a non-empty list
        # if isinstance(category_id, list) and len(category_id) > 0 and isinstance(object_id, list) and len(object_id) > 0:
            # Clear the model before updating
        self.clear_list()
        # Update the label list and model
        self.category_id = category_id
        self.object_id = object_id
        object_list = [f"{self.label_list[id]}" for id in category_id]
        # update the model
        self.model.setStringList(object_list)
        
    def clear_list(self):
        """
        Clears all items from the list view.
        """
        # Clear the list and update the model
        self.object_id.clear()
        self.category_id.clear()
        self.object.clear()
        self.model.setStringList([])
    
    def add_label(self, category_id: str, object_id: int):
        """
        Adds a new label to the list view.

        Args:
            new_label (str): The label to add.
        """
        # Add the new label to the list
        self.object_id.append(object_id)
        self.category_id.append(category_id)
        object_list = [f"{self.label_list[id]}" for id in self.category_id]
        # Update the model
        self.model.setStringList(object_list)
    
    def remove_label(self, data: list):
        """
        Removes a label from the list view.

        Args:
            label (str): The label to remove.
        """
        print(f"Data To Be remoed: {data}")
        category_id = [label["category_id"] for label in data]
        object_id = [label['id'] for label in data]
        self.object = {label['id']: label['category_id'] for label in data}
        self.set_label_list(category_id=category_id, object_id=object_id)

    def edit_label(self, object_id, category_id):
        """
        Triggers inline editing for the selected item.

        Args:
            index (QModelIndex): The index of the item to be edited.
        """
        # index = self.object_id_list.index(object_id)
        # self.label_list[index] = label
        if object_id in self.object:
            index = self.object_id.index(object_id)
            self.category_id[index] = category_id
            self.object[object_id] = category_id
            object_list = [f"{self.label_list[id]}" for id in self.category_id] 
            self.model.setStringList(object_list)
    
    def refresh_list(self, label_list: list):
        """
        Refresh the list view
        """
        self.label_list = label_list
        object_list = [f"{self.label_list[id]}" for id in self.category_id]
        self.model.setStringList(object_list)
    
    def on_item_clicked(self, index):
        """
        Emits the signal with the currently selected item's text.

        Args:
            index (QModelIndex): The index of the current item.
        """
        # Emit the signal with the selected item's text
        # print(f"Index: {index.row()}")
        # print(f"Item: {self.model.data(index, Qt.DisplayRole)}")
        id = self.object_id[index.row()]
        self.object_selection_notification_slot.emit(id)
    
    def mousePressEvent(self, event) -> None:
        """
        Handles mouse press events on the list view. Toggles the checkbox state of
        the item under the mouse cursor.
        """
        index = self.indexAt(event.pos())
        if not index.isValid():
            # Clear the selection if the click is outside items
            self.clearSelection()
            print("Clearing selection")
            self.object_selection_notification_slot.emit(-1)
        # Call the parent class's mousePressEvent to handle normal clicks
        super().mousePressEvent(event)
    
    # def contextMenuEvent(self, event):
    #     """
    #     Handles the context menu event, providing an option to edit the selected item.

    #     Args:
    #         event (QContextMenuEvent): The context menu event object.
    #     """
    #     # Get the index at the mouse position
    #     index = self.indexAt(event.pos()) 
    #     # Check if the index is valid
    #     if index.isValid():
    #         # Create a context menu
    #         menu = QMenu(self) 
    #         # Create an action to edit the item
    #         edit_action = QAction('Edit', self)
    #         # Connect the action to the edit_label method
    #         edit_action.triggered.connect(lambda: self.edit_label_at_index(index)) 
    #         # Add the action to the menu
    #         menu.addAction(edit_action)
    #         # Show the context menu at the mouse position
    #         menu.exec_(event.globalPos())
    
    # def edit_label_at_index(self, index):
    #     """
    #     Triggers inline editing for the selected item.

    #     Args:
    #         index (QModelIndex): The index of the item to be edited.
    #     """
    #     # Start editing the item at the specified index
    #     self.edit(index)

    # @pyqtSlot(QModelIndex, QModelIndex)
    # def handle_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex):
    #     """
    #     Slot to handle data changes in the list view.

    #     Args:
    #         top_left (QModelIndex): The top-left index of the changed data.
    #         bottom_right (QModelIndex): The bottom-right index of the changed data.
    #     """
    #     row = top_left.row()
    #     # get index of the item and old data
        




    #     new_data = self.model.data(top_left, Qt.EditRole)
    #     print(f"Item at row {row} was changed to '{new_data}'")
    #     # Optionally, you can update your data model or UI here