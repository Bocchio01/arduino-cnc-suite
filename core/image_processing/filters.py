"""Image filtering and preprocessing utilities"""

import cv2
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class ImageFilters:
    """Collection of image preprocessing filters"""

    @staticmethod
    def grayscale(img: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img

    @staticmethod
    def gaussian_blur(
        img: np.ndarray, kernel_size: Tuple[int, int] = (5, 5), sigma: float = 0
    ) -> np.ndarray:
        """Apply Gaussian blur"""
        return cv2.GaussianBlur(img, kernel_size, sigma)

    @staticmethod
    def median_blur(img: np.ndarray, kernel_size: int = 5) -> np.ndarray:
        """Apply median blur (good for salt-and-pepper noise)"""
        return cv2.medianBlur(img, kernel_size)

    @staticmethod
    def bilateral_filter(
        img: np.ndarray, d: int = 9, sigma_color: float = 75, sigma_space: float = 75
    ) -> np.ndarray:
        """Apply bilateral filter (edge-preserving smoothing)"""
        return cv2.bilateralFilter(img, d, sigma_color, sigma_space)

    @staticmethod
    def sharpen(img: np.ndarray, amount: float = 1.0) -> np.ndarray:
        """Sharpen image using unsharp mask"""
        gaussian = cv2.GaussianBlur(img, (5, 5), 1.0)
        sharpened = cv2.addWeighted(img, 1.0 + amount, gaussian, -amount, 0)
        return sharpened

    @staticmethod
    def adjust_brightness_contrast(
        img: np.ndarray, brightness: float = 0, contrast: float = 1.0
    ) -> np.ndarray:
        """
        Adjust brightness and contrast

        Args:
            brightness: Add this value to all pixels (-255 to 255)
            contrast: Multiply pixels by this value (0.5 to 3.0)
        """
        adjusted = cv2.convertScaleAbs(img, alpha=contrast, beta=brightness)
        return adjusted

    @staticmethod
    def auto_contrast(img: np.ndarray) -> np.ndarray:
        """Automatically adjust contrast using histogram equalization"""
        if len(img.shape) == 3:
            # Convert to YCrCb color space
            ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
            # Equalize the Y channel
            ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
            # Convert back to BGR
            return cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)
        else:
            return cv2.equalizeHist(img)

    @staticmethod
    def adaptive_threshold(
        img: np.ndarray, block_size: int = 11, c: float = 2
    ) -> np.ndarray:
        """
        Apply adaptive thresholding
        Good for images with varying lighting
        """
        gray = ImageFilters.grayscale(img)
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c
        )

    @staticmethod
    def morphological_opening(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """Remove small noise (erosion followed by dilation)"""
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    @staticmethod
    def morphological_closing(img: np.ndarray, kernel_size: int = 3) -> np.ndarray:
        """Fill small holes (dilation followed by erosion)"""
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
        return cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)

    @staticmethod
    def invert(img: np.ndarray) -> np.ndarray:
        """Invert image colors"""
        return cv2.bitwise_not(img)

    @staticmethod
    def rotate(img: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by given angle (degrees)"""
        height, width = img.shape[:2]
        center = (width // 2, height // 2)

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, rotation_matrix, (width, height))

        return rotated

    @staticmethod
    def crop(img: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Crop image to specified rectangle"""
        return img[y : y + height, x : x + width]

    @staticmethod
    def auto_crop(img: np.ndarray, margin: int = 10) -> np.ndarray:
        """Automatically crop to content (remove white borders)"""
        gray = ImageFilters.grayscale(img)
        _, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            return img

        # Get bounding box of all contours
        x, y, w, h = cv2.boundingRect(np.vstack(contours))

        # Add margin
        x = max(0, x - margin)
        y = max(0, y - margin)
        w = min(img.shape[1] - x, w + 2 * margin)
        h = min(img.shape[0] - y, h + 2 * margin)

        return img[y : y + h, x : x + w]
