import sys
import os
from PyQt5 import QtWidgets
from layout import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog, QApplication
from labelvim.utils.utils import get_image_list, return_mattching
from labelvim.utils.annotaion_manager import AnnotationManager
from labelvim.utils.lablelist_reader import label_list_reader as label_list_manager
from labelvim.utils.config import ANNOTATION_TYPE, ANNOTATION_MODE, OBJECT_LIST_ACTION
from labelvim.widgets.task_selection import TaskSelectionDialog
from labelvim.widgets.canvas_widget import CanvasWidget
from labelvim.widgets.list_widgets import CustomListViewWidget, CustomLabelWidget, CustomObjectListWidget
from labelvim.widgets.export_file import ExportFileDialog
from labelvim.utils.config import ConfigSpecHandler


class LabelVim(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(LabelVim, self).__init__()
        self.setupUi(self)
        self.img_file_list = []
        self.img_list = []
        self.json_file_list = []
        self.json_list = []
        self.save_dir = ''
        self.load_dir = ''
        self.json_data = {}
        self.current_index = 0
        self.annotaion_mode = ANNOTATION_MODE.NONE
        self.annotation_type = ANNOTATION_TYPE.NONE
        self.label_file_name = 'label.yaml'
        self.save_mask = False
        self.include_img = False
        self.config_file_name = 'config.yaml'
        self.config_manager = None

        # Custom Widgets
        self.FileListWidget = CustomListViewWidget(self.centralwidget)
        self.FileListWidget.setObjectName("FileListWidget")
        self.Display = CanvasWidget(self.centralwidget)
        self.Display.setObjectName("Display")
        self.LabelWidget = CustomLabelWidget(self.centralwidget)
        self.LabelWidget.setObjectName("LabelWidget")
        self.ObjectLabelListWidget = CustomObjectListWidget(self.centralwidget)
        self.ObjectLabelListWidget.setObjectName("ObjectLabelListWidget")

        # btn action
        self.OpenDirBtn.clicked.connect(self.__load_directory)
        self.SaveDirBtn.clicked.connect(self.__save_directory)
        self.DeleteFileBtn.clicked.connect(self.__delete_file)
        self.NextBtn.clicked.connect(self.__next)
        self.PreviousBtn.clicked.connect(self.__previous)
        self.CreateObjectBtn.clicked.connect(self.__create_object)
        self.EditObjectBtn.clicked.connect(self.__edit_object)
        self.DeleteAnnotationBtn.clicked.connect(self.__delete_annotation)
        self.ClearAnnotationBtn.clicked.connect(self.__clear_annotation)
        self.SaveBtn.clicked.connect(self.__save)
        self.ZoomInBtn.clicked.connect(self.__zoom_in)
        self.ZoomOutBtn.clicked.connect(self.__zoom_out)
        self.ZoomFitBtn.clicked.connect(self.__zoom_fit)
        self.actionQuit.triggered.connect(self.exit_app)

        self.actionOpen.triggered.connect(self.__load_directory)
        self.actionSave_Folder.triggered.connect(self.__save_directory)
        self.actionDelete_FIle.triggered.connect(self.__delete_file)
        self.actionNext.triggered.connect(self.__next)
        self.actionPrevious.triggered.connect(self.__previous)
        self.actionSave.triggered.connect(self.__save)
        self.actionSave_Mask.triggered.connect(self.__save_mask_flag_set)
        self.actionSave_Mask_include_img.triggered.connect(self.__save_mask_include_img_flag_set)

        self.actionZoom_In.triggered.connect(self.__zoom_in)
        self.actionZoom_Out.triggered.connect(self.__zoom_out)
        self.actionFit_Windows.triggered.connect(self.__zoom_fit)
        self.actionExport.triggered.connect(self.__handel_export)
        # self.actionAnnotation_Type.triggered.connect(self.show_task_selection_dialog)

        self.show()
        self.__disable_btn_at_start()
        # self.show_task_selection_dialog()
        
        # self.LabelWidget.update_annotation_type(self.annotation_type)

        # Connect signals and slots
        self.FileListWidget.notify_selected_item.connect(self.__load_image)
        self.Display.update_label_list_slot_receiver.emit(self.LabelWidget.label_list)
        self.Display.update_label_list_slot_transmitter.connect(self.update_label_list_to_Label_Widget)
        self.Display.scale_factor_slot.connect(self.update_zoom_label)
        self.Display.object_list_action_slot.connect(self.update_data_to_ObjectListWidget)
        self.LabelWidget.update_label_list_slot_transmitter.connect(self.update_label_list_to_Display)
        self.ObjectLabelListWidget.object_selection_notification_slot.connect(self.Display.object_selection_notification_slot_receiver)
        
        self.json_writer = None
        #
        self.annotaion_manager = None
        self.label_list_manager = label_list_manager


    def show_task_selection_dialog(self):
        """
        Displays a custom dialog when the GUI starts, asking the user to choose 
        between object detection or segmentation.
        """
        # if self.annotation_type == ANNOTATION_TYPE.NONE:
        dialog = TaskSelectionDialog(self)
        if dialog.exec_():
            annotation_type = dialog.selected_task()
            if annotation_type != ANNOTATION_TYPE.NONE:
                self.annotation_type = annotation_type
                self.LabelWidget.update_annotation_type(self.annotation_type)
                self.Display.update_annotation_type(self.annotation_type)
        # dialog = TaskSelectionDialog(self)
        # if dialog.exec_():
        #     annotation_type = dialog.selected_task()
        #     if annotation_type != ANNOTATION_TYPE.NONE:
        #         self.annotation_type = annotation_type
        #         self.LabelWidget.update_annotation_type(self.annotation_type)
        #         self.Display.update_annotation_type(self.annotation_type)


    def __load_directory(self):
        """
        Called when the OpenDirBtn is clicked. This is a
        private method that opens a file dialog to allow the user to select a directory. 
        It then loads and processes image files from the chosen directory, updating the 
        file list widget and enabling or disabling buttons based on the presence of images.
        """
        self.load_dir = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if self.load_dir:
            self.__reset()
            self.img_file_list = get_image_list(self.load_dir)
            print(f"Total File in the selected directory {self.load_dir}: {len(self.img_file_list)}")
            self.FileListWidget.update_list.emit(self.img_file_list)
            self.img_list = [os.path.splitext(os.path.split(file)[-1])[0] for file in self.img_file_list]
            if self.img_file_list:
                self.__enable_btn_after_load()
            else:
                self.__disable_btn_at_start()
            

    def __load_image(self, file_name, index):
        """
        called when the user selects an image file from the list widget in FileListWidget.
        """
        self.current_index = index
        if self.current_index < 0:
            self.annotaion_manager = None
            self.__disable_btn_at_start()
            self.Display.reset()
            return
        print(f"current index: {self.current_index}")
        print(f"file name: {file_name}")
        self.Display.load_image(file_name)
        if self.save_dir:
            f_name = os.path.splitext(os.path.split(file_name)[-1])[0]
            print("==============================")
            print(f"File Name: {f_name}")
            print(f"JSON List: {self.json_list}")
            if f_name in self.json_list:
                print(f"JSON file found for {f_name}")
                print(f"JSON file found for {file_name}")
                self.annotaion_manager = AnnotationManager(self.save_dir, f_name + '.json')
                self.annotaion_data = self.annotaion_manager.annotation
                self.Display.annotation_data_slot_receiver.emit(self.annotaion_data['annotations'])
                self.SaveBtn.setEnabled(True)
                self.EditObjectBtn.setEnabled(True)
                self.DeleteAnnotationBtn.setEnabled(True)
                self.ClearAnnotationBtn.setEnabled(True)
                self.actionSave.setEnabled(True)
            else:
                self.annotaion_manager = None
                self.SaveBtn.setEnabled(False)
                self.EditObjectBtn.setEnabled(False)
                self.DeleteAnnotationBtn.setEnabled(False)
                self.ClearAnnotationBtn.setEnabled(False)
                self.actionSave.setEnabled(False)

    def __save_directory(self):
        """
        Opens a dialog to select a save directory, loads JSON files from the directory,
        updates the label list manager, and syncs the list with available image files.
        """
        self.save_dir = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if self.save_dir:
            if not os.path.exists(os.path.join(self.save_dir, 'config.yaml')):
                print("Config file not found")
                self.config_file_name = 'config.yaml'
                self.show_task_selection_dialog()
                self.config_manager = ConfigSpecHandler(os.path.join(self.save_dir, self.config_file_name))
                self.config_parm = self.config_manager.get_config()
                self.config_parm['annotation_type'] = self.annotation_type.value
                self.config_parm['save_mask'] = self.save_mask
                self.config_parm['include_img'] = self.include_img
                self.config_manager.update_config(self.config_parm)
            else:
                self.config_file_name = 'config.yaml'
                print("Config file found")
                self.config_manager = ConfigSpecHandler(os.path.join(self.save_dir, self.config_file_name))
                self.config_parm = self.config_manager.get_config()
                print(f"Config Parm: {self.config_parm}")
                if 'annotation_type' in self.config_parm.keys():
                    print(f"Annotation Type: {self.config_parm['annotation_type']}")
                    self.annotation_type = ANNOTATION_TYPE(self.config_parm['annotation_type'])
                    print(f"Annotation Type: {self.annotation_type}")
                    if self.annotation_type == ANNOTATION_TYPE.NONE:
                        self.show_task_selection_dialog()
                        self.config_parm['annotation_type'] = self.annotation_type.value
                    else:
                        self.LabelWidget.update_annotation_type(self.annotation_type)
                        self.Display.update_annotation_type(self.annotation_type)
                else:
                    self.show_task_selection_dialog()
                    self.config_parm['annotation_type'] = self.annotation_type.value
                if 'save_mask' in self.config_parm.keys():
                    self.save_mask = self.config_parm['save_mask']
                else:
                    self.save_mask = False
                self.config_parm['save_mask'] = self.save_mask
                self.__change_icon_save_mask()
                if 'include_img' in self.config_parm.keys():
                    self.include_img = self.config_parm['include_img']
                else:
                    self.include_img = False
                self.config_parm['include_img'] = self.include_img
                self.__change_icon_save_mask_include_img()
                self.config_manager.update_config(self.config_parm)
                
            self.LabelWidget.update_annotation_type(self.annotation_type)
            print(f"Save Directory: {self.save_dir}")

            # Get list of JSON files in the selected directory
            self.json_file_list = get_image_list(self.save_dir, extension=['.json'])
            print(f"Total JSON file in the selected directory {self.save_dir}: {len(self.json_file_list)}")

            # Extract the base names (without extension) of JSON files
            self.json_list = [os.path.splitext(os.path.split(file)[-1])[0] for file in self.json_file_list]

            # Update the label list manager's path and load the label file if it exists
            self.label_list_manager.label_list_path = os.path.join(self.save_dir, self.label_file_name)
            # print(f"Label List Path: {self.label_list_manager.label_list_path}")
            if os.path.exists(os.path.join(self.save_dir, self.label_file_name)):
                self.label_list_manager.read()
            else:
                self.label_list_manager.update([]) # Initialize with an empty list if the file doesn't exist
            # print(f"Label List: {self.label_list_manager.label_list}")
            self.update_label_list_to_Label_Widget(self.label_list_manager.label_list)
            self.update_label_list_to_Display(self.label_list_manager.label_list)

            # Match JSON files with image files if both lists are available
            if self.json_list and self.img_list:
                self.json_list = return_mattching(self.json_list, self.img_list)
                self.json_file_list = [os.path.join(self.save_dir, file+'.json') for file in self.json_list]
            print(f"Total JSON file in the selected directory {self.save_dir}: {len(self.json_file_list)}")
            print("==============================") 
            print("load directory")
            self.current_index = self.FileListWidget.get_current_index()
            print(f"save dir Current Index: {self.current_index}")
            # Validate the current index
            if 0 <= self.current_index < len(self.img_list):
                current_file = self.img_list[self.current_index]
                print(f"Current File: {current_file}")
                if current_file in self.json_list:
                    print(f"JSON file found for {current_file}")
                
                        # Initialize the annotation manager and load annotation data
                    self.annotaion_manager = AnnotationManager(self.save_dir, current_file + '.json')
                    self.annotaion_data = self.annotaion_manager.annotation
                    # print(f"next Annotation Data: {self.annotaion_data}")
                    
                    # Emit the annotation data to the display
                    self.Display.annotation_data_slot_receiver.emit(self.annotaion_data['annotations'])
                    self.SaveBtn.setEnabled(True)
                    self.DeleteAnnotationBtn.setEnabled(True)
                    self.EditObjectBtn.setEnabled(True)
                    self.ClearAnnotationBtn.setEnabled(True)
                    self.actionSave.setEnabled(True)
    def __delete_file(self):
        """
        Deletes the currently selected file from the list. Removes the file from 
        the image file list and updates the JSON list if applicable.
        """
        # Get the index of the currently selected item
        deleted_file_index = self.FileListWidget.get_current_index()
        print("+==============================+")
        print(f"Deleted File Index: {deleted_file_index}")
        
        if deleted_file_index is not None and deleted_file_index >=0 and deleted_file_index < len(self.img_list):
            # print(f"Deleted File: {self.img_list[deleted_file_index]}")
            # Get the file name corresponding to the index
            file_name = self.img_list[deleted_file_index]
            # print(f"Deleted File Name: {file_name}")
            # Remove the file from the image file list and the image list
            self.img_file_list.pop(deleted_file_index)
            self.img_list.pop(deleted_file_index)
        #     # Remove the file name from the JSON list if it exists and remove the JSON file
            if file_name in self.json_list:
                # print(f"JSON file found for {file_name}")
                self.json_list.remove(file_name)
                # print(f"JSON List: {self.json_list}")
                self.json_file_list.remove(os.path.join(self.save_dir, file_name+'.json'))
                # print(f"JSON File List: {self.json_file_list}")
                if os.path.exists(os.path.join(self.save_dir, file_name+'.json')):
                    # print(f"{os.path.join(self.save_dir, file_name+'.json')}")
                    # print(os.path.exists(os.path.join(self.save_dir, file_name+'.json')))
                    os.remove(os.path.join(self.save_dir, file_name+'.json'))
                    print(os.path.exists(os.path.join(self.save_dir, file_name+'.json')))
            self.FileListWidget.remove_selected_item()

    def __save(self):
        """
        Saves the current annotation data to a JSON file and updates the internal lists.
        """
        # Get the annotation data from the display
        annotation_data = self.Display.update_annotation_to_json()
        
        # Ensure the annotation manager is available
        if self.annotaion_manager is not None:
            # Update and save the annotation
            self.annotaion_manager.update_annotation(annotation_data)
            self.annotaion_manager.save_annotation()
            if self.save_mask:
                import cv2
                # if self.include_img:
                image_data = cv2.imread(os.path.join(self.load_dir, self.img_file_list[self.current_index]))
                image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
                # else:
                #     image_data = None
                if self.annotation_type == ANNOTATION_TYPE.BBOX:
                    mask_type = 'bbox'
                else:
                    mask_type = 'polygon'
                self.annotaion_manager.save_mask(image_data=image_data, label_map=self.label_list_manager.label_list, include_img=self.include_img, mask_type=mask_type)
            
            # Validate the current index and update lists
            if 0 <= self.current_index < len(self.img_list):
                file_name = self.img_list[self.current_index]
                self.json_list.append(file_name)
                self.json_file_list.append(os.path.join(self.save_dir, file_name + '.json'))
            else:
                print("Invalid index. Cannot update JSON lists.")
        else:
            print("Annotation manager is not available.")

    def __next(self):
        """
        Moves to the next item in the file list, updates the current index, and loads 
        annotation data if a JSON file is found for the current image.
        """
        # Move to the next index in the file list
        self.FileListWidget.next_index()
        self.current_index = self.FileListWidget.get_current_index()
        print("========Next Button Clicked========")
        print(f"Current index: {self.current_index}")
        
        # Validate the current index
        if 0 <= self.current_index < len(self.img_list):
            current_file = self.img_list[self.current_index]
            print(f"Current File: {current_file}")
            if current_file in self.json_list:
                print(f"JSON file found for {current_file}")
                
                # Initialize the annotation manager and load annotation data
                self.annotaion_manager = AnnotationManager(self.save_dir, current_file + '.json')
                self.annotaion_data = self.annotaion_manager.annotation
                # print(f"next Annotation Data: {self.annotaion_data}")
                
                # Emit the annotation data to the display
                self.Display.annotation_data_slot_receiver.emit(self.annotaion_data['annotations'])
                self.SaveBtn.setEnabled(True)
                self.DeleteAnnotationBtn.setEnabled(True)
                self.EditObjectBtn.setEnabled(True)
                self.ClearAnnotationBtn.setEnabled(True)
                self.actionSave.setEnabled(True)
            else:
                # Handle case where no JSON file is found
                self.annotaion_manager = None
                self.SaveBtn.setEnabled(False)
                self.DeleteAnnotationBtn.setEnabled(False)
                self.EditObjectBtn.setEnabled(False)
                self.ClearAnnotationBtn.setEnabled(False)
                self.actionSave.setEnabled(False)
        else:
            print("Invalid index. Cannot load annotation data.")

    def __previous(self):
        """
        Moves to the previous item in the file list, updates the current index, and loads 
        annotation data if a JSON file is found for the current image.
        """
        # Move to the previous index in the file list
        self.FileListWidget.previous_index()
        self.current_index = self.FileListWidget.get_current_index()
        print("========Previous Button Clicked========")

        
        print(f"Current index: {self.current_index}")
        
        # Validate the current index
        if 0 <= self.current_index < len(self.img_list):
            current_file = self.img_list[self.current_index]
            print(f"Current File: {current_file}")
            
            if current_file in self.json_list:
                print(f"JSON file found for {current_file}")
                
                # Initialize the annotation manager and load annotation data
                self.annotaion_manager = AnnotationManager(self.save_dir, current_file + '.json')
                self.annotaion_data = self.annotaion_manager.annotation
                # print(f"previous Annotation Data: {self.annotaion_data}")
                # Emit the annotation data to the display
                self.Display.annotation_data_slot_receiver.emit(self.annotaion_data['annotations'])
                self.SaveBtn.setEnabled(True)
                self.DeleteAnnotationBtn.setEnabled(True)
                self.EditObjectBtn.setEnabled(True)
                self.ClearAnnotationBtn.setEnabled(True)
                self.actionSave.setEnabled(True)
            else:
                # Handle case where no JSON file is found
                self.annotaion_manager = None
                self.SaveBtn.setEnabled(False)
                self.DeleteAnnotationBtn.setEnabled(False)
                self.EditObjectBtn.setEnabled(False)
                self.ClearAnnotationBtn.setEnabled(False)
                self.actionSave.setEnabled(False)
        else:
            print("Invalid index. Cannot load annotation data.")

    def __create_object(self):
        """
        Initializes the annotation manager and sets up the environment for creating 
        a new annotation object if a save directory is selected. Enables the save button.
        """
        if self.save_dir:
            print("Create Object")
            
            # Set annotation mode
            self.annotaion_mode = ANNOTATION_MODE.CREATE
            print(f"Annotation Mode: {self.annotaion_mode}")
            self.Display.btn_action_slot.emit(self.annotaion_mode)
            
            # Initialize the annotation manager if not already initialized
            if self.annotaion_manager is None:
                current_image = self.img_list[self.current_index]
                self.annotaion_manager = AnnotationManager(self.save_dir, current_image + '.json')
                self.annotaion_manager.update_basic_info(
                    os.path.basename(self.img_file_list[self.current_index]),
                    self.Display.original_pixmap.width(),
                    self.Display.original_pixmap.height()
                )
                self.annotaion_data = self.annotaion_manager.annotation
            
            # Enable the save button
            self.SaveBtn.setEnabled(True)
            self.DeleteAnnotationBtn.setEnabled(True)
            self.EditObjectBtn.setEnabled(True)
            self.ClearAnnotationBtn.setEnabled(True)
            self.actionSave.setEnabled(True)
        else:
            # Display a message dialog if save directory is not selected
            self.msg_dialog("Save Directory Not Selected", "Please select the save directory first.")
            self.SaveBtn.setEnabled(False)
            self.DeleteAnnotationBtn.setEnabled(False)
            self.EditObjectBtn.setEnabled(False)
            self.ClearAnnotationBtn.setEnabled(False)
            self.actionSave.setEnabled(False)

    def __edit_object(self):
        print("Edit Object")
        self.annotaion_mode = ANNOTATION_MODE.EDIT
        print(f"Annotation Mode: {self.annotaion_mode}")
        self.Display.btn_action_slot.emit(self.annotaion_mode)

    def __delete_annotation(self):
        print("Duplicate Annotation")
        self.annotaion_mode = ANNOTATION_MODE.DELETE
        self.Display.btn_action_slot.emit(self.annotaion_mode)
        print(f"Annotation Mode: {self.annotaion_mode}")

    def __clear_annotation(self):
        print("Clear Annotation")
        self.annotaion_mode = ANNOTATION_MODE.CLEAR
        print(f"Annotation Mode: {self.annotaion_mode}")
        self.Display.btn_action_slot.emit(self.annotaion_mode)

    def __zoom_in(self):
        self.Display.zoom_in()
    def __zoom_out(self):
        self.Display.zoom_out()

    def __zoom_fit(self):
        self.Display.fit_to_window()

    def update_zoom_label(self, scale_factor):
        self.ZoomLabel.setText(f"{scale_factor*100:.2f}%")

    # def __get_file_list(self):
        # self.file_list = get_image_list(self.load_dir)
        # print(f"Total File in the selected directory {self.load_dir}: {len(self.file_list)}")
        # print(self.file_list)

    def __reset(self):
        self.file_list = []
        self.img_list = []
        self.json_file_list = []
        self.save_dir = ''
        self.current_index = 0
        self.FileListWidget.clear_list()
        self.annotaion_mode = ANNOTATION_MODE.NONE
        self.annotation_type = ANNOTATION_TYPE.NONE
    
    def __disable_btn_at_start(self):
        self.DeleteFileBtn.setEnabled(False)
        self.NextBtn.setEnabled(False)
        self.PreviousBtn.setEnabled(False)
        self.CreateObjectBtn.setEnabled(False)
        self.EditObjectBtn.setEnabled(False)
        self.DeleteAnnotationBtn.setEnabled(False)
        self.ClearAnnotationBtn.setEnabled(False)
        self.SaveBtn.setEnabled(False)
        self.ZoomInBtn.setEnabled(False)
        self.ZoomOutBtn.setEnabled(False)
        self.ZoomFitBtn.setEnabled(False)
        # action menu disable
        self.actionNext.setEnabled(False)
        self.actionPrevious.setEnabled(False)
        self.actionDelete_FIle.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.actionZoom_In.setEnabled(False)
        self.actionZoom_Out.setEnabled(False)
        self.actionFit_Windows.setEnabled(False)

    
    def __enable_btn_after_load(self):
        """
        enable the buttons after loading the directory and getting the file list
        """
        self.NextBtn.setEnabled(True)
        self.PreviousBtn.setEnabled(True)
        self.CreateObjectBtn.setEnabled(True)
        self.DeleteFileBtn.setEnabled(True)
        self.ZoomInBtn.setEnabled(True)
        self.ZoomOutBtn.setEnabled(True)
        self.ZoomFitBtn.setEnabled(True)
        # action menu enable
        self.actionNext.setEnabled(True)
        self.actionPrevious.setEnabled(True)
        self.actionDelete_FIle.setEnabled(True)
        self.actionZoom_In.setEnabled(True)
        self.actionZoom_Out.setEnabled(True)
        self.actionFit_Windows.setEnabled(True)
        # self.actionSave.setEnabled(True)
    
    def msg_dialog(self, title, msg):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(msg)
        # msg_box.exec_()
        button = msg_box.exec()
        if button == QtWidgets.QMessageBox.Ok:
            print("OK")

    ## Signal and Slot
    def update_label_list_to_Display(self, label_list):
        # print(f"update_label_list: {label_list}")
        self.label_list_manager.update(label_list)
        self.Display.update_label_list_slot_receiver.emit(label_list)
        self.ObjectLabelListWidget.refresh_list(label_list) # Update the label list in the object list widget
        # self.ObjectLabelListWidget.label_list = label_list 
    
    def update_label_list_to_Label_Widget(self, label_list):
        # print(f"update_label_list: {label_list}")
        self.label_list_manager.update(label_list)
        self.LabelWidget.update_label_list_slot_receiver.emit(label_list)
        self.ObjectLabelListWidget.refresh_list(label_list) # Update the label list in the object list widget
        # self.ObjectLabelListWidget.label_list = label_list # Update the label list in the object list widget
    
    def update_data_to_ObjectListWidget(self, data, action):
        # print(f"update_data_to_ObjectListWidget: {data}")
        # print(f"update_data_to_ObjectListWidget: {action}")
        self.ObjectLabelListWidget.object_list_slot_receiver.emit(data, action)
    
    def __save_mask_flag_set(self):
        self.save_mask = not self.save_mask
        print(f"Save Mask: {self.save_mask}")
        if self.config_manager is not None:
            self.config_parm['save_mask'] = self.save_mask
            self.config_manager.update_config(self.config_parm)
        self.__change_icon_save_mask()
    
    def __save_mask_include_img_flag_set(self):
        self.include_img = not self.include_img
        print(f"Save Mask Include Image: {self.include_img}")
        if self.config_manager is not None:
            self.config_parm['include_img'] = self.include_img
            self.config_manager.update_config(self.config_parm)
        self.__change_icon_save_mask_include_img()
    
    def __change_icon_save_mask(self):
        if self.save_mask:
            self.actionSave_Mask.setIconVisibleInMenu(True)
        else:
            self.actionSave_Mask.setIconVisibleInMenu(False)
    
    def __change_icon_save_mask_include_img(self):
        if self.include_img:
            self.actionSave_Mask_include_img.setIconVisibleInMenu(True)
        else:
            self.actionSave_Mask_include_img.setIconVisibleInMenu(False)
    
    def exit_app(self):
        self.close()
    
    def __handel_export(self):
        dialog = ExportFileDialog()
        dialog.show()
        if dialog.exec_():
            print('Task Type:', dialog.task_type)
            print('Export Type:', dialog.export_type)
            print('Include Mask:', dialog.include_mask)
            
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LabelVim()
    window.show()
    sys.exit(app.exec_())