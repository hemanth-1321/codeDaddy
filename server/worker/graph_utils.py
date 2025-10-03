import networkx as nx

def build_graph_from_ast(tree):
    """
    Build a directed graph from a Tree-sitter AST.
    Each node is labeled as type@start-end.
    """
    graph = nx.DiGraph()
    
    def walk(node, parent=None):
        label = f"{node.type}@{node.start_point}-{node.end_point}"
        graph.add_node(label)
        if parent:
            graph.add_edge(parent, label)
        for child in node.children:
            walk(child, label)
    
    walk(tree.root_node)
    return graph
