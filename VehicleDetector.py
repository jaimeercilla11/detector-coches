import cv2


class VehicleDetector:
    """Handles vehicle detection using background subtraction and contour processing."""
    
    def __init__(self, min_area=500, max_width=420, history=300, var_threshold=50):
        """
        Initialize the VehicleDetector.
        
        Args:
            min_area: Minimum contour area to consider as vehicle
            max_width: Maximum width to consider as vehicle
            history: Number of frames for background model
            var_threshold: Variance threshold for background subtraction
        """
        self.min_area = min_area
        self.max_width = max_width
        
        # Create background subtractor
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=history, 
            varThreshold=var_threshold, 
            detectShadows=False
        )
    
    def detect_vehicles(self, frame):
        """
        Detect vehicles in a frame.
        
        Args:
            frame: Input frame (BGR image)
            
        Returns:
            Tuple of (mask, centroids) where centroids is a list of (x, y) tuples
        """
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply background subtraction
        mask = self.bg_subtractor.apply(gray)
        
        # Morphological processing
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        
        # Find contours
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter and extract centroids
        centroids = []
        for contour in contours:
            if cv2.contourArea(contour) < self.min_area:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            if w > self.max_width:
                continue
            
            centroid_x = x + w // 2
            centroid_y = y + h // 2
            centroids.append((centroid_x, centroid_y))
        
        return mask, centroids
