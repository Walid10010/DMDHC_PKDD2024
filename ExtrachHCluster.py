import matplotlib.pyplot as plt
import numpy as np
import pydotplus as pydot
from sklearn.metrics import normalized_mutual_info_score, adjusted_mutual_info_score
from sklearn.neighbors import NearestNeighbors, KDTree

from D2Punkt import D2Punkt
from FindeCluster import start_sigma
from readFile import read_file
import sys
limit = 999999
sys.setrecursionlimit(limit)
# this time, in graph_type we specify we want a DIrected GRAPH
graph = pydot.Dot(graph_type='digraph', strict=True)
graph.set_size('"50,5!"')
graph.set_bgcolor('white')
ind_to_name = {}
name_to_label = {}
name_to_d2Punkt = {}
label_counter = 0
daten_matrix = None
cluster_dppoints = []
global_outlier_list = set([])
v = "ClusterID {}"
seen_points_name = set([])


def reset():
    global graph, ind_to_name, name_to_label, name_to_d2Punkt, label_counter, daten_matrix, cluster_dppoints,\
        seen_points_name, global_outlier_list,v
    graph = pydot.Dot(graph_type='digraph')
    graph.set_size('"50,5!"')
    graph.set_bgcolor('white')
    ind_to_name = {}
    name_to_label = {}
    name_to_d2Punkt = {}
    label_counter = 0
    daten_matrix = None
    cluster_dppoints = []
    global_outlier_list = set([])
    v = "Cluster {}"
    seen_points_name = set([])


def start_clustering(min_cluster_size, rho, beta, leaf_nr):
    global label_counter, global_outlier_list
    X = index_to_X()
    # plt.scatter(X[:,0], X[:,1])
    # plt.show()
    epsilon = epsilon_abschaetzen(min_cluster_size, X)
    if (epsilon == None):
        for key, item in name_to_d2Punkt.items():
            name = item.name
            global_outlier_list.update(name)
            name_to_label[name] = label_counter
            # print('lennnnnnnnnnnnnnn {}'.format(len(name_to_d2Punkt.keys())))
        return zeichne(leaf_nr)

    kd_abfrage(X, epsilon)
    sigma = sigma_suche()

    if (sigma == None):
        for key, item in name_to_d2Punkt.items():
            name = item.name
            global_outlier_list.update(name)
            name_to_label[name] = label_counter

        return zeichne(leaf_nr)
    beta = min(sigma.std, 0.2)
    sigma_final_result = start_sigma(sigma, ind_to_name, name_to_d2Punkt, rho, beta)
    sigma_final_result.label = label_counter
    label_name = "Cluster: {} \n Avg_k_distance: {:0.2f} \n Size: {}".format(
        label_counter, sigma_final_result.avg_k_distanz, len(sigma_final_result.nachbar)
    )
    label_name = "ClusterID: {}".format(
        label_counter, sigma_final_result.avg_k_distanz, len(sigma_final_result.nachbar)
    )
    node_a = pydot.Node(v.format(sigma_final_result.label, sigma_final_result.avg_k_distanz), shape="box",
                        style="rounded", fontname='electrolize'
                        , height='1', label=label_name)
    node_a.set_name(v.format(sigma_final_result.label, sigma_final_result.avg_k_distanz))
    graph.add_node(node_a)
    cluster_dppoints.append((sigma_final_result))
    # for for_index, ind in enumerate(sigma_final_result.nachbar):
    #     if for_index == 0:
    #         low_density = name_to_d2Punkt[ind_to_name[ind]]
    #     else:
    #         current_point = name_to_d2Punkt[ind_to_name[ind]]
    #         low_density = low_density if current_point.avg_k_distanz > low_density.avg_k_distanz else current_point
    # sigma_final_result.small_copy(low_density)
    for ind in sigma_final_result.nachbar:
        tmp_name = ind_to_name[ind]
        sigma_final_result.nachbar_name.add(tmp_name)
        name_to_label[tmp_name] = label_counter
        if tmp_name == sigma_final_result.name:
            pass

        else:
            del name_to_d2Punkt[tmp_name]

    label_counter += 1
    # sigma_final_result.nachbar_name.add(sigma.name)
    jo = sigma_final_result.name in sigma_final_result.nachbar_name
    size_item = len(name_to_d2Punkt.items())
    seen_points_name.update(set([sigma_final_result.name]))
    if (size_item < min_cluster_size):
        for key, item in name_to_d2Punkt.items():
            name = item.name
            name_to_label[name] = label_counter
            global_outlier_list.update(set([name]))

        return zeichne(leaf_nr)
    else:
        return start_clustering(min_cluster_size, rho, beta, leaf_nr)


