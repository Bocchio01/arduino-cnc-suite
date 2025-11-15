import pytest
import numpy as np
import cv2
from core.image_processing.vectorizer import ImageVectorizer
from pathlib import Path


@pytest.fixture
def test_image():
    """Create a simple test image"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img.fill(255)  # White background

    # Draw a black square
    cv2.rectangle(img, (25, 25), (75, 75), (0, 0, 0), -1)

    return img


@pytest.fixture
def vectorizer():
    return ImageVectorizer(target_size=(100, 100))


def test_resize_maintains_aspect_ratio(vectorizer):
    img = np.zeros((200, 400, 3), dtype=np.uint8)
    resized, scale = vectorizer.resize_image(img)

    height, width = resized.shape[:2]
    assert width == 100  # Limited by target width
    assert height == 50  # Maintains 1:2 ratio
    assert abs(scale - 0.25) < 0.01  # 100/400


def test_edge_detection(vectorizer, test_image):
    edges = vectorizer.edge_detection(test_image)

    # Should be binary image
    assert edges.dtype == np.uint8
    unique_values = np.unique(edges)
    assert len(unique_values) <= 2

    # Should detect square edges
    assert np.sum(edges > 0) > 0


def test_contour_detection(vectorizer, test_image):
    edges = vectorizer.edge_detection(test_image)
    contours = vectorizer.find_contours(edges)

    assert len(contours) > 0

    # First contour should be approximately square-shaped
    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)
    assert area > 2000  # 50x50 square


def test_contour_simplification(vectorizer):
    # Create a complex contour
    contour = np.array(
        [
            [[0, 0]],
            [[1, 0]],
            [[2, 0]],
            [[3, 0]],
            [[3, 1]],
            [[3, 2]],
            [[3, 3]],
            [[2, 3]],
            [[1, 3]],
            [[0, 3]],
            [[0, 2]],
            [[0, 1]],
        ],
        dtype=np.int32,
    )

    simplified = vectorizer.simplify_contour(contour, epsilon=1.0)

    # Should reduce number of points
    assert len(simplified) < len(contour)
    assert len(simplified) >= 4  # At least 4 corners for a square
