import subprocess
import tempfile
import os
import shutil
import json
import networkx as nx
from networkx.readwrite import json_graph
from tree_sitter_languages import get_parser

LANGUAGE_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".go": "go",
    ".java": "java",
}

EXTENSION_GROUPS = {
    "python": [".py"],
    "javascript": [".js", ".jsx", ".mjs"],
    "typescript": [".ts", ".tsx"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
    "go": [".go"],
    "java": [".java"],
}

# ---------- Parse with Tree-sitter ----------
def parse_file_with_tree_sitter(file_path, lang_name):
    parser = get_parser(lang_name)
    with open(file_path, "rb") as f:
        source_code = f.read()
    tree = parser.parse(source_code)
    return tree, source_code

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

def extract_imports_with_tree_sitter(file_path, lang_name):
    """Return list of imported modules/files using Tree-sitter AST."""
    imports = []
    parser = get_parser(lang_name)
    with open(file_path, "rb") as f:
        source_code = f.read()
    tree = parser.parse(source_code)
    root = tree.root_node

    def get_string_value(node):
        """Extract string value from a string node."""
        text = source_code[node.start_byte:node.end_byte].decode("utf-8")
        return text.strip('"').strip("'")

    def walk(node):
        if lang_name == "python":
            if node.type == "import_from_statement":
                # from X import Y
                for child in node.children:
                    if child.type == "dotted_name":
                        module = source_code[child.start_byte:child.end_byte].decode("utf-8")
                        imports.append(module)
                        break
            elif node.type == "import_statement":
                # import X
                for child in node.children:
                    if child.type == "dotted_name":
                        module = source_code[child.start_byte:child.end_byte].decode("utf-8")
                        imports.append(module)
                        
        elif lang_name in ("javascript", "typescript"):
            if node.type == "import_statement":
                # Look for string nodes containing the path
                for child in node.children:
                    if child.type == "string":
                        imports.append(get_string_value(child))
            elif node.type == "call_expression":
                # require() or import()
                func_node = node.child_by_field_name("function")
                if func_node and source_code[func_node.start_byte:func_node.end_byte].decode("utf-8") in ["require", "import"]:
                    args = node.child_by_field_name("arguments")
                    if args:
                        for child in args.children:
                            if child.type == "string":
                                imports.append(get_string_value(child))
                                
        elif lang_name == "go":
            if node.type == "import_spec":
                for child in node.children:
                    if child.type == "interpreted_string_literal":
                        imports.append(get_string_value(child))
                        
        elif lang_name == "java":
            if node.type == "import_declaration":
                text = source_code[node.start_byte:node.end_byte].decode("utf-8")
                # Extract package.Class from "import package.Class;"
                parts = text.replace("import", "").replace(";", "").strip().split()
                if parts:
                    imports.append(parts[0])
                    
        elif lang_name in ("c", "cpp"):
            if node.type == "preproc_include":
                for child in node.children:
                    if child.type in ("string_literal", "system_lib_string"):
                        path = source_code[child.start_byte:child.end_byte].decode("utf-8")
                        imports.append(path.strip('"').strip("<>"))
                        
        for child in node.children:
            walk(child)

    walk(root)
    return imports

def resolve_import_path(import_str, current_file, temp_dir, lang):
    """
    Resolve an import string to an actual file path.
    Returns the relative path from temp_dir if found, None otherwise.
    """
    current_dir = os.path.dirname(os.path.join(temp_dir, current_file))
    extensions = EXTENSION_GROUPS.get(lang, [])
    
    # Handle relative imports
    if import_str.startswith('.'):
        base_path = os.path.normpath(os.path.join(current_dir, import_str))
    else:
        # Try as relative first, then from repo root
        base_path = os.path.normpath(os.path.join(current_dir, import_str))
        if not any(os.path.exists(base_path + ext) for ext in extensions):
            base_path = os.path.normpath(os.path.join(temp_dir, import_str))
    
    # Try with each possible extension
    for ext in extensions:
        candidate = base_path + ext
        if os.path.exists(candidate):
            return os.path.relpath(candidate, temp_dir)
    
    # Try as index file in directory
    for ext in extensions:
        candidate = os.path.join(base_path, f"index{ext}")
        if os.path.exists(candidate):
            return os.path.relpath(candidate, temp_dir)
    
    # For Python, try as package (__init__.py)
    if lang == "python":
        candidate = os.path.join(base_path, "__init__.py")
        if os.path.exists(candidate):
            return os.path.relpath(candidate, temp_dir)
        # Also handle dot notation (a.b.c -> a/b/c.py)
        pkg_path = os.path.join(temp_dir, import_str.replace(".", os.sep) + ".py")
        if os.path.exists(pkg_path):
            return os.path.relpath(pkg_path, temp_dir)
    
    # For Java, convert package.Class to package/Class.java
    if lang == "java":
        java_path = os.path.join(temp_dir, import_str.replace(".", os.sep) + ".java")
        if os.path.exists(java_path):
            return os.path.relpath(java_path, temp_dir)
    
    return None

# ---------- PR processing ----------
def process_pr(pr_data, output_dir="results"):
    repo_url = pr_data["clone_url"]
    pr_number = pr_data["pr_number"]
    base_branch = pr_data["base_branch"]
    head_branch = pr_data["head_branch"]

    print(f"[Worker] Reviewing PR #{pr_number} from {pr_data['repo_name']}")

    temp_dir = tempfile.mkdtemp()
    os.makedirs(output_dir, exist_ok=True)

    try:
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
        subprocess.run(["git", "fetch", "origin", head_branch], cwd=temp_dir, check=True)
        subprocess.run(["git", "checkout", head_branch], cwd=temp_dir, check=True)

        # Get changed files
        diff_cmd = ["git", "diff", "--name-only", f"origin/{base_branch}...origin/{head_branch}"]
        result = subprocess.run(diff_cmd, cwd=temp_dir, capture_output=True, text=True)
        changed_files = result.stdout.splitlines()

        ast_graphs = {}
        combined_graph = nx.DiGraph()
        parsed_files = {}

        def parse_file_if_needed(file_path, file_name):
            if file_name in parsed_files:
                return
            ext = os.path.splitext(file_name)[1]
            if ext not in LANGUAGE_MAP or not os.path.exists(file_path):
                return
            tree, source_code = parse_file_with_tree_sitter(file_path, LANGUAGE_MAP[ext])
            graph = build_graph_from_ast(tree)
            ast_graphs[file_name] = list(graph.edges())
            combined_graph.update(graph)
            parsed_files[file_name] = (tree, source_code)
            return tree, source_code

        # Parse changed files first
        for file in changed_files:
            abs_path = os.path.join(temp_dir, file)
            parse_file_if_needed(abs_path, file)

        # Collect direct imports from changed files
        for current_file in list(parsed_files.keys()):
            ext = os.path.splitext(current_file)[1]
            lang = LANGUAGE_MAP.get(ext)
            if not lang:
                continue

            imports = extract_imports_with_tree_sitter(os.path.join(temp_dir, current_file), lang)
            for import_str in imports:
                resolved_path = resolve_import_path(import_str, current_file, temp_dir, lang)
                
                if resolved_path:
                    if resolved_path not in parsed_files:
                        abs_resolved = os.path.join(temp_dir, resolved_path)
                        parse_file_if_needed(abs_resolved, resolved_path)
                    combined_graph.add_edge(current_file, resolved_path, type="import")

        # ---------- Write outputs ----------
        ast_json_path = os.path.join(output_dir, f"pr_{pr_number}_ast_graphs.json")
        with open(ast_json_path, "w") as f:
            json.dump(ast_graphs, f, indent=2)

        code_graph_json_path = os.path.join(output_dir, f"pr_{pr_number}_code_graph.json")
        json_data = json_graph.node_link_data(combined_graph)
        with open(code_graph_json_path, "w") as f:
            json.dump(json_data, f, indent=2)

        print(f"[Worker] AST graphs written to: {ast_json_path}")
        print(f"[Worker] Code graph written to: {code_graph_json_path}")

        return {
            "pr_number": pr_number,
            "repo": pr_data["repo_name"],
            "changed_files": changed_files,
            "ast_graph_json": ast_json_path,
            "code_graph_json": code_graph_json_path,
        }

    except subprocess.CalledProcessError as e:
        print(f"[Worker] Error: {e}")
        return {"error": str(e)}

    finally:
        shutil.rmtree(temp_dir)