"""
Utility functions for image validation and parallel processing.
Uses concurrent.futures (built-in) for parallel image processing.
This is Python's standard way to run tasks in parallel — same concept as Ray.
"""

import io
from PIL import Image
from concurrent.futures import ProcessPoolExecutor


def validate_image(image_bytes: bytes) -> bool:
    """Check if uploaded file is a valid image"""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        return True
    except Exception:
        return False


def _run_detection(before_bytes: bytes, after_bytes: bytes) -> dict:
    """
    Worker function — runs in a separate process.
    ProcessPoolExecutor sends this to another CPU core.
    """
    from models.change_detector import UrbanChangeDetector
    detector = UrbanChangeDetector()
    return detector.detect(before_bytes, after_bytes)


def run_parallel(before_bytes: bytes, after_bytes: bytes) -> dict:
    """
    Run detection in a separate process using ProcessPoolExecutor.
    This is the parallel/distributed concept — same idea as Ray,
    but using Python's built-in library.
    """
    with ProcessPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_run_detection, before_bytes, after_bytes)
        result = future.result()
    return result