import numpy as np
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, List, Optional
import joblib

class PCBFailurePredictor:
    """AI model for predicting potential PCB failures based on design and manufacturing data."""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the failure predictor.
        
        Args:
            model_path: Path to pre-trained model file (optional)
        """
        self.feature_columns = [
            'trace_width',
            'trace_spacing',
            'via_density',
            'component_density',
            'max_temperature',
            'humidity',
            'copper_thickness',
            'board_thickness'
        ]
        
        if model_path:
            self.model = joblib.load(model_path)
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1
            )
    
    def train(self, training_data: List[Dict], labels: List[int]):
        """
        Train the failure prediction model.
        
        Args:
            training_data: List of PCB feature dictionaries
            labels: List of failure labels (0: no failure, 1: failure)
        """
        X = self._extract_features(training_data)
        self.model.fit(X, labels)
    
    def predict_failure_probability(self, pcb_data: Dict) -> float:
        """
        Predict the probability of PCB failure.
        
        Args:
            pcb_data: Dictionary containing PCB features
            
        Returns:
            Probability of failure (0.0 to 1.0)
        """
        X = self._extract_features([pcb_data])
        return float(self.model.predict_proba(X)[0][1])
    
    def analyze_failure_risks(self, pcb_data: Dict) -> Dict[str, float]:
        """
        Analyze specific failure risks for different aspects of the PCB.
        
        Args:
            pcb_data: Dictionary containing PCB features
            
        Returns:
            Dictionary mapping risk types to risk probabilities
        """
        base_prob = self.predict_failure_probability(pcb_data)
        
        # Analyze specific risk factors
        risks = {
            'thermal_risk': self._analyze_thermal_risk(pcb_data),
            'density_risk': self._analyze_density_risk(pcb_data),
            'manufacturing_risk': self._analyze_manufacturing_risk(pcb_data),
            'overall_risk': base_prob
        }
        
        return risks
    
    def _extract_features(self, pcb_data_list: List[Dict]) -> np.ndarray:
        """Extract feature array from PCB data dictionaries."""
        features = []
        for pcb_data in pcb_data_list:
            feature_vector = [
                pcb_data.get(col, 0.0) for col in self.feature_columns
            ]
            features.append(feature_vector)
        return np.array(features)
    
    def _analyze_thermal_risk(self, pcb_data: Dict) -> float:
        """Analyze risk related to thermal issues."""
        max_temp = pcb_data.get('max_temperature', 0)
        component_density = pcb_data.get('component_density', 0)
        
        # Simple thermal risk model
        base_risk = max(0, (max_temp - 70) / 50)  # Increased risk above 70°C
        density_factor = min(1, component_density / 0.7)  # Density impact
        
        return min(1.0, base_risk * (1 + density_factor))
    
    def _analyze_density_risk(self, pcb_data: Dict) -> float:
        """Analyze risk related to component and trace density."""
        component_density = pcb_data.get('component_density', 0)
        via_density = pcb_data.get('via_density', 0)
        
        # Combined density risk model
        return min(1.0, (component_density + via_density) / 2)
    
    def _analyze_manufacturing_risk(self, pcb_data: Dict) -> float:
        """Analyze risk related to manufacturing parameters."""
        trace_width = pcb_data.get('trace_width', 0)
        trace_spacing = pcb_data.get('trace_spacing', 0)
        
        # Manufacturing complexity risk model
        width_risk = max(0, (0.1 - trace_width) / 0.1)  # Risk increases for very thin traces
        spacing_risk = max(0, (0.1 - trace_spacing) / 0.1)  # Risk increases for tight spacing
        
        return min(1.0, (width_risk + spacing_risk) / 2)
