import attr
import math
from scipy.special import comb
import numpy as np



# The dendogram purity can be computed in a bottom up manner
# at each node within the tree we need the number of data points in each child and have to weight the cases


@attr.s(cmp=False)
class DpNode(object):
    """
    node_id should be in such a way that a smaller number means split before a larger number in a top-down manner
    That is the root should have node_id = 0 and the children of the last split should have node id
    2*n_dps-2 and 2*n_dps-1

    """

    left_child = attr.ib()
    right_child = attr.ib()
    node_id = attr.ib()

    @property
    def children(self):
        return [self.left_child, self.right_child]

    @property
    def is_leaf(self):
        return False


@attr.s(cmp=False)
class DpLeaf(object):
    dp_ids = attr.ib()
    node_id = attr.ib()

    @property
    def children(self):
        return []

    @property
    def is_leaf(self):
        return True



def count_values_in_sequence(seq):
    from collections import defaultdict
    res = defaultdict(lambda : 0)
    for key in seq:
        res[key] += 1
    return dict(res)


def combine_two_trees(tree_a, tree_b):
    def recursive(ta, tb):
        if ta.is_leaf != tb.is_leaf or ta.node_id != tb.node_id:
            print(f"{ta.node_id} != {tb.node_id}")
            raise RuntimeError("Trees are not equivalent!")
        if ta.is_leaf:
            return DpLeaf(ta.dp_ids + tb.dp_ids, ta.node_id)
        else:
            left_child = recursive(ta.left_child, tb.left_child)
            right_child = recursive(ta.right_child, tb.right_child)
            return DpNode(left_child, right_child, ta.node_id)

    return recursive(tree_a, tree_b)



def dendrogram_purity(tree_root, ground_truth):
    total_per_label_frequencies = count_values_in_sequence(ground_truth)
    total_per_label_pairs_count = {k: comb(v, 2, True) for k, v in total_per_label_frequencies.items()}
    total_n_of_pairs = sum(total_per_label_pairs_count.values())

    one_div_total_n_of_pairs = 1. / total_n_of_pairs

    purity = 0.

    def calculate_purity(node, level):
        nonlocal purity
        if node.is_leaf:
            node_total_dp_count = len(node.dp_ids)
            node_per_label_frequencies = count_values_in_sequence(
                [ground_truth[id] for id in node.dp_ids])
            node_per_label_pairs_count = {k: comb(v, 2, True) for k, v in node_per_label_frequencies.items()}

        else:  # it is an inner node
            left_child_per_label_freq, left_child_total_dp_count = calculate_purity(node.left_child, level + 1)
            right_child_per_label_freq, right_child_total_dp_count = calculate_purity(node.right_child, level + 1)
            node_total_dp_count = left_child_total_dp_count + right_child_total_dp_count
            node_per_label_frequencies = {k: left_child_per_label_freq.get(k, 0) + right_child_per_label_freq.get(k, 0) \
                                          for k in set(left_child_per_label_freq) | set(right_child_per_label_freq)}

            node_per_label_pairs_count = {k: left_child_per_label_freq.get(k) * right_child_per_label_freq.get(k) \
                                          for k in set(left_child_per_label_freq) & set(right_child_per_label_freq)}

        for label, pair_count in node_per_label_pairs_count.items():
            label_freq = node_per_label_frequencies[label]
            label_pairs = node_per_label_pairs_count[label]
            purity += one_div_total_n_of_pairs * label_freq / node_total_dp_count * label_pairs
        return node_per_label_frequencies, node_total_dp_count

    calculate_purity(tree_root, 0)
    return purity


def prune_dendrogram_purity_tree(tree, n_leaves):
    """
    This function collapses the tree such that it only has n_leaves.
    This makes it possible to compare different trees with different number of leaves.

    Important, it assumes that the node_id is equal to the split order, that means the tree root should have the smallest split number
    and the two leaf nodes that are splitted the last have the highest node id. And that  max(node_id) == #leaves - 2

    :param tree:
    :param n_levels:
    :return:
    """
    max_node_id = n_leaves - 2

    def recursive(node):
        if node.is_leaf:
            return node
        else:  # node is an inner node
            if node.node_id < max_node_id:
                left_child = recursive(node.left_child)
                right_child = recursive(node.right_child)
                return DpNode(left_child, right_child, node.node_id)
            else:
                work_list = [node.left_child, node.right_child]
                dp_ids = []
                while len(work_list) > 0:
                    nc = work_list.pop()
                    if nc.is_leaf:
                        dp_ids = dp_ids + nc.dp_ids
                    else:
                        work_list.append(nc.left_child)
                        work_list.append(nc.right_child)
                return DpLeaf(dp_ids, node.node_id)
                # raise RuntimeError("should not be here!")

    return recursive(tree)


def to_dendrogram_purity_tree(children_array):
    """
    Can convert the children_ matrix of a  sklearn.cluster.hierarchical.AgglomerativeClustering outcome to a dendrogram_purity tree
    :param children_array:  array-like, shape (n_samples-1, 2)
        The children of each non-leaf nodes. Values less than `n_samples`
            correspond to leaves of the tree which are the original samples.
            A node `i` greater than or equal to `n_samples` is a non-leaf
            node and has children `children_[i - n_samples]`. Alternatively
            at the i-th iteration, children[i][0] and children[i][1]
            are merged to form node `n_samples + i`
    :return:
    """
    n_samples = children_array.shape[0] + 1
    max_id = 2 * n_samples - 2
    node_map = {dp_id: DpLeaf([dp_id], max_id - dp_id) for dp_id in range(n_samples)}
    next_id = max_id - n_samples

    for idx in range(n_samples - 1):
        next_fusion = children_array[idx, :]
        child_a = node_map.pop(next_fusion[0])
        child_b = node_map.pop(next_fusion[1])
        node_map[n_samples + idx] = DpNode(child_a, child_b, next_id)
        next_id -= 1
    if len(node_map) != 1:
        raise RuntimeError("tree must be fully developed! Use ompute_full_tree=True for AgglomerativeClustering")
    root = node_map[n_samples + n_samples - 2]
    return root



if __name__ == "__main__":
    from sklearn.metrics import normalized_mutual_info_score as nmi
    # Here an example of a tree as it could be given back by the algorithm
    # Leaf nodes contains a set of data point ids and a node index
    l4 = DpLeaf([0], 0)
    l7 = DpLeaf([1], 1)
    l8 = DpLeaf([2], 2)
    l5 = DpLeaf([3], 3)
    l6 = DpLeaf([4], 4)
    #We only have currently binary trees so only to children per inner node
    n3 = DpNode(l7,l8,5)
    n1 = DpNode(l4,n3, 6)
    n2 = DpNode(l5,l6,7)
    n0 = DpNode(n1,n2,8)

    #We can then determine the dendrogram_purity against a flat ground truth clustering
    ret = dendrogram_purity(n0,np.asarray([0,1,1,2,3]))
    print(ret) #Data points are contained within pure sub-trees should be one


    ret = dendrogram_purity(n0,np.asarray([0,0,1,2,3]))
    print(ret) #Here the data point 1 switched classes, the sub-trees are not pure anymore


