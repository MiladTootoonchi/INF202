import pytest
from src.Simulation.mesh import Mesh
from src.Simulation.cells import Triangle


@pytest.fixture
def valid_mesh():
    """ makes mesh """
    return Mesh("bay.msh")

def test_if_mesh_is_valid(valid_mesh):
    """ checks if there isnt 0 cells """
    assert len (valid_mesh.cells) > 0
    print(f"Mesh is valid with {len(valid_mesh.cells)} cells.")

def test_if_mesh_is_invalid():
    """ Testing if it doesnt read invalid files """
    with pytest.raises(ValueError) as e: 
        msh = Mesh("invalid_file.msh")
    assert str(e.value) == "Failed to read mesh file invalid_file.msh"

def test_find_neighbors(valid_mesh):
    """ testing if the mesh class can find all the neighbors for cells in bay.msh """
    valid_mesh._find_neighbors()
    for cell in valid_mesh.cells:
        if isinstance(cell, Triangle):
            assert len(cell.neighbors) > 0, f"Cell {cell.index} doesn't have any neighbors. "