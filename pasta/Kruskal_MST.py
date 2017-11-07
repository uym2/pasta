from DisjointSets_ADT import DisjointSets
import operator
from dendropy import Tree, Node
from sys import stdout
from decompose_lib import compute_group_distance_matrix, place_group_onto_tree


def tree_as_newick(tree,outfile=None,append=False):
# dendropy's method to write newick seems to have problem ...
    def __write_newick(node,outstream):
        if node.is_leaf():
            try:
                outstream.write(str(node.taxon.label))
            except:
                outstream.write(str(node.label))
        else:
            outstream.write('(')
            is_first_child = True
            for child in node.child_node_iter():
                if is_first_child:
                    is_first_child = False
                else:
                    outstream.write(',')
                __write_newick(child,outstream)
            outstream.write(')')
        if not node.is_leaf() and node.label is not None:
                outstream.write(str(node.label))
        
        if not node.edge_length is None:
            outstream.write(":"+str(node.edge_length))

    outstream = open(outfile,'a') if append else open(outfile,'w') if outfile else stdout
    __write_newick(tree.seed_node,outstream)
    outstream.write(";\n")
    if outfile:
        outstream.close()    


def graph2tree(G,root=0,names=[]):
    # assum G is acyclic
    seed_node = Node()
    seed_node.label = names[root] if names else str(root)
    T = Tree(seed_node=seed_node)
    n = len(G)
    node_refs = [None for i in range(n)]
    node_refs[root] = seed_node
    count = 1
    curr_v = root

    stk = [root]

    while len(stk) > 0:
        curr_v = stk.pop()
        for v,length in G[curr_v]:
            if node_refs[v] is None:
                stk.append(v)
                new_node = Node()
                new_node.label = names[v] if names else str(v)
                node_refs[v] = new_node
                node_refs[curr_v].add_child(new_node)
                new_node.edge_length = length

    for node in T.leaf_node_iter():
        node.taxon = T.taxon_namespace.new_taxon(label=node.label)

    return T

def build_MST(distance_mtrx,n,names=[]):
    print(names)
    MST = [[] for i in range(n)]
    sorted_d = sorted(distance_mtrx.items(), key=operator.itemgetter(1))
    #print(sorted_d)
    DS = DisjointSets(n)
 
    for edge,length in sorted_d:
        if not DS.is_single():  
            p,q = edge
            if DS.find(p) is not DS.find(q):
                DS.join(p,q)
                print(p,q,length)
                MST[p].append((q,length))
                MST[q].append((p,length))

    MST_tree = graph2tree(MST,names=names)            
    return MST_tree


def build_groups_MST(tree,grouping):
    #print("Building treeMap ...")
    treeMap = place_group_onto_tree(tree,grouping)
    #print("Computing distance matrix ...")
    D = compute_group_distance_matrix(tree,treeMap)
    #print(D)
    #print("Constructing MST ... ")
    MST_tree = build_MST(D,len(treeMap),names=treeMap.keys())

    return MST_tree

#distance_mtrx = {(0,1):1,(0,3):4,(0,4):3,(1,3):4,(1,4):2,(2,4):4,(2,5):5,(3,4):4,(4,5):7}

#T = build_MST(distance_mtrx,6)
#tree_as_newick(T)
