from PyQt5.QtWidgets import QLabel ,QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget, QPushButton, QMessageBox, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal
from enum import Enum
from labelvim.utils.config import ANNOTATION_TYPE

class LabelPopup(QDialog):
    def __init__(self, items: list, data: list, annotation_type: Enum, update_label_list_slot_transmitter: pyqtSignal, parent=None):
        super(LabelPopup, self).__init__(parent)
        
        self.setWindowTitle("Select or Add Item")
        self.setGeometry(100, 100, 300, 400)
        self.data = data
        self.items = items
        self.annotation_type = annotation_type
        self.selected_item = None
        self.selected_index = None
        self.text_filter = False
        self.select_id = -1
        self.id = [-1]
        self.layout = QVBoxLayout(self)

        line_edit_id_combo_layout = QHBoxLayout()
        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Type to filter or add new item")
        self.line_edit.textChanged.connect(self.filter_items)
        line_edit_id_combo_layout.addWidget(self.line_edit)
        if self.annotation_type == ANNOTATION_TYPE.POLYGON:
            label = QLabel("ID", self)
            line_edit_id_combo_layout.addWidget(label)
            self.id_combo = QComboBox(self)
            self.update_id_combo()
            self.id_combo.currentIndexChanged.connect(self.update_list_widget)
            # self.id_combo.addItems([str(i) for i in self.id])
            line_edit_id_combo_layout.addWidget(self.id_combo)
        self.layout.addLayout(line_edit_id_combo_layout)
        
        # self.line_edit = QLineEdit(self)
        # self.line_edit.setPlaceholderText("Type to filter or add new item")
        # self.line_edit.textChanged.connect(self.filter_items)
        # self.layout.addWidget(self.line_edit)
        
        self.list_widget = QListWidget(self)
        self.list_widget.addItems(items)
        self.list_widget.itemClicked.connect(self.item_selected)
        self.layout.addWidget(self.list_widget)
        
        self.add_button = QPushButton("Add", self)
        self.add_button.clicked.connect(self.add_item)
        self.layout.addWidget(self.add_button)
        
        
        self.update_label_list_slot_transmitter = update_label_list_slot_transmitter # Signal to update the label list in the main window
    
    def update_id_combo(self):
        self.id_combo.clear()
        self.id = [str(-1)]
        # print(self.data["annotations"])
        self.id = self.id + [str(i['id']) for i in self.data]
        # print(self.id)
        self.id_combo.addItems(self.id)

    def filter_items(self, text):
        self.text_filter = True
        """Filter the items in the list based on the text."""
        self.list_widget.clear()
        filtered_items = [item for item in self.items if text.lower() in item.lower()]
        self.list_widget.addItems(filtered_items)
        if self.annotation_type == ANNOTATION_TYPE.POLYGON:
            self.id_combo.clear()
            self.id = [str(-1)]
            self.id = self.id + [str(i['id']) for item in filtered_items for i in self.data if item.lower() == self.items[i["category_id"]].lower()]
            self.id_combo.addItems(self.id)
        self.text_filter = False
    
    def update_list_widget(self):
        if not self.text_filter:
            self.list_widget.clear()
            if self.id_combo.currentText() == str(-1):
                self.list_widget.addItems(self.items)
            else:
                id = int(self.id_combo.currentText())
                print(f" id in labepuop: {id}")
                for i in self.data:
                    if i["id"] == id:
                        category_id = int(i["category_id"])
                        break

            # category_id = int(self.data[id]["category_id"])

            self.list_widget.addItems([self.items[category_id]])
            # self.list_widget.addItems([item for item in self.items if item.lower() == self.items[int(self.id_combo.currentText())].lower()])
        
    
    def add_item(self):
        """Add a new item to the list if it doesn't already exist."""
        text = self.line_edit.text().strip()
        if text and text not in self.items:
            self.items.append(text)
            self.list_widget.addItem(text)
            self.update_label_list_slot_transmitter.emit(self.items) # Transmitting the signal to update the label list
            # QMessageBox.information(self, "Item Added", f"'{text}' has been added to the list.")
        elif text in self.items:
            QMessageBox.warning(self, "Item Exists", f"'{text}' already exists in the list.")
        else:
            QMessageBox.warning(self, "Empty Input", "Please enter a valid item name.")
    
    def item_selected(self, item):
        """Handle the selection of an item."""
        self.selected_item = item.text()
        self.selected_index = self.items.index(self.selected_item)
        if self.annotation_type == ANNOTATION_TYPE.POLYGON:
            self.select_id = int(self.id_combo.currentText())
        # self.select_id = int(self.id_combo.currentText())
        self.accept()  # Close the dialog and return
    
    def get_selected_item(self):
        """Return the selected item and its index."""
        return self.selected_item, self.selected_index, self.select_id