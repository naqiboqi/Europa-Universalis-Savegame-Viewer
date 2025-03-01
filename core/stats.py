from PIL import Image



def calculate_all_country_area(
    map_bmp: Image.Image, 
    country_colors: dict[str, tuple[int]]):

    pixels = map_bmp.load()
    width, height = map_bmp.size
    
    color_to_tag = {tuple(color): country for country, color in country_colors.items()}
    country_area = {country: 0 for country in country_colors}
    for x in range(width):
        for y in range(height):
            pixel_color = pixels[x, y]
            if pixel_color in color_to_tag:
                country_area[color_to_tag[pixel_color]] += 1

    return country_area

def sort_by_country_area(country_areas: dict[str, int]):
    return sorted(country_areas.items(), key=lambda item: item[1], reverse=True)

def analyze_map(map_path: str, country_colors: dict[str, tuple[int]]):
    # map_img = Image.open(map_path).convert("RGB")
    # areas = sort_by_country_area(calculate_all_country_area(map_img, country_colors))
    # print(areas)
    
    pass