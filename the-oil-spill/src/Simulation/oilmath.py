import numpy as np

class OilMath:
    """ A class that contains most of the math needed for oil calculations """
    def __init__(self) -> None:
        self._x_star = 0.35
        self._y_star = 0.45
        self._vector_star = np.array([0.35, 0.45])
        
    def calculate_u(self, x: float , y: float) -> float:
        """ Calculates the amount of oil in a cell using a formula """
        vector = np.array([x, y])
        distance_from_star = vector - self._vector_star
        oil_concentration = np.exp(-(np.linalg.norm(distance_from_star))**2 / 0.01)

        return oil_concentration
    
    def _v(self, x: float, y: float) -> tuple:
        """ Calculates the velocity vector for a cell """
        return (y-0.2*x, -x)
    
    def _g(self, u_i: float, u_ngh: float, normal: np.array, v_i: tuple, v_ngh: tuple) -> float:
        """ Calculates the g function / formula in flux """
        v_avg = 0.5 * (np.array(v_i) + np.array(v_ngh))
        v_dot_normal = np.dot(v_avg, normal)

        if v_dot_normal > 0:
            return u_i * v_dot_normal
        else:
            return u_ngh * v_dot_normal
        
    def _area_constant(self, area: float, dt: float) -> float:
        """Calculates the area constand dt / area seperate,
        easier to catch bugs """
        if area<=0:
            raise ValueError("Area is negative or zero")
        return dt / area
        
    def update_oil_distribution(self, cell, all_cells: list, dt: float) -> float:
        """ Updates the oil distribution in a cell """
        u_new = cell.u
        midpoint_coords = np.array(cell.midpoint.point)
        velocity = self._v(*midpoint_coords)
        normals = cell.calculate_normals(all_cells)
        area_const = self._area_constant(cell.area(), dt)

        # Process neighbors
        for ngh, normal in zip(cell.neighbors, normals):
            if not (0 <= ngh < len(all_cells)):  # Skip invalid neighbors
                continue

            neighbor = all_cells[ngh]
            u_ngh = neighbor.u if len(neighbor.points) >= 3 else 0

            neighbor_midpoint = np.array(neighbor.midpoint.point)
            velocity_ngh = self._v(*neighbor_midpoint)

            # Calculate g in flux
            g_flux = self._g(u_new, u_ngh, normal, velocity, velocity_ngh)

            # Update oil concentration
            u_new -= area_const * g_flux

        return u_new
