import React from "react";
import { DocAISidebar } from "@/views/layouts/DocAISidebar";
import { ChatArea } from "@/views/components/ChatArea";
import { ProjectMaterialsPanel } from "@/views/components/ProjectMaterialsPanel";
import { useMaterials } from "@/hooks/useMaterials";

export default function App() {
  const { showPanel, materials, selectedMaterial, togglePanel, closePanel, selectMaterial } =
    useMaterials();

  return (
    <div
      className="flex h-screen overflow-hidden"
      style={{ fontFamily: "'Inter', system-ui, -apple-system, sans-serif", backgroundColor: "#f8f9fc" }}
    >
      <DocAISidebar />

      <div className="flex flex-1 min-w-0">
        <ChatArea
          materialsCount={materials.length}
          showMaterials={showPanel}
          onToggleMaterials={togglePanel}
        />

        {showPanel && (
          <ProjectMaterialsPanel
            materials={materials}
            selectedMaterial={selectedMaterial}
            onSelectMaterial={selectMaterial}
            onClose={closePanel}
          />
        )}
      </div>
    </div>
  );
}
