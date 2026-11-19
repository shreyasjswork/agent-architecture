"""Read a Git range and verify a local release receipt."""
import argparse
import fnmatch
import json
import re
import subprocess
from pathlib import Path


def verify_receipt(receipt, changed_paths):
    scope = receipt.get("scope")
    checks = receipt.get("checks")
    review = receipt.get("review")
    author = receipt.get("author")
    if not isinstance(scope, list) or not scope or not all(
        isinstance(pattern, str) and pattern and not pattern.startswith("/")
        for pattern in scope
    ):
        raise ValueError("Provide repository-relative scope patterns")
    if not isinstance(checks, dict) or not checks or any(value is not True for value in checks.values()):
        raise ValueError("All recorded checks must have passed")
    if not isinstance(review, dict) or review.get("accepted") is not True:
        raise ValueError("The release requires a recorded independent review")
    reviewer = review.get("reviewer")
    if not isinstance(author, str) or not author.strip() or not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("Record the author and reviewer identities")
    if author.strip().casefold() == reviewer.strip().casefold():
        raise ValueError("The reviewer must be independent of the author")
    if review.get("candidate") != receipt.get("candidate"):
        raise ValueError("The review must cover the exact candidate")
    outside = [
        path for path in changed_paths
        if not any(fnmatch.fnmatchcase(path, pattern) for pattern in scope)
    ]
    if outside:
        raise ValueError("Out-of-scope paths: " + ", ".join(sorted(outside)))


def changed_files(repo, base, candidate):
    if not all(isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha) for sha in (base, candidate)):
        raise ValueError("Use full lowercase Git commit hashes")
    if base == candidate:
        raise ValueError("The base and candidate must be different commits")
    if subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, candidate],
        cwd=repo, check=False,
    ).returncode != 0:
        raise ValueError("The base must be an ancestor of the candidate")
    result = subprocess.run(
        ["git", "diff", "--name-only", "-z", "--no-renames", base, candidate, "--"],
        cwd=repo, check=True, stdout=subprocess.PIPE,
    )
    return [path.decode("utf-8") for path in result.stdout.split(b"\0") if path]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        if not isinstance(receipt, dict):
            raise ValueError("The receipt must be a JSON object")
        paths = changed_files(args.repo, receipt.get("base"), receipt.get("candidate"))
        verify_receipt(receipt, paths)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + "\n")
    print(f"Verified {len(paths)} changed paths for {receipt['candidate']}")


if __name__ == "__main__":
    main()
