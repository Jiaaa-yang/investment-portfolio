import json

def read_data(filepath, key):
    with open(filepath, "r") as file:
        data = json.load(file)
    return data.get(key)

def write_data(filepath, key, entry):
    with open(filepath, "r") as read_file:
        data = json.load(read_file)
    # If data to write is funding or holdings history, append instead
    if isinstance(data[key], list):
        history_list = data.get(key)
        history_list.append(entry)
    # Normal data, overwrite previous entry
    else:
        data[key] = entry
    with open(filepath, "w") as write_file:
        json.dump(data, write_file, indent=4)