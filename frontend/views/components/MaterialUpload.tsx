import React from "react";
import { AlertCircle, FileUp, LoaderCircle } from "lucide-react";
import architectureDocument from "@/documents/arquitetura-original.md?raw";

const MAX_SIZE = 10 * 1024 * 1024;
const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".txt", ".md"];

interface MaterialUploadProps {
  onUpload: (file: File) => Promise<void>;
}

export function MaterialUpload({ onUpload }: MaterialUploadProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const [file, setFile] = React.useState<File | null>(null);
  const [dragging, setDragging] = React.useState(false);
  const [submitting, setSubmitting] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  function choose(candidate: File | undefined) {
    if (!candidate) return;
    const extension = `.${candidate.name.split(".").pop()?.toLowerCase() ?? ""}`;
    if (!ACCEPTED_EXTENSIONS.includes(extension)) {
      setError("Formato invalido. Use PDF, DOCX, TXT ou MD.");
      setFile(null);
      return;
    }
    if (candidate.size > MAX_SIZE) {
      setError("O arquivo excede o limite de 10 MB.");
      setFile(null);
      return;
    }
    setFile(candidate);
    setError(null);
  }

  async function upload(candidate: File) {
    if (submitting) return;
    setSubmitting(true);
    setError(null);
    try {
      await onUpload(candidate);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Falha ao indexar documento.");
      setSubmitting(false);
    }
  }

  async function submit() {
    if (!file) return;
    await upload(file);
  }

  async function submitArchitectureDocument() {
    const document = new File([architectureDocument], "arquitetura-original.md", {
      type: "text/markdown",
    });
    setFile(null);
    await upload(document);
  }

  return (
    <div className="px-4 pt-3 pb-3" style={{ borderBottom: "0.5px solid #f0f1f8" }}>
      <div
        role="button"
        tabIndex={0}
        onClick={() => inputRef.current?.click()}
        onKeyDown={(event) => event.key === "Enter" && inputRef.current?.click()}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          choose(event.dataTransfer.files[0]);
        }}
        style={{
          cursor: "pointer",
          borderRadius: "8px",
          border: `1px dashed ${dragging ? "#6366f1" : "#c7d2fe"}`,
          backgroundColor: dragging ? "#eef2ff" : "#f8f9ff",
          padding: "12px",
          textAlign: "center",
        }}
      >
        <FileUp size={18} style={{ color: "#4f46e5", margin: "0 auto 5px" }} />
        <p style={{ margin: 0, color: "#303449", fontSize: "12px", fontWeight: 500 }}>
          Enviar documento
        </p>
        <p style={{ margin: "3px 0 0", color: "#7c80a0", fontSize: "10.5px" }}>
          PDF, DOCX, TXT ou MD ate 10 MB
        </p>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          hidden
          onChange={(event) => choose(event.target.files?.[0])}
        />
      </div>

      <button
        type="button"
        disabled={submitting}
        onClick={submitArchitectureDocument}
        className="w-full mt-2"
        style={{
          backgroundColor: "#eef2ff",
          border: "0.5px solid #c7d2fe",
          borderRadius: "6px",
          color: "#4338ca",
          cursor: submitting ? "wait" : "pointer",
          fontSize: "11px",
          fontWeight: 500,
          padding: "6px 8px",
        }}
      >
        {submitting ? "Indexando..." : "Indexar arquitetura original do DocAI"}
      </button>

      {file && (
        <div className="flex items-center gap-2 mt-2">
          <span
            className="flex-1 truncate"
            style={{ color: "#303449", fontSize: "11px" }}
            title={file.name}
          >
            {file.name}
          </span>
          <button
            type="button"
            disabled={submitting}
            onClick={submit}
            style={{
              alignItems: "center",
              backgroundColor: "#4f46e5",
              border: "none",
              borderRadius: "6px",
              color: "white",
              cursor: submitting ? "wait" : "pointer",
              display: "flex",
              fontSize: "11px",
              gap: "4px",
              padding: "5px 9px",
            }}
          >
            {submitting && <LoaderCircle size={11} />}
            {submitting ? "Indexando..." : "Indexar"}
          </button>
        </div>
      )}
      {error && (
        <p className="flex items-center gap-1 mt-2" style={{ color: "#b91c1c", fontSize: "11px" }}>
          <AlertCircle size={12} />
          {error}
        </p>
      )}
    </div>
  );
}
