"""
Landlord Tool: Optimize pricing strategy for rental properties
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from dashboard.predictor import RentPredictor
from dashboard.components import property_input_form
from dashboard.visualizations import create_price_comparison_chart

# Page config
st.set_page_config(
    page_title="Landlord Tool - HomeVista",
    page_icon="💼",
    layout="wide"
)

# Title
st.title("💼 Landlord Tool: Pricing Optimization")
st.markdown("### Maximize occupancy and revenue with data-driven pricing")

st.markdown("---")

# Info box
st.info(
    """
    **How it works:**
    1. Enter your property details
    2. Get AI-powered pricing recommendation
    3. See the optimal price range to attract tenants
    4. Understand what features impact your rent the most
    """
)

# Initialize predictor (cached)
@st.cache_resource
def load_predictor():
    return RentPredictor()

try:
    predictor = load_predictor()
    
    # Property input form (no listed price needed)
    property_data = property_input_form(show_listed_price=False)
    
    if property_data:
        with st.spinner("Analyzing market and calculating optimal price..."):
            # Get prediction
            prediction = predictor.predict(property_data, return_confidence=True)
            
            # Display results
            st.markdown("---")
            st.subheader("💰 Recommended Pricing Strategy")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Optimal Rent",
                    value=f"{prediction['prediction']:,.0f} AED/year",
                    help="AI-predicted fair market rent"
                )
                st.caption(f"≈ {prediction['prediction']/12:,.0f} AED/month")
            
            with col2:
                st.metric(
                    label="Quick Lease Range",
                    value=f"{prediction['confidence_lower']:,.0f} - {prediction['prediction']:,.0f} AED",
                    help="Price below optimal for faster tenant acquisition"
                )
                st.caption("Attract tenants within 2-4 weeks")
            
            with col3:
                st.metric(
                    label="Premium Range",
                    value=f"{prediction['prediction']:,.0f} - {prediction['confidence_upper']:,.0f} AED",
                    help="Price above optimal, may take longer to lease"
                )
                st.caption("For premium positioning, may take 6-8 weeks")
            
            # Strategy recommendation
            st.markdown("---")
            st.subheader("📊 Pricing Strategy")
            
            strategy_col1, strategy_col2 = st.columns(2)
            
            with strategy_col1:
                st.success(
                    f"""
                    ### ⚡ Recommended: {prediction['prediction']:,.0f} AED/year
                    
                    **Why this price?**
                    - Balances competitiveness and profitability
                    - Based on {property_data['neighborhood']} market data
                    - Accounts for your {property_data['amenity_count']} amenities
                    - Expected to lease within 3-5 weeks
                    
                    **Monthly rent:** {prediction['prediction']/12:,.0f} AED
                    """
                )
            
            with strategy_col2:
                st.info(
                    f"""
                    ### 💡 Alternative Strategies
                    
                    **Quick Lease (Below Market):**
                    - Price: {prediction['confidence_lower']:,.0f} AED/year
                    - Lease time: 2-3 weeks
                    - Trade-off: 5% less annual revenue
                    
                    **Premium Positioning (Above Market):**
                    - Price: {prediction['confidence_upper']:,.0f} AED/year
                    - Lease time: 6-8 weeks
                    - Trade-off: May require concessions or longer vacancy
                    """
                )
            
            # Feature optimization tips
            st.markdown("---")
            st.subheader("🎯 How to Increase Your Rent")
            
            tips_col1, tips_col2 = st.columns(2)
            
            with tips_col1:
                st.markdown("#### Current Property Features")
                st.markdown(f"- **Location:** {property_data['neighborhood']} ({property_data['tier']})")
                st.markdown(f"- **Size:** {property_data['size_sqft']:,} sq ft")
                st.markdown(f"- **Amenities:** {property_data['amenity_count']}")
                st.markdown(f"- **Furnished:** {'Yes ✓' if property_data['furnished'] else 'No ✗'}")
                st.markdown(f"- **Metro Access:** {'Yes ✓' if property_data['has_metro'] else 'No ✗'}")
                st.markdown(f"- **Beach Access:** {'Yes ✓' if property_data['beach_accessible'] else 'No ✗'}")
            
            with tips_col2:
                st.markdown("#### Potential Upgrades")
                
                # Calculate upgrade impact
                upgrades = []
                
                if not property_data.get('furnished'):
                    upgrades.append(("Furnish the property", "+8,000 - 18,000 AED"))
                
                if 'Swimming Pool' not in property_data.get('amenities', []):
                    upgrades.append(("Add swimming pool access", "+3,000 - 5,000 AED"))
                
                if 'Gym' not in property_data.get('amenities', []):
                    upgrades.append(("Add gym access", "+2,500 - 4,000 AED"))
                
                if 'Parking' not in property_data.get('amenities', []):
                    upgrades.append(("Include parking space", "+2,000 - 3,500 AED"))
                
                if not upgrades:
                    st.success("✓ Your property is well-equipped with premium features!")
                else:
                    for upgrade, impact in upgrades[:4]:  # Show top 4
                        st.markdown(f"- {upgrade}: **{impact}**")
            
            # Visualization
            st.markdown("---")
            st.subheader("📈 Visual Price Analysis")
            
            # Create a comparison showing the range
            fig = create_price_comparison_chart(
                prediction['prediction'],
                prediction['prediction'],  # Same for landlord view
                (prediction['confidence_lower'], prediction['confidence_upper'])
            )
            st.plotly_chart(fig, width="stretch")
            
            # Model consensus
            st.markdown("---")
            with st.expander("🤖 Model Consensus (Advanced)"):
                st.markdown("Our prediction is based on 4 different ML models:")
                
                model_col1, model_col2 = st.columns(2)
                
                with model_col1:
                    for model, pred in list(prediction['individual_models'].items())[:2]:
                        st.metric(
                            label=model,
                            value=f"{pred:,.0f} AED",
                            delta=f"{predictor.weights[model]*100:.1f}% weight"
                        )
                
                with model_col2:
                    for model, pred in list(prediction['individual_models'].items())[2:]:
                        st.metric(
                            label=model,
                            value=f"{pred:,.0f} AED",
                            delta=f"{predictor.weights[model]*100:.1f}% weight"
                        )
                
                st.caption(
                    "The final prediction is a weighted average of all models, "
                    "with weights determined by each model's validation performance."
                )

except Exception as e:
    st.error(f"Error loading predictor: {str(e)}")
    st.info("Make sure all ML models are trained and saved in the models/ directory.")
