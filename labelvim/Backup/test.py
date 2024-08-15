from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

class FilterPopup(QDialog):
    def __init__(self, items, parent=None):
        super(FilterPopup, self).__init__(parent)
        
        self.setWindowTitle("Select or Add Item")
        self.setGeometry(100, 100, 300, 400)
        
        self.layout = QVBoxLayout(self)
        
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Type to filter or add new item")
        self.line_edit.textChanged.connect(self.filter_items)
        self.layout.addWidget(self.line_edit)
        
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(items)
        self.list_widget.itemClicked.connect(self.item_selected)
        self.layout.addWidget(self.list_widget)
        
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_item)
        self.layout.addWidget(self.add_button)
        
        self.items = items
        self.selected_item = None
        self.selected_index = None
    
    def filter_items(self, text):
        """Filter the items in the list based on the text."""
        self.list_widget.clear()
        filtered_items = [item for item in self.items if text.lower() in item.lower()]
        self.list_widget.addItems(filtered_items)
    
    def add_item(self):
        """Add a new item to the list if it doesn't already exist."""
        text = self.line_edit.text().strip()
        if text and text not in self.items:
            self.items.append(text)
            self.list_widget.addItem(text)
            QMessageBox.information(self, "Item Added", f"'{text}' has been added to the list.")
        elif text in self.items:
            QMessageBox.warning(self, "Item Exists", f"'{text}' already exists in the list.")
        else:
            QMessageBox.warning(self, "Empty Input", "Please enter a valid item name.")
    
    def item_selected(self, item):
        """Handle the selection of an item."""
        self.selected_item = item.text()
        self.selected_index = self.items.index(self.selected_item)
        self.accept()  # Close the dialog and return
    
    def get_selected_item(self):
        """Return the selected item and its index."""
        return self.selected_item, self.selected_index

# Example usage
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    items = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
    dialog = FilterPopup(items)
    
    if dialog.exec_() == QDialog.Accepted:
        selected_item, selected_index = dialog.get_selected_item()
        print(f"Selected Item: {selected_item}, Index: {selected_index}")
        dialog.close()
    print("Dialog closed")
    app.closeAllWindows
    sys.exit(app.exec_())  # Ensure the application terminates properly
