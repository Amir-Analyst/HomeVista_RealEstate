# 🛠️ Technical Architecture & Implementation Details

## 🏗️ System Overview

HomeVista is built on a modular architecture designed for scalability and maintainability. The system consists of three core components:
1.  **Data Pipeline**: Ingestion, cleaning, and synthetic augmentation.
2.  **ML Engine**: Feature engineering and ensemble inference.
3.  **Dashboard**: Interactive Streamlit frontend.

---

## 🧠 Machine Learning Pipeline

### 1. Data Strategy
*   **Hybrid Dataset**: Combines real-world scraped data (Bayut.com) with statistically generated synthetic data to ensure full market coverage.
*   **Synthetic Generation**: Uses a **Beta(1.2, 6) distribution** to accurately model the right-skewed nature of rental prices (most units are affordable, few are ultra-luxury).
*   **Volume**: 16,050 total listings across 20 key Dubai neighborhoods.

### 2. Feature Engineering (58 Features)
We transform 10 raw inputs into 58 rich features to capture market nuances:
*   **Interaction Terms**: `size_per_bedroom`, `tier_metro_interaction` (captures premium of location + connectivity).
*   **Polynomial Features**: `size_sqft_squared` (models diminishing returns of size).
*   **Domain Features**: `is_luxury`, `has_complete_amenities`.
*   **Target Encoding**: Bayesian-smoothed neighborhood rent averages to handle high-cardinality location data.

### 3. Model Ensemble Architecture
The core prediction engine uses a weighted ensemble of four state-of-the-art algorithms:

| Model | Weight | Role |
|-------|--------|------|
| **LightGBM** | **30%** | Primary driver; excellent speed and accuracy on tabular data. |
| **XGBoost** | **27%** | Captures complex non-linear interactions. |
| **Random Forest** | **25%** | Provides robustness and reduces variance (bagging). |
| **CatBoost** | **18%** | Handles categorical features (Neighborhood, Tier) natively. |

**Performance Metrics:**
*   **R² Score**: 0.9972 (Explains 99.7% of price variance)
*   **MAPE**: 0.95% (Average error < 1%)
*   **Inference Time**: < 50ms per prediction

---

## 💻 Application Architecture

### Backend Logic (`src/`)
*   **`predictor.py`**: Handles model loading, input validation, and ensemble aggregation. Includes robust error handling for missing model files.
*   **`data_generator.py`**: Generates synthetic data using statistical distributions derived from market research.
*   **`components.py`**: Reusable UI components with strict type mapping (e.g., mapping "Tier 1 (Premium)" UI selection to backend "Luxury" category).

### Frontend (`app.py` + `pages/`)
*   **Streamlit**: Chosen for rapid prototyping and interactive data visualization.
*   **Caching**: Uses `@st.cache_resource` to load heavy ML models only once, ensuring instant page loads after initialization.
*   **Plotly**: Interactive charts for market exploration.

---

## 🔄 Deployment Strategy

*   **Model Hosting**: Due to GitHub's 25MB limit, the 72MB model suite is hosted externally (Google Drive) and downloaded automatically via `setup_models.py` during the first run.
*   **Environment**: Python 3.11 with pinned dependencies in `requirements.txt`.
*   **CI/CD**: GitHub Actions for automated testing (`pytest`).

---

## 🧪 Testing & Validation

*   **Unit Tests**: Validate feature engineering logic and model inference.
*   **Integration Tests**: Ensure the dashboard components interact correctly with the backend.
*   **Manual Validation**:
    *   **Price Distribution**: Verified using `verify_correction.py` to ensure mean rents align with Dubai Land Department reports.
    *   **Tier Logic**: Verified that changing location tiers (Budget vs Luxury) correctly impacts price predictions.
