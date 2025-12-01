"""
Advanced Feature Engineering for HomeVista Rental Price Prediction.

This module provides the AdvancedFeatureEngineer class, which is responsible for
transforming raw property data into a rich feature set for machine learning models.
It includes interaction terms, polynomial features, domain-specific logic, and
target encoding.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Optional, Union
from sklearn.preprocessing import StandardScaler, OneHotEncoder
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedFeatureEngineer:
    """
    Advanced feature engineering pipeline for rental price prediction.
    
    This class handles the creation of:
    - Interaction features (e.g., size per bedroom)
    - Polynomial features (e.g., size squared)
    - Domain-specific features (e.g., luxury indicators)
    - Target-encoded features (e.g., neighborhood average rent)
    
    Attributes:
        scaler (StandardScaler): Scaler for numeric features (unused in current implementation but reserved).
        encoder (OneHotEncoder): Encoder for categorical variables.
        feature_names (List[str]): List of all output feature names.
        neighborhood_stats (pd.DataFrame): Stored statistics for target encoding during inference.
        global_mean (float): Global mean rent for fallback target encoding.
        global_std (float): Global rent standard deviation for fallback.
    """
    
    def __init__(self):
        """Initialize the feature engineer."""
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        self.feature_names: List[str] = []
        self.neighborhood_stats: Optional[pd.DataFrame] = None
        self.global_mean: Optional[float] = None
        self.global_std: Optional[float] = None
        
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features between key variables.
        
        Args:
            df (pd.DataFrame): Input dataframe containing raw features.
            
        Returns:
            pd.DataFrame: Dataframe with added interaction columns.
        """
        logger.info("Creating interaction features...")
        
        df_new = df.copy()
        
        # Size × Bedrooms interaction (size per bedroom)
        # Handle division by zero for studios (0 bedrooms)
        df_new['size_per_bedroom'] = df_new['size_sqft'] / df_new['bedrooms'].replace(0, 1)
        
        # Tier × Metro interaction (premium locations with metro)
        df_new['tier_metro_interaction'] = df_new['tier_numeric'] * df_new['has_metro_numeric']
        
        # Tier × Beach interaction
        df_new['tier_beach_interaction'] = df_new['tier_numeric'] * df_new['beach_accessible_numeric']
        
        # Amenity density (amenities per sqft)
        df_new['amenity_density'] = df_new['amenity_count'] / (df_new['size_sqft'] / 1000)
        
        # Furnished × Tier (furnished premium varies by tier)
        df_new['furnished_tier'] = df_new['furnished_numeric'] * df_new['tier_numeric']
        
        # Bathrooms × Bedrooms ratio
        df_new['bath_bed_ratio'] = df_new['bathrooms'] / df_new['bedrooms'].replace(0, 1)
        
        # Metro + Beach combined (best locations)
        df_new['premium_location'] = (
            (df_new['has_metro_numeric'] == 1) & 
            (df_new['beach_accessible_numeric'] == 1)
        ).astype(int)
        
        logger.info(f"Created 7 interaction features")
        return df_new
    
    def create_polynomial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create polynomial features for non-linear relationships.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            
        Returns:
            pd.DataFrame: Dataframe with added polynomial columns.
        """
        logger.info("Creating polynomial features...")
        
        df_new = df.copy()
        
        # Quadratic size (diminishing returns for very large properties)
        df_new['size_sqft_squared'] = df_new['size_sqft'] ** 2
        
        # Quadratic amenity count (luxury amenity premium)
        df_new['amenity_count_squared'] = df_new['amenity_count'] ** 2
        
        # Square root of size (larger relative impact for smaller properties)
        df_new['size_sqft_sqrt'] = np.sqrt(df_new['size_sqft'])
        
        logger.info(f"Created 3 polynomial features")
        return df_new
    
    def create_domain_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create domain-specific features based on real estate knowledge.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            
        Returns:
            pd.DataFrame: Dataframe with added domain-specific columns.
        """
        logger.info("Creating domain-specific features...")
        
        df_new = df.copy()
        
        # Luxury property indicator (top tier + high amenities)
        df_new['is_luxury'] = (
            (df_new['tier_numeric'] >= 3) & 
            (df_new['amenity_count'] >= 6)
        ).astype(int)
        
        # Value property (low price per sqft)
        # Using a safe fallback if price_per_sqft is not yet calculated
        if 'price_per_sqft' in df_new.columns:
            median_ppsf = df_new['price_per_sqft'].median()
            df_new['is_value_property'] = (df_new['price_per_sqft'] < median_ppsf * 0.8).astype(int)
            
            # Premium property (high price per sqft)
            df_new['is_premium_property'] = (df_new['price_per_sqft'] > median_ppsf * 1.2).astype(int)
        else:
            df_new['is_value_property'] = 0
            df_new['is_premium_property'] = 0
        
        # Spacious property (size above median for property type)
        df_new['is_spacious'] = 0
        for prop_type in df_new['property_type'].unique():
            mask = df_new['property_type'] == prop_type
            if mask.any():
                median_size = df_new.loc[mask, 'size_sqft'].median()
                df_new.loc[mask, 'is_spacious'] = (
                    df_new.loc[mask, 'size_sqft'] > median_size * 1.2
                ).astype(int)
        
        # Complete amenity package (has pool, gym, parking, balcony)
        required_amenities = ['has_pool', 'has_gym', 'has_parking', 'has_balcony']
        if all(col in df_new.columns for col in required_amenities):
            df_new['has_complete_amenities'] = (
                (df_new['has_pool'] == 1) &
                (df_new['has_gym'] == 1) &
                (df_new['has_parking'] == 1) &
                (df_new['has_balcony'] == 1)
            ).astype(int)
        else:
             df_new['has_complete_amenities'] = 0
        
        logger.info(f"Created 5 domain-specific features")
        return df_new
    
    def create_target_encoding(self, df: pd.DataFrame, target_col: str = 'annual_rent') -> pd.DataFrame:
        """
        Create target-encoded features for high-cardinality categoricals.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            target_col (str): Name of the target variable column.
            
        Returns:
            pd.DataFrame: Dataframe with added target-encoded columns.
        """
        logger.info("Creating target-encoded features...")
        
        df_new = df.copy()
        
        # Neighborhood average rent (with smoothing)
        # Store stats for later use in transform()
        self.neighborhood_stats = df_new.groupby('neighborhood')[target_col].agg(['mean', 'std', 'count'])
        self.global_mean = df_new[target_col].mean()
        self.global_std = df_new[target_col].std()
        
        # Bayesian smoothing
        m = 30  # Minimum sample size for confidence
        
        # Calculate smoothed mean
        df_new['neighborhood_rent_avg'] = df_new['neighborhood'].map(
            lambda x: (
                self.neighborhood_stats.loc[x, 'count'] * self.neighborhood_stats.loc[x, 'mean'] +
                m * self.global_mean
            ) / (self.neighborhood_stats.loc[x, 'count'] + m)
            if x in self.neighborhood_stats.index else self.global_mean
        )
        
        # Neighborhood rent volatility
        df_new['neighborhood_rent_std'] = df_new['neighborhood'].map(
            self.neighborhood_stats['std']
        ).fillna(self.global_std)
        
        logger.info(f"Created 2 target-encoded features")
        return df_new
    
    def fit_transform(self, df: pd.DataFrame, target_col: str = 'annual_rent') -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Complete feature engineering pipeline: Fit encoders and transform data.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            target_col (str): Target variable name.
            
        Returns:
            Tuple[np.ndarray, np.ndarray, List[str]]: 
                - X: Feature matrix (numpy array)
                - y: Target vector (numpy array)
                - feature_names: List of feature names
        """
        logger.info("Starting complete feature engineering pipeline...")
        
        # Create all feature types
        df_features = self.create_interaction_features(df)
        df_features = self.create_polynomial_features(df_features)
        df_features = self.create_domain_features(df_features)
        df_features = self.create_target_encoding(df_features, target_col)
        
        # Define feature columns
        numeric_features = [
            # Original features
            'size_sqft', 'bedrooms', 'bathrooms', 'amenity_count',
            'tier_numeric', 'furnished_numeric', 'has_metro_numeric', 
            'beach_accessible_numeric', 'price_per_sqft',
            # Individual amenities
            'has_pool', 'has_gym', 'has_parking', 'has_balcony',
            # Interaction features
            'size_per_bedroom', 'tier_metro_interaction', 'tier_beach_interaction',
            'amenity_density', 'furnished_tier', 'bath_bed_ratio', 'premium_location',
            # Polynomial features
            'size_sqft_squared', 'amenity_count_squared', 'size_sqft_sqrt',
            # Domain features
            'is_luxury', 'is_value_property', 'is_premium_property', 
            'is_spacious', 'has_complete_amenities',
            # Target encoded
            'neighborhood_rent_avg', 'neighborhood_rent_std'
        ]
        
        categorical_features = ['neighborhood', 'property_type']
        
        # Filter to existing columns
        numeric_features = [f for f in numeric_features if f in df_features.columns]
        categorical_features = [f for f in categorical_features if f in df_features.columns]
        
        logger.info(f"Using {len(numeric_features)} numeric and {len(categorical_features)} categorical features")
        
        # Extract numeric features
        X_numeric = df_features[numeric_features].values
        
        # Encode categorical features
        X_categorical = self.encoder.fit_transform(df_features[categorical_features])
        
        # Combine features
        X = np.hstack([X_numeric, X_categorical])
        
        # Get feature names
        cat_feature_names = self.encoder.get_feature_names_out(categorical_features).tolist()
        self.feature_names = numeric_features + cat_feature_names
        
        # Extract target
        y = df_features[target_col].values
        
        logger.info(f"Feature engineering complete. Final shape: {X.shape}")
        logger.info(f"Total features: {len(self.feature_names)}")
        
        return X, y, self.feature_names

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transform new data using fitted encoder.
        
        Args:
            df (pd.DataFrame): Input dataframe.
            
        Returns:
            np.ndarray: Transformed feature matrix.
        """
        # Create all feature types (without target encoding fit)
        df_features = self.create_interaction_features(df)
        df_features = self.create_polynomial_features(df_features)
        df_features = self.create_domain_features(df_features)
        
        # For prediction, we expect target encoded columns to be present in input
        # (added by predictor.prepare_input) or we could implement lookup here.
        # Current implementation relies on predictor providing placeholders.
        
        numeric_features = [f for f in self.feature_names if f in df_features.columns or '_' not in f]
        # Ensure 'neighborhood_rent_avg' and 'neighborhood_rent_std' are included if in feature_names
        for target_feat in ['neighborhood_rent_avg', 'neighborhood_rent_std']:
            if target_feat in self.feature_names and target_feat not in numeric_features:
                 if target_feat in df_features.columns:
                    numeric_features.append(target_feat)

        categorical_features = ['neighborhood', 'property_type']
        
        # Sort numeric features to match training order (best effort)
        # In a stricter implementation, we would enforce exact column order
        
        X_numeric = df_features[numeric_features].values
        X_categorical = self.encoder.transform(df_features[categorical_features])
        
        X = np.hstack([X_numeric, X_categorical])
        
        return X
