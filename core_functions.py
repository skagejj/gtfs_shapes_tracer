from qgis.core import QgsVectorLayer, QgsField, edit, QgsExpression, QgsExpressionContext, QgsExpressionContextUtils, QgsVectorFileWriter
import pandas as pd
from qgis import processing
from qgis.PyQt.QtCore import QVariant
import re
import os


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
        shapes = pd.concat([shapes,trip],ignore_index=True)

    shapes = shapes.rename(columns = {'fid':'shape_pt_sequence','line_trip':'shape_id','lon':'shape_pt_lon','lat':'shape_pt_lat'})

    
    if os.path.exists(shapes_txt):
        os.remove(shapes_txt)

    shapes.to_csv(shapes_txt,index=False)
