'''

'''
# Path: src\main.py
import sys
from PyQt5.QtWidgets import QApplication
from src.ui import Window

if __name__ == "__main__":
    # Create a instance of QApplication
    app = QApplication( sys.argv )
    arguments = None
    # Check the arguments
    if len(sys.argv) > 1:
        print("Arguments: ", sys.argv[1:])
        # Check if the number of arguments is pair
        if len(sys.argv[1:]) % 2 != 0:
            print("The number of arguments must be pair.")
            sys.exit(1)
        arguments = sys.argv[1:]
    # Create a window
    Window(arguments)
    # Execute the application
    app.exec_()
    # Exit the application
    sys.exit(0)