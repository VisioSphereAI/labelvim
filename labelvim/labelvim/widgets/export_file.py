from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QRadioButton, QComboBox, QPushButton, QMessageBox,
    QCheckBox, QSlider, QWidget, QFormLayout
)
from PyQt5.QtCore import Qt
from enum import Enum


class TaskType(Enum):
    OBJECT_DETECTION = 0
    SEGMENTATION = 1
    POSE = 2
    CLASSIFICATION = 3

class ExportType(Enum):
    COCO = 0
    PASCAL_VOC = 1
    YOLOV5 = 2
    YOLOV8 = 3    
    YOLOV9 = 4
    YOLOV7 = 5

class ExportFileDialog(QDialog):
    """Dialog to select task type and export format for exporting files."""

    def __init__(self, parent=None, task_type=None, save_dir=None):
        super().__init__(parent)
        self.setWindowTitle('Export Options')
        self.setMaximumHeight(300)
        self.setMaximumWidth(700)
        
        self.task_type = TaskType.OBJECT_DETECTION
        self.export_type = ExportType.COCO
        self.include_mask = False
        self.training_percentage = 70
        self.validation_percentage = 20
        self.test_percentage = 10

        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        
        # Export type selection
        self.export_type_selection = QComboBox(self)
        self.update_export_options(['COCO', 'Pascal VOC', 'YOLOv5', 'YOLOv8', 'YOLOV9', 'YOLOV7'])
        main_layout.addWidget(QLabel('Export Format:'))
        main_layout.addWidget(self.export_type_selection)
        
        # Train/Test/Validation sliders
        sliders_group = self._create_sliders_group()
        main_layout.addWidget(sliders_group)
        
        # Checkbox for include mask
        self.include_mask_checkbox = QCheckBox("Include mask", self)
        main_layout.addWidget(self.include_mask_checkbox)
        
        # Export button
        self.export_button = QPushButton('Export', self)
        main_layout.addWidget(self.export_button)
        
        self.setLayout(main_layout)

    def _create_task_type_group(self):
        """Create a group box for task type selection."""
        group_box = QGroupBox("Task Type", self)
        layout = QHBoxLayout()

        self.object_detection_radio = QRadioButton('Object Detection')
        self.segmentation_radio = QRadioButton('Segmentation')
        self.pose_radio = QRadioButton('Pose')

        self.object_detection_radio.setChecked(True)

        layout.addWidget(self.object_detection_radio)
        layout.addWidget(self.segmentation_radio)
        layout.addWidget(self.pose_radio)

        group_box.setLayout(layout)
        return group_box

    def _create_sliders_group(self):
        """Create a group box for train/test/validation sliders."""
        group_box = QGroupBox("Data Split", self)
        layout = QFormLayout()

        # Train Percentage Slider
        self.train_percentage_slider = QSlider(Qt.Horizontal)
        self.train_percentage_slider.setRange(0, 100)
        self.train_percentage_slider.setValue(self.training_percentage)
        self.train_percentage_slider.setTickPosition(QSlider.TicksBelow)
        self.train_percentage_slider.setTickInterval(10)
        self.train_percentage_slider.valueChanged.connect(self._handle_train_slider_change)
        layout.addRow(QLabel("Training Percentage:"), self.train_percentage_slider)

        # Validation Percentage Slider
        self.test_percentage_slider = QSlider(Qt.Horizontal)
        self.test_percentage_slider.setRange(0, 100)
        self.test_percentage_slider.setValue(100 - self.test_percentage)
        self.test_percentage_slider.setTickPosition(QSlider.TicksBelow)
        self.test_percentage_slider.setTickInterval(10)
        self.test_percentage_slider.valueChanged.connect(self._handle_test_slider_change)
        # self.train_percentage_slider.setStyleSheet(slider_style)
        # self.test_percentage_slider.setStyleSheet(slider_style)
        layout.addRow(QLabel("Validation Percentage:"), self.test_percentage_slider)

        # Display label
        self.label = QLabel()
        layout.addRow(QLabel("Split Details:"), self.label)

        # Initial update
        self._update_train_test_validation()

        group_box.setLayout(layout)
        return group_box

    def _handle_test_slider_change(self):
        """Handle changes in the test percentage slider."""
        if self.test_percentage_slider.value() <= self.train_percentage_slider.value():
            self.test_percentage_slider.setValue(self.train_percentage_slider.value())
        self._update_train_test_validation()

    def _handle_train_slider_change(self):
        """Handle changes in the train percentage slider."""
        if self.train_percentage_slider.value() >= self.test_percentage_slider.value():
            self.train_percentage_slider.setValue(self.test_percentage_slider.value())
        self._update_train_test_validation()

    def _update_train_test_validation(self):
        """Update the train, validation, and test percentages and label."""
        self.training_percentage = self.train_percentage_slider.value()
        self.test_percentage = 100 - self.test_percentage_slider.value()
        self.validation_percentage = self.test_percentage_slider.value() - self.train_percentage_slider.value()
        
        self.label.setText(f"Train: {self.training_percentage}%\n"
                           f"Valid: {self.validation_percentage}%\n"
                           f"Test: {self.test_percentage}%")

    def _connect_signals(self):
        """Connect signals to their respective slots."""
        # self.object_detection_radio.clicked.connect(self._on_task_type_changed)
        # self.segmentation_radio.clicked.connect(self._on_task_type_changed)
        # self.pose_radio.clicked.connect(self._on_task_type_changed)

        self.export_type_selection.currentIndexChanged.connect(self._on_export_type_changed)
        self.export_button.clicked.connect(self._on_export)
        self.include_mask_checkbox.stateChanged.connect(self._on_checkbox_state_changed)

    def _on_task_type_changed(self):
        """Update export options based on the selected task type."""
        if self.object_detection_radio.isChecked():
            self.task_type = TaskType.OBJECT_DETECTION
            self.update_export_options(['YOLOv5', 'YOLOv8'])
        elif self.segmentation_radio.isChecked():
            self.task_type = TaskType.SEGMENTATION
            self.update_export_options(['YOLOv5', 'YOLOv8', 'Pascal VOC', 'COCO'])
        elif self.pose_radio.isChecked():
            self.task_type = TaskType.POSE
            self.update_export_options(['COCO'])

    def update_export_options(self, options):
        """Update the items in the export type combo box."""
        self.export_type_selection.clear()
        self.export_type_selection.addItems(options)
        self.export_type_selection.setCurrentIndex(0)
        self._on_export_type_changed(0)  # Set the initial export type based on the first item

    def _on_export_type_changed(self, index):
        """Update the export type based on the selected combo box item."""
        self.export_type = ExportType(index)
    def _on_checkbox_state_changed(self):
        """Handle the state change of the mask checkbox."""
        self.include_mask = self.include_mask_checkbox.isChecked()

    def _on_export(self):
        """Handle the export operation."""
        self.accept()
        QMessageBox.critical(self, 'Export Failed', 'Failed to export the file.')


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = ExportFileDialog()
    dialog.show()
    if dialog.exec_():
        print('Task Type:', dialog.task_type)
        print('Export Type:', dialog.export_type)
        print('Include Mask:', dialog.include_mask)
