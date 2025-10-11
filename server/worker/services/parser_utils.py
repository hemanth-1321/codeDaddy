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

# ---------- Parse ----------
def parse_file(file_path, lang_name):
    parser = get_parser(lang_name)
    with open(file_path, "rb") as f:
        source_code = f.read()
    print("source code",source_code)
    tree = parser.parse(source_code)
    print("parser",tree)
    
    return tree, source_code


# ---------- Extract functions/classes ----------
def extract_functions_from_ast(tree, source_code, lang_name):
    definitions = []

    def walk(node):
        extracted = None

        if lang_name == "python" and node.type in ("function_definition", "class_definition"):
            name_node = node.child_by_field_name("name")
            if name_node:
                name = source_code[name_node.start_byte:name_node.end_byte]
                params_node = node.child_by_field_name("parameters") if node.type=="function_definition" else None
                params = source_code[params_node.start_byte:params_node.end_byte] if params_node else None
                extracted = {
                    "name": name,
                    "type": node.type.replace("_definition",""),
                    "start_line": node.start_point[0]+1,
                    "end_line": node.end_point[0]+1,
                    "parameters": params,
                    "children": []
                }

        # JS / TS
        elif lang_name in ("javascript","typescript") and node.type in ("function_declaration","class_declaration","method_definition"):
            name_node = node.child_by_field_name("name")
            if name_node:
                name = source_code[name_node.start_byte:name_node.end_byte]
                params_node = node.child_by_field_name("parameters")
                params = source_code[params_node.start_byte:params_node.end_byte] if params_node else None
                extracted = {
                    "name": name,
                    "type": node.type.replace("_declaration","").replace("_definition",""),
                    "start_line": node.start_point[0]+1,
                    "end_line": node.end_point[0]+1,
                    "parameters": params,
                    "children": []
                }

        # Java
        elif lang_name == "java" and node.type in ("method_declaration","class_declaration"):
            name_node = node.child_by_field_name("name")
            if name_node:
                name = source_code[name_node.start_byte:name_node.end_byte]
                params_node = node.child_by_field_name("parameters") if node.type=="method_declaration" else None
                params = source_code[params_node.start_byte:params_node.end_byte] if params_node else None
                extracted = {
                    "name": name,
                    "type": node.type.replace("_declaration",""),
                    "start_line": node.start_point[0]+1,
                    "end_line": node.end_point[0]+1,
                    "parameters": params,
                    "children": []
                }

        # Go
        elif lang_name=="go" and node.type in ("function_declaration","method_declaration","type_declaration"):
            name_node = node.child_by_field_name("name")
            if name_node:
                name = source_code[name_node.start_byte:name_node.end_byte]
                params_node = node.child_by_field_name("parameters")
                params = source_code[params_node.start_byte:params_node.end_byte] if params_node else None
                extracted = {
                    "name": name,
                    "type": node.type.replace("_declaration",""),
                    "start_line": node.start_point[0]+1,
                    "end_line": node.end_point[0]+1,
                    "parameters": params,
                    "children": []
                }

        # C / C++
        elif lang_name in ("c","cpp") and node.type in ("function_definition","class_specifier","struct_specifier"):
            name = None
            for child in node.children:
                if child.type=="function_declarator":
                    for sub in child.children:
                        if sub.type=="identifier":
                            name = source_code[sub.start_byte:sub.end_byte]
                            break
                elif child.type in ("type_identifier","identifier"):
                    name = source_code[child.start_byte:child.end_byte]
            if name:
                extracted = {
                    "name": name,
                    "type": node.type.replace("_definition","").replace("_specifier",""),
                    "start_line": node.start_point[0]+1,
                    "end_line": node.end_point[0]+1,
                    "parameters": None,
                    "children": []
                }

        if extracted:
            definitions.append(extracted)

        for child in node.children:
            walk(child)

    walk(tree.root_node)
    return definitions


# ---------- Extract imports ----------
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

# ---------- Resolve import path ----------
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

