from enum import Enum

class ANNOTATION_TYPE(Enum):
    BBOX = 1
    POLYGON = 2
    NONE = 3

class ANNOTATION_MODE(Enum):
    NONE = 0
    CREATE = 1
    EDIT = 2
    DELETE = 3
    DUPLICATE = 4
    CLEAR = 5

class OBJECT_LIST_ACTION(Enum):
    ADD = 0
    REMOVE = 1
    UPDATE = 2
    CLICKED = 3
    CLEAR = 4
    EDIT = 5
    NONE = 6

class TaskType(Enum):
    OBJECT_DETECTION = 0
    SEGMENTATION = 1
    POSE = 2
    CLASSIFICATION = 3


class ExportType(Enum):
    YOLOV5 = 0
    YOLOV8 = 1
    PASCAL_VOC = 2
    COCO = 3

import yaml
class ConfigSpecHandler:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = {}
        self._read_config()
    
    def _read_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            self._create_config()
    
    def _create_config(self):
        self.save_config()
    
    def get_config(self):
        return self.config
    
    def get_config_value(self, key):
        return self.config[key]
    
    def set_config_value(self, key, value):
        self.config[key] = value
        self.save_config()
    
    def update_config(self, new_config):
        self.config = new_config
        self.save_config()
    def save_config(self):
        with open(self.config_file, 'w') as file:
            yaml.dump(self.config, file)

