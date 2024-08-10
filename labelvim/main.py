from PyQt5 import QtWidgets
from layout import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QStringListModel
from labelvim.utils.utils import get_image_list
from labelvim.widgets.listwidgets import CustomListViewWidget, CustomLabelListWidget
import sys
from PyQt5.QtCore import pyqtSignal
from labelvim.utils.config import ANNOTATION_TYPE
from labelvim.widgets.task_selection import TaskSelectionDialog

class LabelVim(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(LabelVim, self).__init__()
        self.setupUi(self)
        # self.task_selection = 'Object Detection'
        # self.show_task_selection_dialog()
        

        self.file_list = []
        self.img_list = []
        self.save_dir = ''
        self.load_dir = ''
        self.FileListWidget = CustomListViewWidget(self.centralwidget)
        self.FileListWidget.setObjectName("FileListWidget")
        self.FileListWidget.notify_selected_item.connect(self.__load_image)
        self.LabelWidget = CustomLabelListWidget(self.centralwidget)
        self.LabelWidget.setObjectName("LabelWidget")
        self.LabelWidget.update_annotation_type(self.AnnotationComboBox.currentText())
        self.OpenDirBtn.clicked.connect(self.__load_directory)
        self.SaveDirBtn.clicked.connect(self.__save_directory)
        self.DeleteFileBtn.clicked.connect(self.__delete_file)
        self.NextBtn.clicked.connect(self.__next)
        self.PreviousBtn.clicked.connect(self.__previous)
        self.AnnotationComboBox.currentIndexChanged.connect(self.__update_label_list)

    def show_task_selection_dialog(self):
        """
        Displays a custom dialog when the GUI starts, asking the user to choose 
        between object detection or segmentation.
        """
        dialog = TaskSelectionDialog(self)
        if dialog.exec_():
            selected_task = dialog.selected_task()
            print(f"Selected Task: {selected_task}")
            # if selected_task == "Object Detection":
            #     self.start_object_detection()
            # elif selected_task == "Segmentation":
            #     self.start_segmentation()
    
    def __update_label_list(self, index):
        print(f"Index changed: {index}")
        # get value from the combobox
        print(f"Value: {self.AnnotationComboBox.currentText()}")
        # self.LabelWidget.update_list(index)
        self.LabelWidget.update_list(self.AnnotationComboBox.currentText())
    def __load_directory(self):
        """Load directory and update file list"""
        self.load_dir = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if self.load_dir:
            self.__file_list()
            self.FileListWidget.update_list.emit(self.file_list)

    def __load_image(self, file_name):
        print(f"Index changed file name: {file_name}")
        

    def __save_directory(self):
        self.save_dir = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        print(f"save dir: {self.save_dir}")
    
    def __delete_file(self):
        self.FileListWidget.remove_selected_item()

    def __save(self):
        pass

    def __next(self):
        self.FileListWidget.next_index()
    def __previous(self):
        self.FileListWidget.previous_index()

    def __zoom_in(self):

        pass
    def __zoom_out(self):
        pass

    def __zoom_reset(self):
        pass

    def __file_list(self):
        self.file_list = get_image_list(self.load_dir)
        print(f"Total File in the selected directory {self.load_dir}: {len(self.file_list)}")
        # print(self.file_list)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LabelVim()
    window.show()
    sys.exit(app.exec_())