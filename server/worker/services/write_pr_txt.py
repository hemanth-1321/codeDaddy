import os

from .parser_utils import  extract_imports_with_tree_sitter, resolve_import_path, LANGUAGE_MAP




def write_pr_txt(pr_data, parsed_files, changed_files, temp_dir, output_dir="results", file_name=None):
    """
    Create a text file for the PR containing:
    1. Git diff for changed files
    2. Full source code of changed + imported files
    (safe for all encodings + binary protection)
    """
    pr_number = pr_data["pr_number"]
    txt_path = file_name or os.path.join(output_dir, f"pr_{pr_number}_context.txt")

    def is_binary(raw_bytes: bytes) -> bool:
        """Detect if a file is binary based on null bytes."""
        return b"\x00" in raw_bytes

    with open(txt_path, "w", encoding="utf-8") as f:
        # Header
        f.write(f"PR #{pr_number} - Repo: {pr_data.get('repo_name', '')}\n")
        f.write(f"Base branch: {pr_data['base_branch']}, Head branch: {pr_data['head_branch']}\n\n")

        # -------------------------------
        # SECTION 1: GIT DIFFS
        # -------------------------------
        f.write("=== GIT DIFFS ===\n")

        import subprocess

        for file in changed_files:
            diff_path = os.path.join(temp_dir, file)
            if os.path.exists(diff_path):
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

        # -------------------------------
        # SECTION 2: FULL FILES
        # -------------------------------

        f.write("\n=== FULL FILES (Changed + Imported) ===\n")

        included_files = set(changed_files)

        # Find imported files
        for file in changed_files:
            ext = os.path.splitext(file)[1]
            lang = LANGUAGE_MAP.get(ext)

            if lang:
                imports = extract_imports_with_tree_sitter(os.path.join(temp_dir, file), lang)
                for imp in imports:
                    resolved_path = resolve_import_path(imp, file, temp_dir, lang)
                    if resolved_path:
                        included_files.add(resolved_path)

        # Write file contents safely
        for file in included_files:
            abs_path = os.path.join(temp_dir, file)
            if not os.path.exists(abs_path):
                continue

            f.write(f"\n--- {file} ---\n")

            # Always open as raw bytes
            try:
                with open(abs_path, "rb") as code_file:
                    raw = code_file.read()
            except Exception as e:
                f.write(f"[Error reading file: {e}]\n")
                continue

            # Detect binary files — skip
            if is_binary(raw):
                f.write("[Skipped binary file: contains non-text data]\n")
                continue

            # Safe decoding with fallback
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = raw.decode("latin-1", errors="ignore")

            f.write(text)

    return txt_path
