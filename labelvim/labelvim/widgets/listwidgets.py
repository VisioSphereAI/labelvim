from PyQt5 import QtWidgets
from PyQt5.QtCore import QStringListModel, Qt, QRect, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QInputDialog, QMessageBox

# External imports
from labelvim.utils.config import ANNOTATION_TYPE
from labelvim.utils.lablelist_reader import label_list_reader

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
    notify_selected_item = pyqtSignal(str)

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
    
    def get_selected_item(self, current, previous):
        """
        Emits the signal with the currently selected item's text.

        Args:
            current (QModelIndex): The index of the current item.
            previous (QModelIndex): The index of the previously selected item.
        """
        self.notify_selected_item.emit(self.model.data(current, Qt.DisplayRole))
    
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
        if self.selectedIndexes()[0].row() < self.model.rowCount() - 1:
            self.setCurrentIndex(self.model.index(self.selectedIndexes()[0].row() + 1, 0))
    
    def previous_index(self):
        """
        Moves the selection to the previous item in the list view, if possible.
        """
        if self.selectedIndexes()[0].row() > 0:
            self.setCurrentIndex(self.model.index(self.selectedIndexes()[0].row() - 1, 0))
    
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
    
    def mousePressEvent(self, event):
        """
        Handles mouse press events on the list view. Toggles the checkbox state of 
        the item under the mouse cursor.

        Args:
            event (QMouseEvent): The mouse event object.
        """
        index = self.indexAt(event.pos())
        if index.isValid():
            item = self.model.itemFromIndex(index)
            current_state = item.data(Qt.UserRole + 1)
            
            # Toggle the state
            new_state = not current_state
            item.setData(new_state, Qt.UserRole + 1)

        # Call the parent class's mousePressEvent to handle other events
        super(CustomListViewWidget, self).mousePressEvent(event)


class CustomLabelListWidget(QtWidgets.QListView):
    """
    A custom QListView widget for displaying and managing a list of labels. 
    Allows adding new labels by double-clicking and supports updating the list 
    based on an annotation type.

    Attributes:
        model (QStringListModel): The data model for storing label names.
        label_list (list): A list to store label names displayed in the list view.
        annotation_type (str): The type of annotation currently being handled.
    """

    def __init__(self, parent=None):
        """
        Initializes the CustomLabelListWidget.

        Args:
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super(CustomLabelListWidget, self).__init__(parent)
        self.model = QStringListModel()
        self.label_list = []
        self.set_geometry()
        self.set_model()
        self.set_label_list()
        self.annotation_type = "None"

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

    def set_label_list(self, label_list=[]):
        """
        Updates the list view with a new list of labels.

        Args:
            label_list (list, optional): A list of label names to display. Defaults to an empty list.
        """
        if isinstance(label_list, list) and len(label_list) > 0:
            self.label_list = label_list
            self.model.setStringList(self.label_list)
    
    def update_list(self, annotation_type):
        """
        Updates the list of labels based on the provided annotation type.

        Args:
            annotation_type (str): The type of annotation to use for updating the list.
        """
        self.update_annotation_type(annotation_type)
        if annotation_type in label_list_reader.label_list:
            self.set_label_list(label_list_reader.label_list[annotation_type])
    
    def update_annotation_type(self, annotation_type):
        """
        Updates the annotation type currently being used.

        Args:
            annotation_type (str): The new annotation type to use.
        """
        self.annotation_type = annotation_type
    
    def mouseDoubleClickEvent(self, event):
        """
        Handles mouse double-click events on the list view. Prompts the user to 
        add a new label if the left mouse button is double-clicked.

        Args:
            event (QMouseEvent): The mouse event object.
        """
        if self.annotation_type != "None":
            if event.button() == Qt.LeftButton:
                # Show input dialog to add a new label
                new_label, ok = QInputDialog.getText(self, 'Add New Label', 'Enter a new label:')
                if ok and new_label.strip():
                    if new_label not in self.label_list:
                        self.label_list.append(new_label)
                        self.model.setStringList(self.label_list)  # Update the model
                        label_list_reader.label_list[self.annotation_type] = self.label_list
                        label_list_reader.update(label_list_reader.label_list)
                    else:
                        QMessageBox.warning(self, 'Warning', 'This label already exists.')

            super(CustomLabelListWidget, self).mousePressEvent(event)

    # def mousePressEvent(self, event):
    #     """
    #     Handles mouse press events on the list view. If the user clicks anywhere 
    #     outside the existing items, prompts to add a new label.

    #     Args:
    #         event (QMouseEvent): The mouse event object.
    #     """
    #     index = self.indexAt(event.pos())
        
    #     # If the click is not on an existing item, prompt to add a new label
    #     if not index.isValid() and event.button() == Qt.LeftButton:
    #         new_label, ok = QInputDialog.getText(self, 'Add New Label', 'Enter a new label:')
    #         if ok and new_label.strip():
    #             if new_label not in self.label_list:
    #                 self.label_list.append
