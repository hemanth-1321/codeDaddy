import os
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

def parse_file(file_path, lang_name):
    parser = get_parser(lang_name)

    # Read raw bytes
    with open(file_path, "rb") as f:
        raw = f.read()

    # Try UTF-8 first
    try:
        source_code = raw.decode("utf-8")
    except UnicodeDecodeError:
        print(f"[Parser] Non-UTF8 file detected: {file_path}, using latin-1 fallback")
        source_code = raw.decode("latin-1", errors="ignore")

    # MUST encode back to UTF-8 bytes for tree-sitter
    source_bytes = source_code.encode("utf-8")

    print("source code", source_code[:200])
    tree = parser.parse(source_bytes)
    print("parser", tree)

    return tree, source_code




def extract_imports_with_tree_sitter(file_path, lang_name):
    imports = []
    parser = get_parser(lang_name)
    with open(file_path, "rb") as f:
        source_code = f.read()
    tree = parser.parse(source_code)
    root = tree.root_node

    def get_string_value(node):
        text = source_code[node.start_byte:node.end_byte].decode("utf-8")
        return text.strip('"').strip("'")

    def walk(node):
        if lang_name == "python":
            if node.type == "import_from_statement":
                for child in node.children:
                    if child.type == "dotted_name":
                        module = source_code[child.start_byte:child.end_byte].decode("utf-8")
                        imports.append(module)
                        break
            elif node.type == "import_statement":
                for child in node.children:
                    if child.type == "dotted_name":
                        module = source_code[child.start_byte:child.end_byte].decode("utf-8")
                        imports.append(module)
        elif lang_name in ("javascript", "typescript"):
            if node.type == "import_statement":
                for child in node.children:
                    if child.type == "string":
                        imports.append(get_string_value(child))
            elif node.type == "call_expression":
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
    current_dir = os.path.dirname(os.path.join(temp_dir, current_file))
    extensions = EXTENSION_GROUPS.get(lang, [])
    
    if import_str.startswith('.'):
        base_path = os.path.normpath(os.path.join(current_dir, import_str))
    else:
        base_path = os.path.normpath(os.path.join(current_dir, import_str))
        if not any(os.path.exists(base_path + ext) for ext in extensions):
            base_path = os.path.normpath(os.path.join(temp_dir, import_str))
    
    for ext in extensions:
        candidate = base_path + ext
        if os.path.exists(candidate):
            return os.path.relpath(candidate, temp_dir)
    
    for ext in extensions:
        candidate = os.path.join(base_path, f"index{ext}")
        if os.path.exists(candidate):
            return os.path.relpath(candidate, temp_dir)
    
    if lang == "python":
        candidate = os.path.join(base_path, "__init__.py")
        if os.path.exists(candidate):
            return os.path.relpath(candidate, temp_dir)
        pkg_path = os.path.join(temp_dir, import_str.replace(".", os.sep) + ".py")
        if os.path.exists(pkg_path):
            return os.path.relpath(pkg_path, temp_dir)
    
    if lang == "java":
        java_path = os.path.join(temp_dir, import_str.replace(".", os.sep) + ".java")
        if os.path.exists(java_path):
            return os.path.relpath(java_path, temp_dir)
    
    return None

