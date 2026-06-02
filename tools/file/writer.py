import os
from models.schemas import FileWriteResult
from google.genai import types


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


file_write_declaration = types.FunctionDeclaration(
    name="file_write",
    description="Write content to a local file. Use to save research notes, intermediate findings, or final reports.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "path": types.Schema(type=types.Type.STRING, description="File path to write to"),
            "content": types.Schema(type=types.Type.STRING, description="Content to write"),
            "mode": types.Schema(type=types.Type.STRING, description="'w' to overwrite, 'a' to append (default: 'w')")
        },
        required=["path", "content"]
    )
)
