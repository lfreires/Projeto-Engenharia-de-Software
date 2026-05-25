import React from "react";
import { ArrowLeft, FileText, LoaderCircle } from "lucide-react";
import { ProjectMaterial } from "@/models/project";
import { fetchDocumentContent } from "@/services/projectService";

interface MaterialViewerProps {
  material: ProjectMaterial;
  onBack: () => void;
}

export function MaterialViewer({ material, onBack }: MaterialViewerProps) {
  const [content, setContent] = React.useState("");
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    fetchDocumentContent(material.documentId)
      .then((documentContent) => {
        if (!active) return;
        setContent(documentContent);
        setLoading(false);
      })
      .catch((reason: Error) => {
        if (!active) return;
        setError(reason.message);
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [material.documentId]);

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="px-4 py-3" style={{ borderBottom: "0.5px solid #f0f1f8" }}>
        <button
          onClick={onBack}
          className="flex items-center gap-1.5"
          style={{
            background: "none",
            border: "none",
            padding: 0,
            color: "#4f46e5",
            cursor: "pointer",
            fontSize: "12px",
            fontWeight: 500,
          }}
        >
          <ArrowLeft size={13} />
          Voltar aos materiais
        </button>
        <div className="flex items-center gap-2 mt-3">
          <FileText size={15} style={{ color: "#2563eb" }} />
          <span style={{ fontSize: "12.5px", fontWeight: 600, color: "#1e2035" }}>
            {material.filename}
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-3">
        {loading && (
          <div className="flex items-center gap-2" style={{ fontSize: "12px", color: "#7c80a0" }}>
            <LoaderCircle size={13} />
            Carregando documento...
          </div>
        )}
        {error && (
          <p style={{ fontSize: "12px", color: "#991b1b", lineHeight: "1.5", margin: 0 }}>
            Nao foi possivel abrir o documento: {error}
          </p>
        )}
        {!loading && !error && (
          <pre
            style={{
              whiteSpace: "pre-wrap",
              wordBreak: "break-word",
              fontFamily: "'Inter', system-ui, sans-serif",
              fontSize: "12px",
              color: "#303449",
              lineHeight: "1.65",
              margin: 0,
            }}
          >
            {content}
          </pre>
        )}
      </div>
    </div>
  );
}
