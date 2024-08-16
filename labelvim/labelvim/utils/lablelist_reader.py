import yaml
from labelvim.utils.utils import get_project_root  # Utility function to get the project root directory

import os

class LabelListReader:
    """
    Handles reading and writing a list of labels to a YAML file.

    Attributes:
        label_list_path (str): Path to the YAML file containing the label list.
        label_list (list): List of labels read from the YAML file.
    """

    def __init__(self, label_list_path: str = None):
        """
        Initializes the LabelListReader class.

        Args:
            label_list_path (str, optional): Path to the YAML file. If not provided, initializes an empty list.
        """
        self.label_list_path = label_list_path
        self.label_list = [] if label_list_path is None else self.read()

    def read(self):
        """
        Reads the label list from the YAML file.

        Returns:
            list: The list of labels read from the file.
        
        Raises:
            FileNotFoundError: If the specified YAML file does not exist.
        """
        with open(self.label_list_path, 'r') as f:
            self.label_list = yaml.safe_load(f)
        return self.label_list

    def get(self):
        """
        Retrieves the current label list.

        Returns:
            list: The current list of labels.
        """
        return self.label_list

    def write(self, label_list):
        """
        Writes the provided label list to the YAML file.

        Args:
            label_list (list): The list of labels to write to the file.
        """
        with open(self.label_list_path, 'w') as f:
            yaml.dump(label_list, f, indent=4)

    def update(self, label_list):
        """
        Updates the current label list and writes it to the YAML file.

        Args:
            label_list (list): The new list of labels to update.
        """
        self.label_list = label_list
        self.write(label_list)

# Example usage
parent_dir = get_project_root()  # Get the root directory of the project
label_list_path = os.path.join(parent_dir, 'labeled_list.yaml')  # Construct the full path to the YAML file
label_list_reader = LabelListReader(label_list_path)  # Create an instance of LabelListReader with the file path

if __name__ == "__main__":
    # Read the label list from the file
    labels = label_list_reader.read()
    print("Labels read from file:", labels)

    # Update the label list
    new_labels = ['label1', 'label2', 'label3']
    label_list_reader.update(new_labels)
    print("Updated labels:", label_list_reader.get())

    # Write the updated label list to the file
    label_list_reader.write(new_labels)
    print("Labels written to file:", label_list_reader.get())