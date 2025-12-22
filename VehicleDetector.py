import cv2

class VehicleDetector:
    """Solo se encarga de detectar vehículos en el frame"""
    
    def __init__(self, min_area=500, max_width=420):
        self.min_area = min_area
        self. max_width = max_width
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=300, varThreshold=50, detectShadows=False
        )
    
    def detect(self, frame):
        """Retorna mask y lista de centroides detectados"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = self.bg_subtractor. apply(gray)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        _, mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        detections = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            if w > self. max_width: 
                continue
            
            centroid_x = x + w // 2
            centroid_y = y + h // 2
            detections.append((centroid_x, centroid_y))
        
        return mask, detections