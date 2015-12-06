import geojson, sys
from shapely.geometry import shape
import numpy as np
import pandas as pd

"""
DESCRIPTION: two functions:
    - zips_in_DMA: function that identifies the USPS zip codes that are inside a specified Nielsen DMA. returns zip codes as a list
    - zipDMA_togeojson: function that creates a new geojson of the zip code areas that fall inside the specified DMA

REQUIREMENTS: in datasets/, two geojson files and one CSV:
    - a geojson file containing each Nieslen DMA drawn as polygons
    - a geojson file containing each zip code drawn as polygons
    - a csv containing columns "dma_id" and "dma_name" with Nielsen DMA metadata

USAGE: run the script from the command line, specifying the DMA of interest as the first argument, or use/modify the functions independently
"""

#load geojson files as geojson objects
zips = geojson.load(open('datasets/zipcodes.geojson'))
nielsen = geojson.load(open('datasets/nielsendmas.geojson'))

#load Nielsen DMA metadata as Pandas df
dmametadata = pd.read_csv('datasets/nielsenDMAchart.csv', dtype = {'dma_id': 'str'})
dmametadata = dmametadata.set_index('dma_id')

def zips_in_DMA(one_dma_id, to_txt = False):

    #for both zip codes and DMAs, extract properties and geometry from each geojson feature, add each one as a dictionary entry with the DMA ID or zip # as the key and a shapely object as the value
    zips_ = {}
    for i in zips.features:
        zips_[str(i['properties']['ZCTA5CE10'])] = shape(geojson.MultiPolygon(i['geometry']['coordinates']))

    dmas_errors = []
    dmas_ = {}
    for i in nielsen.features:
        try:
            dmas_[str(i['properties']['id'])] = shape(geojson.Polygon(i['geometry']['coordinates']))
        except:
            try:
                dmas_[str(i['properties']['id'])] = shape(geojson.Polygon(i['geometry']['coordinates'][0]))
            except:
                print "error"

    dmaziplist = []
    for i in zips_.iteritems():
        if dmas_[one_dma_id].intersects(i[1]):
            dmaziplist.append(i[0])
        else:
            pass

    dma_filename = dmametadata.ix[one_dma_id]['dma_name'].replace(',', '').replace(' ', '') + one_dma_id
    if to_txt:
        with open(dma_filename + '.txt', 'wb') as zipfile:
            for i in dmaziplist:
                zipfile.write(i)
                zipfile.write('\n')

    return dmaziplist

def zipDMA_togeojson(zipcodes, one_dma_id, to_geojson = False):

    zipfeatures = [j for j in zips.features if j['properties']['ZCTA5CE10'] in zipcodes]
    zipfc = geojson.FeatureCollection(zipfeatures)

    dma_filename = dmametadata.ix[one_dma_id]['dma_name'].replace(',', '').replace(' ', '') + one_dma_id
    if to_geojson:
        geojson.dump(zipfc, open(dma_filename + '.geojson', 'wb'))
    return zipfc

#running the script will run both functions saving a txt and geojson file
zipDMA_togeojson(zips_in_DMA(sys.argv[1], to_txt = True), sys.argv[1], to_geojson = True)
