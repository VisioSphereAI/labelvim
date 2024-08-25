from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QRadioButton, QComboBox, QPushButton, QMessageBox,
    QCheckBox, QSlider, QWidget, QFormLayout, QFileDialog, QProgressDialog
)
from labelvim.utils.config import ANNOTATION_TYPE, ExportType
from labelvim.utils.lablelist_reader import LabelListReader
from PyQt5.QtCore import Qt
from enum import Enum
import yaml
import os
import zipfile
import json
from PIL import Image, ImageDraw
import cv2
import shutil
import time
import numpy as np
import random
from labelvim.utils.save_mask import random_colors_palette
from tqdm import tqdm

def xywh2xyxy(x, y, w, h):
    x1 = x
    y1 = y
    x2 = x + w
    y2 = y + h
    return x1, y1, x2, y2

def xyxy2xywh(x1, y1, x2, y2):
    x = x1
    y = y1
    w = x2 - x1
    h = y2 - y1
    return x, y, w, h

def xywh2yolo(x, y, w, h, image_width, image_height):
    x_center = (x + w / 2) / image_width
    y_center = (y + h / 2) / image_height
    width = w / image_width
    height = h / image_height
    return x_center, y_center, width, height

def yolo2xywh(x_center, y_center, width, height, image_width, image_height):
    x = (x_center * image_width) - (width * image_width) / 2
    y = (y_center * image_height) - (height * image_height) / 2
    w = width * image_width
    h = height * image_height
    return x, y, w, h

def cocoseg2yolo(segmentation, image_width, image_height):
    yolo_segmentation = []
    for i in range(0, len(segmentation), 2):
        x_normalized = segmentation[i] / image_width
        y_normalized = segmentation[i+1] / image_height
        yolo_segmentation.append(x_normalized)
        yolo_segmentation.append(y_normalized)
    return yolo_segmentation

def yolo2cocoseg(yolo_segmentation, image_width, image_height):
    segmentation = []
    for i in range(0, len(yolo_segmentation), 2):
        x = yolo_segmentation[i] * image_width
        y = yolo_segmentation[i+1] * image_height
        segmentation.append(x)
        segmentation.append(y)
    return segmentation

