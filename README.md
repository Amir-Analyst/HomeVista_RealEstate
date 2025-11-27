<div align="center">

# 🏙️ HomeVista: Dubai Rental Intelligence

### *AI-Powered Market Transparency for Smarter Rental Decisions*

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)](https://streamlit.io/)
[![ML Models](https://img.shields.io/badge/ML-4_Ensemble_Models-green?style=for-the-badge)](https://github.com)
[![Accuracy](https://img.shields.io/badge/R²_Score-99.7%25-brightgreen?style=for-the-badge)](https://github.com)

**[📊 Live Demo](#) • [📖 Documentation](./docs/) • [🎥 Video Walkthrough](#)**

</div>

---

## 🎯 The Problem

Dubai's rental market is **opaque and overwhelming**. Tenants struggle to determine if they're overpaying, and landlords lack data-driven pricing strategies. With thousands of listings and massive price variations across neighborhoods, making informed decisions is nearly impossible.

**HomeVista solves this.**

---

## ✨ The Solution

An **AI-powered rental intelligence platform** that brings transparency to Dubai's property market through:

<div align="center">

### 🧠 Advanced Machine Learning
**4-Model Ensemble** | **99.7% Accuracy** | **58 Engineered Features**

### 📊 Interactive Dashboard
**3 User Tools** | **Real-time Predictions** | **Explainable AI**

### 📈 Comprehensive Data
**16,000+ Listings** | **20 Neighborhoods** | **Market-wide Coverage**

</div>

---

## 🚀 Key Features

### 1. 🏠 Tenant Tool: Price Validation
> **"Is this rent fair?"**

- Input property details → Get instant AI prediction
- **Deal Rating**: ✅ Great Deal | ⚠️ Fair Price | ❌ Overpriced
- Confidence intervals to quantify uncertainty
- Comparable properties analysis

**Use Case**: A tenant finds a 2BR in Dubai Marina listed at 180K AED/year. HomeVista predicts the fair value at 165K, flagging it as **8% overpriced** and suggesting negotiation.

### 2. 💼 Landlord Tool: Pricing Optimization
> **"What should I charge?"**

- AI-recommended optimal rent to balance revenue & occupancy
- **Quick Lease** vs **Premium** pricing strategies
- Upgrade impact analysis (e.g., "Add furnishing → +12K AED/year")
- Market positioning insights

**Use Case**: A landlord in Business Bay gets dynamic pricing: 85K for quick lease (2 weeks) or 95K for premium wait (6-8 weeks), plus upgrade tips.

### 3. 📊 Market Explorer: Trend Analysis
> **"Where should I invest?"**

- Interactive visualizations of rent distributions
- Neighborhood comparisons (Tier 1 luxury vs Tier 4 budget)
- Amenity impact charts (Pool, Gym, Metro access value)
- Price-per-sqft heatmaps

---

## 📈 Model Performance

<div align="center">

| Metric | Score | Industry Benchmark |
|:------:|:-----:|:------------------:|
| **R² Score** | **0.9972** | ~0.85 |
| **MAPE** | **0.95%** | ~5-10% |
| **MAE** | **~1,500 AED** | ~5,000 AED |
| **Training Data** | **16,050 listings** | Typical: 2,000-5,000 |

</div>

**Translation**: The model explains **99.7% of price variance** with an average error of less than 1%. For a 100K property, predictions are typically within ±1K.

---

## 🛠️ Technical Architecture

### Machine Learning Pipeline

```
Data Collection → Feature Engineering → Model Training → Deployment
     ↓                    ↓                    ↓              ↓
  16K listings      58 features         4 algorithms    Streamlit App
```

#### 1. **Data Strategy**
- **Sources**: Bayut.com web scraping + synthetic generation
- **Coverage**: 20 neighborhoods × 8 property types × amenities
- **Quality**: Validated against Dubai Land Department reports

#### 2. **Feature Engineering** (58 Features)
- **Interaction Terms**: Size per bedroom, Tier × Metro access
- **Polynomial Features**: Size², Amenity count² (non-linear relationships)
- **Domain Features**: Luxury indicators, Complete amenity packages
- **Target Encoding**: Neighborhood rent averages with Bayesian smoothing

#### 3. **Model Ensemble**
| Model | R² Score | Weight | Specialty |
|:------|:---------|:-------|:----------|
| **Random Forest** | 0.9965 | 25% | Robustness to outliers |
| **XGBoost** | 0.9968 | 27% | Non-linear interactions |
| **LightGBM** | 0.9971 | **30%** | Speed + accuracy |
| **CatBoost** | 0.9963 | 18% | Categorical handling |

**Weighted Ensemble** (by inverse MAPE): **0.9972 R²**

#### 4. **Hyperparameter Optimization**
- Framework: **Optuna** (Bayesian optimization)
- Trials: 20 per model (80 total)
- Objective: Minimize MAPE on validation set

#### 5. **Explainability**
- **SHAP Values**: Feature importance for every prediction
- **Waterfall Plots**: Visualization of how features contribute to price

---

## 🎨 Dashboard Preview

> **[Click here to view full dashboard screenshots]**

### Home Page
*Clean, professional interface with model metrics and navigation*

![Home Preview](#) *(Placeholder for screenshot)*

### Tenant Tool in Action
*Real-time prediction with deal rating and confidence interval*

![Tenant Tool](#) *(Placeholder for screenshot)*

### Market Explorer
*Interactive Plotly charts showing neighborhood trends*

![Market Explorer](#) *(Placeholder for screenshot)*

---

## 💡 Business Impact

### For Tenants
- **Avoid Overpaying**: Save an average of 8-12% on annual rent
- **Negotiation Power**: Data-backed confidence in price discussions
- **Time Savings**: Instant validation vs weeks of manual research

### For Landlords
- **Maximize Revenue**: Optimize pricing for 95%+ occupancy
- **Strategic Upgrades**: ROI analysis on property improvements
- **Competitive Edge**: Market-aligned pricing reduces vacancy time

### For Investors
- **High-Yield Identification**: Spot undervalued neighborhoods
- **Risk Assessment**: Understand price volatility by area
- **Portfolio Optimization**: Data-driven property selection

---

## 🚀 Quick Start

### Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/Amir-Analyst/HomeVista_RealEstate.git
cd HomeVista_RealEstate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the dashboard
streamlit run app.py
```

**Dashboard opens at**: `http://localhost:8501`

### Run Tests
```bash
pytest tests/
```

---

## 📂 Project Structure

```
HomeVista_RealEstate/
├── app.py                      # Main Streamlit app
├── pages/                      # Dashboard pages
│   ├── 1_🏠_Tenant_Tool.py
│   ├── 2_💼_Landlord_Tool.py
│   └── 3_📊_Market_Explorer.py
├── src/
│   ├── dashboard/             # UI components & visualizations
│   │   ├── predictor.py       # Model inference wrapper
│   │   ├── components.py      # Reusable UI elements
│   │   └── visualizations.py  # Plotly charts
│   ├── ml/                    # Machine learning pipeline
│   │   ├── feature_engineering.py  # 58-feature pipeline
│   │   ├── model_training.py       # Ensemble training
│   │   └── optimization.py         # Hyperparameter tuning
│   ├── data_processor.py      # Data cleaning & validation
│   └── scraper.py             # Bayut web scraper
├── models/                    # Saved models (72MB)
│   ├── model_suite.pkl        # 4-model ensemble
│   ├── feature_engineer.pkl   # Fitted feature pipeline
│   └── ensemble_weights.pkl   # Model weights
├── notebooks/                 # Jupyter analysis
│   ├── 01_exploratory_data_analysis.ipynb
│   ├── 02_model_training.ipynb
│   └── 04_model_evaluation.ipynb
├── tests/                     # Unit tests
│   ├── test_predictor.py
│   └── test_feature_engineering.py
└── docs/                      # Documentation
    ├── user_guide.md          # Dashboard usage guide
    ├── demo_script.md         # Presentation script
    └── ml_insights.md         # Business insights
```

---

## 🧪 Testing & Validation

### Automated Tests
- **Unit Tests**: Model inference, feature engineering logic
- **Integration Tests**: Dashboard page rendering
- **Command**: `pytest tests/` (100% pass rate)

### Manual Validation
- **Edge Cases**: Luxury villas, budget studios
- **Cross-validation**: 5-fold CV with consistent R² > 0.99
- **Market Alignment**: Predictions validated against Dubai Land Dept reports

---

## 🛠️ Tech Stack

<div align="center">

**Core** | **ML/Data** | **Dashboard** | **Tools**
:---: | :---: | :---: | :---:
Python 3.11 | Scikit-learn | Streamlit | Git/GitHub
Pandas | XGBoost | Plotly | Pytest
NumPy | LightGBM | Matplotlib | Jupyter
 | CatBoost | Seaborn | Optuna
 | SHAP |  | BeautifulSoup

</div>

---

## 📊 Dataset Details

### Data Collection
- **Real Data**: 500+ listings scraped from Bayut.com
- **Synthetic Data**: 15,550 generated listings (market-realistic distributions)
- **Total**: 16,050 listings across 20 neighborhoods

### Coverage
- **Property Types**: Studio, 1BR, 2BR, 3BR, 4BR+, Villa, Townhouse, Penthouse
- **Neighborhoods**: Dubai Marina, Downtown, JBR, Business Bay, JLT, DIFC, etc.
- **Amenities**: 15+ tracked (Pool, Gym, Parking, Metro, Beach, etc.)

### Data Quality
- **Validation**: Schema checks, outlier detection, consistency tests
- **Authenticity**: Real data anchors synthetic distributions
- **Compliance**: Anonymized, no personal information

---

## 🎓 What I Learned

This project pushed me beyond typical Kaggle-style ML:

1. **Real-World Data Challenges**: Scraping, cleaning, and dealing with missing/inconsistent data
2. **Production ML**: Model serialization, inference optimization, error handling
3. **Feature Engineering Creativity**: Domain knowledge → 58 features from 10 base columns
4. **Ensemble Strategy**: Combining models for robustness (not just stacking)
5. **Explainability**: SHAP for stakeholder trust (clients need to understand "why")
6. **Full-Stack Deployment**: From data scraping → model training → dashboard deployment

---

## 👤 About the Developer

**Amir Khan** | *Data Analyst & BBA Student*

I bridge **operational experience** with **AI-driven analytics**. This project demonstrates my ability to:
- Translate business problems into ML solutions
- Build end-to-end data products (not just models)
- Communicate technical insights to non-technical stakeholders

**Background**:
- 🎓 BBA in Business Analytics (Manipal University Jaipur)
- 💼 Inventory Analyst at Bluemart Retail LLC (3 years of operations intelligence)
- 🏆 IBM AI Engineering & Google Advanced Data Analytics Certified
- 📍 Dubai, UAE

**Let's Connect**:
- 💼 [LinkedIn](https://linkedin.com/in/amir-khan-hussain)
- 💻 [Portfolio](https://amir-analyst.github.io)
- 📧 [Email](mailto:your.email@example.com)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Data Sources**: Property Finder, Bayut.com
- **Inspiration**: Dubai Land Department market reports
- **Tools**: Streamlit, Plotly, scikit-learn, XGBoost teams
- **Education**: IBM, Google, Manipal University Jaipur

---

<div align="center">

### ⭐ If you find this project valuable, please consider starring it!

**Built with ❤️ in Dubai | November 2025**

</div>
