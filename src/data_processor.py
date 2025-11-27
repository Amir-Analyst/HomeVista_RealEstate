"""
Data Processing Pipeline for HomeVista Real Estate Analytics
Merges, cleans, and engineers features for ML-ready analytical dataset
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
import config


def load_datasets():
    """Load all required datasets"""
    print("\n[INFO] Loading datasets...")
    
    scraped = pd.read_csv(config.FILE_SCRAPED_LISTINGS)
    synthetic = pd.read_csv(config.FILE_SYNTHETIC_LISTINGS)
    neighborhoods = pd.read_csv(config.FILE_NEIGHBORHOODS)
    
    print(f"[SUCCESS] Loaded:")
    print(f"  - Scraped: {len(scraped)} listings")
    print(f"  - Synthetic: {len(synthetic)} listings")
    print(f"  - Neighborhoods: {len(neighborhoods)} areas")
    
    return scraped, synthetic, neighborhoods


def align_schemas(scraped_df, synthetic_df):
    """Align column names and add missing columns"""
    print("\n[INFO] Aligning schemas...")
    
    # Rename columns in scraped data to match synthetic
    if 'posting_date' in scraped_df.columns:
        scraped_df = scraped_df.rename(columns={'posting_date': 'posted_date'})
    
    # Add missing columns to scraped data
    if 'monthly_rent' not in scraped_df.columns:
        scraped_df['monthly_rent'] = scraped_df['annual_rent'] / 12
    
    if 'price_per_sqft' not in scraped_df.columns:
        scraped_df['price_per_sqft'] = scraped_df['annual_rent'] / scraped_df['size_sqft']
    
    # Get common columns
    common_cols = list(set(scraped_df.columns) & set(synthetic_df.columns))
    
    print(f"[SUCCESS] Aligned to {len(common_cols)} common columns")
    
    return scraped_df[common_cols], synthetic_df[common_cols]


def merge_datasets(scraped_df, synthetic_df):
    """Merge scraped and synthetic datasets with source tracking"""
    print("\n[INFO] Merging datasets...")
    
    # Add data source column
    scraped_df['data_source'] = 'scraped'
    synthetic_df['data_source'] = 'synthetic'
    
    # Concatenate
    merged = pd.concat([scraped_df, synthetic_df], ignore_index=True)
    
    print(f"[SUCCESS] Merged dataset: {len(merged)} total listings")
    print(f"  - Scraped: {len(scraped_df)} ({len(scraped_df)/len(merged)*100:.1f}%)")
    print(f"  - Synthetic: {len(synthetic_df)} ({len(synthetic_df)/len(merged)*100:.1f}%)")
    
    return merged


def handle_outliers(df, method='cap_99th'):
    """Handle extreme price outliers"""
    print("\n[INFO] Handling outliers...")
    
    original_max = df['annual_rent'].max()
    original_min = df['annual_rent'].min()
    
    if method == 'cap_99th':
        # Cap at 99th percentile
        p99 = df['annual_rent'].quantile(0.99)
        outliers = df['annual_rent'] > p99
        df.loc[outliers, 'annual_rent'] = p99
        
        print(f"  Original range: {original_min:,.0f} - {original_max:,.0f} AED")
        print(f"  99th percentile: {p99:,.0f} AED")
        print(f"  Capped {outliers.sum()} outliers")
        print(f"  New range: {df['annual_rent'].min():,.0f} - {df['annual_rent'].max():,.0f} AED")
    
    # Recalculate derived fields
    df['monthly_rent'] = df['annual_rent'] / 12
    df['price_per_sqft'] = df['annual_rent'] / df['size_sqft']
    
    return df


def clean_missing_values(df):
    """Handle missing data"""
    print("\n[INFO] Cleaning missing values...")
    
    # Report missing values
    missing_counts = df.isnull().sum()
    if missing_counts.sum() > 0:
        print("  Missing values found:")
        for col, count in missing_counts[missing_counts > 0].items():
            print(f"    {col}: {count} ({count/len(df)*100:.1f}%)")
    else:
        print("  No missing values found")
    
    # Fill missing bedrooms based on property_type
    if df['bedrooms'].isnull().any():
        type_to_beds = {'Studio': 0, '1BR': 1, '2BR': 2, '3BR': 3}
        df['bedrooms'] = df['bedrooms'].fillna(df['property_type'].map(type_to_beds))
    
    # Fill missing bathrooms (assume 1 per bedroom, min 1)
    if df['bathrooms'].isnull().any():
        df['bathrooms'] = df['bathrooms'].fillna(df['bedrooms'].clip(lower=1))
    
    # Fill missing amenities
    if df['amenities'].isnull().any():
        df['amenities'] = df['amenities'].fillna('')
    
    # Drop rows with critical missing values
    critical_cols = ['annual_rent', 'size_sqft', 'neighborhood']
    before_count = len(df)
    df = df.dropna(subset=critical_cols)
    after_count = len(df)
    
    if before_count > after_count:
        print(f"  Dropped {before_count - after_count} rows with critical missing values")
    
    return df


def standardize_data_types(df):
    """Ensure consistent data types"""
    print("\n[INFO] Standardizing data types...")
    
    # Numeric columns
    numeric_cols = ['annual_rent', 'monthly_rent', 'size_sqft', 'bedrooms', 'bathrooms', 'price_per_sqft']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Integer columns
    int_cols = ['annual_rent', 'monthly_rent', 'size_sqft', 'bedrooms', 'bathrooms']
    for col in int_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    
    # String columns
    str_cols = ['neighborhood', 'property_type', 'furnished', 'listing_id']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Standardize neighborhood names (titlecase)
    if 'neighborhood' in df.columns:
        df['neighborhood'] = df['neighborhood'].str.title()
    
    print("[SUCCESS] Data types standardized")
    
    return df


def engineer_features(df, neighborhoods_df):
    """Create ML features"""
    print("\n[INFO] Engineering features...")
    
    features_added = []
    
    # Merge with neighborhood metadata
    df = df.merge(
        neighborhoods_df[['neighborhood', 'tier', 'has_metro', 'beach_accessible']],
        left_on='neighborhood',
        right_on='neighborhood',
        how='left',
        suffixes=('', '_ref')
    )
    
    # Use reference tier if tier column doesn't exist or is missing
    if 'tier_ref' in df.columns:
        df['tier'] = df['tier'].fillna(df['tier_ref'])
        df = df.drop(columns=['tier_ref'])
    
    # Tier encoding
    tier_mapping = {'Budget': 1, 'Mid-Market': 2, 'Premium': 3, 'Luxury': 4}
    df['tier_numeric'] = df['tier'].map(tier_mapping).fillna(2)  # Default to mid-market
    features_added.append('tier_numeric')
    
    # Log transformation for rent (useful for ML)
    df['log_rent'] = np.log1p(df['annual_rent'])
    features_added.append('log_rent')
    
    # Amenity features
    df['amenity_count'] = df['amenities'].apply(lambda x: len(str(x).split(';')) if x and str(x) != '' else 0)
    features_added.append('amenity_count')
    
    # Individual amenity flags
    amenity_keywords = {
        'has_pool': 'pool',
        'has_gym': 'gym',
        'has_parking': 'parking',
        'has_balcony': 'balcony',
        'has_maids_room': "maid"
    }
    
    for col, keyword in amenity_keywords.items():
        df[col] = df['amenities'].str.contains(keyword, case=False, na=False).astype(int)
        features_added.append(col)
    
    # Building age category
    if 'building_age_years' in df.columns:
        df['is_new_building'] = (df['building_age_years'] <= 5).astype(int)
        features_added.append('is_new_building')
    
    # Furnished encoding
    furnished_mapping = {'Furnished': 2, 'Semi-Furnished': 1, 'Unfurnished': 0}
    if 'furnished' in df.columns:
        df['furnished_numeric'] = df['furnished'].map(furnished_mapping).fillna(0).astype(int)
        features_added.append('furnished_numeric')
    
    # Property size category
    df['size_category'] = pd.cut(df['size_sqft'], 
                                   bins=[0, 600, 1000, 1500, 3000, 10000],
                                   labels=['Small', 'Medium', 'Large', 'Very Large', 'Mansion'])
    features_added.append('size_category')
    
    # Metro and beach encoding (convert Yes/No to 1/0)
    if 'has_metro' in df.columns:
        df['has_metro_numeric'] = (df['has_metro'] == 'Yes').astype(int)
        features_added.append('has_metro_numeric')
    
    if 'beach_accessible' in df.columns:
        df['beach_accessible_numeric'] = (df['beach_accessible'] == 'Yes').astype(int)
        features_added.append('beach_accessible_numeric')
    
    print(f"[SUCCESS] Added {len(features_added)} engineered features:")
    for feat in features_added:
        print(f"  - {feat}")
    
    return df


def validate_processed_data(df):
    """Quality checks on processed data"""
    print("\n" + "="*60)
    print("DATA VALIDATION REPORT")
    print("="*60)
    
    # Basic stats
    print(f"\nTotal Records: {len(df):,}")
    
    # Missing values
    print("\nMissing Values in Critical Columns:")
    critical_cols = ['annual_rent', 'size_sqft', 'neighborhood', 'property_type', 'tier']
    for col in critical_cols:
        if col in df.columns:
            missing = df[col].isna().sum()
            print(f"  {col}: {missing} ({missing/len(df)*100:.1f}%)")
    
    # Price statistics
    print("\nRent Statistics:")
    print(f"  Min: {df['annual_rent'].min():,.0f} AED/year")
    print(f"  Max: {df['annual_rent'].max():,.0f} AED/year")
    print(f"  Mean: {df['annual_rent'].mean():,.0f} AED/year")
    print(f"  Median: {df['annual_rent'].median():,.0f} AED/year")
    print(f"  Std Dev: {df['annual_rent'].std():,.0f} AED/year")
    
    # Size statistics
    print("\nSize Statistics:")
    print(f"  Min: {df['size_sqft'].min():,.0f} sqft")
    print(f"  Max: {df['size_sqft'].max():,.0f} sqft")
    print(f"  Mean: {df['size_sqft'].mean():,.0f} sqft")
    
    # Distributions
    print("\nProperty Type Distribution:")
    print(df['property_type'].value_counts())
    
    print("\nNeighborhood Coverage:")
    print(f"  Unique neighborhoods: {df['neighborhood'].nunique()}")
    
    print("\nTier Distribution:")
    if 'tier' in df.columns:
        print(df['tier'].value_counts())
    
    print("\nData Source Distribution:")
    if 'data_source' in df.columns:
        print(df['data_source'].value_counts())


def export_datasets(merged_df, analytical_df):
    """Save processed datasets"""
    print("\n[INFO] Exporting datasets...")
    
    # Export merged dataset
    merged_df.to_csv(config.FILE_MERGED_DATA, index=False)
    print(f"[SUCCESS] Exported merged data: {config.FILE_MERGED_DATA}")
    print(f"  Rows: {len(merged_df):,}, Columns: {len(merged_df.columns)}")
    
    # Export analytical dataset
    analytical_df.to_csv(config.FILE_ANALYTICAL_DATASET, index=False)
    print(f"[SUCCESS] Exported analytical data: {config.FILE_ANALYTICAL_DATASET}")
    print(f"  Rows: {len(analytical_df):,}, Columns: {len(analytical_df.columns)}")


def main():
    """Main data processing pipeline"""
    print("\n" + "="*60)
    print("HOMEVISTA DATA PROCESSING PIPELINE")
    print("="*60)
    
    # 1. Load data
    scraped, synthetic, neighborhoods = load_datasets()
    
    # 2. Align schemas
    scraped_aligned, synthetic_aligned = align_schemas(scraped, synthetic)
    
    # 3. Merge datasets
    merged = merge_datasets(scraped_aligned, synthetic_aligned)
    
    # 4. Clean data
    merged = handle_outliers(merged, method='cap_99th')
    merged = clean_missing_values(merged)
    merged = standardize_data_types(merged)
    
    # 5. Engineer features
    analytical = engineer_features(merged.copy(), neighborhoods)
    
    # 6. Validate
    validate_processed_data(analytical)
    
    # 7. Export
    export_datasets(merged, analytical)
    
    print("\n" + "="*60)
    print("[SUCCESS] Data processing completed successfully!")
    print("="*60)
    print("\nOutput Files:")
    print(f"  1. {config.FILE_MERGED_DATA}")
    print(f"  2. {config.FILE_ANALYTICAL_DATASET}")
    print("\nReady for Phase 4: Analytics & Modeling\n")


if __name__ == "__main__":
    main()
