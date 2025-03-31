import os

from core import EUColors, EUWorldData, MapDisplayer, MapPainter



MAP_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "map"))
OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "output"))
SAVES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))
TAGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data", "country_tags"))



# def get_file_input(name: str, filetypes: tuple[str], folder: str):
#     """Prompts the user to select a file to load from the list.
    
#     Args:
#         name (str): The type of file to load (ex. 'savefile')
#         filetypes (tuple[str]): File extensions to check for (ex. '.txt', '.dat', '.eu4')

#     Returns:    
#         option: The chosen option
#     Raises:
#         IndexError: If invalid option is entered.
#         ValueError: If a non-numeric is entered.
#     """
#     print("\nAvailable files:")
#     options = [
#         f"{i}. {filename}" for i, filename in enumerate(os.listdir(folder), start=1)
#         if filename.endswith(filetypes)]

#     if not options:
#         return

#     option = None
#     while not option:
#         try:
#             print("\n".join(options))
#             filenum = int(input(f"\nEnter {name}'s number to open: "))

#             if not 1 <= filenum <= len(options):
#                 raise IndexError

#             option = options[filenum - 1]
#         except ValueError:
#             print("Please enter a number.\n")
#         except IndexError:
#             print("Not a valid option.\n")

#     return option.split()[1]

# def select_main_menu_option():
#     """Prompts the user to select an option from the list.
    
#     Raises:
#         IndexError: If invalid option is entered.
#     """
#     options = [
#         "\n1. Load save file.", 
#         "2. Close program.\n"]

#     print("\n".join(options))
#     option = int(input("Select an option: "))
#     if not 1 <= option <= len(options):
#         raise IndexError
#     return option


def main():
    """Driver function that handles loading the necessary game files."""
    colors = EUColors.load_colors(MAP_FOLDER, TAGS_FOLDER)
    world = EUWorldData.load_world_data(MAP_FOLDER, colors)

    # while True:
    #     try:
    #         option = select_main_menu_option()
    #     except (ValueError, IndexError):
    #         print("Invalid option. Please try again.\n")
    #         continue

    #     match(option):
    #         case 1:
    #             savefile = get_file_input("savefile", (".eu4"), SAVES_FOLDER)
    #             if not savefile:
    #                 print("No .eu4 savefiles to load, please get one from your saves folder.\n")
    #                 continue

    #             save_path = os.path.join(SAVES_FOLDER, savefile)
    #             print(f"Loading savefile {savefile}....")
    #             world.build_world(SAVES_FOLDER, save_path)

    #             map_painter = MapPainter(colors=colors, world_data=world)
    #             map_display = MapDisplayer(painter=map_painter)
    #             map_display.display_map()
    #         case 2:
    #             print("\nExiting...")
    #             exit()

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
