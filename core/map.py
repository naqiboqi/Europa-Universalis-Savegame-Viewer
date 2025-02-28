from PIL import Image



def apply_colors_to_map(
    country_provinces: dict[int, str],
    country_colors: dict[str, tuple[int]], 
    province_colors: dict[tuple[int], int], 
    map_bmp: Image.Image):

    pixels = map_bmp.load()
    width, height = map_bmp.size

    for x in range(width):
        for y in range(height):
            pixel_color = pixels[x, y]
            if pixel_color in province_colors:
                province_id = province_colors[pixel_color]
                country_tag = country_provinces[province_id]

                if country_tag and country_tag in country_colors:
                    pixels[x, y] = country_colors[country_tag]
                elif country_tag == "WASTE":
                    pixels[x, y] = (128, 128, 128)
                elif country_tag == "WATER":
                    pixels[x, y] = (55, 90, 220)

    return map_bmp