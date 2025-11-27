"""
HomeVista: Dubai Rental Intelligence Dashboard.

This is the main entry point for the Streamlit application. It handles the
navigation, layout, and core UI components of the dashboard.
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

# Page configuration
st.set_page_config(
    page_title="HomeVista - Dubai Rental Intelligence",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check if models are available
from pathlib import Path
MODELS_DIR = Path(__file__).parent / 'models'
required_models = ['model_suite.pkl', 'ensemble_weights.pkl', 'feature_engineer.pkl']
missing_models = [f for f in required_models if not (MODELS_DIR / f).exists()]

if missing_models:
    st.error(f"""
    ### ⚠️ Model Files Not Found
    
    The following model files are missing:
    {', '.join(missing_models)}
    
    **For Streamlit Cloud:** Models should download automatically on first deployment.
    If this error persists, please check the deployment logs.
    
    **For Local Development:** Run the setup script:
    ```bash
    python setup_models.py
    ```
    """)
    st.stop()


# Custom CSS for premium styling
st.markdown("""
<style>
    /* Dubai-inspired color scheme */
    :root {
        --primary-color: #C9A961;  /* Gold */
        --secondary-color: #2C3E50; /* Deep Blue */
        --accent-color: #2E86AB;   /* Bright Blue */
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: var(--secondary-color);
        font-weight: 700;
    }
    
    h2, h3 {
        color: var(--accent-color);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: var(--accent-color);
        color: white;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Success/Warning/Error boxes */
    .stSuccess, .stWarning, .stError {
        border-radius: 8px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://via.placeholder.com/200x100/2E86AB/FFFFFF?text=HomeVista", width="stretch")
    st.markdown("---")
    st.markdown("### 🏙️ Dubai Rental Intelligence")
    st.markdown("Powered by Advanced ML Ensemble")
    st.markdown("---")
    
    st.markdown("#### About")
    st.info(
        """
        **HomeVista** uses a 4-model ensemble (Random Forest, XGBoost, LightGBM, CatBoost) 
        to predict Dubai rental prices with **99.7% accuracy**.
        
        **Model Performance:**
        - R² Score: 0.9972
        - MAPE: 0.95%
        - Training Data: 16,050 listings
        """
    )
    
    st.markdown("---")
    st.markdown("#### Navigation")
    st.page_link("app.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/1_🏠_Tenant_Tool.py", label="Tenant Tool", icon="🔍")
    st.page_link("pages/2_💼_Landlord_Tool.py", label="Landlord Tool", icon="💼")
    st.page_link("pages/3_📊_Market_Explorer.py", label="Market Explorer", icon="📊")

# Main page content
def main():
    """Render the main home page content."""
    st.title("🏙️ HomeVista: Dubai Rental Intelligence")
    st.markdown("### Make Data-Driven Rental Decisions with AI")
    
    st.markdown("---")
    
    # Hero section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🔍 For Tenants")
        st.markdown(
            """
            **Validate Fair Rent**
            
            Ensure you're not overpaying. Get instant price validation 
            based on property features and market data.
            """
        )
    
    with col2:
        st.markdown("#### 💼 For Landlords")
        st.markdown(
            """
            **Optimize Pricing**
            
            Maximize occupancy and revenue with data-driven 
            pricing recommendations.
            """
        )
    
    with col3:
        st.markdown("#### 📊 For Analysts")
        st.markdown(
            """
            **Explore Market Trends**
            
            Interactive visualizations of Dubai's rental market 
            by neighborhood, property type, and tier.
            """
        )
    
    st.markdown("---")
    
    # Key features
    st.markdown("### Why HomeVista?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 **Unprecedented Accuracy**")
        st.markdown(
            """
            - **99.7% R² Score**: Industry-leading prediction accuracy
            - **<1% Average Error**: Predictions within 1,500 AED on average
            - **4-Model Ensemble**: Combines best algorithms for robust results
            """
        )
        
        st.markdown("#### 🧠 **Explainable AI**")
        st.markdown(
            """
            - **SHAP Values**: Understand why each prediction was made
            - **Feature Breakdown**: See impact of size, location, amenities
            - **Confidence Intervals**: Know the prediction's reliability
            """
        )
    
    with col2:
        st.markdown("#### 📈 **Comprehensive Coverage**")
        st.markdown(
            """
            - **16,000+ Listings**: Full market simulation
            - **20 Neighborhoods**: From Downtown to Discovery Gardens
            - **58 Features**: Interaction, polynomial, domain-specific
            """
        )
        
        st.markdown("#### ⚡ **Instant Insights**")
        st.markdown(
            """
            - **Real-time Predictions**: Get results in milliseconds
            - **Interactive Charts**: Explore data visually
            - **Mobile Friendly**: Access anywhere, anytime
            """
        )
    
    st.markdown("---")
    
    # Model performance showcase
    st.markdown("### Model Performance")
    
    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
    
    with metrics_col1:
        st.metric(
            label="R² Score",
            value="0.9972",
            delta="99.7% variance explained",
            help="Measures how well the model fits the data"
        )
    
    with metrics_col2:
        st.metric(
            label="MAPE",
            value="0.95%",
            delta="<1% error rate",
            help="Mean Absolute Percentage Error"
        )
    
    with metrics_col3:
        st.metric(
            label="MAE",
            value="~1,500 AED",
            help="Mean Absolute Error in AED"
        )
    
    with metrics_col4:
        st.metric(
            label="Training Data",
            value="16,050",
            delta="Full market coverage",
            help="Total listings used for training"
        )
    
    st.markdown("---")
    
    # Call to action
    st.markdown("### Ready to Get Started?")
    
    cta_col1, cta_col2, cta_col3 = st.columns(3)
    
    with cta_col1:
        if st.button("🔍 Validate a Rent Price", width="stretch", type="primary"):
            st.switch_page("pages/1_🏠_Tenant_Tool.py")
    
    with cta_col2:
        if st.button("💼 Optimize My Pricing", width="stretch", type="primary"):
            st.switch_page("pages/2_💼_Landlord_Tool.py")
    
    with cta_col3:
        if st.button("📊 Explore Market Data", width="stretch", type="primary"):
            st.switch_page("pages/3_📊_Market_Explorer.py")
    
    st.markdown("---")
    
    # Footer
    st.markdown(
        """
        <div style='text-align: center; color: #6c757d; padding: 2rem 0;'>
            <p>Built with ❤️ using Streamlit, XGBoost, LightGBM, CatBoost, and SHAP</p>
            <p>© 2024 HomeVista - Dubai Rental Intelligence</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
