import math
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class PathOptimizer:
    """Optimize plotting paths to reduce travel time"""

    @staticmethod
    def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    @staticmethod
    def path_length(path: List[Tuple[float, float]]) -> float:
        """Calculate total length of a path"""
        if len(path) < 2:
            return 0.0

        total = 0.0
        for i in range(len(path) - 1):
            total += PathOptimizer.distance(path[i], path[i + 1])
        return total

    def nearest_neighbor(
        self,
        paths: List[List[Tuple[float, float]]],
        start_point: Tuple[float, float] = (0, 0),
    ) -> List[List[Tuple[float, float]]]:
        """
        Optimize path order using nearest neighbor algorithm

        Args:
            paths: List of paths to optimize
            start_point: Starting position

        Returns:
            Reordered list of paths
        """
        if not paths:
            return []

        optimized = []
        remaining = paths.copy()
        current_pos = start_point

        while remaining:
            # Find nearest path
            min_distance = float("inf")
            nearest_idx = 0
            reverse = False

            for i, path in enumerate(remaining):
                if not path:
                    continue

                # Check distance to start and end of path
                dist_to_start = self.distance(current_pos, path[0])
                dist_to_end = self.distance(current_pos, path[-1])

                if dist_to_start < min_distance:
                    min_distance = dist_to_start
                    nearest_idx = i
                    reverse = False

                if dist_to_end < min_distance:
                    min_distance = dist_to_end
                    nearest_idx = i
                    reverse = True

            # Add nearest path
            selected_path = remaining.pop(nearest_idx)
            if reverse:
                selected_path = list(reversed(selected_path))

            optimized.append(selected_path)
            current_pos = selected_path[-1]

        logger.info(f"Path optimization complete: {len(optimized)} paths reordered")
        return optimized

    def remove_duplicates(
        self, path: List[Tuple[float, float]], tolerance: float = 0.1
    ) -> List[Tuple[float, float]]:
        """Remove duplicate consecutive points within tolerance"""
        if len(path) < 2:
            return path

        cleaned = [path[0]]
        for point in path[1:]:
            if self.distance(cleaned[-1], point) > tolerance:
                cleaned.append(point)

        return cleaned
