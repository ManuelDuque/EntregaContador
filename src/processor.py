from utils import singleton, Utils
import numpy as np, cv2, os
from MTM import matchTemplates

@singleton
class Processor:

    REAL_TIME_REACTIVE = True
    DEBUG_MODE = True

    def __init__(self, template_path:str = "images/templates"):
        self.__utils__ = Utils()
        # Load the counters json
        self.__counters_config__ = self.__utils__.loadJson("config/counters.json")
        # Load the templates
        self.__templates__ = []
        template_path = self.__utils__.getAbsolutePath(template_path)
        for filename in os.listdir(template_path):
            image = cv2.imread(os.path.join(template_path, filename))
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.__templates__.append( (filename.split(".")[0], image) )
        # Initialize variables
        self.reset()

    def reset(self) -> bool:
        '''
        Reset the processor.
        
        ### Parameters:
        - No parameters.

        ### Returns:
        - `bool`: True if the processor is reset successfully, False otherwise.
        '''
        self.__counters_frames__ = None
        return True
    
    def get_counters_in_frame(self, frame: np.ndarray) -> list:
        '''
        Get a list of counters in the frame.
        
        ### Parameters:
        - `frame`: The frame to be processed.

        ### Returns:
        - `list`: A list of counters (numpy.ndarray -> images) in the frame.
        '''
        if self.REAL_TIME_REACTIVE:
            self.__counters_config__ = self.__utils__.loadJson("config/counters.json")
        # Get the number of counters that has to be in the frame following the config
        counters = self.__utils__.getValueOf(self.__counters_config__, "counters")
        if counters is None:
            raise Exception("The counters are not defined in the config file.")
        # Get the counters images
        counters_to_return = []
        for counter in counters:
            x, y = self.__utils__.getValueOf(counter, "x"), self.__utils__.getValueOf(counter, "y")
            width, height = self.__utils__.getValueOf(counter, "width"), self.__utils__.getValueOf(counter, "height")
            if x is None or y is None or width is None or height is None:
                continue
            # Get the counter image
            counter_image = frame[y:y+height, x:x+width]
            # Append the counter image to the list
            counters_to_return.append(counter_image)
        # Save the counters frames
        self.__counters_frames__ = counters_to_return
        # Return the list of counters frames
        return counters_to_return

    def get_counters_saved(self) -> list:
        '''
        Get the counters from the previous frame processed.
        
        ### Parameters:
        - No parameters.

        ### Returns:
        - `list`: A list of counters (numpy.ndarray -> images) in the frame.
        '''
        return self.__counters_frames__

    def extract_digits(self, counter: np.ndarray) -> int:
        '''
        Extract the digits from the counter.

        ### Parameters:
        - `counter`: The counter to be processed.

        ### Returns:
        - `int`: The value of the counter.
        '''
        value: int = 0
        if self.DEBUG_MODE:
            print(f'{"Extracting digits from the counter":.^100}')
            print(f'{"Transforming to gray":.^100}')
        # Transform the counter image to gray scale
        gray = cv2.cvtColor(counter, cv2.COLOR_BGR2GRAY)
        if self.DEBUG_MODE:
            cv2.imshow("Gray", gray)
            print(f"Gray shape: {gray.shape}")
        # Get the digits per counter from the config
        digits_per_counter = self.__utils__.getValueOf(self.__counters_config__, "digits_per_counter")
        digits_per_counter = digits_per_counter if digits_per_counter is not None else 4
        # Split the counter image in digits (all the digits should have the same width space)
        width = int(gray.shape[1] / digits_per_counter)
        height = gray.shape[0]
        if self.DEBUG_MODE:
            print(f'{"Splitting the counter in digits":.^100}')
            print(f"Counter shape: (width: {width}), (height: {height})")
        digits = []
        for i in range(digits_per_counter):
            digits.append(gray[0:height, i*width:(i+1)*width])
        if self.DEBUG_MODE:
            # Show the digits
            for i in range(digits_per_counter):
                cv2.imshow(f"Digit {i}", digits[i])
        # Get the values the search of template
        score_threshold = self.__utils__.getValueOf(self.__counters_config__, "score_threshold")
        score_threshold = score_threshold if score_threshold is not None else 0.6
        searchBox = self.__utils__.getValueOf(self.__counters_config__, "search_box")
        searchBox = searchBox if searchBox is not None else (0, 0, 90, 130)
        for i in range(digits_per_counter):
            if self.DEBUG_MODE:
                print(f'{"Searching the digit":.^100}')
            digit = digits[i]
            # Search the digit in the templates
            digit_value_filename = matchTemplates(listTemplates=self.__templates__, image=digit, method=cv2.TM_CCOEFF_NORMED, score_threshold=score_threshold, searchBox=searchBox)
            if self.DEBUG_MODE:
                print(f'Digit {i} value: {digit_value_filename}')
            digit_value = 0
            if digit_value is None:
                continue
            # Append the digit value to the value
            value += digit_value * (10 ** (digits_per_counter - i - 1))
        
        return value