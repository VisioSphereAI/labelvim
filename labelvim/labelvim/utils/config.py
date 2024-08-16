from enum import Enum

class ANNOTATION_TYPE(Enum):
    NONE  = 0
    POINT = 1
    LINE = 2
    CIRCLE = 3
    # ELLIPSE = 4
    RECTANGLE = 4
    POLYGON = 5

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