def str_to_name(datenpunkt):
    name = ""
    for item in datenpunkt:
        name += str(item) + "x"
    return name


def init(X):
    global daten_matrix
    daten_matrix = X
    count = 0
    for item in X:
        tmp_name = str_to_name(item)
        if tmp_name not in name_to_d2Punkt:
            count += 1
            d2Punkt = D2Punkt(item, tmp_name)
            name_to_d2Punkt[tmp_name] = d2Punkt



def index_to_X():
    list = []
    for key, item in name_to_d2Punkt.items():
        list.append(item.koordinaten)
    return np.array(list)


def epsilon_abschaetzen(min_cluster_size, X):
    # Hinweis: fall einbinden wenn len X < min_cluster_size
    if min_cluster_size < X.shape[0]:
        factor = 1
        metricNN = NearestNeighbors(n_neighbors=min_cluster_size * factor + 1,
                                    leaf_size=min_cluster_size * factor + 1).fit(X)
        distances, indices = metricNN.kneighbors(X)

        epsilon = distances[0][min_cluster_size]
        for i, distanz in enumerate(distances):
            tmp_epsilon = distanz[min_cluster_size]
            tmp_distanz = 0
            for dis in distanz:
                tmp_distanz += dis
            name = str_to_name(X[i])
            name_to_d2Punkt[name].avg_k_distanz = tmp_distanz
            # name_to_d2Punkt[name].std = np.std(distanz)
            #name_to_d2Punkt[name].std =  distanz[min_cluster_size]
            if epsilon > tmp_epsilon:
                epsilon = tmp_epsilon
        return epsilon
    else:
        return None


def kd_abfrage(X, epsilon):
    kd_tree = KDTree(X)
    ind, dist = kd_tree.query_radius(X, r=epsilon, return_distance=True)
    for i, item in enumerate(X):
        tmp_name = str_to_name(item)
        name_to_d2Punkt[tmp_name].nachbar = ind[i]
        name_to_d2Punkt[tmp_name].std  = np.std(dist[i])
        ind_to_name[i] = tmp_name


def sigma_suche():
    # Hinweis: def von sigma veraendert
    sigma = None
    for key, d2Punkt in name_to_d2Punkt.items():
        if d2Punkt.name in seen_points_name:
            continue
        if sigma == None:
            sigma = d2Punkt
        tmp_avg = d2Punkt.avg_k_distanz
        if tmp_avg < sigma.avg_k_distanz:
            sigma = d2Punkt
    if sigma != None:
       pass
       #plt.scatter(sigma.koordinaten[0], sigma.koordinaten[1], color='k', s=1000)
    return sigma


