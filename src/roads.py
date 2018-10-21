import numpy as np
import pandas as pd
import json
import scipy as sc
from scipy.cluster.hierarchy import fclusterdata
from scipy.cluster.hierarchy import linkage, cut_tree, dendrogram
from sklearn.cluster import KMeans



def read_json(file):
    with open(file) as f:
        return json.load(f)

def custom_dist(p1, p2):
    diff = p1[:2] - p2[:2]
    return np.power(np.vdot(diff, diff), 0.5) * np.abs(np.log(p1[2]) - np.log(p2[2]))
    # think about metric

def custom_argmax(matrix):
    max_coor, max_val = [0, 0], -1
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            if matrix[i, j] > max_val:
                max_val = matrix[i, j]
                max_coor = [i, j]
    return max_coor

def find_nearest(matrix, coor, near=5, threshold=0.1):
    centered = matrix.copy()
    centered[coor] = 0
    nearest = centered[max(0, coor[0]-near):min(matrix.shape[0], coor[0]+near),
              max(0, coor[1]-near):min(matrix.shape[1], coor[1]+near)]
    possible_step = custom_argmax(nearest)
    possible_step[0] += max(0, coor[0]-near)
    possible_step[1] += max(0, coor[1]-near)
    if matrix[tuple(coor)]*threshold > matrix[tuple(possible_step)] or matrix[tuple(possible_step)] < 1e-2 or tuple(coor) == tuple(possible_step):
        return None
    else:
        return possible_step

# slowwwww
def find_in_df(df, lat, lon):
    return df.loc[np.logical_and(df['long_ind'] == lon, df['lat_ind'] == lat)]

