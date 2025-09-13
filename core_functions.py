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
import numpy as np

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

def shape_txt(trip_gpkg,trip_name,shape_csv, trip_vertex_gpkg):
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

    if_remove(shape_csv)
    QgsVectorFileWriter.writeAsVectorFormat(trip_vertex_layer,shape_csv,"utf-8",driverName = "CSV",attributes=idtokeep)

    trip = pd.read_csv(shape_csv,dtype={'fid':'int'})
    i_row = 0
    i_row2 = 1
    i_row3= 2
    i_row4 = 3
    i_row5 = 4
    i_row6 = 5
    i_row7 = 6
    ls_idx_to_del = []
    dlon2 = trip.loc[i_row2,'lon'] - trip.loc[i_row3,'lon']
    dlon = trip.loc[i_row,'lon'] - trip.loc[i_row3,'lon']
    dlat2 = trip.loc[i_row2,'lat'] - trip.loc[i_row3,'lat']
    dlat = trip.loc[i_row,'lat'] - trip.loc[i_row3,'lat']
    if dlon2*dlon2+dlat2*dlat2 >  dlon*dlon+dlat*dlat :
                    ls_idx_to_del.append(i_row)
    while i_row7 < len(trip):
        if trip.loc[i_row2,'lon'] == trip.loc[i_row5,'lon']:
            if trip.loc[i_row2,'lat'] == trip.loc[i_row5,'lat']:
                dlon2 = trip.loc[i_row2,'lon'] - trip.loc[i_row,'lon']
                dlon3 = trip.loc[i_row3,'lon'] - trip.loc[i_row,'lon']
                dlat2 = trip.loc[i_row2,'lat'] - trip.loc[i_row,'lat']
                dlat3 = trip.loc[i_row3,'lat'] - trip.loc[i_row,'lat']
                if dlon2*dlon2+dlat2*dlat2 >  dlon3*dlon3+dlat3*dlat3 :
                    ls_idx_to_del.append(i_row2)
                else:
                    ls_idx_to_del.append(i_row5)
        if trip.loc[i_row3,'lon'] == trip.loc[i_row5,'lon']:
            if trip.loc[i_row3,'lat'] == trip.loc[i_row5,'lat']:
                dlon3 = trip.loc[i_row3,'lon'] - trip.loc[i_row2,'lon']
                dlon4 = trip.loc[i_row4,'lon'] - trip.loc[i_row2,'lon']
                dlat3 = trip.loc[i_row3,'lat'] - trip.loc[i_row2,'lat']
                dlat4 = trip.loc[i_row4,'lat'] - trip.loc[i_row2,'lat']
                if dlon3*dlon3+dlat3*dlat3 > dlon4*dlon4+dlat4*dlat4 :
                    ls_idx_to_del.append(i_row3)
                else:
                    ls_idx_to_del.append(i_row5)
        if trip.loc[i_row4,'lon'] == trip.loc[i_row5,'lon']:
            if trip.loc[i_row4,'lat'] == trip.loc[i_row5,'lat']:
                ls_idx_to_del.append(i_row5)
        if trip.loc[i_row7,'lon'] == trip.loc[i_row3,'lon']:
            if trip.loc[i_row7,'lat'] == trip.loc[i_row3,'lat']:
                dlon4 = trip.loc[i_row4,'lon'] - trip.loc[i_row,'lon']
                dlon3 = trip.loc[i_row3,'lon'] - trip.loc[i_row,'lon']
                dlat4 = trip.loc[i_row4,'lat'] - trip.loc[i_row,'lat']
                dlat3 = trip.loc[i_row3,'lat'] - trip.loc[i_row,'lat']
                if dlon3*dlon3+dlat3*dlat3 > dlon4*dlon4+dlat4*dlat4 :
                    ls_idx_to_del.append(i_row3)
                else:
                    ls_idx_to_del.append(i_row7)
        if trip.loc[i_row6,'lon'] == trip.loc[i_row2,'lon']:
            if trip.loc[i_row6,'lat'] == trip.loc[i_row2,'lat']:
                dlon4 = trip.loc[i_row4,'lon'] - trip.loc[i_row,'lon']
                dlon2 = trip.loc[i_row2,'lon'] - trip.loc[i_row,'lon']
                dlat4 = trip.loc[i_row4,'lat'] - trip.loc[i_row,'lat']
                dlat2 = trip.loc[i_row2,'lat'] - trip.loc[i_row,'lat']
                if dlon2*dlon2+dlat2*dlat2 > dlon4*dlon4+dlat4*dlat4 :
                    ls_idx_to_del.append(i_row2)
                else:
                    ls_idx_to_del.append(i_row6)
        i_row+=1
        i_row2+=1
        i_row3+=1
        i_row4+=1
        i_row5+=1
        i_row6+=1
        i_row7+=1
    
    dlon6 = trip.loc[i_row6,'lon'] - trip.loc[i_row4,'lon']
    dlon5 = trip.loc[i_row5,'lon'] - trip.loc[i_row4,'lon']
    dlat6 = trip.loc[i_row6,'lat'] - trip.loc[i_row4,'lat']
    dlat5 = trip.loc[i_row5,'lat'] - trip.loc[i_row4,'lat']
    if dlon5*dlon5+dlat5*dlat5 >  dlon6*dlon6+dlat6*dlat6 :
                    ls_idx_to_del.append(i_row5)

    trip = trip.drop(ls_idx_to_del)

    trip = trip.reset_index(drop=True)
    trip = trip.reset_index() 
    trip = trip.drop('fid',axis=1)
    trip = trip.rename(columns={'index':'fid'})   
    
    return trip

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
        if np.isnan(Ttbl_with_seq.loc[i_row,'shape_dist_traveled']):
            trip_id = Ttbl_with_seq.loc[i_row,'trip_id']
            i_row_prec = i_row - 1
            for idx in trips.index:
                if  round(trips.loc[idx,'shape_dist_traveled'],3) == round(Ttbl_with_seq.loc[i_row_prec,'shape_dist_traveled'],3):
                    idx2 = idx+1
                    try:
                        Ttbl_with_seq.loc[i_row,'shape_dist_traveled'] = round(trips.loc[idx2,'shape_dist_traveled'],3)
                    except Exception:
                        print (str(trip_id))
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


