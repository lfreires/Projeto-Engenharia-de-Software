from datetime import datetime
from typing import Protocol

from app.schemas import Material, MaterialVersion, Project


class ProjectRepository(Protocol):
    def list_projects(self) -> list[Project]:
        raise NotImplementedError

    def get_project(self, project_id: str) -> Project | None:
        raise NotImplementedError

    def list_materials(self, project_id: str) -> list[Material]:
        raise NotImplementedError


class InMemoryProjectRepository:
    def __init__(self) -> None:
        self._projects = [
            Project(
                id="proj-demo",
                name="DocAI Demo",
                description="Demo project used by the DocAI MVP frontend.",
                created_at=datetime(2026, 1, 1, 12, 0, 0),
            )
        ]
        self._materials = [
            Material(
                id="mat-architecture",
                project_id="proj-demo",
                title="Architecture Notes",
                content_type="application/pdf",
                latest_version=MaterialVersion(
                    id="mat-architecture-v1",
                    material_id="mat-architecture",
                    version=1,
                    document_id="doc-architecture",
                    file_name="architecture.pdf",
                    created_at=datetime(2026, 1, 2, 12, 0, 0),
                ),
            )
        ]

    def list_projects(self) -> list[Project]:
        return list(self._projects)

    def get_project(self, project_id: str) -> Project | None:
        return next((project for project in self._projects if project.id == project_id), None)

    def list_materials(self, project_id: str) -> list[Material]:
        return [material for material in self._materials if material.project_id == project_id]
