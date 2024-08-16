from PyQt5 import QtWidgets
from PyQt5.QtCore import QStringListModel, Qt, QRect, QPoint
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QMenu, QAction
from labelvim.utils.config import ANNOTATION_TYPE

from labelvim.utils.lablelist_reader import label_list_reader

class CustomListViewWidget(QtWidgets.QListView):
    update_list = pyqtSignal(list)
    notify_selected_item = pyqtSignal(str)
    def __init__(self, parent=None):
        super(CustomListViewWidget, self).__init__(parent)
        # self.model = QStringListModel()
        self.model = QStandardItemModel()
        self.label_list = []
        self.set_geometry()
        self.set_model()
        self.set_label_list()
        self.selectionModel().currentChanged.connect(self.get_selected_item)
        self.update_list.connect(self.set_label_list)
    
    def set_geometry(self):
        self.setGeometry(QRect(1390, 531, 450, 271))

    def set_model(self):
        self.setModel(self.model)
        self.setUpdatesEnabled(True)

    def set_label_list(self, label_list=[]):
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
        self.notify_selected_item.emit(self.model.data(current, Qt.DisplayRole))
    
    def remove_selected_item(self):
        if len(self.selectedIndexes()) > 0:
            self.model.removeRow(self.selectedIndexes()[0].row())
        # print(f"Selected Items: {[self.model.data(index) for index in self.selectedIndexes()]}")
        # self.notify_selected_item.emit(self.model.data(self.selectedIndexes()[0]))
    
    def update_current_index(self, index):
        self.setCurrentIndex(index)
    
    def next_index(self):
        if self.selectedIndexes()[0].row() < self.model.rowCount() - 1:
            self.setCurrentIndex(self.model.index(self.selectedIndexes()[0].row() + 1, 0))
    
    def previous_index(self):
        if self.selectedIndexes()[0].row() > 0:
            self.setCurrentIndex(self.model.index(self.selectedIndexes()[0].row() - 1, 0))
    
    def clear_list(self):
        self.model.removeRows(0, self.model.rowCount())
    
    def clear_selection(self):
        self.clearSelection()
    
    def get_label_list(self):
        return self.label_list
    
    def get_selected_index(self):
        return self.selectedIndexes()
    
    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid():
            item = self.model.itemFromIndex(index)
            current_state = item.data(Qt.UserRole + 1)
            
            # Toggle the state
            new_state = not current_state
            item.setData(new_state, Qt.UserRole + 1)

            # # Set the appropriate icon based on the new state
            # if new_state:
            #     checked_icon = QIcon("path/to/checked_icon.png")  # Replace with your checked icon path
            #     item.setIcon(checked_icon)
            # else:
            #     unchecked_icon = QIcon("path/to/unchecked_icon.png")
            #     item.setIcon(unchecked_icon)
        
        # Call the parent class's mousePressEvent to handle other events
        super(CustomListViewWidget, self).mousePressEvent(event)


class CustomLabelListWidget(QtWidgets.QListView):
    def __init__(self, parent=None):
        super(CustomLabelListWidget, self).__init__(parent)
        self.model = QStringListModel()
        self.label_list = []
        self.set_geometry()
        self.set_model()
        self.set_label_list()
        self.annotation_type = "None"
        # self.clicked.connect(self.on_item_clicked)

    def set_geometry(self):
        self.setGeometry(QRect(1390, 30, 450, 192))
    
    def set_model(self):
        self.setModel(self.model)
        self.setUpdatesEnabled(True)
    

    def set_label_list(self, label_list=[]):
        if isinstance(label_list, list) and len(label_list) > 0:
            self.label_list = label_list
            self.model.setStringList(self.label_list)
    
    def update_list(self, annotation_type):
        self.update_annotation_type(annotation_type)
        if annotation_type in label_list_reader.label_list:
            self.set_label_list(label_list_reader.label_list[annotation_type])
    
    def update_annotation_type(self, annotation_type):
        self.annotation_type = annotation_type
    
    # def on_item_clicked(self, index):
    #     # def on_item_clicked(self, index):
    #     # Show input dialog to add a new label
    #     current_label = self.label_list[index.row()]
    #     new_label, ok = QInputDialog.getText(self, 'Add New Label', f'Enter a new label based on "{current_label}":')

    #     if ok and new_label.strip():
    #         if new_label not in self.label_list:
    #             self.label_list.append(new_label)
    #             self.model.setStringList(self.label_list)  # Update the model
    #         else:
    #             QMessageBox.warning(self, 'Warning', 'This label already exists.')

    def mouseDoubleClickEvent(self, event):
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
    
    # def contextMenuEvent(self, event):
    #     # Get the item at the mouse position
    #     index = self.indexAt(event.pos())

    #     if index.isValid():
    #         # Create a context menu
    #         menu = QMenu(self)
    #         delete_action = QAction('Delete', self)
    #         menu.addAction(delete_action)

    #         # Connect the delete action to the delete method
    #         delete_action.triggered.connect(lambda: self.delete_item(index))

    #         # Show the context menu
    #         menu.exec_(event.globalPos())

    # def delete_item(self, index):
    #     # Remove the selected item from the label list
    #     item_text = self.label_list[index.row()]
    #     self.label_list.remove(item_text)

    #     # Update the model to reflect changes
    #     self.model.setStringList(self.label_list)

    #     # Show a confirmation message
    #     QMessageBox.information(self, 'Deleted', f'Item "{item_text}" has been deleted.')

# Example usage:
                