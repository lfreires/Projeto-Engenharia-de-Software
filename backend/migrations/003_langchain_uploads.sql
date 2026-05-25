DELETE FROM materials WHERE id = 'mat-architecture';

DROP TABLE IF EXISTS document_chunks;

ALTER TABLE documents ADD COLUMN IF NOT EXISTS content_type TEXT NOT NULL DEFAULT 'text/plain';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS error_message TEXT;

ALTER TABLE documents DROP CONSTRAINT IF EXISTS documents_status_check;
ALTER TABLE documents
    ADD CONSTRAINT documents_status_check
    CHECK (status IN ('processing', 'indexed', 'failed'));
