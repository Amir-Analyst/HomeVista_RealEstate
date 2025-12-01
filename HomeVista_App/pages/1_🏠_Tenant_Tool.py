"""
Tenant Tool: Validate if a listed rent price is fair
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from dashboard.predictor import RentPredictor
from dashboard.components import property_input_form, price_comparison_card
from dashboard.visualizations import create_price_comparison_chart, create_model_comparison_chart

# Page config
st.set_page_config(
    page_title="Tenant Tool - HomeVista",
    page_icon="🔍",
    layout="wide"
)

# Title
st.title("🔍 Tenant Tool: Price Validation")
st.markdown("### Is this rent fair? Let AI tell you.")

st.markdown("---")

# Info box
st.info(
    """
    **How it works:**
    1. Enter the property details
    2. Enter the listed/asking price
    3. Our AI model predicts the fair market rent
    4. See if you're getting a good deal or overpaying
    """
)

# Initialize predictor (cached)
@st.cache_resource
def load_predictor():
    return RentPredictor()

try:
    predictor = load_predictor()
    
    # Property input form
    property_data = property_input_form(show_listed_price=True)
    
    if property_data:
        with st.spinner("Analyzing property and predicting fair rent..."):
            # Get listed price
            listed_price = property_data.pop('listed_price')
            
            # Get comparison
            comparison = predictor.compare_with_market(property_data, listed_price)
            
            # Display results
            price_comparison_card(comparison)
            
            # Visualization
            st.markdown("---")
            st.subheader("Visual Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Price comparison chart
                fig = create_price_comparison_chart(
                    comparison['predicted_price'],
                    comparison['listed_price'],
                    comparison['confidence_range']
                )
                st.plotly_chart(fig, width="stretch")
            
            with col2:
                # Model breakdown
                prediction_result = predictor.predict(property_data)
                fig = create_model_comparison_chart(
                    prediction_result['individual_models'],
                    predictor.weights
                )
                st.plotly_chart(fig, width="stretch")
            
            # Insights
            st.markdown("---")
            st.subheader("💡 Insights & Recommendations")
            
            if comparison['percent_difference'] < -5:
                st.success(
                    """
                    **This is an excellent deal!** The property is priced significantly below market value. 
                    Consider acting quickly as good deals don't last long in Dubai's rental market.
                    """
                )
            elif comparison['percent_difference'] < 5:
                st.warning(
                    """
                    **Fair pricing.** The listed price is within the expected range for this property's features and location. 
                    You might have limited room for negotiation, but it's a reasonable price.
                    """
                )
            else:
                st.error(
                    f"""
                    **Overpriced by {comparison['percent_difference']:.1f}%.** This property is asking more than market value. 
                    
                    **Negotiation tip:** Show the landlord that similar properties in {property_data['neighborhood']} 
                    rent for around {comparison['predicted_price']:,.0f} AED. You could save 
                    {comparison['difference']:,.0f} AED per year by negotiating or looking for alternatives.
                    """
                )
            
            # Property summary
            st.markdown("---")
            with st.expander("📋 Property Summary"):
                summary_col1, summary_col2, summary_col3 = st.columns(3)
                
                with summary_col1:
                    st.markdown(f"**Location:** {property_data['neighborhood']}")
                    st.markdown(f"**Type:** {property_data['property_type']}")
                    st.markdown(f"**Size:** {property_data['size_sqft']:,} sq ft")
                
                with summary_col2:
                    st.markdown(f"**Bedrooms:** {property_data['bedrooms']}")
                    st.markdown(f"**Bathrooms:** {property_data['bathrooms']}")
                    st.markdown(f"**Tier:** {property_data['tier']}")
                
                with summary_col3:
                    st.markdown(f"**Furnished:** {'Yes' if property_data['furnished'] else 'No'}")
                    st.markdown(f"**Metro Access:** {'Yes' if property_data['has_metro'] else 'No'}")
                    st.markdown(f"**Amenities:** {property_data['amenity_count']}")

except Exception as e:
    st.error(f"Error loading predictor: {str(e)}")
    st.info("Make sure all ML models are trained and saved in the models/ directory.")
