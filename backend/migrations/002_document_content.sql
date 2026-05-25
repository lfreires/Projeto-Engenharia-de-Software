ALTER TABLE documents ADD COLUMN IF NOT EXISTS content TEXT;

UPDATE documents d
SET content = source.content
FROM (
    SELECT document_id, string_agg(chunk_text, E'\n\n' ORDER BY chunk_index) AS content
    FROM document_chunks
    GROUP BY document_id
) source
WHERE d.id = source.document_id AND d.content IS NULL;
