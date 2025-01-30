from abc import ABC, abstractmethod
from typing import List
import numpy as np
from .oilmath import OilMath


class Point:
    """Represents a point in 2D space."""
    def __init__(self, x: float, y: float) -> None:
        self._x = x
        self._y = y
        self._point = (self._x, self._y)

    @property
    def x(self) -> float:
        """ Returns the x value of the point """
        return self._x

    @property
    def y(self) -> float:
        """ Returns the y value of the point """
        return self._y
    
    @property
    def point(self) -> tuple:
        """ Returns a typle with the x and y value """
        return self._point


class Cell(ABC):
    """Abstract base class for cells in the mesh."""
    def __init__(self, index: int, points: List[Point]) -> None:
        self._index = index
        self._points = points
        self._neighbors: List[int] = [] # Indices of neighboring cells
        self._midpoint = self.find_midpoint()

        oil_math = OilMath()
        self._u = oil_math.calculate_u(self._midpoint.x, self._midpoint.y)

    @property
    def u(self) -> float:
        """ Returns the oil value in the cell """
        return self._u
    
    @u.setter
    def u(self, value: float) -> None:
        """ Sets the oil value for the cell """
        self._u = value

    @property
    def index(self) -> int:
        """ Returns the index number of the cell """
        return self._index

    @property
    def points(self) -> List[Point]:
        """ Returns a list of points in the cell """
        return self._points

    @property
    def neighbors(self) -> List[int]:
        """ Returns a list of the cells neighbors index """
        return self._neighbors
    
    @property
    def midpoint(self) -> Point:
        """ Returns the cells midpoint """
        return self._midpoint

    @abstractmethod
    def find_neighbors(self, cells):
        """Abstract method to find neighbors of the cell."""
        pass
    
    def find_midpoint(self) -> Point:
        """Calculate the geometric center of the cell."""
        coords = np.array([[point.x, point.y] for point in self._points])
        midpoint = coords.mean(axis=0)
        return Point(midpoint[0], midpoint[1])
    
    def calculate_normals(self, cells: List['Cell']) -> List[np.array]:
        """ Calculates every normal from the cell to its neighbors """
        normals = []
        midarray = np.array(self._midpoint.point)

        for neighbor_index in self._neighbors:
            if 0 <= neighbor_index < len(cells):  # Ensure valid index
                neighbor = cells[neighbor_index]
               
                shared_points = list(set(self._points) & set(neighbor.points))
                if len(shared_points) != 2:
                    continue
                """ calculating the scaled normal """
                p1 = np.array(shared_points[0].point)
                p2 = np.array(shared_points[1].point)

                length_shared_line = p2 - p1
                scaled_normal = np.array([-length_shared_line[1], length_shared_line[0]])

                """ Finding the right direction of scaled normal """
                mid_to_p2 = p2 - midarray
                if np.dot(mid_to_p2, scaled_normal) < 0:
                    scaled_normal = -scaled_normal

                normals.append(scaled_normal)

        return normals

    def __repr__(self) -> str:
        """ Returns a string with the cell information """
        boundary_status = "Boundary" if self.is_boundary() else "Not Boundary"
        return f"Cell {self._index}: {boundary_status}, Neighbors: {self._neighbors}"


class Triangle(Cell):
    """Represents a triangular cell in the mesh."""
    def __init__(self, index: int, points: List[Point]) -> None:
        super().__init__(index, points)

    def find_neighbors(self, cells: List[Cell]) -> None:
        """Find neighbors that share at least two points with this triangle."""
        self_points_set = set(self._points)
        self._neighbors = [cell.index for cell in cells 
                           if cell != self and len(self_points_set & set(cell.points)) >= 2]
    
    def area(self) -> float:
        """Calculate the area of the triangle using the determinant formula."""
        x1, y1 = self._points[0].x, self._points[0].y
        x2, y2 = self._points[1].x, self._points[1].y
        x3, y3 = self._points[2].x, self._points[2].y
        return 0.5 * abs((x1 - x3) * (y2 - y1) - (x1 - x2) * (y3 - y1))


class Line(Cell):
    """Represents a line segment in the mesh."""
    def __init__(self, index: int, points: List[Point]) -> None:
        super().__init__(index, points)

    def find_neighbors(self, cells: List[Cell]) -> None:
        """ Ignoring this operation for lines """
        pass


class CellFactory:
    """ A factory that makes different cells with their cell_type and their points """
    def __init__(self) -> None:
        self._cell_types = {
            "triangle": Triangle,
            "line": Line
            }

    def register(self, key: str, name: Cell) -> None:
        """ A register to make new cell_types """
        self._cell_types[key] = name

    def __call__(self, msh) -> List[Cell]:
        """ Goes through all cells and point in the meshio.read and 
        makes the cell for their type with their index and their list of points,
        returns a list of all cells"""
        index = 0
        cells = []
        points = [Point(x, y) for x, y, *_ in msh.points]

        for cell in msh.cells:
            cell_class = self._cell_types.get(cell.type)
            if cell_class == None:
                continue
            
            cells.extend(
                cell_class(index + i, [points[p] for p in cell])
                for i, cell in enumerate(cell.data)
            )
            index += len(cell.data)

        return cells