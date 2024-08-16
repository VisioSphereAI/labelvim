import sys
from PyQt5.QtWidgets import QApplication, QListView, QVBoxLayout, QWidget
from PyQt5.QtCore import QStringListModel, pyqtSignal, QModelIndex, Qt

class ListViewDemo(QWidget):
    # Define a custom signal
    itemClicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Create a list view
        self.list_view = QListView()

        # Create a model and populate it with data
        self.model = QStringListModel()
        self.model.setStringList(["Item 1", "Item 2", "Item 3", "Item 4"])

        # Set the model to the list view
        self.list_view.setModel(self.model)

        # Connect the clicked signal of the list view to the custom slot
        self.list_view.clicked.connect(self.on_item_clicked)

        # Layout for the widget
        layout = QVBoxLayout()
        layout.addWidget(self.list_view)
        self.setLayout(layout)

        # Connect the custom signal to a slot
        self.itemClicked.connect(self.handle_item_clicked)

        # Set the window title
        self.setWindowTitle("QListView Item Click Signal Demo")
        self.resize(300, 200)

    def on_item_clicked(self, index: QModelIndex):
        # Get the text of the clicked item
        item_text = self.model.data(index, Qt.DisplayRole)

        # Emit the custom signal with the item text
        self.itemClicked.emit(item_text)

    def handle_item_clicked(self, item_text):
        # Handle the custom signal
        print(f"Item clicked: {item_text}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = ListViewDemo()
    demo.show()
    sys.exit(app.exec_())
