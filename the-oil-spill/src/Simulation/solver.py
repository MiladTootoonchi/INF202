from .cells import Triangle
from .mesh import Mesh
from .oilmath import OilMath
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class Solver:
    """ A class that simulates the oil distribution over a mesh given a time """
    def __init__(self, file: str, borders: list, oil_list: list, time: float) -> None:
        self._mesh = Mesh(file)
        self._time = time
        self._borders = borders
        if self._time == 0.0: 
            self._oil_list = self._start_oil_distribution()
        else: 
            self._oil_list = oil_list

    @property
    def time(self) -> float:
        """ Returns the time / updated time for the simulation """
        return self._time

    @property
    def oil_list(self) -> list:
        """ Return a list of oil value for each cell index in order """
        return self._oil_list
     
    def _start_oil_distribution(self) -> list:
        """ Returns a list of the oil distribution when time is 0 """
        return [cell.u for cell in self._mesh.cells]
    
    def solve(self, dt: float) -> float:
        """ Updates every cell in the mesh for their oil amount and 
        finds out the total amount of oil in fish grounds for the time"""
        self._time += dt
        u_new_list = []
        u_in_fishground_list = []

        for cell in self._mesh.cells:
            oil_math = OilMath()
            if isinstance(cell, Triangle):
                u_new = oil_math.update_oil_distribution(cell, self._mesh.cells, dt)
                u_new = max(0, u_new)
                cell.u = u_new
            u_new_list.append(cell.u)

            if self._borders[0][0] < cell.midpoint.x < self._borders[0][1]:
                if self._borders[1][0] < cell.midpoint.y < self._borders[1][1]:
                    u_in_fishground_list.append(cell.u)
        
        self._oil_list = u_new_list
        return sum(u_in_fishground_list)


    def plot(self, folder: str = "imgs") -> None:
        """ Plots the oil distribution across the mesh and saves the output image in given / img folder """
        # Prepare color mapping
        scalar_map = plt.cm.ScalarMappable(cmap="viridis")
        scalar_map.set_array(self._oil_list)
        umax, umin = max(self._oil_list), min(self._oil_list)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect("equal")

        # Plot each cell with oil concentration color
        for cell, oil_amount in zip(self._mesh.cells, self._oil_list):
            triangle = np.array([p.point for p in cell.points])
            color = plt.cm.viridis(np.clip((oil_amount - umin) / (umax - umin), 0, 1))
            ax.add_patch(plt.Polygon(triangle, color=color, alpha=0.9))

        # Add fishing grounds border rectangle
        x_min, x_max = self._borders[0]
        y_min, y_max = self._borders[1]
        width, height = x_max - x_min, y_max - y_min
        fishing_grounds = patches.Rectangle(
            (x_min, y_min), width, height, edgecolor="red", facecolor="none", lw=2
        )
        ax.add_patch(fishing_grounds)

        # Customizes plot
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        plt.colorbar(scalar_map, ax=ax, label="Amount of Oil", shrink=0.8)

        # Saves image
        output_path = f"{folder}/oil_dist_{self._time:.2f}.png"
        plt.savefig(output_path, dpi=300)
        plt.close(fig)