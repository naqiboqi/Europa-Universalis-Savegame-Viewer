## EU4 Savegame Parser & Map Renderer

Allows you to parse Europa Universalis IV (.eu4) save files and generate a map highlighting provinces controlled by a specific country.

This is a fun little side project born out of my love-hate relationship with EU4 🙃

* Identify country ownership of provinces.

* Render a modified EU4 map highlighting a selected country.

#### Prerequisites:
-------------------

1. **Python 3.10+** **https://www.python.org/downloads/**

    * Make sure that Python is included under your `$PATH`

2. **Packages**
    * To install the necessary packages,
    run this command:
    `pip install -r path/to/requirements.txt` or
    `python -m install -r path/to/requirements.txt`

#### Usage:
Place your EU4 save file(s) within the `saves` folder

Launch the script, it will prompt you to select a save file to load and display.



Example output from the 1444 start:

![alt text](/images/start_date_map.png)

Note that unoccupied provinces will be assigned a random color (as of now...)

#### To-Do
-----------
- [ ] Add other mapmodes native to EU4 (trade, subjects)

- [ ] Add map-painter functionality to control ownership of provinces and create modded saves

- [ ] Add some graphs to show country area (with and without water), and other stats such as development