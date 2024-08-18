import cv2
import numpy as np
import os
import json
from PIL import Image

# random_colors_palette = np.random.randint(0, 255, (30, 3))
random_colors_palette =np.array([[143, 195,  54],
       [234, 168,  85],
       [155, 117, 139],
       [ 59,  64, 124],
       [ 85, 148,  82],
       [116,   4,  28],
       [ 82, 168,  66],
       [ 13,  88,  59],
       [131, 181, 186],
       [220, 237, 240],
       [ 85, 199,  53],
       [ 18, 112, 239],
       [  9,   3, 187],
       [174, 232, 136],
       [167,  86, 145],
       [254, 125, 249],
       [ 78, 207, 201],
       [ 36, 118, 183],
       [233, 140,   2],
       [178, 215, 249],
       [ 84, 234, 239],
       [ 63, 206,   2],
       [153, 213, 184],
       [ 88, 142, 138],
       [ 98, 209, 121],
       [ 57,  12, 107],
       [ 22, 147, 117],
       [253,  62, 126],
       [ 30, 237,  74]])

def save_mask(mask, save_dir, file_name):
    """
    Save the mask to the save directory as a PNG file.
    
    Args:
        mask (np.ndarray): The mask to save.
        save_dir (str): The directory to save the mask to.
        file_name (str): The name of the mask file.
        
    Example:
        >>> mask = np.zeros((100, 100), dtype=np.uint8)
        >>> save_mask(mask, "data", "mask.png")
    """
    mask = Image.fromarray(mask)
    os.makedirs(os.path.join(save_dir, 'mask'), exist_ok=True)
    print(os.path.join(save_dir, 'mask', file_name))
    print(os.listdir(os.path.join(save_dir, 'mask')))
    print(os.listdir(save_dir))
    # os.listdir(os.path.join(save_dir, 'mask'))
    mask.save(os.path.join(save_dir, 'mask', file_name))

def create_mask(image=None, annotations=None, label_map=None, include_img = False, mask_type='polygon'):
    """
    Create a mask from the image and annotations.
    
    Args:
        image (np.ndarray): The image to create the mask from.
        annotations (list): The list of annotations.
        
    Returns:
        np.ndarray: The mask.
        
    Example:
        >>> image = np.zeros((100, 100, 3), dtype=np.uint8)
        >>> annotations = [
        {
            "id": 0,
            "category_id": 2,
            "bbox": [
                431,
                126,
                211,
                269
            ],
            "area": 56759,
            "segmentation": [
                470,
                387,
                541,
                394,
                599,
                370
            ],
            "iscrowd": 0
        }
    ]
        >>> label_map = [Dress, book, Face, Football, laftLowerLeg]
        >>> mask = create_mask(image, annotations)
    """
    mask = np.zeros((image.shape[0], image.shape[1], 3), dtype=np.uint8)
    for annotation in annotations:
        if mask_type == 'polygon':
            segmentation = annotation['segmentation']
            segmentation = np.array(segmentation).reshape(-1, 2)
            segmentation = segmentation.astype(np.int32)
            cv2.fillPoly(mask, [segmentation], color=random_colors_palette[annotation['category_id']].tolist())
            label = label_map[annotation['category_id']]
            cv2.putText(mask, label, (segmentation[0][0], segmentation[0][1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        elif mask_type == 'bbox':
            bbox = annotation['bbox']
            x, y, w, h = bbox
            cv2.rectangle(mask, (x, y), (x + w, y + h), random_colors_palette[annotation['category_id']].tolist(), -1)
            label = label_map[annotation['category_id']]
            cv2.putText(mask, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    if include_img and image is not None:
        mask = cv2.addWeighted(image, 0.5, mask, 0.5, 0)
    return mask