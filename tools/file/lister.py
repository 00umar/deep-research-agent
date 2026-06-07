import os


def file_list(directory: str = "outputs", **_kwargs) -> dict:
    """List all files in a directory."""
    try:
        if not os.path.exists(directory):
            return {"directory": directory, "files": [], "count": 0, "message": "Directory does not exist"}
        files = []
        for name in sorted(os.listdir(directory)):
            full_path = os.path.join(directory, name)
            if os.path.isfile(full_path):
                files.append({
                    "name": name,
                    "path": full_path,
                    "size_bytes": os.path.getsize(full_path)
                })
        return {"directory": directory, "files": files, "count": len(files)}
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


file_list_declaration = {
    "type": "function",
    "function": {
        "name": "file_list",
        "description": "List all files in a directory. Use to check what research notes and reports have already been saved before starting new work.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "Directory path to list (default: 'outputs')"}
            }
        }
    }
}
