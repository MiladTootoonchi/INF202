import pytest 
import numpy as np
from src.Simulation.oilmath import OilMath
from src.Simulation.cells import Triangle


@pytest.fixture
def valid_oilmath():
    """ defining oilmath """
    return OilMath()

@pytest.mark.parametrize("x, y",
                          [(0.35, 0.45), (0.11, 0.0), (0.50, 0.50)])

def test_calculate_u(valid_oilmath, x, y):
    """ testing if the values wont get negative"""
    u = valid_oilmath.calculate_u(x, y)
    assert u >= 0, "Oil concentration is not positive."
    assert u <= 1, "Oil concentration is greater than 1. This is correct"


def test_velocity(valid_oilmath, x, y):
    """ testing the velocity vector """
    velocity= valid_oilmath._v(x,y)
    expected_velocity = (y-0.2*x, -x)
    assert velocity == expected_velocity, f"Expected velocity {expected_velocity}, and got {velocity}."


def test_g():
    """ testing for flux variable g for spesific values"""
    u_i = 0.5
    u_ngh = 0.3
    normal = np.array([1,0])
    v_i = np.array([0,0])
    v_ngh = np.array([0,0])

    flux = OilMath._g(u_i, u_ngh, normal, v_i, v_ngh)
    assert flux == 0, f"Expected flux to be 0, and got {flux}."

    "Test for small v_dot_normal"
    v_i = np.array([0.1, 0.2])
    v_ngh = np.array([0.2, 0.3])
    flux = OilMath._g(u_i, u_ngh, normal, v_i, v_ngh)

    v_avg = 0.5*(v_i + v_ngh)
    v_dot_normal = np.dot(v_avg, normal)
    assert abs(v_dot_normal) < 1, f"v_dot_normal is too large: {v_dot_normal}"

def test_update_oil_distribution(p1, p2, p3):
    cell1 = Triangle(0, [p1, p2, p3])
    cell2 = Triangle(1, [p2, p3, p1])
    all_cells = [cell1, cell2]
    dt = 0.01

    # Set neighbors
    cell1.neighbors = [1]
    cell2.neighbors = [0]

    # Set initial oil concentrations
    cell1.u = 0.8
    cell2.u = 0.5

    # Mock areas for cells
    cell1.area = lambda: 1.0
    cell2.area = lambda: 1.0

    # List of all cells
    all_cells = [cell1, cell2]


    updated_u = OilMath.update_oil_distribution(cell1, all_cells, dt)
    assert updated_u > 0, "Updated oil concentration is not positive."
    assert updated_u <= 1, "Updated oil concentration is greater than 1."

    updated_u = OilMath.update_oil_distribution(cell2, all_cells, dt)
    assert updated_u > 0, "Updated oil concentration is not positive."
    assert updated_u <= 1, "Updated oil concentration is greater than 1."