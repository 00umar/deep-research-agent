import os


def file_exists(path: str) -> dict:
    """Check if a file exists."""
    exists = os.path.exists(path)
    return {
        "path": path,
        "exists": exists,
        "size_bytes": os.path.getsize(path) if exists else None
    }


file_exists_declaration = {
    "type": "function",
    "function": {
        "name": "file_exists",
        "description": "Check if a file already exists before trying to read or write it. Use to avoid overwriting existing work.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The file path to check"}
            },
            "required": ["path"]
        }
    }
}
