import os



class IconLoader:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, icons_folder: str=None):
        if not self._initialized:
            if icons_folder is None:
                base_dir = os.path.dirname(os.path.abspath(__file__))
                icons_folder = os.path.join(base_dir, "../../data/icons/trade_good_icons") 

            self.icons_folder = os.path.abspath(icons_folder)
            self.cache = {}
            self.default = os.path.join(self.icons_folder, "Unknown.png")
            self._initialized = True

    def get_icon(self, icon_name: str):
        if not icon_name.lower().endswith(".png"):
            icon_name += ".png"

        if icon_name in self.cache:
            return self.cache[icon_name]

        if not os.path.exists(self.icons_folder):
            print(f"Warning: Icons folder '{self.icons_folder}' not found.")
            return self.default

        for root, _, files in os.walk(self.icons_folder):
            if icon_name in files:
                icon_path = os.path.abspath(os.path.join(root, icon_name))
                self.cache[icon_name] = icon_path
                return icon_path
        else:
            self.cache[icon_name] = self.default
            return self.default