import yaml
from labelvim.utils.utils import get_project_root

class LabelListReader:
    def __init__(self, label_list_path='labelvim/data/label_list.yaml'):
        self.label_list_path = label_list_path
        self.label_list = self.read()

    def read(self):
        with open(self.label_list_path, 'r') as f:
            label_list = yaml.safe_load(f)
        return label_list

    def write(self, label_list):
        with open(self.label_list_path, 'w') as f:
            yaml.dump(label_list, f, indent=4)

    def update(self, label_list):
        self.label_list = label_list
        self.write(label_list)

label_list_reader = LabelListReader()
parent_dir = get_project_root()
# LABEL_LIST = label_list_reader.read()
print(f"Parent Dir: {parent_dir}")
lebel_list_path = parent_dir + '/labeled_list.yaml'
label_list_reader.label_list_path = lebel_list_path
label_list_reader.write(label_list_reader.label_list)