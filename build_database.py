import pathlib
import re
import sqlite_utils
import markdown

root = pathlib.Path(__file__).parent.resolve()

DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")


def parse_post(filepath, root):
    """Read a markdown file and return a post dict."""
    with open(filepath, "r", encoding="utf-8") as f:
        title = f.readline().lstrip("#").strip()
        body = f.read().strip()

    path = str(filepath.relative_to(root))
    topic = filepath.parent.name

    # Strip date prefix from filename to get the base slug
    stem = filepath.stem
    date_match = DATE_PREFIX_RE.match(stem)
    if date_match:
        date = date_match.group(0).rstrip("-")  # e.g. "2025-01-15"
        base_slug = stem[date_match.end():]      # e.g. "my-first-post"
    else:
        date = ""
        base_slug = stem

    slug = f"{topic}-{base_slug}" if topic else base_slug
    url = f"https://github.com/edeo/my-blog/blob/main/{path}"
    html = markdown.markdown(body)

    return {
        "path": path,
        "slug": slug,
        "topic": topic,
        "title": title,
        "date": date,
        "url": url,
        "body": body,
        "html": html,
    }


def build_database(root):
    db = sqlite_utils.Database(root / "blog.db")
    table = db.table("posts", pk="path")

    # Sort files for deterministic build order
    md_files = sorted(root.glob("*/*.md"))

    posts = [parse_post(fp, root) for fp in md_files]

    if posts:
        table.insert_all(posts, replace=True)

    print(f"Built blog.db with {len(posts)} posts")


if __name__ == "__main__":
    build_database(root)