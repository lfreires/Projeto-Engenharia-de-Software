import { useState, useCallback } from "react";
import { ProjectMaterial } from "@/models/project";
import { getCurrentProject } from "@/services/projectService";

export interface UseMaterialsReturn {
  showPanel: boolean;
  materials: ProjectMaterial[];
  selectedMaterial: ProjectMaterial | null;
  togglePanel: () => void;
  openPanel: () => void;
  closePanel: () => void;
  selectMaterial: (material: ProjectMaterial) => void;
  clearSelection: () => void;
}

export function useMaterials(): UseMaterialsReturn {
  const [showPanel, setShowPanel] = useState(false);
  const [selectedMaterial, setSelectedMaterial] = useState<ProjectMaterial | null>(null);

  const materials = getCurrentProject().materials;

  const togglePanel = useCallback(() => setShowPanel((v) => !v), []);
  const openPanel = useCallback(() => setShowPanel(true), []);
  const closePanel = useCallback(() => setShowPanel(false), []);
  const selectMaterial = useCallback((m: ProjectMaterial) => setSelectedMaterial(m), []);
  const clearSelection = useCallback(() => setSelectedMaterial(null), []);

  return {
    showPanel,
    materials,
    selectedMaterial,
    togglePanel,
    openPanel,
    closePanel,
    selectMaterial,
    clearSelection,
  };
}
