import os

def replace_whitespace(path):
    for root, folders, files in os.walk(path):
        for folder in folders:
            if " " in folder:
                os.rename(os.path.join(path, folder), os.path.join(path, folder.replace(' ', '_')))
        for file in files:
            if " " in file:
                os.rename(os.path.join(path, file), os.path.join(path, file.replace(' ', '_')))


if __name__ == "__main__":
    replace_whitespace(os.getcwd())
