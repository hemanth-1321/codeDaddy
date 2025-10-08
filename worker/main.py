import os
import tempfile
import shutil
from redis import Redis
from rq import Queue
import json
from .services.parser_utils import parse_file, extract_imports_with_tree_sitter, resolve_import_path, LANGUAGE_MAP
from .services.write_pr_txt import write_pr_txt
from .services.graph_utils import build_graph_from_ast, build_semantic_graph
from .services.llm_context import prepare_llm_context
from .services.git_utils import clone_and_checkout, get_changed_files
from server.agentic.main import process_ai_job
import networkx as nx

connection=Redis(host="localhost",port=6379,db=0)
queue=Queue("pr_context_queue",connection=connection)


def process_pr(pr_data, output_dir="results"):
    repo_url = pr_data["clone_url"]
    pr_number = pr_data["pr_number"]
    base_branch = pr_data["base_branch"]
    head_branch = pr_data["head_branch"]
    repo_name = pr_data.get("repo_name", os.path.basename(repo_url).replace(".git", ""))

    # Replace '/' with '_' to make filesystem-safe filename
    safe_repo_name = repo_name.replace("/", "_")

    print(f"[Worker] Reviewing PR #{pr_number} from {repo_name}")

    temp_dir = tempfile.mkdtemp()
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Clone repo and checkout
        clone_and_checkout(repo_url, temp_dir, head_branch)

        # Get changed files
        changed_files = get_changed_files(temp_dir, base_branch, head_branch)

        combined_graph = nx.DiGraph()
        parsed_files = {}

        def parse_file_if_needed(file_path, file_name):
            if file_name in parsed_files:
                return
            ext = os.path.splitext(file_name)[1]
            if ext not in LANGUAGE_MAP or not os.path.exists(file_path):
                return

            tree, source_code = parse_file(file_path, LANGUAGE_MAP[ext])
            if isinstance(source_code, bytes):
                source_code = source_code.decode("utf-8")

            ast_graph = build_graph_from_ast(tree)
            sem_graph = build_semantic_graph(tree, source_code, LANGUAGE_MAP[ext], file_name)
            combined_graph.update(ast_graph)
            combined_graph.update(sem_graph)

            parsed_files[file_name] = (tree, source_code)
            return tree, source_code

        # Parse changed files
        for file in changed_files:
            parse_file_if_needed(os.path.join(temp_dir, file), file)

        # Resolve imports
        for current_file in list(parsed_files.keys()):
            ext = os.path.splitext(current_file)[1]
            lang = LANGUAGE_MAP.get(ext)
            if not lang:
                continue
            imports = extract_imports_with_tree_sitter(os.path.join(temp_dir, current_file), lang)
            for imp in imports:
                resolved_path = resolve_import_path(imp, current_file, temp_dir, lang)
                if resolved_path and resolved_path not in parsed_files:
                    parse_file_if_needed(os.path.join(temp_dir, resolved_path), resolved_path)
                    combined_graph.add_edge(current_file, resolved_path, type="import")

        # Prepare LLM context
        llm_context = prepare_llm_context(
            parsed_files,
            changed_files,
            combined_graph,
            temp_dir,
            base_branch,
            head_branch,
            LANGUAGE_MAP
        )

        # Add PR metadata
        llm_context["pr_metadata"] = {
            "pr_number": pr_number,
            "repo_name": repo_name,
            "repo_url": repo_url,
            "base_branch": base_branch,
            "head_branch": head_branch,
            "total_files_changed": len(changed_files)
        }

        # Write JSON context
        context_json_path = os.path.join(output_dir, f"pr_{safe_repo_name}_{pr_number}_context.json")
        with open(context_json_path, "w", encoding="utf-8") as f:
            json.dump(llm_context, f, indent=2)

        # Write TXT context
        context_txt_path = write_pr_txt(
            pr_data,
            parsed_files,
            changed_files,
            temp_dir,
            output_dir,
            file_name=os.path.join(output_dir, f"pr_{safe_repo_name}_{pr_number}_context.txt")
        )

        print(f"[Worker] LLM context written: JSON -> {context_json_path}, TXT -> {context_txt_path}")

        queue_data = {
            "pr_number": pr_number,
            "repo_name": repo_name,
            "repo_url": repo_url,
            "context_json": context_json_path,
            "context_txt": context_txt_path,
            "total_files_changed": len(changed_files)
        }

        queue.enqueue(process_ai_job, queue_data)

        return {
            "pr_number": pr_number,
            "repo": repo_name,
            "changed_files": changed_files,
            "context_json": context_json_path,
            "context_txt": context_txt_path,
            "llm_context": llm_context
        }

    except Exception as e:
        print(f"[Worker] Error: {e}")
        return {"error": str(e)}

    finally:
        shutil.rmtree(temp_dir)
