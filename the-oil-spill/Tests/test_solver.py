import pytest
from src.Simulation.solver import Solver

@pytest.fixture
def valid_solver():
    """ fixture to create a Solver instance with a valid mesh file """
    return Solver("bay.msh", [[0.35, 0.45],[0.35, 0.45]], [], 0.0)


def test_solver_init(valid_solver):
    """ test Solver initialization """
    assert valid_solver is not None, "Solver object was not created."
    assert len(valid_solver._mesh.cells) > 0, "Mesh has no cells."


def test_start_oil_distribution(valid_solver):
    """ test the initial oil distribution """
    oil_distribution = valid_solver._start_oil_distribution()
    assert len(oil_distribution) > 0, "Oil distribution is empty."
    assert all(u >= 0 for u in oil_distribution), "Oil distribution contains negative values."


def test_solver(valid_solver):
    """ test updating oil distribution for all cells """
    dt = 0.01
    solution = valid_solver.solve(dt)

    assert solution >= 0, " there is negative oil value in fishing grounds "

    assert len(valid_solver._oil_list) > 0, "Updated oil distribution is empty."
    assert all(u >= 0 for u in valid_solver._oil_list), "Updated oil distribution contains negative values."
