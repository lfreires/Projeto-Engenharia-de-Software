from app.repositories.project_repository import ProjectRepository
from app.schemas import Material, Project


class ProjectNotFoundError(Exception):
    pass


class CatalogService:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    def list_projects(self) -> list[Project]:
        return self._repository.list_projects()

    def get_project(self, project_id: str) -> Project:
        project = self._repository.get_project(project_id)
        if project is None:
            raise ProjectNotFoundError()
        return project

    def get_materials_for_project(self, project_id: str) -> list[Material]:
        self.get_project(project_id)
        return self._repository.list_materials(project_id)
