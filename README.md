## **EU4 Savegame Parser & Map Renderer**

Allows you to parse Europa Universalis IV (.eu4) save files and generates the world map. Display all sorts of information about the world's provinces and areas.

This is a fun little side project born out of my love-hate relationship with EU4, and wanting to be able to read and analyze save games without launching the game.

#### Prerequisites:
-------------------

1. **Python 3.10+** **https://www.python.org/downloads/**

    * Make sure that Python is included under your `$PATH`

2. **Packages**
    * To install the necessary packages,
    run this command:
    `pip install -r path/to/requirements.txt` or
    `python -m install -r path/to/requirements.txt`

#### Start:
-----------
* To start, run this command from the `eu4_savegame` directory:
```python main.py```

You will see that it starts to print its progress in the terminal, as (for now) the GUI requires loading some dummy game data before it can open.

* After a minute or so, you are greeted with the GUI and some dummy game data from the 1444 start date, in the **Political** (default) map mode:

![alt text](/images/default_screen.png)

You may also notice that there are some question marks icons and empty spaces, these represent areas where icons and information will be loaded depending on the province/region/area that is selected.

#### Navigation
---------------

* The map supports zooming and panning. Scroll up/down while your cursor is over the map to zoom in/out. Click and drag the mouse to pan (**note** you cannot pan at the minimum zoom level as there is nothing to pan to).

* Hovering over a location in the map will give you basic information about the province depending on your mapmode:

    * **Political** shows the province name and its owner (if any).

    * **Area** shows the provinces name and area that it resides in.

    * **Region** shows the province name and region that it resides in.

    * **Development** shows the province name and its total development.

    * **Religion** shows the province name and its majority religion.

* Selecting a province/area/region can be done in two ways. First you can click on the province/area/region in the image and the map will center on that location, depending on the map mode:

    * **Political**, **Development**, **Religion** will center on the province.

    * **Area** will center on the area (group of provinces as defined by Europa Universaslis IV).

    * **Region** will center on the region (group of aras as defined by Europa Universalis IV).

* The second way is by searching for a name in the search bar on the left. Names are not case sensitive, but you can optionally choose to search for exact matches only:

![alt text](/images/search_example.png)

Here you are given a list of matches. Selecting an item in the list and clicking the **GOTO** button will center the map on the matching object, and display its information in the right info box:

![alt text](/images/search_example_result.png)

Now we get some information about the province of **Stockholm**!

We see that the information in the frame is populated with its name, area, capital, and region
in the top green banner (going clockwise), demographics, trade information, and military information.


* Now here is the screen that shows for the area that Stockholm is a part of, the area of Svaeland:

Now we get information about its name and region (going from left to right), a table showing the provinces that reside in it, and some overall income and trade information.

![alt text](/images/search_area_result.png)

Now for region, Scandinavia:

![alt text](/images/search_example_region.png)

Now we get information about its name, a table with the areas that reside in it, and some information about its total income and trade.

#### Map Modes
--------------
* By default, the GUI loads the **Political** map mode. In this mode, each province is colored according to who owns it. Countries (or TAGS) in EU4 have unique color. Though some countries are generated dynamicall after game start (such as Native Federations, Colonial Nations, or Client States), and will have a seeded (but still unique) color. 

![alt text](/images/political_map_mode.png)

* Here we can see all sorts of colors!

    * I'm not going to list all of them but to start, the bright red near the top center is **England**, muted yellow near the bottom center is **Castille**. The red to **Castille**'s left is its sister nation **Aragon**, and to **Castille**'s right is **Portugal**. To **Castille**'s northeast you see a messy blob consisting of blue **France** and its vassals and appenages (white **Armagnac**, peach **Orleans**, tourquoise **Bourbonnais**, etc. etc.)

* To select a different map mode, you can choose on of the options in the map mode frame on the right.

* When changing map modes, the GUI will freeze for a moment as the map is redrawn. Don't fret!

* Also note, changing the map mode does not affect information that is show in the bottom right info frame.

* And one last note, you may notice some grey, those represent wasteland provinces; impassible to troops and relatively inhospitable and cannot be owned or cored by any nation. Areas such as deserts (i.e. Sahara), extreme mountain ranges (i.e. Himalayas) or the Amazon or Borneo rainforests.


Examples of maps drawn in other modes besides **Political**:

**Area** 

![alt text](/images/area_map_mode.png)

- Breaks the map up into areas, or groups of provinces. Notice that the hovered information tooltip at the top now shows the area. Works similarly for other map modes.


Let's pan a bit to the south for **Region**

![alt text](/images/region_map_mode.png)

- Breaks the map up into regions, or groups of areas. Second-largest subdivision in the game after superregions (which are essentially continents, and not yet implemented....)

Pan and zoom a bit to the northwest for **Development**

![alt text](/images/development_map_mode.png)

* For development, each province is colored green, with brighter, higher intensities meaning higher development (which in EU4 terms, means it produces more taxes, more goods, and more manpower).

* Those of you who know your European geography can see that the location around **London** (Middlesex) is a darker shade of green than **Paris**, as the former has lower development. But **London** is a higher shade of green than **Normandy** or **Nedersticht** (I wish I could get my cursor to appear in these screenshots....)

**Religion**

![alt text](/images/religion_map_mode.png)

* Colors each provice with a seeded color based on its dominant religion

* Here we see light-purple as Catholic, medium-purple as Orthodox, red as Sunni Islam, neon-green as Coptic, and violet as Apostolic.  


#### To-Do
-----------
- [X] Add GUI for viewing and interacting with the map

- [X] Move loading save file functionality to the GUI 

- [ ] Add more mapmodes -> (Trade, Terrain, Religion, Culture)

- [ ] Add map-painter functionality to control ownership of provinces and create modded saves

- [ ] Add timeline to show game history