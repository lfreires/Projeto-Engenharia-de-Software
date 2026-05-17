import { useState, useCallback, useEffect } from "react";
import { ProjectMaterial } from "@/models/project";
import { fetchProjectMaterials } from "@/services/projectService";

export interface UseMaterialsReturn {
  showPanel: boolean;
  materials: ProjectMaterial[];
  selectedMaterial: ProjectMaterial | null;
  connectionError: string | null;
  togglePanel: () => void;
  openPanel: () => void;
  closePanel: () => void;
  selectMaterial: (material: ProjectMaterial) => void;
  clearSelection: () => void;
}

export function useMaterials(): UseMaterialsReturn {
  const [showPanel, setShowPanel] = useState(false);
  const [selectedMaterial, setSelectedMaterial] = useState<ProjectMaterial | null>(null);
  const [materials, setMaterials] = useState<ProjectMaterial[]>([]);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    fetchProjectMaterials()
      .then((items) => {
        if (!active) return;
        setMaterials(items);
        setConnectionError(null);
      })
      .catch((error: Error) => {
        if (!active) return;
        setMaterials([]);
        setConnectionError(error.message);
      });

    return () => {
      active = false;
    };
  }, []);

  const togglePanel = useCallback(() => setShowPanel((v) => !v), []);
  const openPanel = useCallback(() => setShowPanel(true), []);
  const closePanel = useCallback(() => setShowPanel(false), []);
  const selectMaterial = useCallback((m: ProjectMaterial) => setSelectedMaterial(m), []);
  const clearSelection = useCallback(() => setSelectedMaterial(null), []);

  return {
    showPanel,
    materials,
    selectedMaterial,
    connectionError,
    togglePanel,
    openPanel,
    closePanel,
    selectMaterial,
    clearSelection,
  };
}
