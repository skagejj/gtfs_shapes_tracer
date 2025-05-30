from qgis.core import (QgsVectorLayer, 
                        QgsField, 
                        edit, 
                        QgsExpression, 
                        QgsExpressionContext, 
                        QgsExpressionContextUtils, 
                        QgsVectorFileWriter,
                        QgsProject
)

import pandas as pd
from qgis import processing
from qgis.PyQt.QtCore import QVariant
import re
import os

def if_remove(file_path):
    if os.path.exists(file_path):
                os.remove(file_path)

def save_and_stop_editing_layers(layers):
    for layer in layers:
        if layer.isEditable(): 
            if layer.commitChanges():  
                print(f"Changes saved successfully for layer: {layer.name()}")
            else:
                print(f"Failed to save changes for layer: {layer.name()}")
                if not layer.rollBack(): 
                    print(f"Failed to rollback changes for layer: {layer.name()}")
        else:
            print(f"Layer '{layer.name()}' is not in editing mode.")

def shp_dst_trvl(lines_trips_csv,trip_gpkg,trip_name):
    lines_trips = pd.read_csv(lines_trips_csv,dtype='str', index_col='line_trip')
    
    trip_csv = lines_trips.loc[trip_name,'csv']

    trip_layer = QgsVectorLayer(trip_gpkg,trip_name,"ogr")
    
    field_index = trip_layer.fields().indexFromName('dist_stops')
                
    if field_index != -1:
        trip_layer.startEditing()
        trip_layer.deleteAttribute(field_index)
        trip_layer.commitChanges()
    else:
        print('Field dist_stops not found for '+str(trip_name))
    
                    #,QgsField("nd2pos", QVariant.Int)
    pr = trip_layer.dataProvider()
    pr.addAttributes([
                    QgsField("dist_stops", QVariant.Double)])
    trip_layer.updateFields()
    
    expression1 = QgsExpression('$length')
    #expression2 = QgsExpression('regexp_substr( "layer" ,\'(\\d+)$\')')

    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(trip_layer))

    with edit(trip_layer):
        for f in trip_layer.getFeatures():
            context.setFeature(f)
            f['dist_stops'] = expression1.evaluate(context)
            trip_layer.updateFeature(f)
    trip_layer.commitChanges()

    lsto_keep = ['layer','dist_stops']
       
    IDto_delete = [trip_layer.fields().indexOf(field_name) for field_name in lsto_keep]
    IDto_delete = [index for index in IDto_delete if index != -1]
    
    if_remove(trip_csv)
    QgsVectorFileWriter.writeAsVectorFormat(trip_layer,trip_csv,"utf-8",driverName = "CSV",attributes=IDto_delete)

    trip_df = pd.read_csv(trip_csv,dtype={'dist_stops':'float'})

    i_row2 = -1
    i_row = 0
    while i_row< len(trip_df):
        line_trip_1st_2nd = str(trip_df.loc[i_row,'layer'])
        pattern1 = r"^(.*)_"
        pattern2 = r"(\d+)$"
        line_trip = re.match(pattern1,line_trip_1st_2nd).group(1)
        nd2pos = re.search(pattern2,line_trip_1st_2nd).group(1)
        trip_df.loc[i_row,'seq_stpID'] = str(line_trip)+'_pos'+str(nd2pos)
        if i_row2 > -1:
            trip_df.loc[i_row,'shape_dist_traveled'] = trip_df.loc[i_row,'dist_stops'] + trip_df.loc[i_row2,'shape_dist_traveled']
        else:
            trip_df.loc[i_row,'shape_dist_traveled'] = trip_df.loc[i_row,'dist_stops']
        i_row2 += 1
        i_row += 1
    
    if_remove(trip_csv)
    trip_df.to_csv(trip_csv, index=False)

