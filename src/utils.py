def singleton(cls, *args, **kwargs):
    '''
    Singleton decorator for classes that need to be instantiated only once in the application.
    The class will have arguments and keyword arguments to be passed to the constructor.
    '''
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

@singleton
class Utils:

    def getAbsolutePath(self, path):
        '''
        Get the absolute path of the relative path given from the parent directory. If the path is already absolute, return the same path.

        ### Parameters:
        path: The path to transform (str).

        ### Returns:
        The relative path (str).

        ### Example:
        - getAbsolutePath( "config.json" ) -> "C:/Users/.../config.json"
        - getAbsolutePath( "src/config.json" ) -> "C:/Users/.../src/config.json"
        - getAbsolutePath( "C:/Users/.../config.json" ) -> "C:/Users/.../config.json"
        '''
        import os
        if os.path.isabs( path ):
            return path
        current_dir = os.path.dirname( __file__ )
        parent_dir = os.path.abspath( os.path.join( current_dir, os.pardir ) )
        return os.path.normpath( os.path.join( parent_dir, path ) )
    
    def loadJson(self, path):
        '''
        Load a json file and return the data as a dictionary from the relative path given.

        ### Parameters:
        path: The relative path of the json file (str).

        ### Returns:
        The data of the json file as a dictionary (dict).
        '''
        import json
        with open( self.getAbsolutePath( path ) ) as json_file:
            data = json.load( json_file )
        return data
    
    def getValueOf(self, _dict: dict, key, *keys):
        '''
        Get the value of a key or keys from the provided dictionary. If the key or keys are not found, return None.

        ### Parameters:
        _dict: The dictionary to get the value from (dict).
        key: The key to get the value from the dictionary (str).
        keys: The keys to get the value from the dictionary (str).

        ### Returns:
        The value of the key or keys from the dictionary (str).
        '''
        value = _dict.get( key, None )
        # Check if the value is not None
        if value is None:
            return None
        # Check if the keys argument is not empty
        if len( keys ) == 0:
            return value
        # Check if the value is a dictionary
        if not isinstance( value, dict ):
            return None
        # Process the keys
        for key in keys:
            if value is not None:
                value = value.get( key, None )
        # Return the final value
        return value