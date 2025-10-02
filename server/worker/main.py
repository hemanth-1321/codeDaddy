import subprocess
import tempfile
import os
import shutil

def run_docker_linter(image, workdir, cmd):
    """Run a command inside Docker and return stdout/stderr."""
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{workdir}:/app",
        "-w", "/app",
        image
    ] + cmd
    result = subprocess.run(docker_cmd, text=True, capture_output=True)
    return result.stdout.strip(), result.stderr.strip()


def process_pr(pr_data):
    repo_url = pr_data["clone_url"]
    pr_number = pr_data["pr_number"]
    base_branch = pr_data["base_branch"]
    head_branch = pr_data["head_branch"]

    print(f"[Worker] Reviewing PR #{pr_number} from {pr_data['repo_name']}")

    temp_dir = tempfile.mkdtemp()
    findings = []

    try:
        # Clone repo
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
        os.chdir(temp_dir)

        # Checkout PR branch
        subprocess.run(["git", "fetch", "origin", head_branch], check=True)
        subprocess.run(["git", "checkout", head_branch], check=True)

        # Find changed files
        diff_cmd = ["git", "diff", "--name-only", f"origin/{base_branch}...origin/{head_branch}"]
        changed_files = subprocess.run(diff_cmd, capture_output=True, text=True).stdout.splitlines()
        print(f"[Worker] Changed files: {changed_files}")

        # Python files
        py_files = [f for f in changed_files if f.endswith(".py")]
        if py_files:
            out, err = run_docker_linter(
                "pr-linter:latest",
                temp_dir,
                ["bash", "-c", "flake8 " + " ".join(py_files)]
            )
            if out:
                findings.append("Flake8:\n" + "\n".join([line for line in out.splitlines()]))

        # JS/TS files
        js_files = [f for f in changed_files if f.endswith((".js", ".jsx", ".ts", ".tsx"))]
        if js_files:
            out, err = run_docker_linter(
                "pr-linter:latest",
                temp_dir,
                ["bash", "-c", "eslint " + " ".join(js_files) + " -f unix"]
            )
            if out:
                findings.append("ESLint:\n" + "\n".join([line for line in out.splitlines()]))

        # Markdown files
        md_files = [f for f in changed_files if f.endswith(".md")]
        if md_files:
            out, err = run_docker_linter(
                "pr-linter:latest",
                temp_dir,
                ["bash", "-c", "markdownlint-cli2 " + " ".join(md_files)]
            )
            if out:
                findings.append("Markdownlint:\n" + "\n".join([line for line in out.splitlines()]))

        # Print findings or success
        if findings:
            print(f"[Worker] Findings:\n" + "\n\n".join(findings))
        else:
            print("[Worker] No issues found ✅")

    except subprocess.CalledProcessError as e:
        print(f"[Worker] Error: {e}")
    finally:
        shutil.rmtree(temp_dir)