def shape_txt(trip_gpkg,trip_name,shape_csv, trip_vertex_gpkg,shape_folder, shapes_txt):
    processing.run("native:extractvertices", {'INPUT':trip_gpkg,'OUTPUT':trip_vertex_gpkg})
    
    trip_vertex_layer = QgsVectorLayer(trip_vertex_gpkg,trip_name,"ogr")

    pr = trip_vertex_layer.dataProvider()
    pr.addAttributes([QgsField("lon", QVariant.Double),
                        QgsField("lat", QVariant.Double),
                        QgsField("line_trip", QVariant.String)])
    trip_vertex_layer.updateFields()

   
    expression2 = QgsExpression('$x')
    expression3 = QgsExpression('$y')

    context = QgsExpressionContext()
    context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(trip_vertex_layer))

    with edit(trip_vertex_layer):
        for f in trip_vertex_layer.getFeatures():
            context.setFeature(f)
            f['line_trip'] = str(trip_name)
            f['lon'] = expression2.evaluate(context)
            f['lat'] = expression3.evaluate(context)
            trip_vertex_layer.updateFeature(f)

    trip_vertex_layer.commitChanges()

    lstokeep = ['fid','line_trip','lon','lat' ]

    idtokeep = [trip_vertex_layer.fields().indexOf(field_name) for field_name in lstokeep]
    idtokeep = [index for index in idtokeep if index != -1]

    QgsVectorFileWriter.writeAsVectorFormat(trip_vertex_layer,shape_csv,"utf-8",driverName = "CSV",attributes=idtokeep)

    ls_to_concat = os.listdir(shape_folder)

    shapes = pd.DataFrame()

    for csv in ls_to_concat:
        trip_csv = os.path.join(shape_folder,csv)
        trip = pd.read_csv(trip_csv,dtype={'fid':'int'})
        i_row = 0
        i_row2 = 1
        while i_row2 < len(trip):
            if trip.loc[i_row,'lon'] == trip.loc[i_row2,'lon']:
                if trip.loc[i_row,'lat'] == trip.loc[i_row2,'lat']:
                    trip = trip.drop(i_row)
            i_row+=1
            i_row2+=1
            
        trip = trip.reset_index(drop=True)
        trip = trip.reset_index() 
        trip = trip.drop('fid',axis=1)
        trip = trip.rename(columns={'index':'fid'})   
        shapes = pd.concat([shapes,trip],ignore_index=True)

    shapes = shapes.rename(columns = {'fid':'shape_pt_sequence','line_trip':'shape_id','lon':'shape_pt_lon','lat':'shape_pt_lat'})

    
    if os.path.exists(shapes_txt):
        os.remove(shapes_txt)

    shapes.to_csv(shapes_txt,index=False)

def stop_times_update(trip_name, lines_df_csv, lines_trips_csv, OSM_roads_gpkg, temp_folder_linestrip, trip_gpkg):
    lines_df = pd.read_csv(lines_df_csv,dtype='str',index_col='line_name')
    lines_trips = pd.read_csv(lines_trips_csv,dtype='str', index_col='line_trip')
    
    trips = pd.read_csv(lines_trips.loc[trip_name,'csv'])

    line_name = lines_trips.loc[trip_name,'line_name']
    stop_times_with_seq_csv = lines_df.loc[line_name,'GTFSstop_times_with_seq']
    Ttbl_with_seq = pd.read_csv(stop_times_with_seq_csv)

    trips_to_merge = trips[['seq_stpID','shape_dist_traveled']]

    trip = re.search(r"(\d+)$",trip_name).group(1)

    Ttbl_with_seq = Ttbl_with_seq[Ttbl_with_seq['trip'] == int(trip)]

    Ttbl_with_seq = Ttbl_with_seq.merge(trips_to_merge,how='left', on='seq_stpID')
    
    i_row = 0
    while i_row < len(Ttbl_with_seq):
        if Ttbl_with_seq.loc[i_row,'pos'] == 0:
            Ttbl_with_seq.loc[i_row,'shape_dist_traveled'] = 0
        i_row +=1


    # to report the OSM ways-IDs 
    city_roads_layer = QgsVectorLayer(OSM_roads_gpkg,'city_road',"ogr")
    trip_layer = QgsVectorLayer(trip_gpkg,trip_name,"ogr")
    params = {'INPUT':city_roads_layer,
                'PREDICATE':[1,3,5,6],
                'INTERSECT':trip_layer,
                'METHOD':0}
    processing.run("native:selectbylocation", params)

    selected_csv = str(temp_folder_linestrip)+'/'+str(trip_name)+'_OSMways.csv'
    QgsVectorFileWriter.writeAsVectorFormat(city_roads_layer,selected_csv,"utf-8",driverName = "CSV",onlySelected=True,attributes= [1,2])
    selected = pd.read_csv(selected_csv)
    ls_OSMways = selected.full_id.unique()

    lines_trips.loc[trip_name,'selected_ways'] = selected_csv
    lines_trips.loc[trip_name,'ls_unique_ways'] = " ".join(ls_OSMways)

    return Ttbl_with_seq

def if_display(file_path,layer_name):
    if os.path.exists(file_path):
        if not QgsProject.instance().mapLayersByName(layer_name):
            city_r_layer = QgsVectorLayer(file_path,layer_name,"ogr")
            QgsProject.instance().addMapLayer(city_r_layer)


