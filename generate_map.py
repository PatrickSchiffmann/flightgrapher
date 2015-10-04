from skyscanner import FlightsCache
import vincent
import pandas as pd
import json

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

from pprint import pprint

APIKEY = "ah742095586843788617222720175050"

if __name__ == "__main__":
    flights_cache_service = FlightsCache(APIKEY)
    result = flights_cache_service.get_cheapest_price_by_route(
        market='UK',
        currency='GBP',
        locale='en-GB',
        originplace='UK',
        destinationplace='anywhere',
        outbounddate='2015-11',
        inbounddate='2015-12').parsed

    # Extract data from result
    currencies = result["Currencies"]
    routes = result["Routes"]
    places = result["Places"]

    # Transform / filter lists
    places = {place["PlaceId"]:place for place in places}
    routes = [route for route in routes if "Price" in route]

    df_places = pd.DataFrame(places).transpose()
    df_routes = pd.DataFrame(routes)
    df_data = pd.merge(df_routes, df_places, left_on = 'DestinationId', right_on = 'PlaceId')

    # Basic Map data
    world_topo = r'world-countries.topo.json'
    geo_data = [{'name': 'countries',
                 'url': world_topo,
                 'feature': 'world-countries'}]

    replace_fix = {"Name":
                       {"United States":"United States of America",
                        "Bahamas":"The Bahamas",
                        "Serbia":"Republic of Serbia",
                        "DR Congo":"Democratic Republic of the Congo",
                        "Congo":"Republic of the Congo",
                        "Guinea-Bissau":"Guinea Bissau",
                        "Tanzania":"United Republic of Tanzania",
                        "Republic of Macedonia": 'Macedonia'
                        }
                   }

    df_data.replace(replace_fix, inplace=True)

    with open(world_topo) as data_file:
        data = json.load(data_file)

    for country in data["objects"]["world-countries"]["geometries"]:
        if not country["properties"]["name"] in df_data["Name"].unique().tolist():
            print country["properties"]["name"], country["properties"]["name"] in df_data["Name"].unique().tolist()

    vis = vincent.Map(data=df_data, geo_data=geo_data, scale=200,
          data_bind='Price', data_key='Name',
          map_key={'countries': 'properties.name'}, brew="Oranges")

    vis.to_json('map.html',html_out=True,html_path='map_viewer.html')

