import googlemaps
import configparser

config = configparser.ConfigParser()
config.read('../config/config.ini')

gmaps = googlemaps.Client(key=config.get('google.maps', 'ApiKey'))


def snap_to_roads(route):
    gmaps_ready_route = map(lambda node: (node['long'], node['lat']), route)
    snapped_gmaps_route = gmaps.snap_to_roads(gmaps_ready_route, interpolate=False)     # TODO: Interpolate?
    return map(lambda node: {
        'long': node['location']['longitude'],
        'lat': node['location']['latitude']
    }, snapped_gmaps_route)                                                         # TODO: Return to original order?