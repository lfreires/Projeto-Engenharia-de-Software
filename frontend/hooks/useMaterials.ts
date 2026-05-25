import { useState, useCallback, useEffect } from "react";
import { ProjectMaterial } from "@/models/project";
import {
  deleteProjectMaterial,
  fetchProjectMaterials,
  uploadProjectDocument,
} from "@/services/projectService";

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
  uploadMaterial: (file: File) => Promise<void>;
  deleteMaterial: (material: ProjectMaterial) => Promise<void>;
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
  const uploadMaterial = useCallback(async (file: File) => {
    const uploaded = await uploadProjectDocument(file);
    const items = await fetchProjectMaterials();
    const material = items.find((item) => item.id === uploaded.material_id);
    setMaterials(items);
    setConnectionError(null);
    setShowPanel(true);
    if (material) setSelectedMaterial(material);
  }, []);
  const deleteMaterial = useCallback(async (material: ProjectMaterial) => {
    await deleteProjectMaterial(material.id);
    const items = await fetchProjectMaterials();
    setMaterials(items);
    setConnectionError(null);
    setSelectedMaterial((selected) => (selected?.id === material.id ? null : selected));
  }, []);

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
    uploadMaterial,
    deleteMaterial,
  };
}
