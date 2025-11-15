from typing import List, Tuple
import numpy as np
from ..gcode.optimizer import PathOptimizer


class PathPlanner:
    """Convert vectorized paths to optimized plotting sequences"""

    def __init__(self):
        self.optimizer = PathOptimizer()

    def paths_to_gcode_coordinates(
        self,
        paths: List[List[Tuple[float, float]]],
        image_size: Tuple[int, int],
        target_size: Tuple[float, float],
        origin: Tuple[float, float] = (0, 0),
        flip_y: bool = True,
    ) -> List[List[Tuple[float, float]]]:
        """
        Convert image pixel coordinates to machine coordinates

        Args:
            paths: List of paths in pixel coordinates
            image_size: (width, height) of processed image in pixels
            target_size: (width, height) of target area in mm
            origin: (x, y) origin offset in mm
            flip_y: Flip Y axis (images have Y down, machines have Y up)

        Returns:
            List of paths in machine coordinates (mm)
        """
        img_w, img_h = image_size
        target_w, target_h = target_size
        origin_x, origin_y = origin

        # Calculate scaling
        scale_x = target_w / img_w
        scale_y = target_h / img_h

        converted_paths = []
        for path in paths:
            converted_path = []
            for x, y in path:
                # Scale to target size
                new_x = x * scale_x + origin_x

                # Flip Y if needed and scale
                if flip_y:
                    new_y = (img_h - y) * scale_y + origin_y
                else:
                    new_y = y * scale_y + origin_y

                converted_path.append((new_x, new_y))

            if converted_path:
                converted_paths.append(converted_path)

        return converted_paths

    def optimize_plotting_order(
        self,
        paths: List[List[Tuple[float, float]]],
        start_position: Tuple[float, float] = (0, 0),
    ) -> List[List[Tuple[float, float]]]:
        """Optimize path order for minimal travel distance"""
        return self.optimizer.nearest_neighbor(paths, start_position)

    def plan_from_image(
        self,
        paths: List[List[Tuple[float, float]]],
        image_size: Tuple[int, int],
        work_area: Tuple[float, float] = (250, 250),
        optimize: bool = True,
    ) -> List[List[Tuple[float, float]]]:
        """
        Complete planning pipeline

        Args:
            paths: Raw paths from vectorizer
            image_size: Original image dimensions
            work_area: Suite work area in mm
            optimize: Whether to optimize path order

        Returns:
            Ready-to-plot paths in machine coordinates
        """
        # Convert to machine coordinates
        machine_paths = self.paths_to_gcode_coordinates(paths, image_size, work_area)

        # Optimize if requested
        if optimize:
            machine_paths = self.optimize_plotting_order(machine_paths)

        return machine_paths
