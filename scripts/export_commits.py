import os
import subprocess
import sys


def get_commit_hashes(count):
    """Retrieves the last N commit hashes."""
    try:
        cmd = ["git", "log", f"-n{count}", "--pretty=format:%H"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error fetching commit hashes: {e}")
        return []


def get_commit_details(commit_hash):
    """Retrieves metadata and diff for a specific commit."""
    try:
        # --stat adds a summary of files changed, --patch adds the diff
        # --unified=3 ensures 3 lines of context around changes
        # Exclude large raw text datasets and existing export files to keep file size reasonable
        cmd = [
            "git", "show", "--stat", "--patch", "--unified=3", commit_hash,
            "--", ":(exclude)rag/jyotish_rag_data/*", ":(exclude)commits_export.md"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error fetching details for commit {commit_hash}: {e}"


def export_commits(count, output_file="commits_export.md"):
    """Generates a Markdown report of recent commits."""
    hashes = get_commit_hashes(count)
    if not hashes:
        print("No commits found to export.")
        return

    # Use the project root for the output file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(script_dir) == "scripts":
        project_root = os.path.dirname(script_dir)
    else:
        project_root = script_dir

    output_path = os.path.join(project_root, output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Git Commit Export\n")
        f.write(f"Generated on: {subprocess.check_output(['date']).decode().strip()}\n")
        f.write(f"Number of commits requested: {count}\n\n")
        f.write("-" * 80 + "\n\n")

        for i, h in enumerate(hashes):
            details = get_commit_details(h)
            f.write(f"## Commit {i + 1}: {h[:7]}\n\n")
            f.write("```diff\n")
            f.write(details)
            f.write("\n```\n\n")
            f.write("-" * 80 + "\n\n")

    print(f"Successfully exported {len(hashes)} commits to: {output_path}")


def main():
    print("--- Commit Export Tool ---")

    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print("Invalid argument. Usage: python export_commits.py [number]")
            sys.exit(1)
    else:
        try:
            val = input("How many recent commits would you like to export? (Default 5): ").strip()
            n = int(val) if val else 5
        except (ValueError, EOFError):
            n = 5

    export_commits(n)


if __name__ == "__main__":
    main()