def get_edges(num_ticks=85, min_len_route=5, max_h_clusters=100, max_kmean_clusters=50, max_len_from_kmean_cluster=30):
    busstops = read_json('./busstops_good.json')
    busstops = pd.read_json(json.dumps(busstops['data'][1:]))
    busstops = busstops.apply(lambda x: x.apply(lambda y: y[1:-1]))

    lats, longs = np.array(busstops['lat'], dtype=float), np.array(busstops['lng'], dtype=float)

    min_lat, min_long = np.min(lats), np.min(longs)
    mask = lats == min_lat
    lats, longs = lats[~mask], longs[~mask]

    lats = lats - np.min(lats)
    longs = longs - np.min(longs)
    global_lat_min, global_long_min = (2.084949, 41.321643)

    lat_max = np.max(lats)
    long_max = np.max(longs)
    new_grid = np.zeros((num_ticks, num_ticks))
    new_grid_ones = np.zeros((num_ticks, num_ticks))
    x_ticks = np.arange(0, lat_max, lat_max/num_ticks)
    y_ticks = np.arange(0, long_max, long_max/num_ticks)

    for lat, long in zip(lats, longs):
        for lat_right_ind in range(1, len(x_ticks)):
            for long_right_ind in range(1, len(y_ticks)):
                if x_ticks[lat_right_ind-1] <= lat < x_ticks[lat_right_ind] and y_ticks[long_right_ind-1] <= long < y_ticks[long_right_ind]:
                    new_grid_ones[lat_right_ind-1, long_right_ind-1] = 1

    bus_grid = new_grid_ones.copy()

    dencs = read_json('./partialDensities.json')
    dencs2 = read_json('./moreDensities.json')
    denc = pd.read_json(json.dumps(dencs['data'][1:]))
    denc2 = pd.read_json(json.dumps(dencs2['data'][1:]))
    denc = pd.concat((denc, denc2))
    denc[['barri', 'districte', 'lat', 'lng']] = denc[['barri', 'districte', 'lat', 'lng']].apply(lambda x: x.apply(lambda y: y[1:-1]))
    denc.dropna(inplace=True)

    lats, longs = np.array(denc['lat'], dtype=float), np.array(denc['lng'], dtype=float)
    dencities = np.array(denc['density'], dtype=float)
    dencities = np.array([int(i)+1 for i in dencities])
    min_lat, min_long = np.min(lats), np.min(longs)
    mask = lats == min_lat
    lats, longs = lats[~mask], longs[~mask]

    lats = lats - global_lat_min
    longs = longs - global_long_min

    new_grid = np.zeros((num_ticks, num_ticks))
    new_grid_nums = np.zeros((num_ticks, num_ticks))-1

    for lat, long, dencit in zip(lats, longs, dencities):
        for lat_right_ind in range(1, len(x_ticks)):
            for long_right_ind in range(1, len(y_ticks)):
                if x_ticks[lat_right_ind-1] <= lat < x_ticks[lat_right_ind] and y_ticks[long_right_ind-1] <= long < y_ticks[long_right_ind]:
                    new_grid[lat_right_ind-1, long_right_ind-1] += dencit
                    if new_grid_nums[lat_right_ind-1, long_right_ind-1] == -1:
                        new_grid_nums[lat_right_ind-1, long_right_ind-1] = 1
                    else:
                        new_grid_nums[lat_right_ind-1, long_right_ind-1] += 1
    new_grid = new_grid/new_grid_nums


    global_bus_grid = np.multiply(bus_grid, new_grid)
    new_lats_, new_longs_ = np.nonzero(global_bus_grid)
    new_lats, new_longs, new_denc = [], [], []
    for lat, long in zip(new_lats_, new_longs_):
        new_lats.append(x_ticks[lat])
        new_longs.append(y_ticks[long])
        new_denc.append(global_bus_grid[lat, long])
    new_lats, new_longs, new_denc = np.array(new_lats), np.array(new_longs), np.array(new_denc)

    stacked = pd.DataFrame(np.column_stack([new_lats, new_longs, new_denc, new_lats_, new_longs_]),
                           columns=['lat', 'long', 'denc', 'lat_ind', 'long_ind'])

    Z = linkage(stacked.values[:, :3], method='average', metric=custom_dist)
    actual_clusters = cut_tree(Z, max_h_clusters).flatten()
    stacked['hierar_cluster'] = actual_clusters

    cls = KMeans(n_clusters=max_kmean_clusters)
    pred = cls.fit_transform(stacked.values[:, :2])
    centers = cls.cluster_centers_

    cluster_grid = np.zeros((num_ticks, num_ticks))
    for lat, long in zip(centers[:, 0], centers[:, 1]):
        for lat_right_ind in range(1, len(x_ticks)):
            for long_right_ind in range(1, len(y_ticks)):
                if x_ticks[lat_right_ind-1] <= lat < x_ticks[lat_right_ind] and y_ticks[long_right_ind-1] <= long < y_ticks[long_right_ind]:
                    cluster_grid[lat_right_ind-1, long_right_ind-1] = 1
    new_lats_c, new_longs_c = np.nonzero(cluster_grid)
    new_latsc, new_longsc = [], []
    for lat, long in zip(new_lats_c, new_longs_c):
        new_latsc.append(x_ticks[lat])
        new_longsc.append(y_ticks[long])
    new_latsc, new_longsc = np.array(new_latsc), np.array(new_longsc)

    new_bus_martix = global_bus_grid.copy()
    chains = []
    for s_lat, s_long in zip(*np.nonzero(cluster_grid)):
        previous_ind = (s_lat, s_long)
        chain = []
        for _ in range(max_len_from_kmean_cluster):
            next_point = find_nearest(new_bus_martix, previous_ind, near=15, threshold=0.3)
            new_bus_martix[tuple(previous_ind)] /= 2
            if not next_point:
                chains.append(chain)
                break
            chain.append(next_point)
            previous_ind = next_point
        chains.append(chain)
    chains = [i for i in chains if len(i) > min_len_route]
    chains_coor = [{'name': 'route {}'.format(line_ind),
                    'route': [
                        {'lat': find_in_df(stacked, *pair)['lat'].iloc[0]+global_lat_min,
                         'long': find_in_df(stacked, *pair)['long'].iloc[0]+global_long_min}
                        for pair in line]}
                   for line_ind, line in enumerate(chains)]

    cluster_f = stacked.copy()
    clusters = []
    for hiec_cl in np.unique(stacked['hierar_cluster']):
        temp = cluster_f[cluster_f['hierar_cluster']==hiec_cl]
        if temp.shape[0] < min_len_route:
            continue
        clus = []
        for lat, long in zip(temp['lat'], temp['long']):
            clus.append({'lat': lat+global_lat_min, 'long':long+global_long_min})
        clusters.append({'name': 'hclus {}'.format(hiec_cl), 'route': clus})

    full_subm = chains_coor.copy()
    full_subm.extend(clusters)

    return {'data': full_subm}
    # with open('cluster_result.json', 'w') as f:
    #     json.dump({'data': full_subm}, f)


# get_edges(num_ticks=200, min_len_route=5, max_h_clusters=100, max_kmean_clusters=50, max_len_from_kmean_cluster=40)