def zeichne(leaf_nr):
    y_label = []
    for daten_punkt in daten_matrix:
        name = str_to_name(daten_punkt)
        if name in name_to_label:
            y_label.append(name_to_label[name])
        else:

            y_label.append(0)
    colors = np.array([x for x in 'grcmygmgbgrcmybgrcmybgrcmy'])
    np.random.shuffle(colors)
    colors = np.hstack([colors] * 20)


   # plt.figure(1)
    marker = np.array([',', '.'] * 100)
    np_label = np.array(y_label).reshape(-1)
    for sigma_points in cluster_dppoints:
         pass
        #plt.text(sigma_points.koordinaten[0], sigma_points.koordinaten[1], sigma_points.label, fontsize=12, c='green')
    graph_dic = {}
    node_dic = {}
    name_check = set([])
    alone_node_save = set([])

    # start
    for index, sigma_points in enumerate(cluster_dppoints):
        name_check.update(sigma_points.nachbar_name)
        alone_node_save.update(set([sigma_points.label]))
        node_dic[sigma_points.label] = sigma_points
        for sigma_neighbor in cluster_dppoints[index + 1:]:
            if sigma_points.name in sigma_neighbor.nachbar_name:
                alone_node_save = alone_node_save - set([sigma_points.label])
                node_dic[sigma_neighbor.label] = sigma_neighbor
                graph_dic[sigma_points.label] = sigma_neighbor.label

    left_side = set(graph_dic.keys())
    right_side = set(graph_dic.values())
    leaf_size = len(left_side - right_side) + len(alone_node_save)
    under_root = right_side - left_side
    under_root.update(alone_node_save)
    global global_outlier_list, label_counter
    global_outlier_list = global_outlier_list - name_check
    graph_dic = {}
    node_dic = {}
    name_check = set([])
    alone_node = set([])
    merge_dic = {}
    edge_dup = set([]) # um doppelte Kanten zwischen merge zu ziel knoten zu vermeiden
    max_leaf_size = 0
    if len(global_outlier_list) > 0:
        label_counter = label_counter + 1
    leaf_size = leaf_size - max_leaf_size
    max_leaf_size = label_counter - leaf_nr
    max_id = label_counter
    if max_leaf_size < 0:
        return 0, 0, 0
    merge_alone_node = set([])
    for index, sigma_points in enumerate(cluster_dppoints):
        name_check.update(sigma_points.nachbar_name)
        alone_node.update(set([sigma_points.label]))
        node_dic[sigma_points.label] = sigma_points
        if sigma_points.label in alone_node_save and max_leaf_size > 0:
            max_leaf_size = max_leaf_size - 1
            alone_node = alone_node - set([sigma_points.label])
            merge_alone_node.update(sigma_points.nachbar_name)
            graph.del_node(v.format(sigma_points.label))
            del node_dic[sigma_points.label]
            continue
        for sigma_neighbor in cluster_dppoints[index + 1:]:
            if sigma_points.name in sigma_neighbor.nachbar_name and max_leaf_size <= 0:
                # name_check.update(sigma_points.nachbar_name)
                # name_check.update(sigma_neighbor.nachbar_name)
                alone_node = alone_node - set([sigma_points.label])
                sigma_neighbor.nachbar_name = sigma_neighbor.nachbar_name - set([sigma_points.name])
                # sigma_points.nachbar_name.update(set([sigma_points.name]))
                # sigma_neighbor.nachbar_name = sigma_neighbor.nachbar_name - set([sigma_points.name])
                node_dic[sigma_neighbor.label] = sigma_neighbor
                graph_dic[sigma_points.label] = sigma_neighbor.label
                des = graph.get_node(v.format(sigma_points.label))[0]
                src = graph.get_node(v.format(sigma_neighbor.label))[0]
                if sigma_neighbor.label in merge_dic.keys():
                    node_a = merge_dic[sigma_neighbor.label]
                else:
                    # node_a = pydot.Node('Merge {}'.format(sigma_neighbor.label), shape="box",
                    #                     style="rounded", fontname='electrolize'
                    #                     , height='2')
                    max_id += 1
                    node_a = pydot.Node('ClusterID {}'.format(max_id), shape="box",
                                        style="rounded", fontname='electrolize'
                                        , height='2')
                    merge_dic[sigma_neighbor.label] = node_a
                    #graph.add_node(node_a)

                c = 'black'
                src.set_fillcolor('red')
                src.set_fontcolor(c)
                des.set_color(c)
                des.set_fontcolor(c)
                if sigma_points.label in merge_dic:
                    des = merge_dic[sigma_points.label]
                e = pydot.Edge(node_a, des)
                e.set_color(c)
                graph.add_edge(e)
                e = pydot.Edge(node_a, src)
                e.set_color(c)
                edge_name = '{}.{}'.format(node_a.get_name(), src.get_name())
                if not (edge_name in edge_dup):
                    graph.add_edge(e)
                    edge_dup.add(edge_name)

            if sigma_points.name in sigma_neighbor.nachbar_name and max_leaf_size > 0:
                max_leaf_size = max_leaf_size - 1
                sigma_neighbor.nachbar_name.update(sigma_points.nachbar_name)
                graph.del_node(v.format(sigma_points.label))
                alone_node = alone_node - set([sigma_points.label])
                del node_dic[sigma_points.label]

    global_outlier_list = global_outlier_list - name_check

    from tree import create_tree, cal_dendogram_purity
    root_node = pydot.Node('Root', shape="box",
                           style="rounded", fontname='electrolize'
                           , height='2')
    c = 'black'
    for item in under_root:
        try:
            node_A = graph.get_node(v.format(item))[0]
            if item in merge_dic.keys():
                node_A = merge_dic[item]
            e = pydot.Edge(root_node, node_A)
            e.set_color(c)
            graph.add_edge(e)
        except:
            pass
    if len(global_outlier_list) > 0:
        if max_leaf_size <= 0:
            node_a = pydot.Node(v.format('rest'), shape="box",
                                style="rounded", fontname='electrolize'
                                , height='2', label='')
            e = pydot.Edge(root_node, node_a)
            e.set_color(c)
            graph.add_edge(e)
        else:
            merge_alone_node.update(global_outlier_list)
            global_outlier_list = set([])

    root = create_tree(graph_dic, node_dic, global_outlier_list, alone_node, label_counter, merge_alone_node)
    return root, np.array(y_label).reshape(-1)








def DMDHC(X, min_cluster_size, rho, beta, leaf_nr):
    reset()
    init(X)
    return start_clustering(min_cluster_size, rho, beta, leaf_nr)
