import os
from models.schemas import FileReadResult
from google.genai import types


def file_read(path: str) -> dict:
    """Read the contents of a local file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return FileReadResult(
            path=path,
            content=content,
            size_bytes=os.path.getsize(path)
        ).model_dump()
    except FileNotFoundError:
        return {"error": "FileNotFoundError", "message": f"File not found: {path}"}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


file_read_declaration = types.FunctionDeclaration(
    name="file_read",
    description="Read the contents of a local file. Use to retrieve previously saved notes or reports.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "path": types.Schema(type=types.Type.STRING, description="File path to read")
        },
        required=["path"]
    )
)
