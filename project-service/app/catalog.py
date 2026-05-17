from app.dependencies import get_catalog_service
from app.schemas import Material, Project
from app.services.catalog_service import ProjectNotFoundError as ProjectNotFoundError


def list_projects() -> list[Project]:
    return get_catalog_service().list_projects()


def get_project(project_id: str) -> Project:
    return get_catalog_service().get_project(project_id)


def get_materials_for_project(project_id: str) -> list[Material]:
    return get_catalog_service().get_materials_for_project(project_id)
