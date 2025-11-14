import networkx as nx
import uuid


LANG_RULES = {
    "python": {
        "func": [
            "function_definition",
            "async_function_definition",
            "lambda"
        ],
        "class": ["class_definition"],
        "call": ["call"],
        "import": ["import_statement", "import_from_statement"],
    },
    "javascript": {
        "func": [
            "function_declaration",
            "method_definition",
            "arrow_function",
            "function_expression"  # anonymous functions
        ],
        "class": ["class_declaration"],
        "call": [
            "call_expression",
            "new_expression",
            "import_expression"
        ],
        "import": ["import_declaration"],
    },
    "typescript": {
        "func": [
            "function_declaration",
            "method_definition",
            "arrow_function",
            "function_expression"
        ],
        "class": ["class_declaration"],
        "call": [
            "call_expression",
            "new_expression",
            "import_expression"
        ],
        "import": ["import_declaration"],
    },
    "rust": {
        "func": [
            "function_item",     
            "impl_item",          # methods inside impl blocks
            "associated_function" # functions inside traits/impl
        ],
        "class": [
            "struct_item",
            "enum_item",
            "trait_item"
        ],
        "call": [
            "call_expression",
            "method_call_expression",
            "macro_call"         # Rust macros
        ],
        "import": ["use_declaration"],
    },
}




def build_graph_from_ast(tree):
    
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


def build_semantic_graph(tree, source_code, lang, file_path):
    """
    Build a semantic code graph from a Tree-sitter AST.

    Nodes: file-level imports, functions, classes/structs/enums, call targets.
    Edges: 'contains', 'calls', 'imports', 'uses_import'.
    """

    graph = nx.DiGraph()
    lang_rules = LANG_RULES.get(lang, {})

    def node_text(node):
        try:
            return source_code[node.start_byte:node.end_byte].decode("utf-8")
        except Exception:
            return ""

    def add_def(name, kind, node):
        # Use uuid to ensure anonymous functions/classes/macro nodes are unique
        if name.startswith("anon_"):
            name = f"{name}_{uuid.uuid4().hex[:6]}"
        label = f"{file_path}::{kind}::{name}"
        graph.add_node(label, type=kind, name=name, span=(node.start_point, node.end_point))
        return label

    def walk(node, current_def=None):
        node_type = node.type

        # --- function definitions ---
        if node_type in lang_rules.get("func", []):
            name_node = node.child_by_field_name("name") or (node.children[0] if node.children else None)
            name = node_text(name_node).strip() if name_node else f"anon_func@{node.start_point}"
            def_label = add_def(name, "function", node)
            if current_def:
                graph.add_edge(current_def, def_label, type="contains")
            current_def = def_label

        # --- class / struct / enum / trait definitions ---
        if node_type in lang_rules.get("class", []):
            name_node = node.child_by_field_name("name") or (node.children[0] if node.children else None)
            name = node_text(name_node).strip() if name_node else f"anon_class@{node.start_point}"
            def_label = add_def(name, "class", node)
            if current_def:
                graph.add_edge(current_def, def_label, type="contains")
            current_def = def_label

        # --- decorators (Python) ---q
        if lang == "python" and node_type == "decorator":
            dec_text = node_text(node).strip()
            dec_label = f"{file_path}::decorator::{dec_text}"
            graph.add_node(dec_label, type="decorator", code=dec_text)
            if current_def:
                graph.add_edge(current_def, dec_label, type="has_decorator")
            else:
                file_anchor = f"{file_path}::file"
                graph.add_node(file_anchor, type="file")
                graph.add_edge(file_anchor, dec_label, type="has_decorator")

        # --- imports / use ---
        if node_type in lang_rules.get("import", []):
            import_text = node_text(node).strip()
            imp_label = f"{file_path}::import::{import_text}"
            graph.add_node(imp_label, type="import", code=import_text)
            file_anchor = f"{file_path}::file"
            graph.add_node(file_anchor, type="file")
            graph.add_edge(file_anchor, imp_label, type="imports")

        # --- call expressions ---
        if node_type in lang_rules.get("call", []):
            callee = node.child_by_field_name("function") or (node.children[0] if node.children else None)
            if callee is not None:
                called_name = node_text(callee).split("(")[0].strip()
                # unique label for root-level calls too
                called_label = f"{file_path}::call::{called_name}_{uuid.uuid4().hex[:6]}"
                graph.add_node(called_label, type="call_target", name=called_name)
                # attach to current_def if inside a function/class, else to file node
                parent = current_def if current_def else f"{file_path}::file"
                graph.add_node(parent, type="file")
                graph.add_edge(parent, called_label, type="calls")

        for child in node.children:
            walk(child, current_def)

    walk(tree.root_node)
    return graph
