import os
import json

data_folder = os.path.abspath("KQAPro.IID")

with open(os.path.join(data_folder, "train.json")) as train_file:
    train_data = json.load(train_file)
    print(train_data)
