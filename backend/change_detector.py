"""
Change Detector Model :

Takes two satellite images (before & after) and detects urban changes.
Uses classical computer vision (OpenCV) for reliable, explainable results.

"""

import cv2
import numpy as np
from PIL import Image
import io
import base64
from scipy import ndimage


class UrbanChangeDetector:
    """
    Pipeline:
    1. Preprocess both images (resize, normalize)
    2. Compute absolute difference
    3. Apply Gaussian blur to remove noise
    4. Otsu thresholding to create binary change mask
    5. Morphological cleanup (remove tiny dots)
    6. Find contours (changed regions)
    7. Generate colored change map and heatmap
    8. Compute statistics
    """

    def __init__(self, image_size=(512, 512)):
        self.image_size = image_size

    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        """Convert uploaded image bytes → normalized numpy array"""
        pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pil_image = pil_image.resize(self.image_size)
        img_array = np.array(pil_image, dtype=np.float32)
        # Normalize to 0-1
        img_array = img_array / 255.0
        return img_array

    def compute_difference(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """
        Compute per-pixel absolute difference between two images.
        Higher value = more change at that pixel.
        """
        diff = np.abs(img2 - img1)
        # Convert to grayscale difference (average across RGB channels)
        diff_gray = np.mean(diff, axis=2)
        return diff_gray

    def create_change_mask(self, diff_gray: np.ndarray) -> np.ndarray:
        """
        Apply Otsu's thresholding to separate changed vs unchanged pixels.
        Otsu automatically finds the best threshold — no manual tuning needed.
        """
        # Scale to 0-255 for OpenCV
        diff_uint8 = (diff_gray * 255).astype(np.uint8)

        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(diff_uint8, (5, 5), 0)

        # Otsu thresholding
        _, binary_mask = cv2.threshold(
            blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )

        # Morphological operations: remove tiny specks and fill gaps
        kernel = np.ones((3, 3), np.uint8)
        mask_cleaned = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel)   # remove noise
        mask_cleaned = cv2.morphologyEx(mask_cleaned, cv2.MORPH_CLOSE, kernel) # fill gaps

        return mask_cleaned

    def create_heatmap(self, diff_gray: np.ndarray) -> np.ndarray:
        """
        Create a colored heatmap: blue=no change → red=high change
        """
        diff_uint8 = (diff_gray * 255).astype(np.uint8)
        heatmap = cv2.applyColorMap(diff_uint8, cv2.COLORMAP_JET)
        return heatmap

    def create_change_overlay(
        self, original_img: np.ndarray, mask: np.ndarray
    ) -> np.ndarray:
        """
        Overlay detected changes (in red) on the original image.
        Red = new urban growth / change detected.
        """
        overlay = (original_img * 255).astype(np.uint8).copy()
        # Where mask is white (changed), paint red
        overlay[mask == 255] = [255, 50, 50]  # Red highlight
        return overlay

    def compute_statistics(self, mask: np.ndarray, diff_gray: np.ndarray) -> dict:
        """Calculate meaningful statistics about detected changes"""
        total_pixels = mask.shape[0] * mask.shape[1]
        changed_pixels = np.sum(mask == 255)
        change_percentage = (changed_pixels / total_pixels) * 100

        # Severity: based on average difference in changed regions
        changed_region_diff = diff_gray[mask == 255]
        if len(changed_region_diff) > 0:
            avg_intensity = float(np.mean(changed_region_diff))
        else:
            avg_intensity = 0.0

        # Classify severity
        if change_percentage < 5:
            severity = "Low"
            growth_class = "Minimal Urban Growth"
        elif change_percentage < 20:
            severity = "Moderate"
            growth_class = "Moderate Urban Expansion"
        elif change_percentage < 40:
            severity = "High"
            growth_class = "Significant Urban Growth"
        else:
            severity = "Critical"
            growth_class = "Rapid Urban Sprawl"

        # Find number of distinct changed regions (clusters)
        labeled_array, num_features = ndimage.label(mask == 255)

        return {
            "change_percentage": round(change_percentage, 2),
            "changed_pixels": int(changed_pixels),
            "total_pixels": int(total_pixels),
            "avg_change_intensity": round(avg_intensity * 100, 2),
            "severity": severity,
            "growth_classification": growth_class,
            "num_change_clusters": int(num_features),
        }

    def numpy_to_base64(self, img_array: np.ndarray) -> str:
        """Convert numpy image array to base64 string for sending to frontend"""
        if img_array.dtype != np.uint8:
            img_array = (img_array * 255).astype(np.uint8)
        # Convert BGR to RGB if needed
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = img_array
        pil_img = Image.fromarray(img_rgb)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    def detect(self, before_bytes: bytes, after_bytes: bytes) -> dict:
        """
        Main method: takes two image byte streams, returns full analysis.
        """
        # Step 1: Preprocess
        img_before = self.preprocess(before_bytes)
        img_after = self.preprocess(after_bytes)

        # Step 2: Compute difference
        diff_gray = self.compute_difference(img_before, img_after)

        ml_result = self.classify_changes_ml(diff_gray)


        # Step 3: Create binary change mask
        mask = self.create_change_mask(diff_gray)

        # Step 4: Heatmap and overlay
        heatmap = self.create_heatmap(diff_gray)
        overlay = self.create_change_overlay(img_after, mask)

        # Step 5: Statistics
        stats = self.compute_statistics(mask, diff_gray)

        # Step 6: Encode images for frontend
        result = {
            "statistics": stats,
            "change_map": self.numpy_to_base64(mask),
            "heatmap": self.numpy_to_base64(heatmap),
            "change_overlay": self.numpy_to_base64(overlay),
            "before_processed": self.numpy_to_base64(img_before),
            "after_processed": self.numpy_to_base64(img_after),
            "ml_classification_map": self.numpy_to_base64(ml_result["color_map"]),
            "category_percentages": ml_result["category_percentages"]
        }
        return result
    
    def classify_changes_ml(self, diff_gray: np.ndarray) -> dict:
        """
        Use KMeans clustering to classify change intensity into 3 groups:
        - No Change
        - Moderate Change  
        - High Change (Urban Growth)
        
        This is the ML component — unsupervised learning, no training needed.
        """
        from sklearn.cluster import KMeans
        
        # Flatten image to 1D array of pixel values
        pixels = diff_gray.flatten().reshape(-1, 1)
        
        # KMeans with 3 clusters: no change / moderate / high change
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        kmeans.fit(pixels)
        labels = kmeans.labels_.reshape(diff_gray.shape)
        
        # Sort clusters by their center value (low=no change, high=change)
        centers = kmeans.cluster_centers_.flatten()
        sorted_idx = np.argsort(centers)  # indices from lowest to highest
        
        # Map cluster labels to category names
        label_map = {
            sorted_idx[0]: "No Change",
            sorted_idx[1]: "Moderate Change",
            sorted_idx[2]: "Urban Growth"
        }
        
        # Create colored output: green=none, yellow=moderate, red=growth
        color_map = np.zeros((*diff_gray.shape, 3), dtype=np.uint8)
        color_map[labels == sorted_idx[0]] = [34, 197, 94]    # green
        color_map[labels == sorted_idx[1]] = [251, 191, 36]   # yellow
        color_map[labels == sorted_idx[2]] = [239, 68, 68]    # red
        
        # Count pixels in each category
        total = labels.size
        category_counts = {
            label_map[sorted_idx[0]]: round(np.sum(labels == sorted_idx[0]) / total * 100, 2),
            label_map[sorted_idx[1]]: round(np.sum(labels == sorted_idx[1]) / total * 100, 2),
            label_map[sorted_idx[2]]: round(np.sum(labels == sorted_idx[2]) / total * 100, 2),
        }
        
        return {
            "color_map": color_map,
            "category_percentages": category_counts
        }