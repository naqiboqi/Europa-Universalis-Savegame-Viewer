import os

from core import EUColors, EUWorldData, MapPainter



MAP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "map"))
OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))
SAVES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))
TAGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "country_tags"))



def get_file_input(name: str, filetypes: tuple[str], folder: str):
    print("\nAvailable files:")
    options = [
        f"{i}. {filename}" for i, filename in enumerate(os.listdir(folder), start=1)
        if filename.endswith(filetypes)]

    if not options:
        return

    option = None
    while not option:
        try:
            print("\n".join(options))
            filenum = int(input(f"\nEnter {name}'s number to open: "))

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
        "\n1. Load save file.", 
        "2. Close program.\n"]

    print("\n".join(options))
    option = int(input("Select an option: "))
    if not 1 <= option <= len(options):
        raise IndexError
    return option


def main():
    colors = EUColors.load_colors(MAP_FOLDER, TAGS_FOLDER)
    world = EUWorldData.load_world_data(MAP_FOLDER, colors)

    while True:
        try:
            option = select_main_menu_option()
        except (ValueError, IndexError):
            print("Invalid option. Please try again.\n")
            continue

        match(option):
            case 1:
                savefile = get_file_input("savefile", (".eu4"), SAVES_FOLDER)
                if not savefile:
                    print("No .eu4 savefiles to load, please get one from your saves folder.\n")
                    continue

                save_path = os.path.join(SAVES_FOLDER, savefile)
                print(f"Loading savefile {savefile}....")
                world.build_world(SAVES_FOLDER, save_path)
                world_painter = MapPainter(colors=colors, world_data=world)
                world_painter.draw_map()
            case 2:
                print("\nExiting...")
                exit()


if __name__ == "__main__":
    main()
