import os

from core import MapDisplayer, MapPainter



MAP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "map"))
SAVES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))
TAGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "country_tags"))


def main():
    map_painter = MapPainter()
    map_display = MapDisplayer(painter=map_painter, saves_folder=SAVES_FOLDER)
    map_display.launch(maps_folder=MAP_FOLDER, tags_folder=TAGS_FOLDER)


if __name__ == "__main__":
    main()
