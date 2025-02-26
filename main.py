import json
import os
import re



DATA_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
SAVES_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "saves"))



def get_provinces_block(savefile_path: str):
    with open(savefile_path, "r", encoding="utf-8") as file:
        lines = iter(file)
        inside = False
        depth = 0
        data = []

        for line in file:
            line = line.strip()
            if not inside and line == "provinces={":
                next_line = next(lines, "").strip()
                if next_line == "-1={":
                    inside = True
                    depth = 2
                    data.extend([line + "\n", next_line + "\n"])
                    continue

            if inside:
                data.append(line + "\n")
                depth += line.count("{") - line.count("}")
                if depth == 0:
                    break

    return data


def get_country_provinces(datafile_path: str):
    with open(datafile_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    countries: dict[str, list[str]] = {}

    for i in range(len(lines)):
        line = lines[i]
        if is_province_subblock(line):
            j = i

            key = ""
            while not key:
                if j >= len(lines):
                    return countries

                search_line = lines[j].strip()
                key = get_country_id(search_line)
                if key:
                    prov_id = get_prov_id(line)
                    if key in countries:
                        countries[key].append(prov_id)
                    else:
                        countries[key] = [prov_id]
                    i = j
                else:
                    j += 1

    return countries

def get_prov_id(line: str):
    pattern = r"^-(\d+)={"
    match = re.match(pattern, line)
    return match.group(1) if match else None

def is_province_subblock(line: str):
    pattern = r"^-\d+={$"
    return bool(re.match(pattern, line))

def get_country_id(line: str):
    pattern = r'^owner="(\w+)"'
    match = re.match(pattern, line)
    return match.group(1) if match else None


def main():
    options = [f"{i}. {filename}" for i, filename in enumerate(os.listdir(SAVES_FOLDER), start=1)]

    file_option = None
    while not file_option:
        try:
            print("\n".join(options) + "\n")
            filenum = int(input("Enter savefile number to open: \n"))

            if not 1 <= filenum <= len(options):
                raise IndexError

            file_option = options[filenum - 1]
        except ValueError:
            print("Please enter a number.\n")
        except IndexError:
            print("Not a valid option.\n")

    savefile_path = file_option.split()[-1]
    filepath = os.path.join(SAVES_FOLDER, savefile_path)
    data = get_provinces_block(filepath)

    data_filename = f"{savefile_path[:-4]}.prov"
    data_path = os.path.join(DATA_FOLDER, data_filename)
    with open(data_path, "w", encoding="utf-8") as file:
        file.writelines(data)

    provinces = get_country_provinces(data_path)
    print(provinces)

if __name__ == "__main__":
    main()
