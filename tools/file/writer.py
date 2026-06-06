import os
from models.schemas import FileWriteResult


def file_write(path: str, content: str, mode: str = "w") -> dict:
    """Write content to a local file."""
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, mode, encoding="utf-8") as f:
            f.write(content)
        return FileWriteResult(
            path=path,
            success=True,
            message=f"Wrote {len(content)} characters to {path}"
        ).model_dump()
    except Exception as e:
        return FileWriteResult(path=path, success=False, message=str(e)).model_dump()


file_write_declaration = {
    "type": "function",
    "function": {
        "name": "file_write",
        "description": "Write content to a local file. Use to save research notes, intermediate findings, or final reports.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to write to"},
                "content": {"type": "string", "description": "Content to write"},
                "mode": {"type": "string", "description": "'w' to overwrite, 'a' to append (default: 'w')"}
            },
            "required": ["path", "content"]
        }
    }
}
