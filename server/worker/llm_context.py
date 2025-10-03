from .parser_utils import extract_functions_from_ast
from .git_utils import get_actual_diff

def prepare_llm_context(parsed_files, changed_files, combined_graph, temp_dir, base_branch, head_branch, LANGUAGE_MAP):
    """
    Build structured context for LLM consumption.
    """
    context = {
        "summary": {
            "total_files_changed": len(changed_files),
            "files_changed": changed_files
        },
        "files": {}
    }

    for file in changed_files:
        if file not in parsed_files:
            continue
        
        tree, source_code = parsed_files[file]
        ext = file.split('.')[-1]
        lang = LANGUAGE_MAP.get(f".{ext}")
        
        definitions = extract_functions_from_ast(tree, source_code, lang)
        diff = get_actual_diff(temp_dir, base_branch, head_branch, file)

        imports = []
        imported_by = []
        for edge in combined_graph.edges(data=True):
            if edge[2].get('type') == 'import':
                if edge[0] == file:
                    imports.append(edge[1])
                if edge[1] == file:
                    imported_by.append(edge[0])
        
        context["files"][file] = {
            "language": lang,
            "diff": diff,
            "definitions": definitions,
            "imports": imports,
            "imported_by": imported_by,
            "total_definitions": len(definitions)
        }
    
    return context
