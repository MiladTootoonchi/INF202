import pytest
import numpy as np
from src.Simulation.oilmath import OilMath
from src.Simulation.cells import Point, Triangle, Line

@pytest.mark.parametrize("p1, p2, p3, p4, p5", 
                         [
                             (Point(0, 0), Point(1, 0), Point(0, 1), Point(4, 4), Point(5, 5)),
                             (Point(1, 1), Point(2, 2), Point(3, 3), Point(3, 3), Point(6, 6)),
                             (Point(2, 1), Point(1, 2), Point(2, 2), Point(1, 1), Point(0, 0))
                         ])

def test_cell_creation(p1, p2, p3):
    """ test creating a Cell and accessing its properties """
    
    cell = Triangle(0, [p1, p2, p3])
    
    assert cell.index == 0
    assert cell.points == [p1, p2, p3]

    oil_math = OilMath()
    midpoint = cell.midpoint()
    expected_u = oil_math.calculate_u(midpoint.x, midpoint.y)
    assert pytest.approx(cell.u, rel=1e-5) == expected_u      

def test_find_neighbors(p1, p2, p3, p4):
    """Test the find_neighbors method."""

    cell1 = Triangle(0, [p1, p2, p3])
    cell2 = Triangle(1, [p2, p3, p4])
    all_cells = [cell1, cell2]

    cell1.find_neighbors(all_cells)
    cell2.find_neighbors(all_cells)

    assert cell1.neighbors == [1]
    assert cell2.neighbors == [0]     

def test_triangle_midpoint(p1, p2, p3):
    """Test the midpoint method for a Triangle cell."""
    triangle = Triangle(0, [p1, p2, p3])
    midpoint = triangle.midpoint()
   
    expected_x = (0 + 1 + 0) / 3  
    expected_y = (0 + 0 + 1) / 3  
    
    assert pytest.approx(midpoint.x, rel=1e-5) == expected_x
    assert pytest.approx(midpoint.y, rel=1e-5) == expected_y  

def test_line_midpoint(p1, p2):
    """Test the midpoint method for a Line cell."""
    line = Line(0, [p1, p2])
    midpoint = line.midpoint()
    
    expected_x = (0 + 2) / 2  
    expected_y = (0 + 0) / 2  
    
    assert pytest.approx(midpoint.x, rel=1e-5) == expected_x
    assert pytest.approx(midpoint.y, rel=1e-5) == expected_y  

def test_calculate_normals(p1, p2 , p3, p4):
    """ Test the calculations for normals """
    cell1 = Triangle(0, [p1, p2, p3])
    cell2 = Triangle(1, [p1, p2, p4])
    
    cell1._neighbors = [1]  
    cell2._neighbors = [0]  
    cells = [cell1, cell2]
    normals = cell1.calculate_normals(cells)
    first_points_normal = np.array([0, -1]) # The normal for the first points in pytest.mark.parametrize

    assert len(normals) == 1
    np.testing.assert_almost_equal(normals[0], first_points_normal, decimal=5)  


def test_find_neighbors(p1, p2, p3, p4, p5):
    """ Rest the find neighbors method for for more points """
    cell1 = Triangle(0, [p1, p2, p3])  
    cell2 = Triangle(1, [p2, p3, p4])  
    cell3 = Triangle(2, [p1, p2, p5]) 

    cells = [cell1, cell2, cell3]
    cell1.find_neighbors(cells)
    assert cell1._neighbors == [1, 2]


def test_area(p1, p2, p3):
    """ Testing the area calculations """
    triangle = Triangle(0, [p1, p2, p3])
    area = triangle.area()
    expected_area = 0.5
    assert abs(area - expected_area) < 1e-6  

def test_find_neighbors_line(p1, p2, p3, p4, p5):
    """ testing that find neigbors for lines pass """
    line1 = Line(0, [p1, p2])  
    line2 = Line(1, [p2, p3])  
    line3 = Line(2, [p3, p4])  
    line4 = Line(3, [p1, p5])  

    cells = [line1, line2, line3, line4]
    line1.find_neighbors(cells)

    assert line1._neighbors == None


def test_cell_factory():
    """ Testing the cell factory """
    msh = {
        'points': [(0, 0), (1, 0), (1, 1), (0, 1)],  
        'cells': [
            {'type': 'triangle', 'data': [(0, 1, 2)]},  
            {'type': 'line', 'data': [(0, 1)]}          
        ]
    }

    def create_triangle(index, points): 
        return {'index': index, 'type': 'triangle', 'points': points}
    
    def create_line(index, points): 
        return {'index': index, 'type': 'line', 'points': points}

    def cell_factory(msh):
        cell_types = {'triangle': create_triangle, 'line': create_line}
        points = [Point(x, y) for x, y in msh['points']]
        cells = []
        index = 0
        for cell in msh['cells']:
            create_cell = cell_types.get(cell['type'])
            if create_cell:
                for data in cell['data']:
                    cells.append(create_cell(index, [points[p] for p in data]))
                    index += 1
        return cells, points

    cells, _ = cell_factory(msh)

    assert len(cells) == 2, f"Expected 2 cells, got {len(cells)}"
    assert cells[0]['type'] == 'triangle', f"Expected 'triangle', got {cells[0]['type']}"
    assert cells[1]['type'] == 'line', f"Expected 'line', got {cells[1]['type']}"

    