import os
import tempfile
import shutil
import networkx as nx
import json
import boto3
from redis import Redis
from rq import Queue
from dotenv import load_dotenv
from tree_sitter_languages import get_parser
import uuid

from server.worker.services.parser_utils import  extract_imports_with_tree_sitter, resolve_import_path, LANGUAGE_MAP
# from server.worker.services.write_pr_txt import write_pr_txt
# from server.worker.services.graph_utils import build_graph_from_ast, build_semantic_graph
# from server.worker.services.llm_context import prepare_llm_context
from server.worker.services.git_utils import clone_and_checkout, get_changed_files
# from server.agentic.main import process_ai_job


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



def parse_file(file_path, lang_name):
    parser = get_parser(lang_name)
    # print("parser",parser)
    with open(file_path, "rb") as f:
        source_code = f.read()
    # print("source code",source_code)
    tree = parser.parse(source_code)
    # print("parser",tree.root_node)
    
    return tree, source_code

def print_ast(node, indent=0):
    """
    Recursively print the AST nodes.
    
    Args:
        node: tree_sitter.Node
        indent: current indentation level for pretty printing
    """
    prefix = "  " * indent
    # print(f"{prefix}{node.type} [{node.start_point} - {node.end_point}]")
    for child in node.children:
        print_ast(child, indent + 1)

def build_graph_form_ast(tree):
    graph=nx.DiGraph()
    def walk(node,parent=None):
        label=f"{node.type}@{node.start_point}-{node.end_point}"
        # print("label",label)
        graph.add_node(label)
        if parent:
            graph.add_edge(parent,label)
        for child in node.children:
            # print("child",child)
            walk(child,label)
    
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

        # --- decorators (Python) ---
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

        # recurse children
        for child in node.children:
            walk(child, current_def)

    walk(tree.root_node)
    return graph





def process_pr_async(pr_data):
    repo_url = pr_data["clone_url"]
    pr_number = pr_data.get("pr_number")
    base_branch = pr_data.get("base_branch")
    head_branch = pr_data.get("head_branch")
    repo_name = pr_data.get("repo_name", os.path.basename(repo_url).replace(".git", ""))
    safe_repo_name = repo_name.replace("/", "_")
    s3_prefix = f"pr_contexts/{safe_repo_name}_{pr_number}"

    # Create a temp directory
    temp_dir = tempfile.mkdtemp()
    print("Temp dir created:", temp_dir)
    print("Safe repo name:", safe_repo_name)
    print("S3 prefix created:", s3_prefix)

    # Clone repo and checkout the PR branch
    clone_and_checkout(repo_url, temp_dir, head_branch)

    # Get changed files between base and head
    changed_files = get_changed_files(temp_dir, base_branch, head_branch)
    # print("Changed files:", changed_files)
    combined_graph=nx.DiGraph()
    parsed_files={}
    # print("changed",combined_graph)


    def parse_file_if_needed(file_path,file_name):
        if file_name in parsed_files:
            return
        extention=os.path.splitext(file_name)[1]
        print("ext",extention)
        if extention not in LANGUAGE_MAP or not os.path.exists(file_path):
            return
        tree,source_code=parse_file(file_path,LANGUAGE_MAP[extention])
        if isinstance(source_code,bytes):
            source_code=source_code.decode('utf-8')
        # print('source code',source_code)
        # print_ast(tree.root_node)
        graph=build_graph_form_ast(tree)
        sem_graph = build_semantic_graph(tree, source_code, LANGUAGE_MAP[extention], file_name)
        # print("graph",graph)
        print("graph sem",sem_graph)


    
    for file in changed_files:
        print("changed",changed_files)
        parse_file_if_needed(os.path.join(temp_dir,file),file)
        
# Example usage
process_pr_async(pr_data={
    "clone_url": "https://github.com/hemanth-1321/codedaddy",
    "repo_name": "codedaddy",
    "pr_number": 123,
    "base_branch": "main",
    "head_branch": "test"
})
