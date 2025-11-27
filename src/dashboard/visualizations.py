"""
Visualization utilities for HomeVista dashboard
Creates interactive Plotly charts
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Dict


def create_price_comparison_chart(predicted: float, listed: float, confidence_range: tuple) -> go.Figure:
    """
    Create a comparison chart showing predicted vs listed price.
    
    Args:
        predicted: Predicted price
        listed: Listed price
        confidence_range: (lower, upper) confidence bounds
    
    Returns:
        Plotly figure
    """
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        x=['Predicted Fair Rent', 'Listed Price'],
        y=[predicted, listed],
        marker_color=['#2E86AB', '#A23B72'],
        text=[f'{predicted:,.0f} AED', f'{listed:,.0f} AED'],
        textposition='auto',
    ))
    
    # Add confidence interval as error bar
    fig.add_trace(go.Scatter(
        x=['Predicted Fair Rent'],
        y=[predicted],
        error_y=dict(
            type='data',
            symmetric=False,
            array=[confidence_range[1] - predicted],
            arrayminus=[predicted - confidence_range[0]],
            color='rgba(46, 134, 171, 0.3)'
        ),
        mode='markers',
        marker=dict(size=0),
        showlegend=False
    ))
    
    fig.update_layout(
        title="Price Comparison",
        yaxis_title="Annual Rent (AED)",
        template="plotly_white",
        height=400,
        showlegend=False
    )
    
    return fig


def create_neighborhood_distribution(df: pd.DataFrame) -> go.Figure:
    """
    Create a box plot of rent distribution by neighborhood.
    
    Args:
        df: DataFrame with 'neighborhood' and 'annual_rent' columns
    
    Returns:
        Plotly figure
    """
    fig = px.box(
        df,
        x='annual_rent',
        y='neighborhood',
        orientation='h',
        title='Rent Distribution by Neighborhood',
        labels={'annual_rent': 'Annual Rent (AED)', 'neighborhood': 'Neighborhood'},
        template='plotly_white'
    )
    
    fig.update_layout(
        height=600,
        xaxis_title="Annual Rent (AED)",
        yaxis_title="",
        showlegend=False
    )
    
    return fig


def create_price_per_sqft_chart(df: pd.DataFrame) -> go.Figure:
    """
    Create a scatter plot of price per sqft by property type.
    
    Args:
        df: DataFrame with property data
    
    Returns:
        Plotly figure
    """
    fig = px.scatter(
        df,
        x='size_sqft',
        y='annual_rent',
        color='property_type',
        size='amenity_count',
        hover_data=['neighborhood', 'bedrooms', 'bathrooms'],
        title='Rental Price vs. Size',
        labels={
            'size_sqft': 'Size (sq ft)',
            'annual_rent': 'Annual Rent (AED)',
            'property_type': 'Property Type',
            'amenity_count': 'Amenities'
        },
        template='plotly_white'
    )
    
    fig.update_layout(height=500)
    
    return fig


def create_amenity_impact_chart(amenity_stats: Dict[str, float]) -> go.Figure:
    """
    Create a bar chart showing the impact of each amenity on rent.
    
    Args:
        amenity_stats: Dict mapping amenity name to average rent increase
    
    Returns:
        Plotly figure
    """
    amenities = list(amenity_stats.keys())
    impacts = list(amenity_stats.values())
    
    fig = go.Figure(go.Bar(
        x=impacts,
        y=amenities,
        orientation='h',
        marker_color='#2E86AB',
        text=[f'+{v:,.0f} AED' for v in impacts],
        textposition='auto'
    ))
    
    fig.update_layout(
        title='Average Rent Increase by Amenity',
        xaxis_title='Rent Increase (AED/year)',
        yaxis_title='',
        template='plotly_white',
        height=400
    )
    
    return fig


def create_tier_comparison(df: pd.DataFrame) -> go.Figure:
    """
    Create a violin plot comparing rent across different tiers.
    
    Args:
        df: DataFrame with 'tier' and 'annual_rent' columns
    
    Returns:
        Plotly figure
    """
    fig = px.violin(
        df,
        x='tier',
        y='annual_rent',
        color='tier',
        box=True,
        points='outliers',
        title='Rent Distribution by Location Tier',
        labels={'tier': 'Location Tier', 'annual_rent': 'Annual Rent (AED)'},
        template='plotly_white'
    )
    
    fig.update_layout(height=500, showlegend=False)
    
    return fig


def create_model_comparison_chart(model_predictions: Dict[str, float], weights: Dict[str, float]) -> go.Figure:
    """
    Create a chart showing individual model predictions and their weights.
    
    Args:
        model_predictions: Dict of model name to prediction
        weights: Dict of model name to ensemble weight
    
    Returns:
        Plotly figure
    """
    models = list(model_predictions.keys())
    predictions = [model_predictions[m] for m in models]
    weight_pcts = [weights[m] * 100 for m in models]
    
    fig = go.Figure()
    
    # Predictions bar chart
    fig.add_trace(go.Bar(
        x=models,
        y=predictions,
        name='Prediction',
        marker_color='#2E86AB',
        yaxis='y',
        offsetgroup=0
    ))
    
    # Weights bar chart (secondary axis)
    fig.add_trace(go.Bar(
        x=models,
        y=weight_pcts,
        name='Ensemble Weight',
        marker_color='#F18F01',
        yaxis='y2',
        offsetgroup=1
    ))
    
    fig.update_layout(
        title='Model Predictions & Ensemble Weights',
        xaxis_title='Model',
        yaxis=dict(title='Predicted Rent (AED)'),
        yaxis2=dict(title='Ensemble Weight (%)', overlaying='y', side='right'),
        template='plotly_white',
        height=400,
        barmode='group'
    )
    
    return fig