class YOLOConversion:
    """Class to convert annotations to YOLO format."""
    
    def __init__(self, save_dir, data_dir, file_list, training_percentage, validation_percentage, test_percentage, include_mask=False, include_img=False, include_instance = False, annotation_type=ANNOTATION_TYPE.BBOX):
        self.save_dir = save_dir
        self.data_dir = data_dir
        self.file_list = file_list
        self.training_percentage = training_percentage
        self.validation_percentage = validation_percentage
        self.test_percentage = test_percentage
        self.include_mask = include_mask
        self.include_img = include_img
        self.include_instance = include_instance
        self.annotation_type = annotation_type
        self.train_file_list = []
        self.valid_file_list = []
        self.test_file_list = []
        self.label_list = []
        os.makedirs("temp", exist_ok=True)
        self.temp_dir = "temp"
        self.get_labels_list()
        self._split_data()
        self.zip_filename = self._create_zip_file()

    def get_labels_list(self): 
        label_list_reader = LabelListReader(os.path.join(self.save_dir, 'label.yaml'))
        self.label_list = label_list_reader.get()
    
    def _split_data(self):
        """Split the data into training, validation, and test sets."""
        train = int(len(self.file_list)*self.training_percentage/100)
        valid = int(len(self.file_list)*self.validation_percentage/100)
        self.train_file_list = self.file_list[:train]
        self.valid_file_list = self.file_list[train:train+valid]
        self.test_file_list = self.file_list[train+valid:]
    
    def _convert_to_yolov5_bbox_format(self, bbox, image_width, image_height):
        """Convert bounding box to YOLOv5 format."""
        x_center, y_center, width, height = xywh2yolo(bbox[0], bbox[1], bbox[2], bbox[3], image_width, image_height)
        return x_center, y_center, width, height
    
    def _convert_to_yolov8_bbox_format(self, bbox, image_width, image_height):
        """Convert bounding box to YOLOv8 format."""
        x_center, y_center, width, height = xywh2yolo(bbox[0], bbox[1], bbox[2], bbox[3], image_width, image_height)
        return x_center, y_center, width, height
    
    def _convert_to_yolov9_bbox_format(self, bbox, image_width, image_height):
        """Convert bounding box to YOLOv9 format."""
        x_center, y_center, width, height = xywh2yolo(bbox[0], bbox[1], bbox[2], bbox[3], image_width, image_height)
        return x_center, y_center, width, height
    
    def _convert_to_yolov7_bbox_format(self, bbox, image_width, image_height):
        """Convert bounding box to YOLOv7 format."""
        x_center, y_center, width, height = xywh2yolo(bbox[0], bbox[1], bbox[2], bbox[3], image_width, image_height)
        return x_center, y_center, width, height
    
    def _convert_to_yolov5_segmentation_format(self, segmentation_points, image_width, image_height):
        """Convert segmentation to YOLOv5 format."""
        yolo_segmentation = cocoseg2yolo(segmentation_points, image_width, image_height)
        return yolo_segmentation

    def _convert_to_yolov8_segmentation_format(self, segmentation_points, image_width, image_height):
        """Convert segmentation to YOLOv8 format."""
        yolo_segmentation = cocoseg2yolo(segmentation_points, image_width, image_height)
        return yolo_segmentation

    def _convert_to_yolov9_segmentation_format(self, segmentation_points, image_width, image_height):
        """Convert segmentation to YOLOv9 format."""
        yolo_segmentation = cocoseg2yolo(segmentation_points, image_width, image_height)
        return yolo_segmentation

    def _convert_to_yolov7_segmentation_format(self, segmentation_points, image_width, image_height):
        """Convert segmentation to YOLOv7 format."""
        yolo_segmentation = cocoseg2yolo(segmentation_points, image_width, image_height)
        return yolo_segmentation
        
    
    def _generate_yolov5_image_labels_and_masks(self, file_name):
        """Generate YOLOv5 labels and masks for an image."""
        # labels = 
        annotation_file = os.path.join(self.save_dir, file_name)
        with open(annotation_file, 'r') as file:
            annotation_data = json.load(file)
        # annotation_data = json.load(open(annotation_file))
        image_name = annotation_data['imagePath']
        image_width = annotation_data['imageWidth']
        image_height = annotation_data['imageHeight']
        annotations = annotation_data['annotations']
       

        image_path = os.path.join(self.data_dir, image_name)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        label_txt_path = os.path.join('temp', f"{base_name}.txt")
        mask_path = None
        mask_image_path = None
        mask_instance_path = None
        if self.include_mask:
            if self.annotation_type == ANNOTATION_TYPE.BBOX:
                mask = cv2.imread(image_path)
            else:
                mask = np.zeros((image_height, image_width, 3), dtype=np.uint8)
            mask_path = os.path.join('temp', f"{base_name}_mask.png")
        if self.include_img:
            image = cv2.imread(image_path)
            mask_image_path = os.path.join('temp', f"{base_name}_img.png")
        if self.include_instance:
            instance_image = np.zeros((image_height, image_width, 3), dtype=np.uint8)
            mask_instance_path = os.path.join('temp', f"{base_name}_instance.png")

        with open(label_txt_path, 'w') as label_txt:
            for annotation in annotations:
                label = annotation['category_id']
                if self.annotation_type == ANNOTATION_TYPE.BBOX:
                    bbox = annotation['bbox']
                    yolov5_bbox = self._convert_to_yolov5_bbox_format(bbox, image_width, image_height)
                    label_txt.write(f"{label} {yolov5_bbox[0]} {yolov5_bbox[1]} {yolov5_bbox[2]} {yolov5_bbox[3]}\n")
                    if self.include_mask:
                        color = random_colors_palette[label].tolist()
                        cv2.rectangle(mask, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), color, 2)
                        cv2.putText(mask, self.label_list[label], (bbox[0], bbox[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                elif self.annotation_type == ANNOTATION_TYPE.POLYGON:
                    segmentation = annotation['segmentation']
                    yolov5_segmentation = self._convert_to_yolov5_segmentation_format(segmentation, image_width, image_height)
                    label_txt.write(f"{label} {yolov5_segmentation}\n")
                    bbox = annotation['bbox']
                    segmentation = np.array(segmentation).reshape(-1, 2)
                    segmentation = segmentation.astype(np.int32)
                    if self.include_mask:
                        color = random_colors_palette[label].tolist()
                        cv2.fillPoly(mask, [segmentation], color)
                        # cv2.rectangle(mask, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), color, 2)
                        # cv2.putText(mask, self.label_list[label], (bbox[0], bbox[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    
                    if self.include_instance:
                        color = random.choice(random_colors_palette.tolist())
                        cv2.fillPoly(instance_image, [segmentation], color)
                        # cv2.rectangle(instance_image, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), color, 2)
                        # cv2.putText(instance_image, self.label_list[label], (bbox[0], bbox[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
            if self.include_img:
                # cv2.fillPoly(image, [segmentation], (0, 0, 255))
                # cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), (0, 0, 255), 2)
                # cv2.putText(image, self.label_list[label], (bbox[0], bbox[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                # print(f"mask shape: {mask.shape}")
                # print(f"mask_image shape: {image.shape}")
                image = cv2.addWeighted(image, 0.5, mask, 0.5, 0) 
        if self.include_mask:
            cv2.imwrite(mask_path, mask)
        if self.include_img:
            cv2.imwrite(mask_image_path, image)
        if self.include_instance:
            cv2.imwrite(mask_instance_path, instance_image)
        
        return image_path, label_txt_path, mask_path, mask_image_path, mask_instance_path

    def _create_zip_file(self):
        """Create a ZIP file containing YOLOv5 labels and masks."""
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(None, "Save Zip File", "yolov5_data.zip", "Zip Files (*.zip)", options=options)
        if not save_path:
            return None
        
        # Calculate the total number of files to add to the ZIP
        total_files = len(self.train_file_list) + len(self.valid_file_list) + len(self.test_file_list)

        # Initialize progress dialog
        progress_dialog = QProgressDialog("Creating ZIP file...", "Cancel", 0, total_files)
        progress_dialog.setGeometry(400, 400, 300, 100)
        progress_dialog.setWindowTitle("Export Progress")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        with zipfile.ZipFile(save_path, 'w') as zipf:
            current_progress = 0
            for file_name in self.train_file_list:
                # image_path = os.path.join(self.data_dir, file_name)
                image_path, label_txt_path, mask_path, mask_image_path, mask_instance_path = self._generate_yolov5_image_labels_and_masks(file_name)
                zipf.write(image_path, os.path.join("train","images", os.path.basename(image_path)))
                zipf.write(label_txt_path, os.path.join("train","labels", os.path.basename(label_txt_path)))
                if self.include_mask:
                    zipf.write(mask_path, os.path.join("train","masks", os.path.basename(mask_path)))
                if self.include_img:
                    zipf.write(mask_image_path, os.path.join("train","masks", os.path.basename(mask_image_path)))
                if self.include_instance:
                    zipf.write(mask_instance_path, os.path.join("train","masks", os.path.basename(mask_instance_path)))
                current_progress += 1
                progress_dialog.setValue(current_progress)
                if progress_dialog.wasCanceled():
                    # Remove the ZIP file if the operation was canceled
                    os.remove(save_path)
                    break
                time.sleep(1)
            for file_name in self.valid_file_list:
                # image_path = os.path.join(self.data_dir, file_name)
                image_path, label_txt_path, mask_path, mask_image_path, mask_instance_path = self._generate_yolov5_image_labels_and_masks(file_name)
                zipf.write(image_path, os.path.join("valid","images", os.path.basename(image_path)))
                zipf.write(label_txt_path, os.path.join("valid","labels", os.path.basename(label_txt_path)))
                if self.include_mask:
                    zipf.write(mask_path, os.path.join("valid","masks", os.path.basename(mask_path)))
                if self.include_img:
                    zipf.write(mask_image_path, os.path.join("valid","masks", os.path.basename(mask_image_path)))
                if self.include_instance:
                    zipf.write(mask_instance_path, os.path.join("valid","masks", os.path.basename(mask_instance_path)))
                current_progress += 1
                progress_dialog.setValue(current_progress)
                if progress_dialog.wasCanceled():
                     # Remove the ZIP file if the operation was canceled
                    os.remove(save_path)
                    break
                time.sleep(1)
            for file_name in self.test_file_list:
                # image_path = os.path.join(self.data_dir, file_name)
                image_path, label_txt_path, mask_path, mask_image_path, mask_instance_path = self._generate_yolov5_image_labels_and_masks(file_name)
                zipf.write(image_path, os.path.join("test","images", os.path.basename(image_path)))
                zipf.write(label_txt_path, os.path.join("test","labels", os.path.basename(label_txt_path)))
                if self.include_mask:
                    zipf.write(mask_path, os.path.join("test","masks", os.path.basename(mask_path)))
                if self.include_img:
                    zipf.write(mask_image_path, os.path.join("test","masks", os.path.basename(mask_image_path)))
                if self.include_instance:
                    zipf.write(mask_instance_path, os.path.join("test","masks", os.path.basename(mask_instance_path)))
                current_progress += 1
                progress_dialog.setValue(current_progress)
                if progress_dialog.wasCanceled():
                     # Remove the ZIP file if the operation was canceled
                    os.remove(save_path)
                    break
                time.sleep(1)

            """
            train: ../train/images
            val: ../valid/images
            test: ../test/images

            nc: 1
            names: ['Landslide']
            
            """
            with open("data.yaml", 'w') as file:
                file.write(f"train: ../train/images\n")
                file.write(f"val: ../valid/images\n")
                file.write(f"test: ../test/images\n\n")
                file.write(f"nc: {len(self.label_list)}\n")
                file.write(f"names: {self.label_list}\n")
                file.write(f"\nlabelvim:\n")

            zipf.write("data.yaml", "data.yaml")
        shutil.rmtree(self.temp_dir)
        progress_dialog.setValue(total_files)
        if progress_dialog.wasCanceled():
            # Remove the ZIP file if the operation was canceled
            os.remove(save_path)
            return None
        return save_path


class COCOConversion:
    """Class to convert annotations to COCO format."""
    
    def __init__(self, save_dir, data_dir, file_list, training_percentage, validation_percentage, test_percentage, include_mask=False, include_img=False, include_instance=False, annotation_type = ANNOTATION_TYPE.BBOX):
        self.save_dir = save_dir
        self.data_dir = data_dir
        self.file_list = file_list
        self.training_percentage = training_percentage
        self.validation_percentage = validation_percentage
        self.test_percentage = test_percentage
        self.include_mask = include_mask
        self.include_img = include_img
        self.include_instance = include_instance
        self.annotation_type = annotation_type
        self.train_file_list = []
        self.valid_file_list = []
        self.test_file_list = []
        self.temp_dir = "temp"
        self.label_list = []
        self.get_labels_list()
        os.makedirs(self.temp_dir, exist_ok=True)
        self._split_data()
        
        self.zip_filename = self._create_zip_file()
    
    def get_labels_list(self): 
        label_list_reader = LabelListReader(os.path.join(self.save_dir, 'label.yaml'))
        self.label_list = label_list_reader.get()

    def _split_data(self):
        """Split the data into training, validation, and test sets."""
        random.shuffle(self.file_list)
        train = int(len(self.file_list) * self.training_percentage / 100)
        valid = int(len(self.file_list) * self.validation_percentage / 100)
        self.train_file_list = self.file_list[:train]
        self.valid_file_list = self.file_list[train:train+valid]
        self.test_file_list = self.file_list[train+valid:]

    def _get_image_info(self, image_path):
        """Get image info for COCO format."""
        image = cv2.imread(image_path)
        height, width, _ = image.shape
        # image_id = os.path.splitext(os.path.basename(image_path))[0]
        return {
            "file_name": os.path.basename(image_path),
            "height": height,
            "width": width,
            "id": None
        }

    def _get_annotation_info(self, annotation, image_id, annotation_id):
        """Get annotation info for COCO format."""
        bbox = annotation['bbox']
        segmentation = annotation.get('segmentation', [])
        area = bbox[2] * bbox[3]
        return {
            "id": annotation_id,
            "image_id": image_id,
            "category_id": annotation['category_id'],
            "bbox": bbox,
            "segmentation": segmentation,
            "area": area,
            "iscrowd": 0
        }

    def _convert_to_coco_format(self, file_list, subset):
        """Convert a file list to COCO format."""
        coco_json = {
            "images": [],
            "annotations": [],
            # "categories": [{"id": 0, "name": "category_0"}]  # Update this based on actual categories
            "categories": [{"id": idx, "name": label} for idx, label in enumerate(self.label_list)]
        }
        annotation_id = 0
        image_id = 0
        image_path_list = []
        mask_image_list = []
        mask_list = []
        mask_instance_list = []

        for file_name in tqdm(file_list, desc=f"Converting {subset}"):
            annotation_file = os.path.join(self.save_dir, file_name)
            with open(annotation_file, 'r') as file:
                annotation_data = json.load(file)
            
            image_name = annotation_data['imagePath']
            image_path = os.path.join(self.data_dir, image_name)
            image_info = self._get_image_info(image_path)
            image_info["id"] = image_id
            coco_json["images"].append(image_info)
            
            # image_id = image_info["id"]
            for annotation in annotation_data['annotations']:
                annotation_info = self._get_annotation_info(annotation, image_id, annotation_id)
                coco_json["annotations"].append(annotation_info)
                annotation_id += 1
            image_id += 1
            # If masks or instances are to be saved as images
            if self.include_mask or self.include_img or self.include_instance:
                mask_path, img_path, instance_path = self._generate_masks_and_images(annotation_data, image_info)
            
            if self.include_mask:
                mask_list.append(mask_path)
            if self.include_img:
                mask_image_list.append(img_path)
            if self.include_instance:
                mask_instance_list.append(instance_path)
            image_path_list.append(image_path)

        with open(os.path.join(self.temp_dir, f"{subset}_coco.json"), 'w') as json_file:
            json.dump(coco_json, json_file, indent=4)
        
        return os.path.join(self.temp_dir, f"{subset}_coco.json"), image_path_list, mask_list, mask_image_list, mask_instance_list
    
    def _generate_masks_and_images(self, annotation_data, image_info):
        """Generate mask and image files for COCO format if required."""
        image_name = annotation_data['imagePath']
        image_path = os.path.join(self.data_dir, image_name)
        image = cv2.imread(image_path)
        base_name = os.path.splitext(os.path.basename(image_path))[0]

        # mask_path = None
        if self.include_mask:
            if self.annotation_type == ANNOTATION_TYPE.BBOX:
                mask = cv2.imread(image_path)
            else:
                mask = np.zeros((image_info["height"], image_info["width"],3), dtype=np.uint8)
        if self.include_img:
            image = cv2.imread(image_path)
        if self.include_instance:
            instance_image = np.zeros((image_info["height"], image_info["width"],3), dtype=np.uint8)

        for annotation in annotation_data['annotations']:
            segmentation = np.array(annotation['segmentation']).reshape(-1, 2)
            segmentation = segmentation.astype(np.int32)
            if self.include_mask:
                color = random_colors_palette[annotation["category_id"]].tolist()
                cv2.fillPoly(mask, [segmentation], 255)
            if self.include_instance:
                color = random.choice(random_colors_palette.tolist())
                cv2.fillPoly(instance_image, [segmentation], color)
            
        if self.include_img:
            image = cv2.addWeighted(image, 0.5, mask, 0.5, 0)

        if self.include_mask:
            mask_path = os.path.join(self.temp_dir, f"{image_info['id']}_mask.png")
            cv2.imwrite(mask_path, mask)
        else:
            mask_path = None
        if self.include_img:
            img_path = os.path.join(self.temp_dir, f"{image_info['id']}_img.png")
            cv2.imwrite(img_path, image)
        else:
            img_path = None
        if self.include_instance:
            instance_path = os.path.join(self.temp_dir, f"{image_info['id']}_instance.png")
            cv2.imwrite(instance_path, instance_image)
        else:
            instance_path = None
        return mask_path, img_path, instance_path
        
    def _create_zip_file(self):
        """Create a ZIP file containing YOLOv5 labels and masks."""
        options = QFileDialog.Options()
        save_path, _ = QFileDialog.getSaveFileName(None, "Save Zip File", "coco_data.zip", "Zip Files (*.zip)", options=options)
        if not save_path:
            return None
        
        # Calculate the total number of files to add to the ZIP
        total_files = len(self.train_file_list) + len(self.valid_file_list) + len(self.test_file_list)

        # Initialize progress dialog
        progress_dialog = QProgressDialog("Creating ZIP file...", "Cancel", 0, total_files)
        progress_dialog.setGeometry(400, 400, 300, 100)
        progress_dialog.setWindowTitle("Export Progress")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        with zipfile.ZipFile(save_path, 'w') as zipf:
            current_progress = 0
            coco_json_path, image_path_list, mask_list, mask_image_list, mask_instance_list = self._convert_to_coco_format(self.train_file_list, "train")
            zipf.write(coco_json_path, os.path.join("train", "_annotations.coco.json"))
            for idx, image_path in enumerate(image_path_list):
                zipf.write(image_path, os.path.join("train", os.path.basename(image_path)))
                if self.include_mask:
                # for mask_path in mask_list:
                    zipf.write(mask_list[idx], os.path.join("mask", "train", os.path.basename(mask_list[idx])))
                if self.include_img:
                # for mask_image_path in mask_image_list:
                    zipf.write(mask_image_list[idx], os.path.join("mask", "train", os.path.basename(mask_image_list[idx])))
                if self.include_instance:
                # for mask_instance_path in mask_instance_list:
                    zipf.write(mask_instance_list[idx], os.path.join("mask", "train", os.path.basename(mask_instance_list[idx])))
                current_progress += 1
                progress_dialog.setValue(current_progress)
                if progress_dialog.wasCanceled():
                    # Remove the ZIP file if the operation was canceled
                    os.remove(save_path)
                    break
                time.sleep(1)
            
            coco_json_path, image_path_list, mask_list, mask_image_list, mask_instance_list = self._convert_to_coco_format(self.valid_file_list, "valid")
            zipf.write(coco_json_path, os.path.join("valid", "_annotations.coco.json"))
            for idx, image_path in enumerate(image_path_list):
                zipf.write(image_path, os.path.join("valid", os.path.basename(image_path)))
                if self.include_mask:
                # for mask_path in mask_list:
                    zipf.write(mask_list[idx], os.path.join("mask", "valid", os.path.basename(mask_list[idx])))
                if self.include_img:
                # for mask_image_path in mask_image_list:
                    zipf.write(mask_image_list[idx], os.path.join("mask", "valid", os.path.basename(mask_image_list[idx])))
                if self.include_instance:
                # for mask_instance_path in mask_instance_list:
                    zipf.write(mask_instance_list[idx], os.path.join("mask", "valid", os.path.basename(mask_instance_list[idx])))
                current_progress += 1
                progress_dialog.setValue(current_progress)
                if progress_dialog.wasCanceled():
                    # Remove the ZIP file if the operation was canceled
                    os.remove(save_path)
                    break
                time.sleep(1)
            
            coco_json_path, image_path_list, mask_list, mask_image_list, mask_instance_list = self._convert_to_coco_format(self.test_file_list, "test")
            zipf.write(coco_json_path, os.path.join("test", "_annotations.coco.json"))
            for idx, image_path in enumerate(image_path_list):
                zipf.write(image_path, os.path.join("test", os.path.basename(image_path)))
                if self.include_mask:
                # for mask_path in mask_list:
                    zipf.write(mask_list[idx], os.path.join("mask", "test", os.path.basename(mask_list[idx])))
                if self.include_img:
                # for mask_image_path in mask_image_list:
                    zipf.write(mask_image_list[idx], os.path.join("mask", "test", os.path.basename(mask_image_list[idx])))
                if self.include_instance:
                # for mask_instance_path in mask_instance_list:
                    zipf.write(mask_instance_list[idx], os.path.join("mask", "test", os.path.basename(mask_instance_list[idx])))
                current_progress += 1
                progress_dialog.setValue(current_progress)
                if progress_dialog.wasCanceled():
                    # Remove the ZIP file if the operation was canceled
                    os.remove(save_path)
                    break
                time.sleep(1)
        shutil.rmtree(self.temp_dir)
        progress_dialog.setValue(total_files)
        if progress_dialog.wasCanceled():
            # Remove the ZIP file if the operation was canceled
            os.remove(save_path)
            return None
        return save_path


class ExportFileDialog(QDialog):
    """Dialog to select task type and export format for exporting files."""

    def __init__(self, parent=None, save_dir=None, data_dir=None):
        super().__init__(parent)
        self.setWindowTitle('Export Options')
        self.setMaximumHeight(300)
        self.setMaximumWidth(700)

        self.save_dir = save_dir
        self.data_dir = data_dir
        self.file_list = []
        self.config_file = 'config.yaml'
        self.task_type = ANNOTATION_TYPE.BBOX
        self.export_type = ExportType.COCO
        self.include_mask = False
        self.include_img = False
        self.include_instance = False
        self.training_percentage = 60
        self.validation_percentage = 20
        self.test_percentage = 20

        self._read_config()
        self._init_ui()
        self._connect_signals()
        self._update_train_test_validation()
    
    def _read_config(self):
        try:
            with open(os.path.join(self.save_dir, self.config_file), 'r') as file:
                self.config = yaml.safe_load(file)
                # print(self.config)
                self.task_type = ANNOTATION_TYPE(self.config['annotation_type'])
                # self.include_mask = self.config['save_mask']
                self.file_list = [file for file in os.listdir(self.save_dir) if file.endswith('.json')]
                # print(self.file_list)
                print(f"file length: {len(self.file_list)}")
        except FileNotFoundError:
            print('File not found')

    def _init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        
        # Export type selection
        self.export_type_selection = QComboBox(self)
        self.update_export_options(['COCO', 'Pascal VOC', 'YOLOv5', 'YOLOV7', 'YOLOv8', 'YOLOV9'])
        main_layout.addWidget(QLabel('Export Format:'))
        main_layout.addWidget(self.export_type_selection)
        
        # Train/Test/Validation sliders
        sliders_group = self._create_sliders_group()
        main_layout.addWidget(sliders_group)
        
        # Checkbox for include mask
        self.mask_group = QGroupBox("Mask Options", self)
        self.mask_layout = QHBoxLayout()

        self.include_mask_checkbox = QCheckBox("Include mask", self)
        self.mask_layout.addWidget(self.include_mask_checkbox)
        self.mask_group.setLayout(self.mask_layout)
        main_layout.addWidget(self.mask_group)

        
        # Export button
        self.export_button = QPushButton('Export', self)
        main_layout.addWidget(self.export_button)
        
        self.setLayout(main_layout)

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
        train = int(len(self.file_list)*self.training_percentage/100)
        valid = int(len(self.file_list)*self.validation_percentage/100)
        test = len(self.file_list) - train - valid
        self.label.setText(f"Train: {self.training_percentage}% ({train})\n"
                           f"Valid: {self.validation_percentage}% ({valid})\n"
                           f"Test: {self.test_percentage}% ({test})")

    def _connect_signals(self):
        """Connect signals to their respective slots."""
        # self.object_detection_radio.clicked.connect(self._on_task_type_changed)
        # self.segmentation_radio.clicked.connect(self._on_task_type_changed)
        # self.pose_radio.clicked.connect(self._on_task_type_changed)

        self.export_type_selection.currentIndexChanged.connect(self._on_export_type_changed)
        self.export_button.clicked.connect(self._on_export)
        self.include_mask_checkbox.stateChanged.connect(self._on_checkbox_state_changed)

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
        if self.task_type == ANNOTATION_TYPE.POLYGON:
            if self.include_mask:
                print(f"task type: {self.task_type}")
                self.include_img_checkbox = QCheckBox("Include img", self)
                self.include_img_checkbox.stateChanged.connect(self._on_img_checkbox_state_changed)
                self.mask_layout.addWidget(self.include_img_checkbox)
                self.include_instance_checkbox = QCheckBox("Include instance", self)
                self.include_instance_checkbox.stateChanged.connect(self._on_instance_checkbox_state_changed)
                self.mask_layout.addWidget(self.include_instance_checkbox)
            else:
                self.mask_layout.removeWidget(self.include_img_checkbox)
                self.include_img_checkbox.deleteLater()
                self.include_img = False
                self.mask_layout.removeWidget(self.include_instance_checkbox)
                self.include_instance_checkbox.deleteLater()
                self.include_instance = False
    def _on_instance_checkbox_state_changed(self):
        """Handle the state change of the instance checkbox."""
        self.include_instance = self.include_instance_checkbox.isChecked()
    
    def _on_img_checkbox_state_changed(self):
        """Handle the state change of the img checkbox."""
        self.include_img = self.include_img_checkbox.isChecked()
    def _on_export(self):
        """Handle the export operation."""
        if self.export_type == ExportType.YOLOV5 or self.export_type == ExportType.YOLOV7 or self.export_type == ExportType.YOLOV8 or self.export_type == ExportType.YOLOV9:
            yolo_conversion = YOLOConversion(self.save_dir, self.data_dir, self.file_list, self.training_percentage, self.validation_percentage, self.test_percentage, self.include_mask, self.include_img, self.include_instance, self.task_type)
            if yolo_conversion.zip_filename:
                QMessageBox.information(self, 'Export Successful', f'Exported data to {yolo_conversion.zip_filename}')
                self.accept()
                return
        elif self.export_type == ExportType.COCO:
            coco_conversion = COCOConversion(self.save_dir, self.data_dir, self.file_list, self.training_percentage, self.validation_percentage, self.test_percentage, self.include_mask, self.include_img, self.include_instance, self.task_type)
            if coco_conversion.zip_filename:
                QMessageBox.information(self, 'Export Successful', f'Exported data to {coco_conversion.zip_filename}')
                self.accept()
                return
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
