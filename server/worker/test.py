import networkx as nx
import os
from parser_utils import parse_file, LANGUAGE_MAP
from graph_utils import build_graph_from_ast

# ---------------------------
# Globals
# ---------------------------
combined_graph = nx.DiGraph()
parsed_files = {}

# ---------------------------
# Helper: Pretty-print AST graph
# ---------------------------
def print_tree(graph, root, indent=0):
    print("  " * indent + root)
    for child in graph.successors(root):
        print_tree(graph, child, indent + 1)

# ---------------------------
# Parse file, build AST graph
# ---------------------------
def parse_file_if_needed(file_path, file_name):
    if file_name in parsed_files:
        return parsed_files[file_name]

    ext = os.path.splitext(file_name)[1]
    if ext not in LANGUAGE_MAP or not os.path.exists(file_path):
        print(f"Skipping {file_name}, unsupported extension or missing")
        return None

    tree, source_code = parse_file(file_path, LANGUAGE_MAP[ext])

    # --- AST graph ---
    graph = build_graph_from_ast(tree)
    combined_graph.update(graph)
    parsed_files[file_name] = (tree, source_code)

    # --- Print graph ---
    print("\n--- AST Graph Nodes ---")
    for node in graph.nodes:
        print(node)

    print("\n--- AST Graph Edges ---")
    for edge in graph.edges:
        print(edge)

    # Pretty-print
    root_label = f"{tree.root_node.type}@{tree.root_node.start_point}-{tree.root_node.end_point}"
    print("\n--- Pretty-printed AST ---")
    print_tree(graph, root_label)

    return tree, source_code


# ---------------------------
# Example usage
# ---------------------------
file_path = "example.py"   # Make sure this file exists with some code
file_name = "example.py"

result = parse_file_if_needed(file_path, file_name)

if result:
    tree, source_code = result
    print("\n--- AST parsed successfully ---")
    print("Source code snippet:", source_code[:100])

    # --- Build PDG ---
    
    
else:
    print("File was skipped or not parsed")
