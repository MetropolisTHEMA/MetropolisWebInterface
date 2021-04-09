#import pandas as pd
#import geopandas as gpd
#from pyproj import CRS
#from shapely import affinity
#from shapely.geometry import Point, LineString
#import networkx as nx
#import sys
#import os
#mport tkinter as tk
#from tkinter import filedialog
#mport math
#from math import cos
#import datetime
#from datetime import datetime
#

"""
Street Network
==============
The main task of this function is to draw an interactive web map representing a street network.

.. figure:: ../images/idf.png
   :height: 500px
   :align: center


Steps
-----
* importing nodes and edges files, nodes first.
* merging them into one dataframe which will be converted as a geodataframe
* Setting geometry's variables.
* spliting network : abstract (Simple=True) and real (Simple=False) network
* adding oneway column to separte multidirectional and one-way roads
* appliying an offset distance in multi-directional roads to repesent them

Prerequisites
-------------
Installing Python 3 and all imprted packages in the module

Input
-----
The function receive two files containing nodes and edges of a street network.

"""
def metroweb_network(Simple,
         set_initial_crs,
         zone_radius=15,
         intersection_radius_percentage = 0.8,
         distance_offset_percentage = 0.8,
         line_color='orange',
         link_side = 'right'
         ):

    '''
    Parameters
    ----------
    Simple                         : boolean, if True this is an abstract network, False a valid network
    set_initial_crs                : initial coordinates system reference from which the data is created.
    convert_to_crs                 : projection coordinates system reference we want to project the data
    zone_radius                    : radius of zone nodes (in meter)
    intersection_radius_percentage : number between 0 and 1, representing a percentage of zone's radius
    distance_offset_percentage     : number between 0 and 1, representing a percentage of zone's radius
    line_color                     : color of lines
    link_side                      : shift made to the right or left

    Returns
    -------
    Html object representing an interactive folium map.
    '''

    # Statical variables
    initial_crs = "EPSG:{}".format(set_initial_crs)
    initial_crs = CRS(initial_crs)
    convert_to_crs = "EPSG:4326"
    default_crs = "EPSG:3857"

    # Opening the folder containing the two files (filedialog)
    root = tk.Tk()
    root.withdraw()
    root.iconbitmap("/Users/ndiayeabass/desktop/Metropolis/CY/Tasks")
    file_path_1 = filedialog.askopenfilename(initialdir="/Users/ndiayeabass/desktop/Metropolis/CY/Tasks",
                    title="Select a Metropolis file",
                    filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    file_path_2 = filedialog.askopenfilename(initialdir="/Users/ndiayeabass/desktop/Metropolis/CY/Tasks",
                    title="Select a Metropolis file",
                    filetypes=(("csv files", "*.csv"), ("all files", "*.*")))

    nodes_df = pd.read_csv(file_path_1)
    nodes_df.rename(columns = {'id': 'id_node'}, inplace=True)

    edges_df = pd.read_csv(file_path_2)#,delimiter=';')
    edges_df.rename(columns = {'id': 'id_edge'}, inplace=True)

    # merge origin coordonates
    edges_df = edges_df.merge(nodes_df[['id_node','x','y']], left_on = 'origin', right_on='id_node')

    # rename x and y coordiantes
    edges_df.rename(columns= {'x': 'x_origin', 'y': 'y_origin'},  inplace=True)
    edges_df.drop('id_node', axis=1, inplace=True) # drop id_node from the table

    # merge destination coordinates
    edges_df=edges_df.merge(nodes_df[['id_node', 'x','y']], left_on='destination', right_on='id_node')
    edges_df.rename(columns={'x':'x_dest', 'y':'y_dest'}, inplace=True)
    edges_df.drop('id_node', axis=1, inplace=True)

    # Convert a dataframe to a geodataframe
    nodes_geometry = gpd.points_from_xy(nodes_df.x, nodes_df.y)
    edges_geometry = edges_df.apply(lambda x: LineString([(x['x_origin'], x['y_origin']), (x['x_dest'],
                                                           x['y_dest'])]), axis=1)


    # Split street network caracteristics like Circular City (Simple=True) and others huge one (Simple=False)
    if Simple:
        nodes_gdf = gpd.GeoDataFrame(nodes_df, geometry = nodes_geometry)
        edges_gdf = gpd.GeoDataFrame(edges_df, geometry = edges_geometry)
        edges_gdf = edges_gdf[edges_gdf.geometry.length>0]                  # Delete edges with null lenght (points)
        edges_gdf.set_crs(convert_to_crs, inplace=True)                     # Setting projection equal to 4326
        nodes_gdf.set_crs(convert_to_crs, inplace=True)                     # Setting projection equal to 4326
        intersection_radius = min(edges_gdf.geometry.length)*0.1            # output is a degree value which we will convert to meter in next line
        intersection_radius = intersection_radius*111.11*1000               # applying a formula which convert degree to meter (regle de trois)
        zone_radius = intersection_radius/intersection_radius_percentage    # zone_radius and intersection_radius are dependents
        distance_offset =distance_offset_percentage*intersection_radius     # distance_offset depends on intersection_radius (meter)
        tiles_layer = None
    else:
        nodes_gdf = gpd.GeoDataFrame(nodes_df, crs=initial_crs, geometry = nodes_geometry)
        edges_gdf = gpd.GeoDataFrame(edges_df, crs=initial_crs, geometry = edges_geometry)
        nodes_gdf.to_crs(convert_to_crs, inplace=True)
        edges_gdf = edges_gdf[edges_gdf.geometry.length>0]                                   # Delete edges with null lenght (points)
        intersection_radius = intersection_radius_percentage*zone_radius
        zone_radius=zone_radius
        distance_offset =distance_offset_percentage*zone_radius
        tiles_layer = 'OpenStreetMap'


    # Takes only valid links and nodes
    # edges_gdf = edges_gdf[edges_gdf.is_valid==True]
    # nodes_gdf = nodes_gdf[nodes_gdf.is_valid==True]

    # Convert a GeoDataFrame to a Graph
    G = nx.from_pandas_edgelist(edges_gdf,'origin', 'destination',
                                  ['key','id_edge', 'name', 'lanes','length',
                                  'speed', 'capacity', 'function', 'geometry'],
                                  create_using=nx.MultiDiGraph())

    # Add nodes to the graph G
    #data = nodes_gdf.set_index('id_node').to_dict('index').items()
    #G.add_nodes_from(data)

    # Add oneway column (it is a boolean column)
    for u,v,d in G.edges(keys=False, data=True):
        if G.has_edge(v,u):
            G.edges[u,v,0]['oneway'] = False
        else:
            G.edges[u,v,0]['oneway'] = True

    # df_oneway = df_parallel_roads = df.loc[df['oneway']==True].copy()
    df_graph_to_pandas = nx.to_pandas_edgelist(G, source='origin', target='destination')
    df_all_roads= df_graph_to_pandas.copy()
    df_all_roads = gpd.GeoDataFrame(df_all_roads, crs =set_initial_crs)

    # We convert to meters (m) before applying the offset in order to have the same unit
    df_all_roads.to_crs(crs=default_crs, inplace=True)

    # Let's define the parallel offset GeoSerie
    df_all_roads['_offset_geometry_'] = df_all_roads[['geometry', 'oneway']].apply(lambda x:
                            x['geometry'].parallel_offset(distance_offset, link_side) if not x['oneway']
                            else x['geometry'].parallel_offset(0, link_side), axis=1)

    # Drop the old geometry and replace it by __offset_geometry_
    df_all_roads.drop('geometry', axis=1, inplace=True)
    gdf_all_roads = gpd.GeoDataFrame(df_all_roads, geometry ='_offset_geometry_', crs=default_crs)
    gdf_all_roads.to_crs(crs=convert_to_crs, inplace=True)

    # Ploting the network
    nodes_gdf=nodes_gdf.sort_values(by="zone", ascending=True, ignore_index=True)
    latitudes = list(nodes_gdf['geometry'].y)
    longitudes = list(nodes_gdf['geometry'].x)
    labels = list(nodes_gdf['zone'])

    # Initialize the map
    m = folium.Map(location=[latitudes[0],longitudes[0]],max_zoom = 18, prefer_canvas=True,
                   tiles = tiles_layer)

    # Create a GeoJson onject and display the street network
    layer = folium.GeoJson(gdf_all_roads,tooltip=folium.GeoJsonTooltip(
        fields=['oneway','id_edge','lanes', 'length','speed', 'capacity'], localize=True),
        style_function = lambda x: {'color': line_color,
                                'dashArray':'5, 5' if x['properties']['function']==1 else '5, 1'}
                                ).add_to(m)

    # Bounding box the map such that the network is entirely center and visible
    m.fit_bounds(layer.get_bounds())

    # Adding the nodes points
    dx=zone_radius*10**-3/111.3  #  Conversion metre en degres
    for lat, long, label in list(zip(latitudes, longitudes, labels)):
        if label == False:
            folium.Circle(location = [lat, long], color='cyan',fill=True, fill_opacity=1, radius=intersection_radius,
                          tooltip='Intersection').add_to(m)
        else:
            folium.Rectangle(bounds=[(lat-dx/2, long-dx/2), (lat+dx/2, long+dx/2) ], color='#4CFF33', line_join='round',
                             tooltip='Zone', fill=True, fill_opacity=1).add_to(m)

    # Adding a seach navigation bar
    Search(layer=layer, geom_type="Point", placeholder="Search for a street", search_label="id_edge",
           search_zoom = 16, collapsed=True, position='topright').add_to(m)

    # Saving the map as an html file
    m.save('index.html')
    print("Executed at ", datetime.now())

if __name__ == "__main__":
    #main(False, 7133)                            # Amsterdam  7073,
    #main(False,3857)                            # Brussels
    #main(Simple=True)                           # Circular city
    metroweb_network(False,27561)                           # IDF
