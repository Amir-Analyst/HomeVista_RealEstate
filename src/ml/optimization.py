"""
Hyperparameter Optimization using Optuna
Optimizes XGBoost, LightGBM, Random Forest, and CatBoost models
"""

import optuna
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
import joblib
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
import config
from ml.feature_engineering import AdvancedFeatureEngineer

def load_and_prep_data():
    """Load and prepare data for optimization"""
    df = pd.read_csv(config.FILE_ANALYTICAL_DATASET)
    
    engineer = AdvancedFeatureEngineer()
    X, y, _ = engineer.fit_transform(df)
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.5, random_state=42
    )
    
    return X_train, y_train, X_val, y_val

def objective_xgb(trial, X_train, y_train, X_val, y_val):
    """XGBoost objective function"""
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 15),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'random_state': 42,
        'n_jobs': -1,
        'verbosity': 0,
        'early_stopping_rounds': 20
    }
    
    model = XGBRegressor(**params)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
    
    preds = model.predict(X_val)
    return mean_absolute_error(y_val, preds)

def objective_lgbm(trial, X_train, y_train, X_val, y_val):
    """LightGBM objective function"""
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 15),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'num_leaves': trial.suggest_int('num_leaves', 20, 100),
        'random_state': 42,
        'n_jobs': -1,
        'verbose': -1
    }
    
    model = LGBMRegressor(**params)
    model.fit(X_train, y_train, eval_set=[(X_val, y_val)], callbacks=[])
    
    preds = model.predict(X_val)
    return mean_absolute_error(y_val, preds)

def objective_rf(trial, X_train, y_train, X_val, y_val):
    """Random Forest objective function"""
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 500),
        'max_depth': trial.suggest_int('max_depth', 5, 30),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
        'random_state': 42,
        'n_jobs': -1,
        'verbose': 0
    }
    
    model = RandomForestRegressor(**params)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_val)
    return mean_absolute_error(y_val, preds)

def objective_cat(trial, X_train, y_train, X_val, y_val):
    """CatBoost objective function"""
    params = {
        'iterations': trial.suggest_int('iterations', 100, 1000),
        'depth': trial.suggest_int('depth', 4, 12),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
        'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1, 10),
        'random_state': 42,
        'verbose': 0,
        'allow_writing_files': False
    }
    
    model = CatBoostRegressor(**params)
    model.fit(X_train, y_train, eval_set=(X_val, y_val), early_stopping_rounds=20)
    
    preds = model.predict(X_val)
    return mean_absolute_error(y_val, preds)

def optimize_all():
    """Run optimization for all models"""
    X_train, y_train, X_val, y_val = load_and_prep_data()
    
    print("="*60)
    print("STARTING HYPERPARAMETER OPTIMIZATION")
    print("="*60)
    
    studies = {}
    
    # 1. XGBoost
    print("\n[1/4] Optimizing XGBoost...")
    study_xgb = optuna.create_study(direction='minimize')
    study_xgb.optimize(lambda trial: objective_xgb(trial, X_train, y_train, X_val, y_val), n_trials=20)
    studies['XGBoost'] = study_xgb
    print(f"  Best MAE: {study_xgb.best_value:.2f}")
    
    # 2. LightGBM
    print("\n[2/4] Optimizing LightGBM...")
    study_lgbm = optuna.create_study(direction='minimize')
    study_lgbm.optimize(lambda trial: objective_lgbm(trial, X_train, y_train, X_val, y_val), n_trials=20)
    studies['LightGBM'] = study_lgbm
    print(f"  Best MAE: {study_lgbm.best_value:.2f}")
    
    # 3. Random Forest (fewer trials as it's slower)
    print("\n[3/4] Optimizing Random Forest...")
    study_rf = optuna.create_study(direction='minimize')
    study_rf.optimize(lambda trial: objective_rf(trial, X_train, y_train, X_val, y_val), n_trials=10)
    studies['Random Forest'] = study_rf
    print(f"  Best MAE: {study_rf.best_value:.2f}")
    
    # 4. CatBoost
    print("\n[4/4] Optimizing CatBoost...")
    study_cat = optuna.create_study(direction='minimize')
    study_cat.optimize(lambda trial: objective_cat(trial, X_train, y_train, X_val, y_val), n_trials=10)
    studies['CatBoost'] = study_cat
    print(f"  Best MAE: {study_cat.best_value:.2f}")
    
    # Save best parameters
    print("\n[INFO] Saving best parameters...")
    best_params = {name: study.best_params for name, study in studies.items()}
    joblib.dump(best_params, config.MODELS_DIR / 'best_hyperparameters.pkl')
    print(f"[SUCCESS] Parameters saved to {config.MODELS_DIR / 'best_hyperparameters.pkl'}")

if __name__ == "__main__":
    optimize_all()
