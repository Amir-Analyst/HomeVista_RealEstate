"""
Model Evaluation and Explainability using SHAP
"""

import shap
import matplotlib.pyplot as plt
import joblib
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
import config


def load_model_suite():
    """Load trained models and artifacts"""
    models = joblib.load(config.MODELS_DIR / 'model_suite.pkl')
    weights = joblib.load(config.MODELS_DIR / 'ensemble_weights.pkl')
    engineer = joblib.load(config.MODELS_DIR / 'feature_engineer.pkl')
    return models, weights, engineer


def generate_shap_values(model, X_sample):
    """
    Generate SHAP values for a given model
    
    Args:
        model: Trained model (Tree-based)
        X_sample: Sample of data for explanation
    """
    print(f"\n[INFO] Generating SHAP values for {type(model).__name__}...")
    
    # Create explainer
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)
    
    return explainer, shap_values


def plot_shap_summary(shap_values, X_sample, title="SHAP Summary Plot"):
    """Generate global feature importance plot"""
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_sample, show=False)
    plt.title(title)
    plt.tight_layout()
    
    # Save plot
    output_path = config.REPORTS_DIR / 'figures' / 'shap_summary.png'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    print(f"[SUCCESS] Saved SHAP summary to {output_path}")
    plt.close()


def plot_shap_waterfall(explainer, shap_values, X_sample, index=0):
    """Generate waterfall plot for a single prediction"""
    plt.figure(figsize=(10, 6))
    
    # For some models shap_values is a list, handle that
    if isinstance(shap_values, list):
        sv = shap_values[index]
    else:
        sv = shap_values[index]
        
    shap.plots.waterfall(shap.Explanation(values=sv, 
                                         base_values=explainer.expected_value, 
                                         data=X_sample.iloc[index], 
                                         feature_names=X_sample.columns),
                        show=False)
    
    output_path = config.REPORTS_DIR / 'figures' / 'shap_waterfall.png'
    plt.savefig(output_path, bbox_inches='tight')
    print(f"[SUCCESS] Saved SHAP waterfall to {output_path}")
    plt.close()


def evaluate_ensemble(models, weights, X_test, y_test):
    """Evaluate ensemble performance on test set"""
    print("\n" + "="*60)
    print("ENSEMBLE EVALUATION")
    print("="*60)
    
    predictions = {}
    for name, model in models.items():
        predictions[name] = model.predict(X_test)
        
    ensemble_pred = sum(weights[name] * predictions[name] for name in predictions)
    
    # Metrics
    from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, mean_absolute_percentage_error
    
    r2 = r2_score(y_test, ensemble_pred)
    mae = mean_absolute_error(y_test, ensemble_pred)
    rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
    mape = mean_absolute_percentage_error(y_test, ensemble_pred) * 100
    
    print(f"Test Set Performance:")
    print(f"  R²: {r2:.4f}")
    print(f"  MAE: {mae:,.0f} AED")
    print(f"  RMSE: {rmse:,.0f} AED")
    print(f"  MAPE: {mape:.2f}%")
    
    return ensemble_pred


if __name__ == "__main__":
    # Example usage
    models, weights, engineer = load_model_suite()
    
    # Load data (simplified for example)
    df = pd.read_csv(config.FILE_ANALYTICAL_DATASET)
    X, y, feature_names = engineer.fit_transform(df)
    
    # Convert to DataFrame for SHAP
    X_df = pd.DataFrame(X, columns=feature_names)
    
    # Use a sample for SHAP (it's slow on full dataset)
    X_sample = X_df.sample(1000, random_state=42)
    
    # Generate SHAP for best model (highest weight)
    best_model_name = max(weights, key=weights.get)
    best_model = models[best_model_name]
    
    explainer, shap_values = generate_shap_values(best_model, X_sample)
    plot_shap_summary(shap_values, X_sample)
    plot_shap_waterfall(explainer, shap_values, X_sample)
