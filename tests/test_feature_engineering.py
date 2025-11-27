"""
Unit tests for AdvancedFeatureEngineer class.
"""

import pytest
import pandas as pd
import numpy as np
from src.ml.feature_engineering import AdvancedFeatureEngineer

@pytest.fixture
def engineer():
    """Fixture to initialize feature engineer."""
    return AdvancedFeatureEngineer()

@pytest.fixture
def sample_df():
    """Fixture for a sample dataframe."""
    return pd.DataFrame([{
        'neighborhood': 'Dubai Marina',
        'property_type': '2BR',
        'size_sqft': 1200,
        'bedrooms': 2,
        'bathrooms': 2,
        'amenity_count': 5,
        'tier_numeric': 4,
        'furnished_numeric': 1,
        'has_metro_numeric': 1,
        'beach_accessible_numeric': 1,
        'price_per_sqft': 100,
        'annual_rent': 120000,
        'has_pool': 1,
        'has_gym': 1,
        'has_parking': 1,
        'has_balcony': 1
    }])

def test_create_interaction_features(engineer, sample_df):
    """Test interaction feature creation."""
    df_new = engineer.create_interaction_features(sample_df)
    
    assert 'size_per_bedroom' in df_new.columns
    assert 'tier_metro_interaction' in df_new.columns
    assert df_new['size_per_bedroom'].iloc[0] == 600  # 1200 / 2

def test_create_polynomial_features(engineer, sample_df):
    """Test polynomial feature creation."""
    df_new = engineer.create_polynomial_features(sample_df)
    
    assert 'size_sqft_squared' in df_new.columns
    assert df_new['size_sqft_squared'].iloc[0] == 1440000  # 1200^2

def test_create_domain_features(engineer, sample_df):
    """Test domain feature creation."""
    df_new = engineer.create_domain_features(sample_df)
    
    assert 'is_luxury' in df_new.columns
    assert 'has_complete_amenities' in df_new.columns
    # Should be 0 because amenity_count is 5 (needs >= 6 for luxury)
    assert df_new['is_luxury'].iloc[0] == 0  

def test_fit_transform_shape(engineer, sample_df):
    """Test that fit_transform produces correct output shape."""
    # We need more than 1 sample for OneHotEncoder to learn categories effectively
    # but for shape check 1 is fine if we accept whatever categories it finds
    X, y, features = engineer.fit_transform(sample_df, target_col='annual_rent')
    
    assert isinstance(X, np.ndarray)
    assert len(features) > 0
    assert X.shape[1] == len(features)
