# OSM Import Roads and Public Transport Stops Plugin
This is the last one of 4 Plugins

## Overview
This QGIS plugin facilitates the seamless import and processing of OpenStreetMap (OSM) data for city road networks and public transport stops. It streamlines the integration of OSM data with GTFS (General Transit Feed Specification) datasets, enabling advanced spatial analysis and routing capabilities for public transport systems.

## Features
- **Road Network Import**: Automatically downloads and processes OSM road data, including highways, bus lanes, and other road types.
- **Public Transport Stops Integration**: Imports public transport stops from OSM and matches them with GTFS stops, ensuring consistency and accuracy.
- **GTFS Data Processing**: Enhances GTFS stop times and routes with spatial attributes derived from OSM data.
- **Routing Preparation**: Generates optimized layers for routing analysis, including stop positions and road segments.

## Teasing
Watch the teaser for this plugin [here](https://drive.google.com/file/d/1oaudC09QLDbCJ0qPIztnBvTf7KJRwrF7/view?usp=sharing).

## Plugin Series
This plugin is the second in a series of four plugins designed to work together for comprehensive public transport analysis:
1. **GTFS Agency Selection** ([GitHub Repository](https://github.com/skagejj/gtfsagency_selection)): Focuses on selecting and filtering GTFS data for specific agencies.
2. **OSM Import Roads and Public Transport Stops** ([GitHub Repository](https://github.com/skagejj/OSMimport_roads_PTstops)): Handles the import and integration of OSM road and stop data with GTFS datasets.
3. **OSM PT Routing** ([GitHub Repository](https://github.com/skagejj/osm_pt_routing)): Provides advanced routing capabilities using the processed OSM and GTFS data.
4. **GTFS Shapes Tracer** (This plugin): Implements the shapes in the original GTFS.

## Usage
1. **Import Roads and Stops**: Use the plugin to download and process OSM road and stop data for your city.
2. **Enhance GTFS Data**: Match GTFS stops with OSM stops and enrich GTFS datasets with spatial attributes.
3. **Prepare Routing Layers**: Generate layers optimized for routing analysis, including stop positions and road segments.

## Video Tutorial
Watch the video tutorial for this plugin [here](https://drive.google.com/file/d/1-LpZNxSGjI7SOaZ7Hn3MHk-4omOrxm9-/view?usp=sharing).

## Installation
1. Clone or download the plugin repository.
2. Place the plugin folder in your QGIS plugins directory:
   ```
   c:\Users\<your_username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\
   ```
3. Restart QGIS and enable the plugin from the Plugin Manager.

## Dependencies
- QGIS 3.x
- Python libraries: `pandas`, `numpy`, `statistics`
- QGIS Processing Toolbox
- QuickOSM

## License
This plugin is distributed under the GNU General Public License v2.0 or later.

## Author
Luigi Dal Bosco  
Email: luigi.dalbosco@gmail.com  
Generated using [QGIS Plugin Builder](http://g-sherman.github.io/Qgis-Plugin-Builder/).
