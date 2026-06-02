from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class SearchResult(BaseModel):
    query: str
    results: List[Dict[str, Any]] = Field(default_factory=list)


class ScrapeResult(BaseModel):
    url: str
    title: str
    content: str
    word_count: int


class SummaryResult(BaseModel):
    original_length: int
    summary: str
    key_points: List[str] = Field(default_factory=list)


class FileReadResult(BaseModel):
    path: str
    content: str
    size_bytes: int


class FileWriteResult(BaseModel):
    path: str
    success: bool
    message: str


class ResearchReport(BaseModel):
    title: str
    query: str
    summary: str
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    word_count: int
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ToolError(BaseModel):
    tool_name: str
    error_type: str
    message: str
    retry_after: Optional[int] = None
