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


"""
ast tree for print("hello world")
module@(0, 0)-(0, 20)
  expression_statement@(0, 0)-(0, 20)
    call@(0, 0)-(0, 20)
      identifier@(0, 0)-(0, 5)
      argument_list@(0, 5)-(0, 20)
        (@(0, 5)-(0, 6)
        string@(0, 6)-(0, 19)
          string_start@(0, 6)-(0, 7)
          string_content@(0, 7)-(0, 18)
          string_end@(0, 18)-(0, 19)
        )@(0, 19)-(0, 20)

--- PDG Edges ---
('module@(0, 0)-(0, 20)', 'expression_statement@(0, 0)-(0, 20)', 'control')
('expression_statement@(0, 0)-(0, 20)', 'call@(0, 0)-(0, 20)', 'control')
('call@(0, 0)-(0, 20)', 'identifier@(0, 0)-(0, 5)', 'control')
('call@(0, 0)-(0, 20)', 'argument_list@(0, 5)-(0, 20)', 'control')
('argument_list@(0, 5)-(0, 20)', '(@(0, 5)-(0, 6)', 'control')
('argument_list@(0, 5)-(0, 20)', 'string@(0, 6)-(0, 19)', 'control')
('string@(0, 6)-(0, 19)', 'string_start@(0, 6)-(0, 7)', 'control')
('string@(0, 6)-(0, 19)', 'string_content@(0, 7)-(0, 18)', 'control')
('string@(0, 6)-(0, 19)', 'string_end@(0, 18)-(0, 19)', 'control')
('argument_list@(0, 5)-(0, 20)', ')@(0, 19)-(0, 20)', 'control')

"""



def build_semantic_graph(tree, source_code, lang, file_path):
    """
    Build a semantic code graph from a Tree-sitter AST.

    - Nodes are: file-level imports, functions, classes and inferred call targets (best-effort).
    - Edges are typed: `defines`, `calls`, `imports`, `contains`.

    This is intentionally language-aware in small places (e.g. python function/class naming)
    but will fall back to generic heuristics for other languages.

    Returns a networkx.DiGraph.
    """
    graph = nx.DiGraph()

    def node_text(node):
        try:
            return source_code[node.start_byte:node.end_byte].decode("utf-8")
        except Exception:
            return ""

    # helper to add definition nodes
    def add_def(name, kind, node):
        label = f"{file_path}::{kind}::{name}"
        graph.add_node(label, type=kind, name=name, span=(node.start_point, node.end_point))
        return label

    # keep track of current enclosing definition (function/class) while walking
    def walk(node, current_def=None):
        # --- definitions ---
        if lang == "python":
            if node.type == "function_definition":
                name_node = node.child_by_field_name("name")
                if name_node is not None:
                    name = node_text(name_node)
                    def_label = add_def(name, "function", node)
                    # contains edge
                    if current_def:
                        graph.add_edge(current_def, def_label, type="contains")
                    current_def = def_label
            elif node.type == "class_definition":
                name_node = node.child_by_field_name("name")
                if name_node is not None:
                    name = node_text(name_node)
                    def_label = add_def(name, "class", node)
                    if current_def:
                        graph.add_edge(current_def, def_label, type="contains")
                    current_def = def_label
        else:
            # generic heuristics: function_like, class_like
            if node.type in ("function_declaration", "method_declaration", "function_definition"):
                # try to get child named 'name'
                name_node = node.child_by_field_name("name")
                name = node_text(name_node) if name_node is not None else f"anon@{node.start_point}"
                def_label = add_def(name, "function", node)
                if current_def:
                    graph.add_edge(current_def, def_label, type="contains")
                current_def = def_label
            if node.type in ("class_declaration", "class_definition"):
                name_node = node.child_by_field_name("name")
                name = node_text(name_node) if name_node is not None else f"anonclass@{node.start_point}"
                def_label = add_def(name, "class", node)
                if current_def:
                    graph.add_edge(current_def, def_label, type="contains")
                current_def = def_label

        # --- imports ---
        if lang == "python" and node.type in ("import_statement", "import_from_statement"):
            import_text = node_text(node).strip()
            imp_label = f"{file_path}::import::{import_text}"
            graph.add_node(imp_label, type="import", code=import_text)
            if current_def:
                graph.add_edge(current_def, imp_label, type="uses_import")
            else:
                # file-level import node; create a "file" anchor
                file_anchor = f"{file_path}::file"
                graph.add_node(file_anchor, type="file")
                graph.add_edge(file_anchor, imp_label, type="imports")

        # --- call detection (heuristic) ---
        # Python: call nodes have type 'call'; function expression often first child
        if lang == "python" and node.type == "call":
            # function expression can be identifier or attribute
            func_node = None
            # Common child patterns: function is first child or child by field name 'function'
            if node.child_by_field_name("function"):
                func_node = node.child_by_field_name("function")
            elif len(node.children) > 0:
                func_node = node.children[0]

            if func_node is not None and current_def is not None:
                called_name = node_text(func_node).split("(")[0].strip()
                # create a node for the called name (best-effort, may be external)
                called_label = f"{file_path}::call::{called_name}"
                graph.add_node(called_label, type="call_target", name=called_name)
                graph.add_edge(current_def, called_label, type="calls")

        # Generic heuristic for call-like nodes
        if lang != "python" and node.type in ("call_expression", "invocation_expression", "call"):
            # take first child as callee if present
            callee = node.children[0] if node.children else None
            if callee and current_def:
                called_name = node_text(callee).split("(")[0].strip()
                called_label = f"{file_path}::call::{called_name}"
                graph.add_node(called_label, type="call_target", name=called_name)
                graph.add_edge(current_def, called_label, type="calls")

        # Recurse children
        for child in node.children:
            walk(child, current_def)

    walk(tree.root_node)
    return graph

