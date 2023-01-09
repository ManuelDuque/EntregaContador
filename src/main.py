'''

'''
# Path: src\main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui import Window

if __name__ == "__main__":
    # Create a instance of QApplication
    app = QApplication( sys.argv )
    # Create a window
    window = Window()
    # Execute the application
    app.exec_()
    # Exit the application
    sys.exit(0)