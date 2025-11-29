"""
Multi-Model Ensemble for Rental Price Prediction
Trains XGBoost, LightGBM, Random Forest, and CatBoost models
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, mean_absolute_percentage_error
import joblib
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
import config
from ml.feature_engineering import AdvancedFeatureEngineer


def load_data():
    """Load analytical dataset"""
    return pd.read_csv(config.FILE_ANALYTICAL_DATASET)


def train_model_suite(X_train, y_train, X_val, y_val):
    """
    Train 4 different models and compare performance
    
    Returns:
        models: Dict of trained models
        scores: Dict of validation scores
    """
    models = {}
    scores = {}
    
    print("\n" + "="*60)
    print("TRAINING MODEL SUITE")
    print("="*60)
    
    # 1. Random Forest
    print("\n[1/4] Training Random Forest...")
    rf = RandomForestRegressor(
        n_estimators=100,  # Reduced from 200
        max_depth=15,      # Reduced from 30
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_val)
    scores['Random Forest'] = {
        'MAE': mean_absolute_error(y_val, rf_pred),
        'RMSE': np.sqrt(mean_squared_error(y_val, rf_pred)),
        'R2': r2_score(y_val, rf_pred),
        'MAPE': mean_absolute_percentage_error(y_val, rf_pred) * 100
    }
    models['Random Forest'] = rf
    print(f"  R²: {scores['Random Forest']['R2']:.4f}, MAPE: {scores['Random Forest']['MAPE']:.2f}%")
    
    # 2. XGBoost
    print("\n[2/4] Training XGBoost...")
    xgb = XGBRegressor(
        n_estimators=150,  # Reduced from 200
        learning_rate=0.05,
        max_depth=6,       # Reduced from 10
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbosity=0,
        early_stopping_rounds=20
    )
    xgb.fit(X_train, y_train, 
            eval_set=[(X_val, y_val)],
            verbose=False)
    xgb_pred = xgb.predict(X_val)
    scores['XGBoost'] = {
        'MAE': mean_absolute_error(y_val, xgb_pred),
        'RMSE': np.sqrt(mean_squared_error(y_val, xgb_pred)),
        'R2': r2_score(y_val, xgb_pred),
        'MAPE': mean_absolute_percentage_error(y_val, xgb_pred) * 100
    }
    models['XGBoost'] = xgb
    print(f"  R²: {scores['XGBoost']['R2']:.4f}, MAPE: {scores['XGBoost']['MAPE']:.2f}%")
    
    # 3. LightGBM
    print("\n[3/4] Training LightGBM...")
    lgbm = LGBMRegressor(
        n_estimators=150,  # Reduced from 200
        learning_rate=0.05,
        max_depth=6,       # Reduced from 10
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    lgbm.fit(X_train, y_train,
             eval_set=[(X_val, y_val)],
             callbacks=[])
    lgbm_pred = lgbm.predict(X_val)
    scores['LightGBM'] = {
        'MAE': mean_absolute_error(y_val, lgbm_pred),
        'RMSE': np.sqrt(mean_squared_error(y_val, lgbm_pred)),
        'R2': r2_score(y_val, lgbm_pred),
        'MAPE': mean_absolute_percentage_error(y_val, lgbm_pred) * 100
    }
    models['LightGBM'] = lgbm
    print(f"  R²: {scores['LightGBM']['R2']:.4f}, MAPE: {scores['LightGBM']['MAPE']:.2f}%")
    
    # 4. CatBoost
    print("\n[4/4] Training CatBoost...")
    cat = CatBoostRegressor(
        iterations=150,    # Reduced from 200
        learning_rate=0.05,
        depth=6,           # Reduced from 10
        random_state=42,
        verbose=0,
        allow_writing_files=False
    )
    cat.fit(X_train, y_train, eval_set=(X_val, y_val), early_stopping_rounds=20)
    cat_pred = cat.predict(X_val)
    scores['CatBoost'] = {
        'MAE': mean_absolute_error(y_val, cat_pred),
        'RMSE': np.sqrt(mean_squared_error(y_val, cat_pred)),
        'R2': r2_score(y_val, cat_pred),
        'MAPE': mean_absolute_percentage_error(y_val, cat_pred) * 100
    }
    models['CatBoost'] = cat
    print(f"  R²: {scores['CatBoost']['R2']:.4f}, MAPE: {scores['CatBoost']['MAPE']:.2f}%")
    
    return models, scores


def create_ensemble(models, X_val, y_val):
    """
    Create weighted ensemble based on validation performance
    
    Returns:
        weights: Optimal model weights
        ensemble_pred: Ensemble predictions
    """
    print("\n" + "="*60)
    print("CREATING ENSEMBLE")
    print("="*60)
    
    # Get individual predictions
    predictions = {}
    for name, model in models.items():
        predictions[name] = model.predict(X_val)
    
    # Calculate optimal weights (inverse of MAPE)
    mapes = {name: mean_absolute_percentage_error(y_val, pred) 
             for name, pred in predictions.items()}
    
    # Inverse MAPE as weights (lower error = higher weight)
    inv_mape = {name: 1/mape for name, mape in mapes.items()}
    total = sum(inv_mape.values())
    weights = {name: w/total for name, w in inv_mape.items()}
    
    print("\nOptimal Weights:")
    for name, weight in weights.items():
        print(f"  {name}: {weight:.3f}")
    
    # Create ensemble prediction
    ensemble_pred = sum(weights[name] * predictions[name] for name in predictions)
    
    # Evaluate ensemble
    ensemble_r2 = r2_score(y_val, ensemble_pred)
    ensemble_mape = mean_absolute_percentage_error(y_val, ensemble_pred) * 100
    
    print(f"\nEnsemble Performance:")
    print(f"  R²: {ensemble_r2:.4f}")
    print(f"  MAPE: {ensemble_mape:.2f}%")
    
    return weights, ensemble_pred


def main():
    """Main training pipeline"""
    # Load data
    df = load_data()
    
    # Feature engineering
    print("\n[INFO] Engineering features...")
    engineer = AdvancedFeatureEngineer()
    X, y, feature_names = engineer.fit_transform(df)
    
    # Split data
    print("\n[INFO] Splitting data...")
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )
    
    print(f"  Training: {len(X_train):,} samples")
    print(f"  Validation: {len(X_val):,} samples")
    print(f"  Test: {len(X_test):,} samples")
    
    # Train models
    models, scores = train_model_suite(X_train, y_train, X_val, y_val)
    
    # Create ensemble
    weights, ensemble_pred = create_ensemble(models, X_val, y_val)
    
    # Save models
    print("\n[INFO] Saving models...")
    config.MODELS_DIR.mkdir(exist_ok=True)
    
    joblib.dump(models, config.MODELS_DIR / 'model_suite.pkl')
    joblib.dump(weights, config.MODELS_DIR / 'ensemble_weights.pkl')
    joblib.dump(engineer, config.MODELS_DIR / 'feature_engineer.pkl')
    
    print(f"[SUCCESS] Models saved to {config.MODELS_DIR}")


if __name__ == "__main__":
    main()
