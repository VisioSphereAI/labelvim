import os
import yaml
import json
from labelvim.utils.save_mask import random_colors_palette, create_mask, save_mask

ANNOTATION_LABEL = "label.json"
# bounding box format: [x, y, width, height]
# segmentation format: [[x1, y1, x2, y2, x3, y3, x4, y4]]
# area: width * height
# Reference: https://bboxconverter.readthedocs.io/en/latest/explanation/bounding_box_ultimate_guide.html

def list_json_annotation_files(directory):
    """
    List all JSON annotation files in a directory.

    Args:
        directory (str): The directory to search for JSON files.

    Returns:
        list: A list of JSON files in the directory.
    """
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    return json_files

def load_annotation_label(save_dir):
    """
    Load the annotation label from the save directory.

    Args:
        save_dir (str): The directory to load the annotation label from.

    Returns:
        dict: The annotation label data.
    """
    with open(os.path.join(save_dir, ANNOTATION_LABEL), 'r') as file:
        return json.load(file)
    
def check_annotation_label(save_dir):
    """
    Check if the annotation label file exists in the save directory.

    Args:
        save_dir (str): The directory to check for the annotation label file.

    Returns:
        bool: True if the annotation label file exists, False otherwise.
    """
    return os.path.exists(os.path.join(save_dir, ANNOTATION_LABEL))

def save_annotation_label(save_dir, annotation_label):
    """
    Save the annotation label to the save directory.

    Args:
        save_dir (str): The directory to save the annotation label to.
        annotation_label (dict): The annotation label data.
    """
    with open(os.path.join(save_dir, ANNOTATION_LABEL), 'w') as file:
        json.dump(annotation_label, file, indent=4)


class AnnotationManager:
    """
    A class to manage image annotations for object detection or segmentation tasks.

    Attributes:
        save_dir (str): The directory to save the annotation label to.
        file_name (str): The name of the annotation label file.
        annotation (dict): The annotation label data.
    
    Methods:
        __init__(save_dir, file_name): 
            Initialize the annotation manager with the save directory and file name
        check_annotation_exists(): 
            Check if the annotation label file exists.
        load_annotation(): 
            Load the annotation label from the save directory.
        update_basic_info(image_path, image_height, image_width, image_data): 
            Update the basic information of the annotation.
        add_annotation(annotation): 
            Add a new annotation to the annotation label.
        delete_annotation(annotation_id): 
            Delete an annotation label by ID.
        
    """
    def __init__(self, save_dir, file_name) -> None:
        """
        Initialize the annotation manager with the save directory and file name.
        
        Args:
            save_dir (str): The directory to save the annotation label to.
            file_name (str): The name of the annotation label file.
        
        Example:
            >>> manager = AnnotationManager("data", "file_name.json")
        """
        self.save_dir = save_dir
        self.file_name = file_name
        if self.check_annotation_exists():
            self.annotation = self.load_annotation()
        else:
            self.annotation = {
                "annotations": [],
                "imagePath": None,
                "imageData": None,
                "imageHeight": None,
                "imageWidth": None,
                "imageData": None
            }            

    def check_annotation_exists(self):
        """
        Check if the annotation label file exists in the save directory.
        
        Returns:
            bool: True if the annotation label file exists, False otherwise.
        """
        return os.path.exists(os.path.join(self.save_dir, self.file_name))

    def load_annotation(self):
        """
        Load the annotation label from the save directory.
        
        Returns:
            dict: The annotation label data.
            
        Example:
            >>> manager = AnnotationManager("data", "file_name.json")
            >>> manager.load_annotation()
        """
        with open(os.path.join(self.save_dir, self.file_name), 'r') as file:
            return json.load(file)
    
    def update_basic_info(self, image_path, image_height, image_width, image_data = None):
        """
        Update the basic information of the annotation.

        Args:
            image_path (str): The path to the image file.
            image_height (int): The height of the image.
            image_width (int): The width of the image.
            image_data (str): The image data in base64 format.

        Example:
            >>> manager.update_basic_info("data/image.jpg", 768, 1024)
            >>> manager.update_basic_info("data/image.jpg", 768, 1024, "base64data")
        """
        self.annotation["imagePath"] = image_path
        self.annotation["imageHeight"] = image_height
        self.annotation["imageWidth"] = image_width
        self.annotation["imageData"] = image_data
    
    def add_annotation(self, annotation: dict):
        """
        Add a new annotation to the annotation label.

        Args:
            annotation (dict): The annotation to add or update. It should contain the following keys:
                - id (int): The unique identifier for the annotation.
                - category_id (int): The category ID for the annotation.
                - bbox (list): The bounding box coordinates [x, y, width, height].
                - area (int): The area of the bounding box.
                - segmentation (list): The segmentation coordinates.
                - iscrowd (int): Indicates if the annotation is a crowd.

        
        Example:
            >>> annotation = {
            ...     "id": 1,
            ...     "category_id": 1,
            ...     "bbox": [10, 20, 100, 200],
            ...     "area": 1000,
            ...     "segmentation": [[10, 20, 100, 20, 100, 200, 10, 200]],
            ...     "iscrowd": 0
            ... }
            >>> manager.add_annotation(annotation)
        """

        # check if the annotation already exists
        for idx, ann in enumerate(self.annotation["annotations"]):
            if ann['id'] == annotation['id']:
                # update that index annotation
                self.annotation["annotations"][idx] = annotation
                break
            else:
                self.annotation["annotations"].append(annotation)
    
    def delete_annotation(self, annotation_id: int):
        """
        Delete an annotation label by ID.

        Args:
            annotation_id (int): The ID of the annotation to delete.
        
        Example:
            >>> manager.delete_annotation(1)
        """
        self.annotation["annotations"] = [ann for ann in self.annotation["annotations"] if ann['id'] != annotation_id]
    
    def update_annotation(self, annotation: list):
        self.annotation["annotations"] = annotation
    
    def save_annotation(self):
        """
        Save the annotation label to the save directory.
        
        Example:
            >>> manager.save_annotation()
        """
        with open(os.path.join(self.save_dir, self.file_name), 'w') as file:
            json.dump(self.annotation, file, indent=4)
    
    def save_mask(self, label_map, image_data=None, include_img=True, mask_type='polygon'):
        """
        Create a mask from the image and annotations.
        
        Args:
            label_map (list): The list of label names.
            image_data (np.ndarray): The image to create the mask from.
            include_img (bool): Whether to include the image in the mask.
            mask_type (str): The type of mask to create ('polygon' or 'bbox').
        
        Returns:
            np.ndarray: The mask.
            
        Example:
            >>> mask = manager.create_mask()
        """
        file_name = self.annotation["imagePath"]
        annotations = self.annotation["annotations"]
        label_map = label_map
        mask = create_mask(image=image_data, annotations=annotations, label_map=label_map, include_img=include_img, mask_type=mask_type)
        save_mask(mask, self.save_dir, file_name)
    

    



    
