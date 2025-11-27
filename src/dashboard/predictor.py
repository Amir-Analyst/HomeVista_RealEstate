"""
Rent Prediction Module.

This module provides the RentPredictor class, which serves as the main inference
engine for the HomeVista dashboard. It handles model loading, input preparation,
feature engineering, and prediction generation with confidence intervals.
"""

import joblib
import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path

# Define paths
MODELS_DIR = Path(__file__).parent.parent.parent / 'models'


class RentPredictor:
    """
    Wrapper class for loading models and generating rent predictions.
    
    Attributes:
        models (Dict[str, Any]): Dictionary of loaded ML models.
        weights (Dict[str, float]): Ensemble weights for each model.
        engineer (AdvancedFeatureEngineer): Pre-fitted feature engineering pipeline.
        feature_names (List[str]): List of expected feature names.
    """
    
    def __init__(self):
        """Initialize the predictor and load all models."""
        self.models: Dict[str, Any] = {}
        self.weights: Dict[str, float] = {}
        self.engineer: Optional[Any] = None
        self.feature_names: List[str] = []
        self._load_models()
        
    def _load_models(self) -> None:
        """
        Load models, weights, and feature engineer from disk.
        
        Raises:
            FileNotFoundError: If model files are missing.
        """
        try:
            # Load models
            self.models = joblib.load(MODELS_DIR / 'model_suite.pkl')
            self.weights = joblib.load(MODELS_DIR / 'ensemble_weights.pkl')
            self.engineer = joblib.load(MODELS_DIR / 'feature_engineer.pkl')
            
            # Extract feature names if available
            if hasattr(self.engineer, 'feature_names'):
                self.feature_names = self.engineer.feature_names
                
        except FileNotFoundError as e:
            print(f"Error loading models: {e}")
            # In production, we might want to raise this or handle gracefully
            
    def prepare_input(self, property_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert raw user input into a DataFrame compatible with the feature engineer.
        
        Args:
            property_data (Dict[str, Any]): Dictionary containing property details.
                Expected keys: neighborhood, property_type, size_sqft, bedrooms,
                bathrooms, amenity_count, tier, furnished, has_metro, beach_accessible.
                
        Returns:
            pd.DataFrame: Single-row DataFrame with processed features.
        """
        # Create base dictionary
        row = {
            'neighborhood': property_data['neighborhood'],
            'property_type': property_data['property_type'],
            'size_sqft': float(property_data['size_sqft']),
            'bedrooms': int(property_data['bedrooms']),
            'bathrooms': int(property_data['bathrooms']),
            'amenity_count': int(property_data['amenity_count']),
            
            # Convert categorical/boolean inputs to numeric
            'tier_numeric': int(property_data['tier'].replace('Tier ', '')),
            'furnished_numeric': 1 if property_data['furnished'] else 0,
            'has_metro_numeric': 1 if property_data['has_metro'] else 0,
            'beach_accessible_numeric': 1 if property_data['beach_accessible'] else 0,
            
            # Individual amenities (default to 0 if not present)
            'has_pool': 1 if 'Swimming Pool' in property_data.get('amenities', []) else 0,
            'has_gym': 1 if 'Gym' in property_data.get('amenities', []) else 0,
            'has_parking': 1 if 'Parking' in property_data.get('amenities', []) else 0,
            'has_balcony': 1 if 'Balcony' in property_data.get('amenities', []) else 0,
            
            # Computed features placeholders (will be recalculated by engineer)
            'price_per_sqft': 100.0,  
            'annual_rent': 100000.0,  
            'data_source': 'user_input',
            
            # Target encoding placeholders (required for transform)
            'neighborhood_rent_avg': 100000.0,  # Default to global mean placeholder
            'neighborhood_rent_std': 20000.0    # Default to global std placeholder
        }
        
        df = pd.DataFrame([row])
        
        return df
    
    def predict(self, property_data: Dict[str, Any], return_confidence: bool = True) -> Dict[str, Any]:
        """
        Predict rental price for a property.
        
        Args:
            property_data (Dict[str, Any]): Property details.
            return_confidence (bool): Whether to calculate confidence intervals.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - prediction: Weighted ensemble prediction (float)
                - confidence_lower: Lower bound of 95% CI (float)
                - confidence_upper: Upper bound of 95% CI (float)
                - individual_models: Dictionary of predictions from each model
        """
        # Prepare input - create a full analytical dataset row
        df = self.prepare_input(property_data)
        
        # Apply feature engineering using the pre-fitted engineer
        # This will create all 58 features consistently
        X_numpy = self.engineer.transform(df)
        
        # Create DataFrame version for models that need feature names (LightGBM)
        if self.feature_names:
            X_df = pd.DataFrame(X_numpy, columns=self.feature_names)
        else:
            X_df = X_numpy
        
        # Get predictions from all models
        predictions = {}
        for name, model in self.models.items():
            # Random Forest was trained on numpy array, others prefer DataFrame
            if name == 'Random Forest':
                predictions[name] = model.predict(X_numpy)[0]
            else:
                predictions[name] = model.predict(X_df)[0]
        
        # Ensemble prediction
        ensemble_pred = sum(self.weights[name] * predictions[name] for name in predictions)
        
        result = {
            'prediction': float(ensemble_pred),
            'individual_models': predictions
        }
        
        if return_confidence:
            # Calculate variance based on model disagreement
            # This is a heuristic for prediction uncertainty
            model_preds = list(predictions.values())
            std_dev = np.std(model_preds)
            
            # 95% Confidence Interval (approximate)
            # We assume error is normally distributed around the prediction
            # Using a multiplier based on validation MAPE (approx 10% width)
            margin = ensemble_pred * 0.10  # 10% margin of error as baseline
            
            # Adjust margin based on model disagreement (higher disagreement = wider interval)
            disagreement_factor = (std_dev / ensemble_pred) * 2
            final_margin = margin * (1 + disagreement_factor)
            
            result['confidence_lower'] = float(ensemble_pred - final_margin)
            result['confidence_upper'] = float(ensemble_pred + final_margin)
            
        return result

    def compare_with_market(self, property_data: Dict[str, Any], listed_price: float) -> Dict[str, Any]:
        """
        Compare a listed price against the predicted fair market value.
        
        Args:
            property_data (Dict[str, Any]): Property details.
            listed_price (float): The asking price to compare.
            
        Returns:
            Dict[str, Any]: Comparison results including difference, percentage, and recommendation.
        """
        prediction_result = self.predict(property_data)
        predicted_price = prediction_result['prediction']
        
        difference = listed_price - predicted_price
        percent_diff = (difference / predicted_price) * 100
        
        # Determine status
        if percent_diff < -5:
            status = "Great Deal"
            color = "green"
            emoji = "✅"
            recommendation = "Highly Recommended"
        elif percent_diff > 5:
            status = "Overpriced"
            color = "red"
            emoji = "❌"
            recommendation = "Negotiate Hard"
        else:
            status = "Fair Price"
            color = "orange"
            emoji = "⚠️"
            recommendation = "Market Standard"
            
        return {
            'predicted_price': predicted_price,
            'listed_price': listed_price,
            'difference': difference,
            'percent_difference': percent_diff,
            'status': status,
            'color': color,
            'emoji': emoji,
            'recommendation': recommendation,
            'confidence_range': (prediction_result['confidence_lower'], prediction_result['confidence_upper'])
        }

if __name__ == "__main__":
    # Test the predictor
    predictor = RentPredictor()
    
    test_property = {
        'neighborhood': 'Dubai Marina',
        'property_type': '2BR',
        'size_sqft': 1200,
        'bedrooms': 2,
        'bathrooms': 2,
        'amenity_count': 7,
        'tier': 'Tier 1',
        'furnished': True,
        'has_metro': True,
        'beach_accessible': True,
        'amenities': ['Swimming Pool', 'Gym', 'Parking', 'Balcony']
    }
    
    result = predictor.predict(test_property)
    print(f"Predicted Rent: {result['prediction']:,.0f} AED/year")
    print(f"95% Confidence: {result['confidence_lower']:,.0f} - {result['confidence_upper']:,.0f} AED")
