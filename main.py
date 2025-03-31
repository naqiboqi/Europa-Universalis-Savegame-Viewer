import os

from core import EUColors, EUWorldData, MapDisplayer, MapPainter



MAP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "map"))
OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))
SAVES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))
TAGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "country_tags"))


def main():
    """Driver function that handles loading the necessary game files."""
    colors = EUColors.load_colors(MAP_FOLDER, TAGS_FOLDER)
    world = EUWorldData.load_world_data(MAP_FOLDER, colors)

    default_savefile_path = os.path.join(SAVES_FOLDER, "default_1444.eu4")
    if os.path.exists(default_savefile_path):
        print("Loading default save....")
        world.build_world(SAVES_FOLDER, default_savefile_path)
    else:
        print("Warning.... Default savefile not found!")
        return

    map_painter = MapPainter(colors=colors, world_data=world)
    map_display = MapDisplayer(painter=map_painter, saves_folder=SAVES_FOLDER)
    map_display.display_map()


if __name__ == "__main__":
    main()
