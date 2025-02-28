import os

from PIL import Image

from core import load_province_colors, load_tag_colors
from core import apply_colors_to_map
from core import extract_provinces_block, map_provinces_to_countries



MAP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "map"))
SAVES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))
TAGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "country_tags"))

OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))



def get_savefile_input():
    options = [f"{i}. {filename}" for i, filename in enumerate(os.listdir(SAVES_FOLDER), start=1)]

    option = None
    while not option:
        try:
            print("\n".join(options) + "\n")
            filenum = int(input("Enter savefile number to open: \n"))

            if not 1 <= filenum <= len(options):
                raise IndexError

            option = options[filenum - 1]
        except ValueError:
            print("Please enter a number.\n")
        except IndexError:
            print("Not a valid option.\n")

    return option.split()[1]


def main():
    savefile = get_savefile_input()

    block_data = extract_provinces_block(os.path.join(SAVES_FOLDER, savefile))
    print("Getting provinces....")
    provinces = map_provinces_to_countries(block_data)

    print("Getting colors for country....")
    tag_files = os.listdir(TAGS_FOLDER)
    country_colors = load_tag_colors(tag_files=tag_files, tags_folder=TAGS_FOLDER)

    print("Getting province bmp colors....")
    def_path = os.path.join(MAP_FOLDER, "definition.csv")
    province_colors = load_province_colors(defpath=def_path)

    print("Filling in map....")
    bmp_path = os.path.join(MAP_FOLDER, "provinces.bmp")
    map_bmp = Image.open(bmp_path).convert("RGB")
    colored_map = apply_colors_to_map(provinces, country_colors, province_colors, map_bmp)
    colored_map.save(os.path.join(OUTPUT_FOLDER, "new_map.png"))

if __name__ == "__main__":
    main()
