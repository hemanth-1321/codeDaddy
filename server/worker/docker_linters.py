import subprocess

def run_docker_linter(image, workdir, cmd):
    """
    Run a command inside Docker and return combined stdout+stderr.
    """
    docker_cmd = [
        "docker", "run", "--rm",
        "-v", f"{workdir}:/app",
        "-w", "/app",
        image
    ] + cmd

    result = subprocess.run(docker_cmd, text=True, capture_output=True)
    combined = "\n".join(filter(None, [result.stdout.strip(), result.stderr.strip()]))
    return combined if combined else None


def lint_python(files, workdir, image="python:3.11"):
    if not files:
        return None
    cmd = ["bash", "-c", "pip install flake8 >/dev/null && flake8 " + " ".join(files)]
    return run_docker_linter(image, workdir, cmd)


def lint_js(files, workdir, image="node:18"):
    if not files:
        return None
    cmd = ["bash", "-c", "npm install -g eslint >/dev/null && eslint " + " ".join(files) + " -f unix"]
    return run_docker_linter(image, workdir, cmd)


def lint_markdown(files, workdir, image="node:18"):
    if not files:
        return None
    cmd = ["bash", "-c", "npm install -g markdownlint-cli2 >/dev/null && markdownlint-cli2 " + " ".join(files)]
    return run_docker_linter(image, workdir, cmd)
