# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import numpy as np
from itertools import permutations
import folium

#data cleaning and reforming
cities = pd.read_csv('/home/scrappycoco/Documents/uscities.csv')
cities = cities.loc[cities['population']>99999]
nycBorough = cities[cities['city'].isin(['Staten Island','Brooklyn','Manhattan','Bronx','Queens'])]
cities.drop(nycBorough.index,inplace = True)
cities.drop(['source','military','incorporated','timezone','ranking','zips','id'], axis=1, inplace=True)
cities_sort = cities.sort_values(by=['population','density'], ascending=False)
city_names = cities['city']+', '+cities['state_name']
cords = cities['lat'].astype('string')+','+cities['lng'].astype('string')
cords = cities.loc[:,['lat','lng']]
cityWcords = pd.DataFrame({'id':cities['county_fips'],'city':city_names,'cords':cords.values.tolist()})
print(cities)
print(cityWcords)

#city combinations
perm = pd.DataFrame(list(permutations(cityWcords.values, 2)),columns=['start','end'])
print(perm.shape)

#distances between combinations of cities
from geopy.distance import geodesic
perm['physical_dist'] = perm.apply(lambda row: geodesic(row.start[2],row.end[2]).miles,axis=1)

#dropping duplicate combinations
perm.drop_duplicates(subset=['physical_dist'],inplace=True)

#solving average travel time between cities
perm['time'] = perm['physical_dist']/65

#reorganizing
combos = perm
split1 = pd.DataFrame(combos['start'].to_list(), columns = ['city1id', 'city1name', 'city1location'])
split2 = pd.DataFrame(combos['end'].to_list(), columns = ['city2id', 'city2name', 'city2location'])
combos1 = split1.merge(split2,left_index=True,right_index=True)
combos1['time'] = perm['time']
combos1['phys_dist'] = perm['physical_dist']
combos1 = combos1.loc[(combos1['time']<12) & (combos1['time']>6)]
combos1 = combos1.merge(cities[['population', 'density']], left_on = ['city1id'], right_on = cities['county_fips'], how = 'inner')
combos1.rename(columns = {'population':'city1pop','density':'city1density'}, inplace = True)
combos1 = combos1.merge(cities[['population', 'density']], left_on = ['city2id'], right_on = cities['county_fips'], how = 'inner')
combos1.rename(columns = {'population':'city2pop','density':'city2density'}, inplace = True)
combos1 = combos1.drop_duplicates(subset = ['city1id', 'city2id']).reset_index(drop = True)

#model
population_thresh = combos1['city1pop'].quantile(0.4)
density_thresh = combos1['city1density'].quantile(0.8)
print(population_thresh)
print(density_thresh)

combos_final = combos1.loc[(combos1['city1pop']>=population_thresh) & (combos1['city1density']>=density_thresh)]
combos_final = combos_final.drop_duplicates(subset = ['city1id', 'city2id']).reset_index(drop = True)

#map generation

bus_map = folium.Map(location=[48,-102],zoom_start=4)


# import googlemaps
# from datetime import datetime
# gmaps = googlemaps.Client(key='AIzaSyDqiAIhlaR8X48AN5vNEhv-f35KeVPZRRI')
# dt = datetime.strptime("06/11/22 20:30", "%d/%m/%y %H:%M")
# permSample = perm.sample(10)
# permSample['googleapi_raw'] = permSample.apply(lambda row: gmaps.distance_matrix(tuple(row.start[1]), tuple(row.end[1]), mode='driving', departure_time=dt),axis=1)
# permSample['time'] = permSample.apply(lambda row: row.googleapi_raw['rows'][0]['elements'][0]['duration']['value']/3600, axis=1)

# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
# reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))

# Request directions via public transit
# now = datetime.now()
# directions_result = gmaps.distance_matrix((40.6943, -73.9249),
#                                      (42.7677, -86.0985),
#                                      mode="driving",
#                                      departure_time=now)


# import requests, json
  
# api_key ='AIzaSyAEAQs6rd5MMB9p371w5KiJYdNBK9HJqGQ'
  
# source = cityWcords.loc[cityWcords['city']=='New York, New York']['cords']
  
# dest = cityWcords.loc[cityWcords['city']=='Los Angeles, California']['cords']
  
# url ='https://maps.googleapis.com/maps/api/distancematrix/json?'
  
# r = requests.get(url + 'origins = ' + source +
#                    '&destinations = ' + dest +
#                    '&key = ' + api_key)

# x = r.json()
# print(x)

