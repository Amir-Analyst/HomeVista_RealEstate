# Manual Data Regeneration & Model Training Guide

Follow these steps to completely refresh your data and models. This ensures all changes (including the new price distribution) are fully applied.

**⚠️ Run these commands in your terminal (PowerShell), NOT inside the IDE's interactive window.**

### Step 1: Regenerate Synthetic Data
This will create 16,000+ new listings with the corrected price distribution (Beta 1.2, 6).

```powershell
python src/data_generator.py
```
*Expected Output:* `Generated 16050 synthetic listings...`

### Step 2: Process Data
This cleans the data and prepares it for training.

```powershell
python src/data_processor.py
```
*Expected Output:* `Data processing complete. Saved to data/processed/analytical_dataset.csv`

### Step 3: Retrain Models (Heavy Compute)
This trains Random Forest, XGBoost, LightGBM, and CatBoost. It may take 5-10 minutes.

```powershell
python src/ml/model_training.py
```
*Expected Output:* `Training complete. Models saved to models/`

### Step 4: Verify Correction
Check if the new prices match the target (Mean ~65k-68k).

```powershell
python verify_correction.py
```
*(Note: If you deleted this script during cleanup, you can skip this step or ask me to recreate it.)*

### Step 5: Restart App
To see the changes, you must restart the Streamlit app.

1. Stop the current app (`Ctrl+C` in terminal).
2. Run:
```powershell
streamlit run app.py
```
