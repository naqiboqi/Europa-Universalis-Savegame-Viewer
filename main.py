import os

from PIL import Image
from core import *


MAP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "map"))
OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))
SAVES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))
TAGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "country_tags"))



def get_file_input(name: str, filetypes: tuple[str], folder: str):
    options = [
        f"{i}. {filename}" for i, filename in enumerate(os.listdir(folder), start=1)
        if filename.endswith(filetypes)]

    if not options:
        return

    option = None
    while not option:
        try:
            print("\n".join(options) + "\n")
            filenum = int(input(f"Enter {name} number to open: \n"))

            if not 1 <= filenum <= len(options):
                raise IndexError

            option = options[filenum - 1]
        except ValueError:
            print("Please enter a number.\n")
        except IndexError:
            print("Not a valid option.\n")

    return option.split()[1]

def select_main_menu_option():
    options = [
        "1. Load processed map image.",
        "2. Load save file.", 
        "3. Close program."]

    print("\n".join(options) + "\n")
    option = int(input("Select an option!\n"))
    if not 1 <= option <= len(options):
        raise IndexError
    return option


def main():
    world = EUWorldData.load_world_data(MAP_FOLDER)
    print(world.provinces)
    colors = EUColors.load_colors(MAP_FOLDER, TAGS_FOLDER)

    while True:
        try:
            option = select_main_menu_option()
        except (ValueError, IndexError):
            print("Invalid option. Please try again.\n")
            continue

        match(option):
            case 1:
                mapfile = get_file_input("mapfile", (".png", ".bmp"), OUTPUT_FOLDER)
                if not mapfile:
                    print("No .png or .bmp mapfiles to load, please process a save first.\n")
                    continue

                map_path = os.path.join(OUTPUT_FOLDER, mapfile)
                analyze_map(map_path, colors.country_colors)
            case 2:
                savefile = get_file_input("savefile", (".eu4"), SAVES_FOLDER)
                if not savefile:
                    print("No .eu4 savefiles to load, please get one from your saves folder.\n")
                    continue

                save_path = os.path.join(SAVES_FOLDER, savefile)
                country_provinces = world.load_savefile_provinces(MAP_FOLDER, save_path)

                print("Filling in map....")
                bmp_path = os.path.join(MAP_FOLDER, "provinces.bmp")
                map_bmp = Image.open(bmp_path).convert("RGB")
                colored_map = apply_colors_to_map(country_provinces, colors.country_colors, colors.default_colors, map_bmp)
                colored_map.save(os.path.join(OUTPUT_FOLDER, "new_map.png"))
            case 3:
                print("\nExiting...")
                exit()


if __name__ == "__main__":
    main()
