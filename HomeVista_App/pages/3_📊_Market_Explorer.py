"""
Market Explorer: Interactive visualization of Dubai rental market
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

import config
from dashboard.visualizations import (
    create_neighborhood_distribution,
    create_price_per_sqft_chart,
    create_tier_comparison
)

# Page config
st.set_page_config(
    page_title="Market Explorer - HomeVista",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("📊 Market Explorer: Dubai Rental Insights")
st.markdown("### Explore market trends and data patterns")

st.markdown("---")

# Load data
@st.cache_data
def load_market_data():
    return pd.read_csv(config.FILE_ANALYTICAL_DATASET)

try:
    df = load_market_data()
    
    # Overview metrics
    st.subheader("Market Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Listings",
            value=f"{len(df):,}",
            help="Total properties in dataset"
        )
    
    with col2:
        st.metric(
            label="Average Rent",
            value=f"{df['annual_rent'].mean():,.0f} AED",
            help="Average annual rent across all properties"
        )
    
    with col3:
        st.metric(
            label="Median Rent",
            value=f"{df['annual_rent'].median():,.0f} AED",
            help="Median annual rent (less affected by outliers)"
        )
    
    with col4:
        st.metric(
            label="Neighborhoods",
            value=df['neighborhood'].nunique(),
            help="Number of distinct neighborhoods covered"
        )
    
    st.markdown("---")
    
    # Filters
    st.subheader("🔍 Filter Data")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    
    with filter_col1:
        selected_neighborhoods = st.multiselect(
            "Neighborhoods",
            options=sorted(df['neighborhood'].unique()),
            default=[],
            help="Leave empty to include all"
        )
    
    with filter_col2:
        selected_property_types = st.multiselect(
            "Property Types",
            options=sorted(df['property_type'].unique()),
            default=[],
            help="Leave empty to include all"
        )
    
    with filter_col3:
        price_range = st.slider(
            "Annual Rent Range (AED)",
            min_value=int(df['annual_rent'].min()),
            max_value=int(df['annual_rent'].max()),
            value=(int(df['annual_rent'].min()), int(df['annual_rent'].max())),
            step=5000
        )
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_neighborhoods:
        filtered_df = filtered_df[filtered_df['neighborhood'].isin(selected_neighborhoods)]
    
    if selected_property_types:
        filtered_df = filtered_df[filtered_df['property_type'].isin(selected_property_types)]
    
    filtered_df = filtered_df[
        (filtered_df['annual_rent'] >= price_range[0]) &
        (filtered_df['annual_rent'] <= price_range[1])
    ]
    
    st.info(f"📊 Showing {len(filtered_df):,} properties (filtered from {len(df):,} total)")
    
    st.markdown("---")
    
    # Visualizations
    st.subheader("📈 Market Visualizations")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "By Neighborhood", 
        "By Property Type", 
        "By Location Tier",
        "Advanced Analysis"
    ])
    
    with tab1:
        st.markdown("#### Rent Distribution by Neighborhood")
        if len(filtered_df) > 0:
            fig = create_neighborhood_distribution(filtered_df)
            st.plotly_chart(fig, width="stretch")
            
            # Summary stats
            st.markdown("##### Neighborhood Statistics")
            neighborhood_stats = filtered_df.groupby('neighborhood')['annual_rent'].agg([
                ('Count', 'count'),
                ('Average', 'mean'),
                ('Median', 'median'),
                ('Min', 'min'),
                ('Max', 'max')
            ]).round(0).sort_values('Average', ascending=False)
            
            st.dataframe(
                neighborhood_stats.style.format({
                    'Average': '{:,.0f}',
                    'Median': '{:,.0f}',
                    'Min': '{:,.0f}',
                    'Max': '{:,.0f}'
                }),
                width="stretch"
            )
        else:
            st.warning("No data available with current filters")
    
    with tab2:
        st.markdown("#### Rent vs. Size by Property Type")
        if len(filtered_df) > 0:
            fig = create_price_per_sqft_chart(filtered_df)
            st.plotly_chart(fig, width="stretch")
            
            # Property type summary
            st.markdown("##### Property Type Statistics")
            property_stats = filtered_df.groupby('property_type')['annual_rent'].agg([
                ('Count', 'count'),
                ('Average Rent', 'mean'),
                ('Avg Size (sqft)', lambda x: filtered_df.loc[x.index, 'size_sqft'].mean()),
                ('Price/sqft', lambda x: (x / filtered_df.loc[x.index, 'size_sqft']).mean())
            ]).round(0).sort_values('Average Rent', ascending=False)
            
            st.dataframe(
                property_stats.style.format({
                    'Average Rent': '{:,.0f}',
                    'Avg Size (sqft)': '{:,.0f}',
                    'Price/sqft': '{:.0f}'
                }),
                width="stretch"
            )
        else:
            st.warning("No data available with current filters")
    
    with tab3:
        st.markdown("#### Rent Distribution by Location Tier")
        if len(filtered_df) > 0:
            fig = create_tier_comparison(filtered_df)
            st.plotly_chart(fig, width="stretch")
            
            # Tier premium analysis
            st.markdown("##### Tier Premium Analysis")
            tier_stats = filtered_df.groupby('tier')['annual_rent'].agg([
                ('Count', 'count'),
                ('Average', 'mean'),
                ('Median', 'median')
            ]).round(0)
            
            # Calculate premium vs baseline (Tier 3)
            if 'Tier 3' in tier_stats.index:
                baseline = tier_stats.loc['Tier 3', 'Average']
                tier_stats['Premium vs Tier 3'] = ((tier_stats['Average'] - baseline) / baseline * 100).round(1)
            
            st.dataframe(
                tier_stats.style.format({
                    'Average': '{:,.0f}',
                    'Median': '{:,.0f}',
                    'Premium vs Tier 3': '{:+.1f}%'
                }),
                width="stretch"
            )
        else:
            st.warning("No data available with current filters")
    
    with tab4:
        st.markdown("#### Advanced Market Analysis")
        
        if len(filtered_df) > 0:
            adv_col1, adv_col2 = st.columns(2)
            
            with adv_col1:
                st.markdown("##### Amenity Impact")
                
                # Calculate average rent by amenity count
                amenity_impact = filtered_df.groupby('amenity_count')['annual_rent'].mean().round(0)
                
                st.line_chart(amenity_impact)
                st.caption("Average rent increases with more amenities")
            
            with adv_col2:
                st.markdown("##### Furnished vs Unfurnished")
                
                if 'furnished_numeric' in filtered_df.columns:
                    furnished_comparison = filtered_df.groupby('furnished_numeric')['annual_rent'].agg([
                        ('Count', 'count'),
                        ('Average Rent', 'mean')
                    ]).round(0)
                    
                    furnished_comparison.index = furnished_comparison.index.map({0: 'Unfurnished', 1: 'Furnished'})
                    
                    st.dataframe(
                        furnished_comparison.style.format({
                            'Average Rent': '{:,.0f}'
                        }),
                        width="stretch"
                    )
                    
                    if len(furnished_comparison) == 2:
                        premium = furnished_comparison.loc['Furnished', 'Average Rent'] - \
                                furnished_comparison.loc['Unfurnished', 'Average Rent']
                        st.metric("Furnished Premium", f"+{premium:,.0f} AED/year")
            
            # Metro & Beach impact
            st.markdown("---")
            st.markdown("##### Location Premium Factors")
            
            premium_col1, premium_col2 = st.columns(2)
            
            with premium_col1:
                if 'has_metro_numeric' in filtered_df.columns:
                    metro_comparison = filtered_df.groupby('has_metro_numeric')['annual_rent'].mean().round(0)
                    if len(metro_comparison) == 2:
                        metro_premium = metro_comparison[1] - metro_comparison[0]
                        st.metric(
                            "Metro Access Premium",
                            f"+{metro_premium:,.0f} AED",
                            help="Average rent increase for properties with metro access"
                        )
            
            with premium_col2:
                if 'beach_accessible_numeric' in filtered_df.columns:
                    beach_comparison = filtered_df.groupby('beach_accessible_numeric')['annual_rent'].mean().round(0)
                    if len(beach_comparison) == 2:
                        beach_premium = beach_comparison[1] - beach_comparison[0]
                        st.metric(
                            "Beach Access Premium",
                            f"+{beach_premium:,.0f} AED",
                            help="Average rent increase for beach-accessible properties"
                        )
        else:
            st.warning("No data available with current filters")
    
    # Data export
    st.markdown("---")
    st.subheader("📥 Export Data")
    
    if st.button("Download Filtered Data as CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="homevista_filtered_data.csv",
            mime="text/csv"
        )

except FileNotFoundError:
    st.error("Dataset not found. Please ensure the analytical dataset is generated first.")
    st.info(f"Looking for: {config.FILE_ANALYTICAL_DATASET}")
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
