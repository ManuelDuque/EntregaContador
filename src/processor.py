from utils import singleton, Utils
import numpy as np, cv2, os, pandas as pd
from MTM import matchTemplates

@singleton
class Processor:

    REAL_TIME_REACTIVE = True
    DEBUG_MODE = False

    def __init__(self, template_path:str = "images/templates"):
        self.__utils__ = Utils()
        # Load the counters json
        self.__counters_config__ = self.__utils__.loadJson("config/counters.json")
        # Load the templates
        self.__templates__ = []
        template_path = self.__utils__.getAbsolutePath(template_path)
        for folder in os.listdir(template_path):
            # Check if the folder is a folder
            if os.path.isdir(os.path.join(template_path, folder)):
                new_path = os.path.join(template_path, folder)
                # Iterate inside of all the files inside the folder
                for file in os.listdir(new_path):
                    # Check if the file is a file
                    file_path = os.path.join(new_path, file)
                    if os.path.isfile(file_path):
                        # Rename the file with the new name
                        try:
                            image = cv2.imread(file_path)
                            self.__templates__.append( (file.split(".")[0], image) )
                        except Exception as e:
                            print(e)
        # Check the integrity of the templates
        if len(self.__templates__) == 0:
            raise Exception("No templates were loaded.")
        # Reset the processor
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
        if self.DEBUG_MODE:
            print(f'{"Getting the counters from the previous frame":.^100}')
        return self.__counters_frames__
    
    def extract_digits(self, counter: cv2.Mat) -> int:
        '''
        Extract the digits from the counter.

        ### Parameters:
        - `counter`: The counter to be processed.

        ### Returns:
        - `str`: The value of the counter. If the counter is not valid, the value can contain the character `?`.
        '''
        gray = counter.copy()
        if self.DEBUG_MODE:
            print(f'\n{"Extracting digits from the counter":.^100}\n')
            print(f'{"Resizing the counter to equals size than templates":.^100}')
            print(f"Counter shape: {counter.shape}")
            # print(f'{"Transforming to gray":.^100}')
        # Transform the counter image to gray scale
        # gray: cv2.Mat = cv2.cvtColor(counter, cv2.COLOR_BGR2GRAY)
        # if self.DEBUG_MODE:
            # print(f"Gray shape: {gray.shape}")
            # cv2.imshow("Gray", gray)
        # Get the digits per counter from the config
        digits_per_counter = self.__utils__.getValueOf(self.__counters_config__, "digits_per_counter")
        digits_per_counter = digits_per_counter if digits_per_counter is not None else 4
        # Split the counter image in digits (all the digits should have the same width space)
        width = int(gray.shape[1] / digits_per_counter)
        height = gray.shape[0]
        if self.DEBUG_MODE:
            print(f'{"Splitting the counter in digits":.^100}')
            print(f"Counter shape for each digit: (width: {width}), (height: {height})")
        digits = []
        for i in range(digits_per_counter):
            image = gray[0:height, i*width:(i+1)*width]
            # Resize the image to the template size
            image = cv2.resize(image, (self.__templates__[0][1].shape[1], self.__templates__[0][1].shape[0]), interpolation=cv2.INTER_CUBIC)
            digits.append(image)
        if self.DEBUG_MODE:
            # Show the digits
            for i in range(digits_per_counter):
                cv2.imshow(f"Digit {i}", digits[i])
        # Get the values the search of template
        score_threshold = self.__utils__.getValueOf(self.__counters_config__, "score_threshold")
        score_threshold = score_threshold if score_threshold is not None else 0.6
        maxOverlap = self.__utils__.getValueOf(self.__counters_config__, "max_overlap")
        maxOverlap = maxOverlap if maxOverlap is not None else 0.6
        searchBox = self.__utils__.getValueOf(self.__counters_config__, "search_box")
        searchBox = searchBox if searchBox is not None else (0, 0, self.__templates__[0][1].shape[1], self.__templates__[0][1].shape[0])
        value: str = ""
        for i in range(digits_per_counter):
            if self.DEBUG_MODE:
                cv2.imshow(f"Digit {i}", digits[i])
                template = self.__templates__[0][1]
                cv2.imshow(f"Template {i}", template)
                print(f'\n\n{"Searching the digit":.^100}\n')
                print(f"Parameters to search template: score_threshold: {score_threshold}, maxOverlap: {maxOverlap}, searchBox: {searchBox}")
            digit = digits[i]
            # Search the digit in the templates
            match_response: pd.DataFrame = matchTemplates(listTemplates=self.__templates__, image=digit, method=cv2.TM_CCOEFF_NORMED, score_threshold=score_threshold, searchBox=searchBox, maxOverlap=maxOverlap)
            if self.DEBUG_MODE:
                print(f'Digit {i} response of match:\n {match_response}')
            # Transform the response to a digit value 
            digit_value = "?"
            if match_response is not None and not match_response.empty:
                digit_value = int(match_response.get("TemplateName").values[0].split("_")[0])
            # Append the digit value to the value
            value += str(digit_value)
        # Adapt the valut of counter with the coma
        decimals_after_coma = self.__utils__.getValueOf(self.__counters_config__, "decimals_after_coma")
        decimals_after_coma = decimals_after_coma if decimals_after_coma is not None else 0
        if decimals_after_coma > 0:
            value = value[:-decimals_after_coma] + "." + value[-decimals_after_coma:]
        # Return the value of the counter
        return value