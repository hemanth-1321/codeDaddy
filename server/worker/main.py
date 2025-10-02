import subprocess
import tempfile
import os
import shutil
import json
import ast as py_ast
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

# ---------- Parse with Tree-sitter ----------
def parse_file_with_tree_sitter(file_path, lang_name):
    parser = get_parser(lang_name)
    with open(file_path, "rb") as f:
        source_code = f.read()
    tree = parser.parse(source_code)
    return tree

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

# ---------- Extract Python imports ----------
def extract_python_imports(file_path):
    """Return list of module names imported by a Python file."""
    imports = []
    try:
        with open(file_path, "r") as f:
            tree = py_ast.parse(f.read(), filename=file_path)
        for node in py_ast.walk(tree):
            if isinstance(node, py_ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, py_ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
    except Exception:
        pass
    return imports

# ---------- Process PR ----------
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

        diff_cmd = ["git", "diff", "--name-only", f"origin/{base_branch}...origin/{head_branch}"]
        result = subprocess.run(diff_cmd, cwd=temp_dir, capture_output=True, text=True)
        changed_files = result.stdout.splitlines()

        ast_graphs = {}
        combined_graph = nx.DiGraph()

        # Map from module/file name to absolute path for imports
        file_path_map = {os.path.splitext(f)[0]: os.path.join(temp_dir, f) for f in changed_files}

        for file in changed_files:
            ext = os.path.splitext(file)[1]
            if ext in LANGUAGE_MAP:
                abs_path = os.path.join(temp_dir, file)
                if os.path.exists(abs_path):
                    print(f"[Worker] Parsing {file}")
                    tree = parse_file_with_tree_sitter(abs_path, LANGUAGE_MAP[ext])
                    graph = build_graph_from_ast(tree)
                    ast_graphs[file] = list(graph.edges())
                    combined_graph = nx.compose(combined_graph, graph)

                    # ---------- Add import edges for Python ----------
                    if ext == ".py":
                        imports = extract_python_imports(abs_path)
                        for imported_module in imports:
                            if imported_module in file_path_map:
                                combined_graph.add_edge(file, os.path.basename(file_path_map[imported_module]),
                                                        type="import")

        # ---------- Write AST graphs ----------
        ast_json_path = os.path.join(output_dir, f"pr_{pr_number}_ast_graphs.json")
        with open(ast_json_path, "w") as f:
            json.dump(ast_graphs, f, indent=2)

        # ---------- Write code graph ----------
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
