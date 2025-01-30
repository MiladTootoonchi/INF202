from typing import List
from .cells import Point, Cell, CellFactory
import meshio

class Mesh:
    """Represents a 2D mesh with points and cells."""
    def __init__(self, file: str) -> None:
        self._cells: List[Cell] = []
        self._read_mesh(file)
        self._find_neighbors()
    
    @property
    def cells(self) -> list[Cell]:
        """ Returns a list of all cells in the mesh """
        return self._cells
    
    def _read_mesh(self, file: str) -> None:
        """ Reads the mesh from a file and puts the readed meshio in th cell factory, 
        Gives an error if the file doesnt exist,
        saves the list of all cells in self"""
        try:
            msh = meshio.read(file)
        except Exception as e:
            raise ValueError(f"Failed to read mesh file {file}")
        
        make_cells = CellFactory()

        self._cells = make_cells(msh)

    def _find_neighbors(self) -> None:
        """ Runs the find_neighbors method for all cells """
        for cell in self.cells:
            cell.find_neighbors(self.cells)