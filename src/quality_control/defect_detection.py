import cv2
import numpy as np
import torch
import torch.nn as nn
from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class DefectDetection:
    """Class for storing defect detection results."""
    defect_type: str
    confidence: float
    location: Tuple[int, int, int, int]  # x, y, width, height
    severity: float

class PCBDefectDetector:
    """AI-powered PCB defect detection using computer vision."""
    
    def __init__(self, model_path: str = None):
        """
        Initialize the defect detector.
        
        Args:
            model_path: Path to pre-trained model weights
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._build_model()
        if model_path:
            self.model.load_state_dict(torch.load(model_path))
        self.model.to(self.device)
        self.model.eval()
        
    def _build_model(self) -> nn.Module:
        """Build the neural network model for defect detection."""
        # Simple CNN for demonstration
        model = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(128, 5)  # 5 defect types
        )
        return model
    
    def detect_defects(self, image: np.ndarray) -> List[DefectDetection]:
        """
        Detect defects in a PCB image.
        
        Args:
            image: RGB image of the PCB
            
        Returns:
            List of detected defects with their properties
        """
        # Preprocess image
        processed_image = self._preprocess_image(image)
        
        # Run inference
        with torch.no_grad():
            predictions = self.model(processed_image)
            
        # Post-process predictions
        defects = self._process_predictions(predictions, image.shape)
        
        return defects
    
    def _preprocess_image(self, image: np.ndarray) -> torch.Tensor:
        """Preprocess image for model input."""
        # Resize image
        image = cv2.resize(image, (224, 224))
        
        # Normalize
        image = image.astype(np.float32) / 255.0
        image = (image - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        
        # Convert to tensor
        image = torch.from_numpy(image.transpose(2, 0, 1))
        image = image.unsqueeze(0)
        return image.to(self.device)
    
    def _process_predictions(self, predictions: torch.Tensor, 
                           original_shape: Tuple[int, ...]) -> List[DefectDetection]:
        """Process model predictions into defect detections."""
        defect_types = ['solder_bridge', 'missing_component', 
                       'misalignment', 'crack', 'copper_exposure']
        
        defects = []
        probs = torch.sigmoid(predictions[0])
        
        for i, prob in enumerate(probs):
            if prob > 0.5:  # Confidence threshold
                # For demonstration, generate random bounding box
                h, w = original_shape[:2]
                x = np.random.randint(0, w - 50)
                y = np.random.randint(0, h - 50)
                width = np.random.randint(20, 50)
                height = np.random.randint(20, 50)
                
                defect = DefectDetection(
                    defect_type=defect_types[i],
                    confidence=float(prob),
                    location=(x, y, width, height),
                    severity=float(prob)  # Use confidence as severity
                )
                defects.append(defect)
        
        return defects
    
    def analyze_defect_pattern(self, defects: List[DefectDetection]) -> Dict:
        """
        Analyze patterns in detected defects.
        
        Args:
            defects: List of detected defects
            
        Returns:
            Dictionary containing pattern analysis results
        """
        analysis = {
            'defect_counts': {},
            'severity_stats': {},
            'spatial_clustering': {}
        }
        
        # Count defects by type
        for defect in defects:
            if defect.defect_type not in analysis['defect_counts']:
                analysis['defect_counts'][defect.defect_type] = 0
            analysis['defect_counts'][defect.defect_type] += 1
            
            # Calculate severity statistics
            if defect.defect_type not in analysis['severity_stats']:
                analysis['severity_stats'][defect.defect_type] = []
            analysis['severity_stats'][defect.defect_type].append(defect.severity)
        
        # Calculate average severity for each defect type
        for defect_type in analysis['severity_stats']:
            severities = analysis['severity_stats'][defect_type]
            analysis['severity_stats'][defect_type] = {
                'mean': np.mean(severities),
                'max': np.max(severities),
                'std': np.std(severities)
            }
        
        return analysis
    
    def generate_inspection_report(self, image: np.ndarray) -> Dict:
        """
        Generate a comprehensive inspection report.
        
        Args:
            image: RGB image of the PCB
            
        Returns:
            Dictionary containing inspection results and analysis
        """
        # Detect defects
        defects = self.detect_defects(image)
        
        # Analyze patterns
        pattern_analysis = self.analyze_defect_pattern(defects)
        
        # Generate report
        report = {
            'timestamp': np.datetime64('now'),
            'num_defects': len(defects),
            'defects': [vars(d) for d in defects],
            'pattern_analysis': pattern_analysis,
            'overall_quality_score': self._calculate_quality_score(defects)
        }
        
        return report
    
    def _calculate_quality_score(self, defects: List[DefectDetection]) -> float:
        """Calculate overall quality score based on detected defects."""
        if not defects:
            return 1.0
            
        # Weight defects by severity
        total_severity = sum(d.severity for d in defects)
        num_defects = len(defects)
        
        # Simple scoring formula
        score = 1.0 - (total_severity / num_defects) * min(1.0, num_defects / 10)
        return max(0.0, score)
