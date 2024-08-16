import json

class AnnotationManager:
    """
    A class to manage image annotations for object detection or segmentation tasks.

    Attributes:
        images (list of dict): List of dictionaries containing image metadata.
        annotations (list of dict): List of dictionaries containing annotation data.
        categories (list of dict): List of dictionaries containing category data.

    Methods:
        __init__(self, images=None, annotations=None, categories=None):
            Initializes the manager with optional lists of images, annotations, and categories.
        
        add_annotation(self, annotation):
            Adds a new annotation to the list.
        
        update_annotation(self, annotation_id, updated_annotation):
            Updates an existing annotation by ID.
        
        delete_annotation(self, annotation_id):
            Deletes an annotation by ID.
        
        save_annotations_to_json(self, output_file):
            Saves the current images, annotations, and categories to a JSON file.
        
        load_annotations_from_json(self, input_file):
            Loads images, annotations, and categories from a JSON file.
    """

    def __init__(self, images=None, annotations=None, categories=None):
        """
        Initializes the AnnotationManager with optional lists of images, annotations, and categories.

        Args:
            images (list of dict, optional): List of dictionaries containing image metadata. Defaults to None.
            annotations (list of dict, optional): List of dictionaries containing annotation data. Defaults to None.
            categories (list of dict, optional): List of dictionaries containing category data. Defaults to None.

        Example:
            >>> manager = AnnotationManager(
            ...     images=[{"id": 1, "file_name": "image1.jpg", "width": 1024, "height": 768}],
            ...     annotations=[],
            ...     categories=[{"id": 1, "name": "cat", "supercategory": "animal"}]
            ... )
        """
        self.images = images if images else []
        self.annotations = annotations if annotations else []
        self.categories = categories if categories else []

    def add_annotation(self, annotation):
        """
        Add a new annotation to the list.

        Args:
            annotation (dict): A dictionary containing annotation data.

        Example:
            >>> new_annotation = {
            ...     "id": 1,
            ...     "image_id": 1,
            ...     "category_id": 3,
            ...     "segmentation": [[150, 250, 300, 250, 300, 400, 150, 400]],
            ...     "area": 22500,
            ...     "bbox": [150, 250, 150, 150],
            ...     "iscrowd": 0
            ... }
            >>> manager.add_annotation(new_annotation)
        """
        self.annotations.append(annotation)

    def update_annotation(self, annotation_id, updated_annotation):
        """
        Update an existing annotation by ID.

        Args:
            annotation_id (int): The ID of the annotation to update.
            updated_annotation (dict): A dictionary containing updated annotation data.

        Returns:
            bool: True if the annotation was updated successfully, False otherwise.

        Example:
            >>> updated_annotation = {
            ...     "id": 1,
            ...     "image_id": 1,
            ...     "category_id": 3,
            ...     "segmentation": [[160, 260, 310, 260, 310, 410, 160, 410]],
            ...     "area": 24000,
            ...     "bbox": [160, 260, 150, 150],
            ...     "iscrowd": 0
            ... }
            >>> manager.update_annotation(1, updated_annotation)
            True
        """
        for i, annotation in enumerate(self.annotations):
            if annotation['id'] == annotation_id:
                self.annotations[i] = updated_annotation
                return True
        return False

    def delete_annotation(self, annotation_id):
        """
        Delete an annotation by ID.

        Args:
            annotation_id (int): The ID of the annotation to delete.

        Example:
            >>> manager.delete_annotation(1)
        """
        self.annotations = [ann for ann in self.annotations if ann['id'] != annotation_id]

    def save_annotations_to_json(self, output_file):
        """
        Save the current images, annotations, and categories to a JSON file.

        Args:
            output_file (str): Path to the output JSON file.

        Example:
            >>> manager.save_annotations_to_json("annotations.json")
        """
        data = {
            "images": self.images,
            "annotations": self.annotations,
            "categories": self.categories
        }

        with open(output_file, 'w') as json_file:
            json.dump(data, json_file, indent=4)
    
    def update_category(self, category_id, updated_category):
        """
        Update an existing category by ID.

        Args:
            category_id (int): The ID of the category to update.
            updated_category (dict): A dictionary containing updated category data.

        Returns:
            bool: True if the category was updated successfully, False otherwise.

        Example:
            >>> updated_category = {
            ...     "id": 1,
            ...     "name": "cat",
            ...     "supercategory": "animal"
            ... }
            >>> manager.update_category(1, updated_category)
            True
        """
        for i, category in enumerate(self.categories):
            if category['id'] == category_id:
                self.categories[i] = updated_category
                return True
        return False
    
    def delete_category(self, category_id):
        """
        Delete a category by ID.

        Args:
            category_id (int): The ID of the category to delete.
        
        Example:
            >>> manager.delete_category(1)
        """
        self.categories = [cat for cat in self.categories if cat['id'] != category_id]
    
    def update_image(self, image_id, updated_image):
        """
        Update an existing image by ID.

        Args:
            image_id (int): The ID of the image to update.
            updated_image (dict): A dictionary containing updated image metadata.

        Returns:
            bool: True if the image was updated successfully, False otherwise.

        Example:
            >>> updated_image = {
            ...     "id": 1,
            ...     "file_name": "image1.jpg",
            ...     "width": 1024,
            ...     "height": 768
            ... }
            >>> manager.update_image(1, updated_image)
            True
        """
        for i, image in enumerate(self.images):
            if image['id'] == image_id:
                self.images[i] = updated_image
                return True
        return False


    def load_annotations_from_json(self, input_file):
        """
        Load images, annotations, and categories from a JSON file.

        Args:
            input_file (str): Path to the input JSON file.

        Example:
            >>> manager.load_annotations_from_json("annotations.json")
            >>> print(manager.images)
            >>> print(manager.annotations)
            >>> print(manager.categories)
        """
        with open(input_file, 'r') as json_file:
            data = json.load(json_file)
            self.images = data.get('images', [])
            self.annotations = data.get('annotations', [])
            self.categories = data.get('categories', [])

# Example usage:
if __name__ == "__main__":
    # Example image data
    images = [
        {"id": 1, "file_name": "image1.jpg", "width": 1024, "height": 768},
        {"id": 2, "file_name": "image2.jpg", "width": 1024, "height": 768}
    ]

    # Example categories
    categories = [
        {"id": 1, "name": "cat", "supercategory": "animal"},
        {"id": 2, "name": "dog", "supercategory": "animal"},
        {"id": 3, "name": "car", "supercategory": "vehicle"}
    ]

    # Initialize the manager
    manager = AnnotationManager(images, annotations=[], categories=categories)

    # Add a new annotation
    new_annotation = {
        "id": 1,
        "image_id": 1,
        "category_id": 3,
        "segmentation": [[150, 250, 300, 250, 300, 400, 150, 400]],
        "area": 22500,
        "bbox": [150, 250, 150, 150],
        "iscrowd": 0
    }
    manager.add_annotation(new_annotation)

    # Update an existing annotation
    updated_annotation = {
        "id": 1,
        "image_id": 1,
        "category_id": 3,
        "segmentation": [[160, 260, 310, 260, 310, 410, 160, 410]],
        "area": 24000,
        "bbox": [160, 260, 150, 150],
        "iscrowd": 0
    }
    manager.update_annotation(1, updated_annotation)

    # Delete an annotation
    manager.delete_annotation(1)

    # Save to JSON file
    output_file = "annotations.json"
    manager.save_annotations_to_json(output_file)
    print(f"Annotations saved to {output_file}")

    # Load from JSON file
    manager.load_annotations_from_json(output_file)
    print("Loaded annotations:", manager.annotations)
