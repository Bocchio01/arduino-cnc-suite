import cv2
import numpy as np
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageVectorizer:
    """Convert images to vector paths suitable for plotting"""

    def __init__(self, target_size: Tuple[int, int] = (250, 250)):
        """
        Args:
            target_size: Maximum dimensions in mm (width, height)
        """
        self.target_size = target_size

    def load_image(self, filepath: str) -> np.ndarray:
        """Load and preprocess image"""
        img = cv2.imread(filepath)
        if img is None:
            raise ValueError(f"Could not load image: {filepath}")
        return img

    def resize_image(self, img: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Resize image to fit target size while maintaining aspect ratio

        Returns:
            Resized image and scale factor
        """
        height, width = img.shape[:2]
        target_w, target_h = self.target_size

        # Calculate scale to fit in target size
        scale = min(target_w / width, target_h / height)

        new_width = int(width * scale)
        new_height = int(height * scale)

        resized = cv2.resize(img, (new_width, new_height))
        logger.info(
            f"Resized image from {width}x{height} to {new_width}x{new_height} (scale: {scale:.3f})"
        )

        return resized, scale

    def edge_detection(
        self, img: np.ndarray, threshold1: int = 100, threshold2: int = 200
    ) -> np.ndarray:
        """
        Apply Canny edge detection

        Args:
            img: Input image
            threshold1: Lower threshold for edge detection
            threshold2: Upper threshold for edge detection
        """
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Edge detection
        edges = cv2.Canny(blurred, threshold1, threshold2)

        return edges

    def threshold_image(self, img: np.ndarray, threshold: int = 127) -> np.ndarray:
        """
        Apply binary threshold for filled areas

        Args:
            img: Input image
            threshold: Threshold value (0-255)
        """
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        return binary

    def find_contours(self, binary_img: np.ndarray) -> List[np.ndarray]:
        """
        Find contours in binary image

        Returns:
            List of contours, each as numpy array of points
        """
        contours, _ = cv2.findContours(
            binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
        )
        logger.info(f"Found {len(contours)} contours")
        return contours

    def simplify_contour(self, contour: np.ndarray, epsilon: float = 2.0) -> np.ndarray:
        """
        Simplify contour using Douglas-Peucker algorithm

        Args:
            contour: Input contour
            epsilon: Approximation accuracy (higher = more simplified)
        """
        perimeter = cv2.arcLength(contour, True)
        simplified = cv2.approxPolyDP(contour, epsilon, True)
        return simplified

    def contour_to_points(self, contour: np.ndarray) -> List[Tuple[float, float]]:
        """Convert OpenCV contour to list of (x, y) tuples"""
        points = []
        for point in contour:
            x, y = point[0]
            points.append((float(x), float(y)))
        return points

    def process_image(
        self,
        filepath: str,
        mode: str = "edge",
        quality: int = 100,
        simplification: float = 2.0,
    ) -> Tuple[List[List[Tuple[float, float]]], Tuple[int, int]]:
        """
        Full pipeline: load, process, and vectorize image

        Args:
            filepath: Path to image file
            mode: "edge" for edge detection or "fill" for filled areas
            quality: Detection quality (1-255)
            simplification: Contour simplification level

        Returns:
            List of paths (each path is a list of points) and image dimensions
        """
        # Load and resize
        img = self.load_image(filepath)
        resized, scale = self.resize_image(img)

        # Process based on mode
        if mode == "edge":
            processed = self.edge_detection(resized, quality, quality)
        else:  # fill mode
            processed = self.threshold_image(resized, quality // 2)

        # Find and simplify contours
        contours = self.find_contours(processed)

        paths = []
        for contour in contours:
            # Filter out tiny contours
            if cv2.contourArea(contour) < 10:
                continue

            # Simplify
            simplified = self.simplify_contour(contour, simplification)

            # Convert to points
            points = self.contour_to_points(simplified)
            paths.append(points)

        height, width = resized.shape[:2]
        logger.info(f"Vectorization complete: {len(paths)} paths generated")

        return paths, (width, height)
