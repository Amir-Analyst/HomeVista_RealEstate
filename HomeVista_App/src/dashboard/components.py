"""
Reusable UI components for Streamlit dashboard
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional


def property_input_form(show_listed_price: bool = False) -> Optional[Dict]:
    """
    Create a property input form.
    
    Args:
        show_listed_price: Whether to include listed price field
    
    Returns:
        Dict with property details or None if not submitted
    """
    with st.form("property_form"):
        st.subheader("Property Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            neighborhood = st.selectbox(
                "Neighborhood",
                options=[
                    "Dubai Marina", "Jumeirah Beach Residence (JBR)", "Downtown Dubai",
                    "Business Bay", "Dubai Internet City", "Dubai Media City",
                    "Jumeirah Lake Towers (JLT)", "Barsha Heights (Tecom)", "Al Barsha",
                    "Dubai Sports City", "Discovery Gardens", "International City",
                    "Deira", "Bur Dubai", "Jumeirah", "Arabian Ranches",
                    "Motor City", "Dubai Silicon Oasis", "DIFC", "Al Nahda"
                ],
                help="Select the neighborhood where the property is located"
            )
            
            property_type = st.selectbox(
                "Property Type",
                options=["Studio", "1BR", "2BR", "3BR", "Villa"],
                help="Type of property"
            )
            
            size_sqft = st.number_input(
                "Size (sq ft)",
                min_value=300,
                max_value=10000,
                value=1000,
                step=50,
                help="Property size in square feet"
            )
            
            tier = st.selectbox(
                "Location Tier",
                options=["Tier 1 (Premium)", "Tier 2 (High-end)", "Tier 3 (Mid-market)", "Tier 4 (Budget)"],
                index=2,
                help="Quality tier of the location"
            )
        
        with col2:
            bedrooms = st.number_input(
                "Bedrooms",
                min_value=0,
                max_value=10,
                value=2,
                help="Number of bedrooms (0 for Studio)"
            )
            
            bathrooms = st.number_input(
                "Bathrooms",
                min_value=1,
                max_value=10,
                value=2,
                help="Number of bathrooms"
            )
            
            furnished = st.checkbox("Furnished", value=False)
            has_metro = st.checkbox("Metro Access", value=False)
            beach_accessible = st.checkbox("Beach Access", value=False)
        
        st.subheader("Amenities")
        amenities = st.multiselect(
            "Select Available Amenities",
            options=["Swimming Pool", "Gym", "Parking", "Balcony", "Security", 
                    "Maid's Room", "Central AC", "Built-in Wardrobes", "Pets Allowed", "Study Room"],
            default=["Parking", "Central AC"]
        )
        
        listed_price = None
        if show_listed_price:
            listed_price = st.number_input(
                "Listed Price (AED/year)",
                min_value=10000,
                max_value=1000000,
                value=100000,
                step=5000,
                help="The asking price for this property"
            )
        
        submitted = st.form_submit_button("Get Prediction", type="primary", width="stretch")
        
        if submitted:
            # Extract tier value using robust mapping
            tier_ui_map = {
                "Tier 1 (Premium)": "Luxury",
                "Tier 2 (High-end)": "Premium",
                "Tier 3 (Mid-market)": "Mid-Market",
                "Tier 4 (Budget)": "Budget"
            }
            tier_value = tier_ui_map.get(tier, "Mid-Market")  # Default fallback
            
            property_data = {
                'neighborhood': neighborhood,
                'property_type': property_type,
                'size_sqft': size_sqft,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'amenity_count': len(amenities),
                'tier': tier_value,
                'furnished': furnished,
                'has_metro': has_metro,
                'beach_accessible': beach_accessible,
                'amenities': amenities
            }
            
            if listed_price:
                property_data['listed_price'] = listed_price
            
            return property_data
    
    return None


def price_comparison_card(comparison: Dict):
    """
    Display price comparison card with visual indicators.
    
    Args:
        comparison: Dict from predictor.compare_with_market()
    """
    st.markdown("---")
    st.subheader("Price Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Predicted Fair Rent",
            value=f"{comparison['predicted_price']:,.0f} AED",
            help="Model prediction based on property features"
        )
    
    with col2:
        st.metric(
            label="Listed Price",
            value=f"{comparison['listed_price']:,.0f} AED",
            delta=f"{comparison['difference']:,.0f} AED",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="Price Difference",
            value=f"{comparison['percent_difference']:.1f}%",
            help="Percentage difference from fair market rent"
        )
    
    # Recommendation
    emoji = comparison['emoji']
    recommendation = comparison['recommendation']
    color = comparison['color']
    
    if color == "green":
        st.success(f"{emoji} **{recommendation}**: This property is priced below market value!")
    elif color == "orange":
        st.warning(f"{emoji} **{recommendation}**: This property is fairly priced.")
    else:
        st.error(f"{emoji} **{recommendation}**: This property is above market value. Consider negotiating.")
    
    # Confidence interval
    st.info(
        f"**95% Confidence Range:** {comparison['confidence_range'][0]:,.0f} - {comparison['confidence_range'][1]:,.0f} AED/year"
    )


def metric_card(label: str, value: str, delta: Optional[str] = None, help_text: Optional[str] = None):
    """
    Create a styled metric display card.
    
    Args:
        label: Metric label
        value: Primary value
        delta: Optional delta value
        help_text: Optional help tooltip
    """
    st.metric(label=label, value=value, delta=delta, help=help_text)


def feature_importance_table(features: List[str], importances: List[float]):
    """
    Display feature importance as a table.
    
    Args:
        features: Feature names
        importances: Importance values
    """
    df = pd.DataFrame({
        'Feature': features,
        'Importance': importances
    }).sort_values('Importance', ascending=False)
    
    st.dataframe(
        df,
        hide_index=True,
        width="stretch"
    )
