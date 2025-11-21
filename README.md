# 🏙️ HomeVista: AI-Powered Dubai Rental Intelligence

> An AI-augmented predictive analytics system analyzing Dubai's rental market to help expats and investors make data-driven housing decisions.

**Status:** 🚧 In Development

---

## 📋 Project Overview

HomeVista combines real-world scraped data with synthetic generation to create a comprehensive rental market intelligence system for Dubai. Using machine learning models, the project predicts rental prices, segments neighborhoods, and provides actionable insights for both renters and investors.

**Key Features:**
- 🎯 Rental price prediction using ensemble ML models
- 📊 Neighborhood segmentation and comparison
- 💰 Investment ROI calculator for property investors
- 📈 Interactive Streamlit dashboard
- 🔍 Market insights based on 2025 Dubai rental data

---

## 🎓 Academic Context

This project serves as:
- **BBA Coursework**: Practical application of Business Analytics (Semester 5)
- **MBA Preparation**: Foundation for AI-Driven Business Strategy program
- **Portfolio Project**: Demonstrates progression from descriptive to predictive analytics

---

## 🗂️ Project Structure

```
HomeVista_RealEstate/
├── data/
│   ├── raw/                    # Scraped and original data
│   ├── processed/              # Cleaned and engineered data
│   └── reference/              # Neighborhoods, property types
├── notebooks/
│   ├── 01_data_collection.ipynb
│   ├── 02_data_processing.ipynb
│   ├── 03_eda.ipynb
│   └── 04_modeling.ipynb
├── src/
│   ├── config.py              # Configuration settings
│   ├── scraper.py             # Web scraping functions
│   ├── data_generator.py      # Synthetic data generation
│   ├── data_processor.py      # Data cleaning and features
│   └── models.py              # ML model training
├── models/
│   └── rental_price_model.pkl  # Saved trained model
├── dashboard/
│   └── app.py                 # Streamlit dashboard
├── docs/
│   └── market_research.md     # Market research notes
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Amir-Analyst/homevista.git
cd HomeVista_RealEstate
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Initialize project directories**
```bash
python src/config.py
```

---

## 📊 Dataset

**Hybrid Approach: Real + Synthetic Data**

- **Real Data (30%)**: Scraped from Property Finder and Bayut
  - ~300-500 actual rental listings
  - Validates market authenticity
  
- **Synthetic Data (70%)**: Generated using Faker and NumPy
  - ~2,500 listings with realistic distributions
  - Controlled scenarios for analysis

**Data Sources:**
- Property Finder: https://www.propertyfinder.ae
- Bayut: https://www.bayut.com
- Dubai Land Department: Market reports and insights

---

## 🤖 Machine Learning Approach

### Models Tested
1. **Linear Regression** (Baseline)
2. **Random Forest** (Selected)
3. **XGBoost** (Optional)

### Features
- Property characteristics (bedrooms, size, type)
- Location attributes (neighborhood, metro proximity)
- Amenities (parking, pool, gym, furnished)
- Market factors (construction year, view type)

### Performance Metrics
- **Target**: R² > 0.75, MAE < 10,000 AED
- *(Will be updated after model training)*

---

## 💡 Key Insights

### For Expats
*(To be completed after analysis)*

### For Investors
*(To be completed after analysis)*

---

## 🎨 Dashboard Features

**Interactive Streamlit Application:**

1. **Rental Price Predictor**
   - Input property details
   - Get predicted rent ± confidence interval
   - Compare to neighborhood averages

2. **Neighborhood Comparison Tool**
   - Side-by-side area comparison
   - Visualize rent/sqft, amenities, profiles

3. **Investment ROI Calculator**
   - Calculate rental yield
   - Break-even analysis
   - Compare ROI across neighborhoods

---

## 🛠️ Technical Stack

- **Languages**: Python 3.11
- **Data Science**: Pandas, NumPy, SciPy
- **Machine Learning**: Scikit-learn, XGBoost
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Web Scraping**: BeautifulSoup, Selenium
- **Dashboard**: Streamlit
- **Version Control**: Git, GitHub

---

## 📈 Development Roadmap

- [x] Project setup and configuration
- [ ] Market research and data collection
- [ ] Synthetic data generation
- [ ] Exploratory data analysis
- [ ] ML model development
- [ ] Dashboard implementation
- [ ] Documentation and testing
- [ ] GitHub deployment

---

## 👤 Author

**Amir Khan**
- 🎓 BBA Student (Business Analytics focus)
- 💼 Inventory Analyst & Operations Support
- 🏆 IBM AI Engineering & Google Advanced Data Analytics Certified
- 📍 Dubai, UAE

**Connect:**
- LinkedIn: [amir-khan-hussain](https://linkedin.com/in/amir-khan-hussain)
- GitHub: [Amir-Analyst](https://github.com/Amir-Analyst)
- Portfolio: [amir-analyst.github.io](https://amir-analyst.github.io)

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Property Finder and Bayut for market data
- IBM and Google for professional certifications
- Manipal University Jaipur for BBA program

---

**Last Updated:** November 2025
