import os

from .parser_utils import  extract_imports_with_tree_sitter, resolve_import_path, LANGUAGE_MAP


def write_pr_txt(pr_data, parsed_files, changed_files, temp_dir, output_dir="results",file_name=None):
    """
    Create a text file for the PR containing:
    1. Git diff for changed files
    2. Full source code of changed + imported files
    """
    pr_number = pr_data["pr_number"]
    txt_path = file_name or os.path.join(output_dir, f"pr_{pr_number}_context.txt")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"PR #{pr_number} - Repo: {pr_data.get('repo_name', '')}\n")
        f.write(f"Base branch: {pr_data['base_branch']}, Head branch: {pr_data['head_branch']}\n\n")

        f.write("=== GIT DIFFS ===\n")
        for file in changed_files:
            diff_path = os.path.join(temp_dir, file)
            if os.path.exists(diff_path):
                import subprocess
                try:
                    diff_text = subprocess.check_output(
                        ["git", "diff", f"{pr_data['base_branch']}", f"{pr_data['head_branch']}", "--", file],
                        cwd=temp_dir,
                        text=True
                    )
                    f.write(f"\n--- {file} ---\n")
                    f.write(diff_text)
                except Exception as e:
                    f.write(f"\n--- {file} ---\nError generating diff: {e}\n")

        f.write("\n=== FULL FILES (Changed + Imported) ===\n")
        included_files = set(changed_files)
        for file in changed_files:
            ext = os.path.splitext(file)[1]
            lang = LANGUAGE_MAP.get(ext)
            if lang:
                imports = extract_imports_with_tree_sitter(os.path.join(temp_dir, file), lang)
                for imp in imports:
                    resolved_path = resolve_import_path(imp, file, temp_dir, lang)
                    if resolved_path:
                        included_files.add(resolved_path)

        for file in included_files:
            abs_path = os.path.join(temp_dir, file)
            if os.path.exists(abs_path):
                f.write(f"\n--- {file} ---\n")
                with open(abs_path, "r", encoding="utf-8") as code_file:
                    f.write(code_file.read())

    return txt_path