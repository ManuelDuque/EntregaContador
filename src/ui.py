'''
ui module for the application to handle the user interface events
'''
from utils import singleton, Utils
from processor import Processor
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QFileDialog, QLabel
import cv2, numpy as np

@singleton
class Window:
    '''
    Window of user interface for the application.
    '''

    def __init__(self, *arguments):
        # Load the utils class
        self.utils = Utils()
        # Load the processor class
        self.processor = Processor()
        # Load the default configuration file
        self.ui_config = self.utils.loadJson("config/ui_config.json")
        # Process the arguments
        self.__process_args__(*arguments)
        # Load the ui file
        ui_file = self.utils.getValueOf(self.ui_config, "ui", "ui_relative_path")
        ui_file = ui_file if ui_file is not None else "./../config/ui_config.ui"
        self.ui = uic.loadUi(ui_file)
        # Set the window title
        title = self.utils.getValueOf(self.ui_config, "ui", "title")
        title = title if title is not None else "Counter Example"
        self.ui.setWindowTitle(title)
        # Set the connections
        self.__set_events_connections__()
        # Run the window
        self.ui.show()
    
    def __process_args__(self, *arguments):
        '''
        Process the arguments to work with the application.
        '''
        # Iterate over the arguments
        for i in range(0, len(arguments), 2):
            # Get the operation and the value
            operation = arguments[i]
            argument = arguments[i+1]
            # Check the operation
            if operation == "-ui":
                # Set the config file of the ui
                self.ui_config = self.utils.loadJson(argument)
                # Check the integrity of the configuration file
                if self.ui_config is None:
                    raise Exception("The configuration file is not valid.")
            elif operation == "-counter":
                # Set the counter file configuration
                self.processor.set_config(argument)

    def __set_events_connections__(self):
        '''
        Set the connections of the ui.
        '''
        # When user press "load" button
        self.ui.Load_button.clicked.connect(self.__load_event__)
        # When user press "clip" button
        self.ui.Clip_button.clicked.connect(self.__clip_event__)
        # When user press "extract" button
        self.ui.OCR_button.clicked.connect(self.__extract_event__)
        # When user press "global" button
        self.ui.GLOBAL_button.clicked.connect(self.__global_event__)
    
    def __load_event__(self) -> bool:
        '''
        Handle the event of load button.

        ### Parameters:
        - `None`: Nothing

        ### Returns:
        - `bool`: True if the event is handled successfully, False otherwise.
        '''
        # Get the default folder for images
        images_dir = self.utils.getValueOf(self.ui_config, "images", "folder_relative_path")
        images_dir = images_dir if images_dir is not None else "./../images/sources"
        # Get the caption of the dialog
        caption = self.utils.getValueOf(self.ui_config, "images", "load_dialog_caption")
        caption = caption if caption is not None else "Select an image"
        # Get the filter of the dialog
        filter = self.utils.getValueOf(self.ui_config, "images", "load_dialog_filter")
        filter = filter if filter is not None else "Images (*.png *.xpm *.jpg)"
        # Launch the dialog
        dialog = QFileDialog.getOpenFileName(self.ui, caption, images_dir, filter)
        # Process the dialog input
        image_url = str(dialog[0])
        if image_url is None or image_url == "":
            return False
        # Reset the ui
        self.__reset__()
        # Load the image
        image = cv2.imread(image_url)
        # Adapt the image to the viewer size
        image = self.__adapt_to_viewer__(viewer = self.ui.viewer_original, frame = image)
        # Save the current image
        self.__image__ = image
        # Set the image to the viewer
        return self.__set_image_to_viewer__(viewer = self.ui.viewer_original, frame = image)

    def __reset__(self):
        '''
        Reset the ui.
        '''
        pass

    def __clip_event__(self) -> bool:
        '''
        Handle the event of clip button.

        ### Parameters:
        - `None`: Nothing

        ### Returns:
        - `bool`: True if the event is handled successfully, False otherwise.

        ### Notes:
        - The events are handled successfully if the image of all the counters are set to the ui.
        - The image must be loaded before.
        - The counters must be defined in the counters config file.
        '''
        # Validate the event
        successfully = True
        # For each counter in the screen
        counters = self.processor.get_counters_in_frame(frame = self.__image__)
        for index, counter in enumerate(counters):
            # Get the corresponding viewer
            viewer: QLabel = self.ui.__dict__.get(f"viewer_counter{index+1}", None)
            if viewer is None:
                print(f"WARN: viewer_counter{index+1} not found")
                successfully = False
                continue
            # Adapt to the ui
            counter = self.__adapt_to_viewer__(viewer = viewer, frame = counter)
            # Set the image to the viewer
            if not self.__set_image_to_viewer__(viewer = viewer, frame = counter):
                successfully = False
        # Return successfully if all the counters are set to the ui or not
        return successfully
    
    def __extract_event__(self) -> bool:
        '''
        Handle the event of extract button.
        '''
        # Validate the event
        successfully = True
        # For each counter previusly processed, extract all the digits
        counters = self.processor.get_counters_saved()
        for index, counter in enumerate(counters):
            # Extract the digits
            digits = self.processor.extract_digits(counter = counter)
            # Show the digits in the ui
            label = self.ui.__dict__.get(f"resultado{str(index+1)}", None)
            if label is None:
                print(f"WARN: resultado{index+1} not found")
                successfully = False
                continue
            # Set the text to the viewer label
            label.setText(str(digits))
        return successfully

    def __global_event__(self) -> bool:
        '''
        Handle the event of global button.
        '''
        # Simulate a press to the load button
        sucessfully = self.__load_event__()
        if not sucessfully:
            return False
        # Simulate a press to the clip button
        sucessfully = self.__clip_event__()
        if not sucessfully:
            return False
        # Simulate a press to the extract button
        return self.__extract_event__()

    def __adapt_to_viewer__(self, viewer:QLabel, frame:np.ndarray) -> np.ndarray:
        '''
        ### Private method.
        Adapt the frame to the viewer size.

        ### Parameters:
        - `viewer`: The viewer window.
        - `frame`: The frame to adapt.

        ### Returns:
        - `frame`: The frame adapted to the view_source size.
        '''
        if frame is None:
            return None
        # Get width and height of the video_source window
        width, height = viewer.width(), viewer.height()
        # Resize the frame
        print(f"INFO: Resizing frame to {width}x{height}")
        print(f"INFO: Previous frame shape: {frame.shape}")
        try:
            frame = cv2.resize(frame, dsize=(width, height), interpolation=cv2.INTER_CUBIC)
        except Exception as e:
            print(f"ERROR: {e}")
        return frame
    
    def __set_image_to_viewer__(self, viewer:QLabel, frame:np.ndarray=None) -> bool:
        '''
        Set the image to the viewer window.

        ### Parameters:
        - `viewer`: The viewer window.
        - `image`: The image to set.

        ### Returns:
        - `bool`: True if the image is set successfully, False otherwise.
        '''
        if frame is None:
            return False
        # Get the pixmap from the image and show it
        qimage = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage( qimage.rgbSwapped() )
        # Show the image in the video_source window
        viewer.setPixmap(pixmap)
        return True