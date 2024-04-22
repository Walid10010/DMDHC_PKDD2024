class Leaf:
    def __init__(self, data, name):
        self.data = data
        self.name = name


class Node:
    def __init__(self, data, name, childern=None):
        self.children = childern
        self.name = name
        self.data = data
        self.orgi_data = data.copy()


# Node -> children
def get_data(node):
    collect_data = set([])
    if type(node) == Node:
        for child in node.children:
            collect_data.update(get_data(child))
            child.data.update(get_data(child))
            collect_data.update(child.data)
        return collect_data
    else:
        return node.data


def lca(value, node):
    if type(node) == Leaf:
        if value.issubset(node.data):
            return node
    if value.issubset(node.data):
        for child in node.children:
            if value.issubset(child.data):
                return lca(value, child)
    return node


def create_tree(graph_dic, node_dic, outlier_set, alone_node, label_counter):
    root = Node(set([]), 'root')
    left_side = set(graph_dic.keys())
    right_side = set(graph_dic.values())
    right_side.update(alone_node)
    diff = right_side.difference(left_side)
    leaf_diff = left_side.difference(right_side)
    node_name_dic = {}
    node_dic['root'] = root
    li = []

    node = Node(outlier_set, label_counter, [])
    li.append(node)
    for item in diff:
        #        print(item.label)
        node = Node(node_dic[item].nachbar_name, item, [])
        node_name_dic[item] = node
        print('Name Node {}'.format(item))
        li.append(node)
    root.children = li
    while len(graph_dic.keys()) > 0:
        from copy import deepcopy
        print(graph_dic.keys())
        li = []
        local_dic = deepcopy(graph_dic)
        for key, value in local_dic.items():
            if value in diff:
                node = None
                if key in leaf_diff:
                    node = Leaf(node_dic[key].nachbar_name, key)
                else:
                    node = Node(node_dic[key].nachbar_name, key, [])
                node_name_dic[key] = node
                node_name_dic[value].children.append(node)
                print('Links {} -> Rechts {}'.format(key, value))
                del graph_dic[key]
                li.append(key)
        diff.update(set(li))
    root.data = get_data(root)
    return root
    print(len(root.data))


def str_to_name(datenpunkt):
    name = ""
    name +=str(datenpunkt) + "x"
    # for index, item in enumerate(datenpunkt):
    #     n = item
    #     name += str(item) + "x"
    # j = name
    return name

#old!
# def purity(c1, c2):
#     if type(c2) != set:
#         c2_new = set([])
#         for item in c2:
#             c2_new.update(set([(item)]))
#         c2 = c2_new
#     return len(c1.intersection(c2)) / len(c1)
#

# def to_set(c2):
#     return set(c2)
#
# def purity(c1, c2):
#     if type(c2) != set:
#         to_set(c2)
#     return len(c1.intersection(c2)) / len(c1)

#dendo_gram 0.7936729056980395

def purity(c1, c2):
    count = 0
    for item in c2:
        if item in c1:
           count = count + 1
    return count/len(c1)



def cal_dendogram_purity(X, Y, tree):
    import numpy as np
    li = []
    for i, item in enumerate(X):
        li.append(str_to_name(item))
    X = np.array(li)
    max_label = Y.max()
    print('max label {}'.format(max_label))
    sum_div = 0
    count_purity = 0
    for index in range(0, max_label + 1):
        print('index {}'.format(index))
        c = X[Y == index].shape[0]
        sum_div += (c * (c - 1)) / 2
        count_1 = 0
        count_2 = 0
        for i, x in enumerate(X[Y == index]):
            for next_index, next_item in enumerate(X[Y == index][i + 1:]):
                node = lca(set([next_item, x]), tree)
                if type(node) == Node and set([next_item, x]).issubset(node.orgi_data):
                    tmp_purity = purity(node.orgi_data, X[Y == index])
                    count_purity = count_purity + tmp_purity
                else:
                    tmp_purity = purity(node.data, X[Y == index])
                    count_purity = count_purity + tmp_purity
    print(count_1)
    print(count_2)
    print(sum_div)
    return count_purity / sum_div
