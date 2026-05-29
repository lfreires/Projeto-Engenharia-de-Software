import React from "react";
import { useMaterials } from "@/hooks/useMaterials";
import { fetchProject, PROJECT_ID } from "@/services/projectService";
import { ChatArea } from "@/views/components/ChatArea";
import { ProjectMaterialsPanel } from "@/views/components/ProjectMaterialsPanel";
import { DocAISidebar } from "@/views/layouts/DocAISidebar";

function ConnectionBanner({ message }: { message: string }) {
  return (
    <div
      className="px-4 py-2"
      style={{
        backgroundColor: "rgba(239, 68, 68, 0.12)",
        borderBottom: "1px solid rgba(239, 68, 68, 0.35)",
        color: "#fca5a5",
        fontSize: "13px",
        fontWeight: 500,
      }}
    >
      Falha de conexao com o backend: {message}
    </div>
  );
}

export default function App() {
  const {
    showPanel,
    materials,
    selectedMaterial,
    togglePanel,
    closePanel,
    selectMaterial,
    clearSelection,
    uploadMaterial,
    deleteMaterial,
    connectionError: materialsError,
  } = useMaterials();
  const [projectName, setProjectName] = React.useState(PROJECT_ID);
  const [projectError, setProjectError] = React.useState<string | null>(null);
  const [chatError, setChatError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let active = true;
    fetchProject()
      .then((project) => {
        if (!active) return;
        setProjectName(project.name);
        setProjectError(null);
      })
      .catch((error: Error) => {
        if (!active) return;
        setProjectError(error.message);
      });
    return () => {
      active = false;
    };
  }, []);

  const connectionError = projectError ?? materialsError ?? chatError;

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{
        fontFamily: "'Inter', system-ui, -apple-system, sans-serif",
        backgroundColor: "#0b0d12",
        color: "#e6e8ee",
      }}
    >
      <DocAISidebar />

      <div className="flex flex-col flex-1 min-w-0">
        {connectionError && <ConnectionBanner message={connectionError} />}
        <div className="flex flex-1 min-h-0 min-w-0">
          <ChatArea
            materialsCount={materials.length}
            projectName={projectName}
            showMaterials={showPanel}
            onToggleMaterials={togglePanel}
            onConnectionError={setChatError}
          />

          {showPanel && (
            <ProjectMaterialsPanel
              materials={materials}
              selectedMaterial={selectedMaterial}
              onSelectMaterial={selectMaterial}
              onClearSelection={clearSelection}
              onUpload={uploadMaterial}
              onDelete={deleteMaterial}
              onClose={closePanel}
            />
          )}
        </div>
      </div>
    </div>
  );
}
