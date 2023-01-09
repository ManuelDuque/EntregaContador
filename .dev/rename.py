import sys, os

def rename_files(path:str):
    # Iterate inside of all the folders inside the folder named output
    for folder in os.listdir(path):
        # Check if the folder is a folder
        if os.path.isdir(os.path.join(path, folder)):
            digit_value = str(folder)
            index_value = 0
            new_path = os.path.join(path, folder)
            # Iterate inside of all the files inside the folder
            for file in os.listdir(new_path):
                # Check if the file is a file
                file_path = os.path.join(new_path, file)
                if os.path.isfile(file_path):
                    # Rename the file with the new name
                    try:
                        os.rename(file_path, os.path.join(new_path, f"{digit_value}_{index_value}.png"))
                    except Exception as e:
                        # print(e)
                        pass
                    index_value += 1

if __name__ == "__main__":
    if len(sys.argv) == 2:
            rename_files(sys.argv[1])
    else:
        print(f"Usage: python {sys.argv[0]} <path>")
    exit(0)