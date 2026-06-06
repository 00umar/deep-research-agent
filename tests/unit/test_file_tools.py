"""Unit tests for tools/file/writer.py and tools/file/reader.py — filesystem only, no API calls."""
import os
import pytest
from tools.file.writer import file_write
from tools.file.reader import file_read


@pytest.fixture
def tmp_path_str(tmp_path):
    """Return a string path inside pytest's tmp_path for file tool compatibility."""
    return str(tmp_path / "test_output.txt")


class TestFileWrite:
    def test_writes_content_to_file(self, tmp_path_str):
        result = file_write(tmp_path_str, "Hello, world!")
        assert result["success"] is True
        with open(tmp_path_str, encoding="utf-8") as f:
            assert f.read() == "Hello, world!"

    def test_returns_success_true_on_write(self, tmp_path_str):
        result = file_write(tmp_path_str, "some content")
        assert result["success"] is True
        assert tmp_path_str in result["path"] or result["path"] == tmp_path_str

    def test_creates_nested_directories(self, tmp_path):
        nested = str(tmp_path / "a" / "b" / "report.md")
        result = file_write(nested, "# Report")
        assert result["success"] is True
        assert os.path.exists(nested)

    def test_append_mode_adds_to_existing_content(self, tmp_path_str):
        file_write(tmp_path_str, "line 1\n")
        file_write(tmp_path_str, "line 2\n", mode="a")
        with open(tmp_path_str, encoding="utf-8") as f:
            content = f.read()
        assert "line 1" in content
        assert "line 2" in content

    def test_overwrite_mode_replaces_content(self, tmp_path_str):
        file_write(tmp_path_str, "original")
        file_write(tmp_path_str, "replaced")
        with open(tmp_path_str, encoding="utf-8") as f:
            assert f.read() == "replaced"

    def test_message_reports_character_count(self, tmp_path_str):
        result = file_write(tmp_path_str, "abc")
        assert "3" in result["message"]


class TestFileRead:
    def test_reads_written_content(self, tmp_path_str):
        file_write(tmp_path_str, "# Due Diligence Report\nSome content.")
        result = file_read(tmp_path_str)
        assert "Due Diligence Report" in result["content"]
        assert result["size_bytes"] > 0

    def test_nonexistent_file_returns_error(self, tmp_path):
        result = file_read(str(tmp_path / "does_not_exist.txt"))
        assert "error" in result

    def test_result_has_required_keys(self, tmp_path_str):
        file_write(tmp_path_str, "data")
        result = file_read(tmp_path_str)
        for key in ("path", "content", "size_bytes"):
            assert key in result