# a = Node(set([1, 2]), 'A')
# b = Node(set([3, 4]), 'B')
# c = Leaf(set([5, 6, 7]),'C')
# d = Leaf(set([8, 9]),'D')
# e = Node(set([10, 11]),'E')
# f = Leaf(set([23,45]),'F')


# a = Node(set(["1x", "2x"]), 0)
# b = Node(set(["3x", "4x"]), 1)
# c = Leaf(set(["5x", "6x"]),2)
# d = Leaf(set(["8x", "9x"]),3)
# e = Node(set(["10x", "11x"]), 4)
# f = Leaf(set(["23x","45x"]),5)
#bsp dendrogram
# a = Leaf(set(["1x"]), 0)
# b = Leaf(set(["2x"]), 1)
# c = Leaf(set(["3x"]),2)
# d = Leaf(set(["4x"]),3)
# e = Leaf(set(["5x"]), 4)
# f = Leaf(set(["6x"]),5)
# li = [1,2,3,4,5,6,8,9,10,11,23,45]
# y_li = [0,0,1,1,2,2,3,3,4,4,5,5]
import numpy as np
# X  = np.array(li)
# Y = np.array(y_li)
# root = Node(set([]), 'root')
# root.children = [a, b]
# a.children = [c, d]
# b.children = [e]
# e.children = [f]
# root.data = get_data(root)
# a = Leaf(set(["1x"]), 0)
# b = Leaf(set(["2x","3x","4x"]), 1)
# c = Node(set([]),2)
# root = Node(set([]), 'root')
# c.children = [b]
# root.children = [a,c]
# li = [1,2,3,4]
# X = np.array(li)
# Y = np.array([0,1,1,1])
# root.data =get_data(root)
# print(c.data)
# print(cal_dendogram_purity(X,Y,root))
# # print(get_data(root))
# print(len(root.data))
# print(b.data)
# print(lca(set([3,45]), root).name)
# #print(e.data)
# # g = set(range(0,12))
# # e = set([11,45])
# # print(e.issubset(g))

#### Baum für 6.csv #######
# a = Leaf(set(["0x"]), 0)
# b = Leaf(set(["1x"]), 1)
# c = Leaf(set(["2x"]),2)
# b_c = Node(set([]), 6)
# b_c.children = [b,c]
# a_e = Node(set([]),7)
# d = Leaf(set(["3x"]),3)
# e = Leaf(set(["4x"]), 4)
# f = Leaf(set(["5x"]),5)
# a_e.children = [a,e]
# combi_5 = Node(set([]), 8)
# combi_5.children = [f,b_c]
# combi_3 = Node(set([]), 9)
# combi_3.children = [d, combi_5]
# root = Node(set([]), 'root')
# root.children = [a_e, combi_3]
# root.data = get_data(root)
#
# li = [0,1,2,3,4,5]
# X = np.array(li)
# Y = np.array([1,0,0,1,0,0])
# root.data =get_data(root)
# print(root.data)
# print('data')
# print(lca(set(['0x', '3x']), root).name)
# print(cal_dendogram_purity(X,Y,root))

#######################

a = Leaf(set(["0x"]), 0)
b = Leaf(set(["1x"]), 1)
c = Leaf(set(["2x"]),2)
d = Leaf(set(["3x"]),3)
e = Leaf(set(["4x"]), 4)
f = Leaf(set(["5x"]),5)
g = Leaf(set(["6x"]),6)
h = Leaf(set(["7x"]),7)

a_e = Node(set([]), 8)
a_e.children = [a,e]
b_f = Node(set([]), 9)
b_f.children = [b,f]
c_g = Node(set([]), 10)
c_g.children = [c,g]
d_h = Node(set([]), 11)
d_h.children = [d, h]

merge_1 = Node(set([]), 12)
merge_1.children = [a_e, b_f]


merge_2 = Node(set([]), 13)
merge_2.children = [merge_1, c_g]

root = Node(set([]), 'root')
root.children = [merge_2, d_h]
root.data = get_data(root)
li = [0,1,2,3,4,5,6,7]
X = np.array(li)
Y = np.array([1, 1, 0, 0, 0, 1, 0, 0])
Y = np.array([1, 1, 0, 0, 1, 1, 1, 0])


print(cal_dendogram_purity(X,Y,root))