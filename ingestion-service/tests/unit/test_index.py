from app.index import chunk_text, index_document, reset_index, search_chunks


def setup_function():
    reset_index()


def test_chunk_text_splits_content_by_word_limit():
    chunks = chunk_text("one two three four five", max_words=2)

    assert chunks == ["one two", "three four", "five"]


def test_index_document_stores_chunk_metadata():
    document = index_document(
        project_id="proj-demo",
        material_id="mat-1",
        file_name="notes.md",
        content="DocAI indexes chunks for retrieval.",
    )

    assert document.status == "indexed"
    assert document.chunk_count == 1


def test_search_chunks_returns_ranked_project_matches():
    index_document(
        project_id="proj-demo",
        material_id="mat-1",
        file_name="notes.md",
        content="identity project ingestion query",
    )
    index_document(
        project_id="other",
        material_id="mat-2",
        file_name="private.md",
        content="identity project ingestion query",
    )

    results = search_chunks(project_id="proj-demo", query="query ingestion", top_k=5)

    assert len(results) == 1
    assert results[0].project_id == "proj-demo"
    assert results[0].score == 2
