import base64
import hashlib
import src.sampleData
import src.maps


def dictify_hash_tuple(tup):
    new_dict = dict(tup)
    new_dict.update({'hash': hex(hash(tup))})
    return new_dict


def get_hash(node, node_library):
    matching_nodes = list(filter(lambda possible_node:          # Filter possible matching nodes to location matches...
                                 possible_node['lat'] == node['lat'] and possible_node['long'] == node['long'],
                                 node_library))                 # ...from possible nodes
    if len(matching_nodes) > 1:
        print("Multiple possible node matches found! {}".format(matching_nodes))

    return matching_nodes[0]['hash']


def process_routes(routes_obj):
    # First straighten the routes using Google Maps API
    straightened_routes_obj = {'data': list(map(lambda route_from_obj: {
        'name': route_from_obj['name'],
        'route': src.maps.snap_to_roads(route_from_obj['route']),
    }, routes_obj['data']))}

    print(straightened_routes_obj)

    # Second find the unique nodes as bus stops
    routes_stops = list(map(lambda sub_route: (sub_route['route']), straightened_routes_obj['data']))   # Extract routes
    stops = [y for x in routes_stops for y in x]                                        # Flatten stops
    uniq_stops = [dictify_hash_tuple(t) for t in {tuple(d.items()) for d in stops}]     # Deduplicate
    print(uniq_stops)

    # Then replace the locations of the routes with hashes
    hashed_routes = []

    for route in straightened_routes_obj['data']:
        hashed_routes.append({
            'name': route['name'],
            'route': list(map(lambda node: {
                'id': get_hash(node, uniq_stops),
                'isStop': True
            }, route['route']))
        })

    return {
        'routes': hashed_routes,
        'nodes': uniq_stops,
        # 'lat': None,
        # 'lng': None,
    }


# process_routes(input_json)
