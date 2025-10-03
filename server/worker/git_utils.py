import subprocess

def clone_and_checkout(repo_url, temp_dir, branch):
    subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
    subprocess.run(["git", "fetch", "origin", branch], cwd=temp_dir, check=True)
    subprocess.run(["git", "checkout", branch], cwd=temp_dir, check=True)

def get_changed_files(temp_dir, base_branch, head_branch):
    diff_cmd = ["git", "diff", "--name-only", f"origin/{base_branch}...origin/{head_branch}"]
    result = subprocess.run(diff_cmd, cwd=temp_dir, capture_output=True, text=True)
    return result.stdout.splitlines()

def get_actual_diff(temp_dir, base_branch, head_branch, file_path):
    cmd = ["git", "diff", f"origin/{base_branch}...origin/{head_branch}", "--", file_path]
    result = subprocess.run(cmd, cwd=temp_dir, capture_output=True, text=True)
    return result.stdout
