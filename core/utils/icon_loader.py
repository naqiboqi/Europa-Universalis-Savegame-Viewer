import os



class IconLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, icons_folder):
        if not self._initialized:
            self.icons_folder = icons_folder
            self.cache = {}
            self._initialized = True

    def get_icon(self, icon_name: str):
        if icon_name in self.cache:
            return self.cache[icon_name]
        
        for root, _, files in os.walk(self.icons_folder):
            if icon_name in files:
                icon_path = os.path.join(root, icon_name)
                self.cache[icon_name] = icon_path
                return icon_path
        else:
            print(f"Warning, unable to find icon {icon_name} in {self.icons_folder}")
            return None