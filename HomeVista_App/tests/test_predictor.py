"""
Unit tests for RentPredictor class.
"""

import pytest
import pandas as pd
import numpy as np
from src.dashboard.predictor import RentPredictor

@pytest.fixture
def predictor():
    """Fixture to initialize predictor."""
    return RentPredictor()

@pytest.fixture
def sample_property():
    """Fixture for a sample property dictionary."""
    return {
        'neighborhood': 'Dubai Marina',
        'property_type': '2BR',
        'size_sqft': 1200,
        'bedrooms': 2,
        'bathrooms': 2,
        'amenity_count': 5,
        'tier': 'Tier 1',
        'furnished': True,
        'has_metro': True,
        'beach_accessible': True,
        'amenities': ['Swimming Pool', 'Gym', 'Parking', 'Balcony']
    }

def test_prepare_input(predictor, sample_property):
    """Test if input dictionary is correctly converted to DataFrame."""
    df = predictor.prepare_input(sample_property)
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df['neighborhood'].iloc[0] == 'Dubai Marina'
    assert df['tier_numeric'].iloc[0] == 1
    assert df['furnished_numeric'].iloc[0] == 1
    assert 'neighborhood_rent_avg' in df.columns

def test_predict_structure(predictor, sample_property):
    """Test if predict returns correct dictionary structure."""
    result = predictor.predict(sample_property)
    
    assert 'prediction' in result
    assert 'confidence_lower' in result
    assert 'confidence_upper' in result
    assert 'individual_models' in result
    assert isinstance(result['prediction'], float)
    assert result['prediction'] > 0

def test_confidence_interval(predictor, sample_property):
    """Test if confidence interval is logical."""
    result = predictor.predict(sample_property)
    
    assert result['confidence_lower'] < result['prediction']
    assert result['confidence_upper'] > result['prediction']

def test_compare_with_market(predictor, sample_property):
    """Test market comparison logic."""
    # Test fair price
    prediction = predictor.predict(sample_property)['prediction']
    result = predictor.compare_with_market(sample_property, prediction)
    assert result['status'] == "Fair Price"
    
    # Test overpriced
    high_price = prediction * 1.2
    result_high = predictor.compare_with_market(sample_property, high_price)
    assert result_high['status'] == "Overpriced"
    
    # Test great deal
    low_price = prediction * 0.8
    result_low = predictor.compare_with_market(sample_property, low_price)
    assert result_low['status'] == "Great Deal"
