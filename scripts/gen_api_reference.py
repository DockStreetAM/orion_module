"""Generate docs/API_REFERENCE.md from the orionapi class docstrings + signatures.

Dependency-free. Run: poetry run python scripts/gen_api_reference.py
"""

import inspect
import re

import orionapi

CLASSES = ["OrionAPI", "EclipseV1", "EclipseV2", "Eclipse"]


def endpoint_for(func):
    """Best-effort: pull the API path + HTTP verb from the method body."""
    try:
        body = inspect.getsource(func)
    except OSError:
        return ""
    body = re.sub(r'"\s*\n\s*f?"', "", body)  # join split f-strings
    m = re.search(r'base_url(_v2)?\}([^"\']+)', body)
    if not m:
        return ""
    path = ("/api/v2" if m.group(1) else "") + m.group(2).split("?")[0]
    verb = "GET"
    if "requests.post" in body:
        verb = "POST"
    elif "requests.put" in body:
        verb = "PUT"
    elif "requests.delete" in body:
        verb = "DELETE"
    elif "requests.patch" in body:
        verb = "PATCH"
    return f"`{verb} {path}`"


def summary(func):
    doc = inspect.getdoc(func) or ""
    return doc.split("\n", 1)[0].strip()


def public_methods(cls):
    out = []
    for name, fn in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        if fn.__qualname__.split(".")[0] != cls.__name__:
            continue  # only methods defined on this class, not inherited
        out.append((name, fn))
    return sorted(out)


def main():
    lines = [
        f"# orionapi API Reference (v{orionapi.__version__})",
        "",
        "Auto-generated from docstrings by `scripts/gen_api_reference.py`. "
        "Eclipse methods note their underlying endpoint.",
        "",
        "Classes: `OrionAPI` (Orion Advisor), `EclipseV1` / `EclipseV2` "
        "(explicit Eclipse surfaces), `Eclipse` (best-of-both unifier). "
        "Response TypedDicts live in `orionapi.models`.",
        "",
    ]
    for cname in CLASSES:
        cls = getattr(orionapi, cname)
        methods = public_methods(cls)
        lines.append(f"## {cname}")
        lines.append("")
        doc = (inspect.getdoc(cls) or "").split("\n\n")[0].replace("\n", " ")
        lines.append(f"{doc}")
        lines.append("")
        lines.append(f"**{len(methods)} methods.**")
        lines.append("")
        lines.append("| Method | Endpoint | Description |")
        lines.append("|---|---|---|")
        for name, fn in methods:
            try:
                sig = str(inspect.signature(fn)).replace("self, ", "").replace("self", "")
            except (ValueError, TypeError):
                sig = "(...)"
            ep = endpoint_for(fn)
            desc = summary(fn).replace("|", "\\|")
            lines.append(f"| `{name}{sig}` | {ep} | {desc} |")
        lines.append("")
    out = "\n".join(lines)
    with open("docs/API_REFERENCE.md", "w") as f:
        f.write(out)
    total = sum(len(public_methods(getattr(orionapi, c))) for c in CLASSES)
    print(f"Wrote docs/API_REFERENCE.md — {total} methods across {len(CLASSES)} classes")


if __name__ == "__main__":
    main()
