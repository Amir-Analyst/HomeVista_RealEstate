<div align="center">

<div align="center">
    <img src="assets/homevista.png" width="500">
</div>

# 🏙️ HomeVista: Dubai Rental Intelligence

### *AI-Powered Market Transparency for Smarter Rental Decisions*

[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit)](https://streamlit.io/)
[![ML Models](https://img.shields.io/badge/ML-4_Ensemble_Models-green?style=for-the-badge)](https://github.com)
[![Accuracy](https://img.shields.io/badge/R²_Score-99.7%25-brightgreen?style=for-the-badge)](https://github.com)

**[📊 Live Demo](https://homevista-realestate.streamlit.app) • [📖 Technical Docs](docs/TECHNICAL_ARCHITECTURE.md) • [💻 GitHub](https://github.com/Amir-Analyst/HomeVista_RealEstate)**

</div>

---

## 🎯 The Problem

Dubai's rental market is **fast-paced and opaque**. 
*   **Tenants** struggle to know if a listing is fair or overpriced.
*   **Landlords** guess at pricing, leading to vacancy or lost revenue.
*   **Investors** lack granular data to spot high-yield neighborhoods.

With thousands of listings and massive price variations, making informed decisions is nearly impossible without data.

**HomeVista solves this.**

---

## ✨ The Solution

An **AI-powered rental intelligence platform** that brings transparency to the market. We combined **16,000+ data points** with advanced machine learning to predict fair market rents with **99.7% accuracy**.

<div align="center">

### 🧠 Advanced AI
**4-Model Ensemble** (XGBoost, LightGBM, CatBoost, Random Forest)

### 📊 Real-Time Insights
**Instant Predictions** & **Interactive Market Trends**

### 📈 Business Impact
**Save 10% on Rent** or **Optimize Yields by 15%**

</div>

---

## 🚀 Key Features

### 1. 🏠 Tenant Tool: Price Validation
> **"Am I overpaying?"**
Input property details and get an instant "Fair Price" prediction.
*   **Deal Rating**: ✅ Great Deal | ⚠️ Fair Price | ❌ Overpriced
*   **Negotiation Power**: Use data to negotiate better terms.

### 2. 💼 Landlord Tool: Pricing Optimization
> **"What should I charge?"**
Maximize revenue with data-driven pricing strategies.
*   **Dynamic Pricing**: "Quick Lease" vs "Premium Wait" recommendations.
*   **Upgrade ROI**: See how much furnishing or upgrades add to your rent.

### 3. 📊 Market Explorer
> **"Where are the trends?"**
Visualize the heartbeat of Dubai's real estate.
*   **Heatmaps**: Price per sqft across 20+ neighborhoods.
*   **Tier Analysis**: Compare Luxury vs Budget sectors.

---

## 🛠️ Under the Hood

HomeVista isn't just a dashboard; it's a robust engineering project.

*   **Data Pipeline**: Hybrid dataset of scraped real-world listings and statistically generated synthetic data (Beta distribution) for full market coverage.
*   **Feature Engineering**: 58 engineered features, including interaction terms (`Tier × Metro`) and polynomial features.
*   **Model Ensemble**: A weighted average of 4 top-tier algorithms, optimized via Bayesian hyperparameter tuning.

👉 **[Read the full Technical Architecture](docs/TECHNICAL_ARCHITECTURE.md)** for deep dives on the ML pipeline and system design.

---

## 🚀 Quick Start

### 🌐 Try the Live Demo

**👉 [Launch HomeVista Dashboard](https://homevistarealestate.streamlit.app/)**

No installation required! The app is deployed on Streamlit Cloud and ready to use.

---

### 💻 Run Locally (Optional)

For development or customization:

```bash
# 1. Clone the repository
git clone https://github.com/Amir-Analyst/HomeVista_RealEstate.git
cd HomeVista_RealEstate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup Models (Downloads 72MB model suite)
python setup_models.py

# 4. Launch the dashboard
streamlit run app.py
```

**Dashboard opens at**: `http://localhost:8501`

---

## 👤 About the Developer

**Amir Khan** | *Data Analyst*

I bridge the gap between **business operations** and **advanced analytics**. This project demonstrates my ability to:
*   **Solve Real Problems**: Translated a market pain point into a deployed AI solution.
*   **Build End-to-End**: From web scraping and data cleaning to ML training and frontend development.
*   **Deliver Quality**: Achieved <1% error rate through rigorous testing and ensemble modeling.

**Let's Connect**:
*   💼 [LinkedIn](https://linkedin.com/in/amir-khan-hussain)
*   💻 [Portfolio](https://amir-analyst.github.io)
*   📧 [Email](mailto:your.email@example.com)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">

### ⭐ If you find this project valuable, please consider starring it!

**Built with ❤️ in Dubai | November 2025**

</div>
