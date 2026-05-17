import pytest

from app.catalog import ProjectNotFoundError, get_materials_for_project, get_project


def test_get_project_returns_demo_project():
    project = get_project("proj-demo")

    assert project.id == "proj-demo"
    assert project.name == "DocAI Demo"


def test_get_project_raises_for_unknown_project():
    with pytest.raises(ProjectNotFoundError):
        get_project("missing")


def test_get_materials_for_project_returns_material_versions():
    materials = get_materials_for_project("proj-demo")

    assert materials[0].id == "mat-architecture"
    assert materials[0].latest_version.version == 1


def test_get_materials_for_project_checks_project_exists():
    with pytest.raises(ProjectNotFoundError):
        get_materials_for_project("missing")
