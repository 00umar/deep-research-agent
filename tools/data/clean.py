import re
from bs4 import BeautifulSoup


def text_clean(text: str) -> dict:
    """Remove HTML tags, extra whitespace, and junk characters from text."""
    try:
        soup = BeautifulSoup(text, "html.parser")
        cleaned = soup.get_text(separator=" ")
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'[^\x20-\x7E\n]', '', cleaned)
        cleaned = cleaned.strip()
        return {
            "original_length": len(text),
            "cleaned_length": len(cleaned),
            "text": cleaned
        }
    except Exception as e:
        return {"error": type(e).__name__, "message": str(e)}


text_clean_declaration = {
    "type": "function",
    "function": {
        "name": "text_clean",
        "description": "Clean scraped text by stripping HTML tags, extra whitespace, and non-printable characters. Use before processing raw scraped content.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The raw text to clean"}
            },
            "required": ["text"]
        }
    }
}
