import pytest
from core.image_processing.path_planner import PathPlanner
from core.gcode.optimizer import PathOptimizer


@pytest.fixture
def planner():
    return PathPlanner()


@pytest.fixture
def optimizer():
    return PathOptimizer()


def test_coordinate_conversion(planner):
    paths = [
        [(0, 0), (100, 100)],
    ]

    converted = planner.paths_to_gcode_coordinates(
        paths, image_size=(100, 100), target_size=(200, 200), flip_y=True
    )

    # Should scale by 2x and flip Y
    assert converted[0][0] == (0, 200)  # (0, 0) -> (0, 200)
    assert converted[0][1] == (200, 0)  # (100, 100) -> (200, 0)


def test_distance_calculation(optimizer):
    dist = optimizer.distance((0, 0), (3, 4))
    assert abs(dist - 5.0) < 0.01  # 3-4-5 triangle


def test_path_optimization(optimizer):
    # Create scattered paths
    paths = [
        [(100, 100), (110, 110)],  # Far
        [(10, 10), (20, 20)],  # Near start
        [(50, 50), (60, 60)],  # Middle
    ]

    optimized = optimizer.nearest_neighbor(paths, start_point=(0, 0))

    # First path should be nearest to origin
    assert optimized[0] == paths[1]  # (10, 10) path


def test_duplicate_removal(optimizer):
    path = [
        (0, 0),
        (0.05, 0.05),  # Very close to previous
        (1, 1),
        (1.01, 1.01),  # Very close to previous
        (2, 2),
    ]

    cleaned = optimizer.remove_duplicates(path, tolerance=0.1)

    # Should remove close duplicates
    assert len(cleaned) == 3
    assert cleaned == [(0, 0), (1, 1), (2, 2)]
