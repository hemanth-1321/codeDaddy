import os
import tempfile
import shutil
import networkx as nx
import json
import boto3
from redis import Redis
from rq import Queue
from dotenv import load_dotenv
from .services.parser_utils import parse_file, extract_imports_with_tree_sitter, resolve_import_path, LANGUAGE_MAP
from .services.write_pr_txt import write_pr_txt
from .services.graph_utils import build_graph_from_ast, build_semantic_graph
from .services.llm_context import prepare_llm_context
from .services.git_utils import clone_and_checkout, get_changed_files
from server.agentic.main import process_ai_job
load_dotenv()


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    connection = Redis.from_url(REDIS_URL, decode_responses=False)
    connection.ping()
    print("[Worker] Connected to Redis successfully from worker")
except Exception as e:
    print("[Worker] Redis connection failed:", e)
    raise

queue = Queue("pr_context_queue", connection=connection)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
)
bucket_name = os.getenv("S3_BUCKET")
if not bucket_name:
    raise ValueError("S3_BUCKET not set in environment variables")

def upload_to_s3(file_path, key_prefix):
    """Upload a file to S3 and return its S3 URI."""
    file_name = os.path.basename(file_path)
    s3_key = f"{key_prefix}/{file_name}"
    s3_client.upload_file(file_path, bucket_name, s3_key)
    return f"s3://{bucket_name}/{s3_key}"

def process_pr(pr_data):
    """Process a PR: parse files, build graph, generate context, enqueue AI job."""
    repo_url = pr_data["clone_url"]
    pr_number = pr_data["pr_number"]
    base_branch = pr_data["base_branch"]
    head_branch = pr_data["head_branch"]
    repo_name = pr_data.get("repo_name", os.path.basename(repo_url).replace(".git", ""))
    commit_sha = pr_data.get("commit_sha")
    
    progress_comment_id = pr_data.get("progress_comment_id")
    installation_id = pr_data.get("installation_id")
    owner = pr_data.get("owner")
    repo = pr_data.get("repo")
    
    safe_repo_name = repo_name.replace("/", "_")
    s3_prefix = f"pr_contexts/{safe_repo_name}_{pr_number}"

    print(f"[Worker] Reviewing PR #{pr_number} from {repo_name}")

    temp_dir = tempfile.mkdtemp()

    try:
        # Clone PR
        clone_and_checkout(repo_url, temp_dir, head_branch)
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

        # Parse imported files
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
            parsed_files, changed_files, combined_graph,
            temp_dir, base_branch, head_branch, LANGUAGE_MAP
        )

        llm_context["pr_metadata"] = {
            "pr_number": pr_number,
            "repo_name": repo_name,
            "repo_url": repo_url,
            "base_branch": base_branch,
            "head_branch": head_branch,
            "total_files_changed": len(changed_files)
        }

        # Write JSON/TXT locally first
        context_json_path = os.path.join(temp_dir, f"pr_{safe_repo_name}_{pr_number}_context.json")
        with open(context_json_path, "w", encoding="utf-8") as f:
            json.dump(llm_context, f, indent=2)

        context_txt_path = write_pr_txt(
            pr_data, parsed_files, changed_files, temp_dir, temp_dir,
            file_name=os.path.join(temp_dir, f"pr_{safe_repo_name}_{pr_number}_context.txt")
        )

        # Upload to S3
        s3_json_uri = upload_to_s3(context_json_path, s3_prefix)
        s3_txt_uri = upload_to_s3(context_txt_path, s3_prefix)
        print(f"[Worker] Uploaded context files to S3: {s3_json_uri}, {s3_txt_uri}")

        # Enqueue AI job with S3 URIs and progress comment info
        queue_data = {
            "pr_number": pr_number,
            "repo_name": repo_name,
            "repo_url": repo_url,
            "context_json": s3_json_uri,
            "context_txt": s3_txt_uri,
            "total_files_changed": len(changed_files),
            "commit_sha": commit_sha,
            "progress_comment_id": progress_comment_id,
            "installation_id": installation_id,
            "owner": owner,
            "repo": repo
        }
        queue.enqueue(process_ai_job, queue_data)

        return {
            "pr_number": pr_number,
            "repo": repo_name,
            "changed_files": changed_files,
            "context_json": s3_json_uri,
            "context_txt": s3_txt_uri,
            "llm_context": llm_context,
            "progress_comment_id": progress_comment_id
        }

    except Exception as e:
        print(f"[Worker] Error: {e}")
        return {"error": str(e)}

    finally:
        shutil.rmtree(temp_dir)