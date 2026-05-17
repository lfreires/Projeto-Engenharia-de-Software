from datetime import datetime

from pydantic import BaseModel


class Project(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime


class MaterialVersion(BaseModel):
    id: str
    material_id: str
    version: int
    document_id: str
    file_name: str
    created_at: datetime


class Material(BaseModel):
    id: str
    project_id: str
    title: str
    content_type: str
    latest_version: MaterialVersion


class ProjectsResponse(BaseModel):
    projects: list[Project]


class MaterialsResponse(BaseModel):
    materials: list[Material]
