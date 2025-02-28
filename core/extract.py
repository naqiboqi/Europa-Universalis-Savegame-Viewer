import os

from core.colors import extract_province_colors
from core.provinces import extract_provinces_block, map_provinces_to_countries



def extract_save_data(
    savefile: str,
    map_folder: str,
    save_folder: str):

    block_data = extract_provinces_block(os.path.join(save_folder, savefile))
    print("Getting provinces....")
    country_provinces = map_provinces_to_countries(block_data)

    print("Getting province bmp colors....")
    def_path = os.path.join(map_folder, "definition.csv")
    province_colors = extract_province_colors(defpath=def_path)
    return country_provinces, province_colors