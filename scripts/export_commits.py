import os
import subprocess
import sys


def get_commit_hashes(count: int) -> list[str]:
    """Retrieves the most recent N commit hashes from Git."""
    try:
        cmd = ["git", "log", f"-n{count}", "--pretty=format:%H"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error fetching commit hashes: {e}")
        return []


def get_commit_details(commit_hash: str, max_lines_per_diff: int = 300) -> str:
    """
    Retrieves metadata and code diff for a specific commit.
    Filters out heavy non-code paths (e.g. source-material/) and caps large diffs.
    """
    try:
        # Exclude non-code/data directories from diff inspection to keep context lean
        cmd = [
            "git",
            "show",
            "--stat",
            "--patch",
            "--unified=3",
            commit_hash,
            "--",
            ".",
            ":(exclude)source-material/*",
            ":(exclude)*.db",
            ":(exclude)*.sqlite",
            ":(exclude)*.jsonl",
            ":(exclude)*.bin",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()

        if len(lines) > max_lines_per_diff:
            truncated = lines[:max_lines_per_diff]
            truncated.append(
                f"\n[... Diff truncated: showing first {max_lines_per_diff} lines of {len(lines)} total lines ...]"
            )
            return "\n".join(truncated)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error fetching details for commit {commit_hash}: {e}"


def export_commits(
    count: int = 5, output_file: str = "commits_export.txt", max_lines_per_diff: int = 300
) -> None:
    """Generates a text/markdown file export of recent commits."""
    hashes = get_commit_hashes(count)
    if not hashes:
        print("No commits found to export.")
        return

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(project_root, output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Git Commit Export\n")
        f.write(f"Number of commits requested: {count}\n\n")
        f.write("=" * 80 + "\n\n")

        for i, h in enumerate(hashes, 1):
            details = get_commit_details(h, max_lines_per_diff=max_lines_per_diff)
            f.write(f"## Commit {i}: {h[:7]} ({h})\n\n")
            f.write("```diff\n")
            f.write(details)
            f.write("\n```\n\n")
            f.write("=" * 80 + "\n\n")

    print(f"Successfully exported {len(hashes)} commit(s) to: {output_path}")


def main():
    print("--- Git Commit Export Tool ---")

    count = 5
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Invalid number provided. Usage: python scripts/export_commits.py [number_of_commits]")
            sys.exit(1)
    else:
        try:
            val = input("How many recent commits would you like to export? (Default 5): ").strip()
            if val:
                count = int(val)
        except (ValueError, EOFError):
            count = 5

    export_commits(count)


if __name__ == "__main__":
    main()
