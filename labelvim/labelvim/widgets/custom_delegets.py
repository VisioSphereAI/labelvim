from PyQt5.QtWidgets import QStyledItemDelegate, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt

"""
CustomDelegate: Now checks for duplicates in the QStringList
Model and handles committing data appropriately.

The setModelData method iterates through the string list to 
check for duplicates and updates the model if the new text is valid.
CustomObjectListWidget: Uses QStringListModel for the list data.

add_item: Appends new items to the list.
This setup integrates QStringListModel with the custom delegate, 
allowing you to edit list items and ensure that no duplicates are added.

"""

class CustomDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = parent

    def createEditor(self, parent, option, index):
        """
        Create and return a new editor widget for the item.
        
        Args:
            parent (QWidget): The parent widget.
            option (QStyleOptionViewItem): The option for the item.
            index (QModelIndex): The index of the item.
        
        Returns:
            QLineEdit: The editor widget.
        """
        editor = QLineEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        """
        Set the data for the editor widget.
        
        Args:
            editor (QWidget): The editor widget.
            index (QModelIndex): The index of the item.
        """
        data = index.model().data(index, Qt.EditRole)
        editor.setText(data)

    def setModelData(self, editor, model, index):
        """
        Retrieve the data from the editor widget and set it in the model.
        
        Args:
            editor (QWidget): The editor widget.
            model (QAbstractItemModel): The model.
            index (QModelIndex): The index of the item.
        """
        new_text = editor.text()
        # Check if the new text already exists in the model
        for row in range(model.rowCount()):
            item_text = model.data(model.index(row, 0), Qt.DisplayRole)
            if item_text == new_text and model.index(row, 0) != index:
                QMessageBox.warning(self.parent_view, 'Validation Error', 'The entered text already exists in the list.')
                return

        model.setData(index, new_text, Qt.EditRole)

    def commitData(self, editor):
        """
        Validate and commit the edited data.
        
        Args:
            editor (QWidget): The editor widget.
        """
        super().commitData(editor)
