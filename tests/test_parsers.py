from app.ingestion.parsers import parse_file


def test_markdown_parser_preserves_sections(tmp_path):
    path = tmp_path / "handbook.md"
    path.write_text(
        "# Operations\nRunbooks are required.\n"
        "## Security\nUse least privilege.\n",
        encoding="utf-8",
    )

    sections = parse_file(path)

    assert [section.section for section in sections] == ["Operations", "Security"]
    assert sections[0].content_type == "text/markdown"
    assert "Runbooks are required" in sections[0].text
    assert "Use least privilege" in sections[1].text


def test_plain_text_parser_sets_content_type(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("hello", encoding="utf-8")

    sections = parse_file(path)

    assert len(sections) == 1
    assert sections[0].content_type == "text/plain"
