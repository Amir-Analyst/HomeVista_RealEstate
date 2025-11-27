"""
Synthetic Data Generator for HomeVista Real Estate Analytics
Generates realistic rental property listings based on Dubai market research
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
import config

# Initialize Faker
fake = Faker()
np.random.seed(config.RANDOM_SEED)
Faker.seed(config.RANDOM_SEED)


def load_reference_data():
    """Load neighborhood and property type reference data"""
    print("[INFO] Loading reference data...")
    
    neighborhoods = pd.read_csv(config.FILE_NEIGHBORHOODS)
    property_types = pd.read_csv(config.FILE_PROPERTY_TYPES)
    
    print(f"[SUCCESS] Loaded {len(neighborhoods)} neighborhoods and {len(property_types)} property types")
    return neighborhoods, property_types


def calculate_rent(neighborhood_row, property_type, size_sqft):
    """
    Calculate realistic rent based on neighborhood, property type, and size
    Uses normal distribution within the market research ranges
    """
    # Get rent range for this neighborhood and property type
    min_col = f"{property_type.lower().replace('br', 'br')}_min"
    max_col = f"{property_type.lower().replace('br', 'br')}_max"
    
    rent_min = neighborhood_row[min_col]
    rent_max = neighborhood_row[max_col]
    
    # Handle edge case where min == max
    if rent_min == rent_max:
        return rent_min
    
    # Calculate mean and std dev for normal distribution
    rent_mean = (rent_min + rent_max) / 2
    rent_std = (rent_max - rent_min) / 4  # 95% of data within range
    
    # Generate rent with normal distribution
    base_rent = np.random.normal(rent_mean, rent_std)
    
    # Ensure within bounds
    base_rent = np.clip(base_rent, rent_min, rent_max)
    
    # Get size range for this property type
    size_min_col = f"{property_type.lower().replace('br', 'br')}_size_min"
    size_max_col = f"{property_type.lower().replace('br', 'br')}_size_max"
    
    size_min = neighborhood_row[size_min_col]
    size_max = neighborhood_row[size_max_col]
    
    # Adjust rent based on size (larger = more expensive)
    # Handle case where size_min == size_max
    if size_max > size_min:
        size_percentile = (size_sqft - size_min) / (size_max - size_min)
        size_percentile = np.clip(size_percentile, 0, 1)
        
        # Apply size adjustment (±15% based on size)
        size_adjustment = 1 + (size_percentile - 0.5) * 0.3
        final_rent = base_rent * size_adjustment
    else:
        final_rent = base_rent
    
    return round(final_rent, -2)  # Round to nearest 100


def assign_amenities(annual_rent, property_type_row, tier):
    """
    Assign amenities based on property price tier and type
    Higher priced properties get more premium amenities
    """
    # Base amenities from property type
    base_amenities = property_type_row['base_amenities'].split(';')
    amenities = base_amenities.copy()
    
    # Additional amenities pool
    additional_amenities = [
        "Swimming Pool",
        "Gym",
        "Balcony",
        "Maid's Room",
        "Study Room",
        "Pets Allowed",
        "Shared Spa",
        "Children's Play Area",
        "Covered Parking",
        "View (Sea/Marina/Park)"
    ]
    
    # Determine number of additional amenities based on tier
    amenity_counts = {
        'Luxury': (5, 8),
        'Premium': (3, 6),
        'Mid-Market': (2, 4),
        'Budget': (1, 3)
    }
    
    min_amenities, max_amenities = amenity_counts.get(tier, (2, 4))
    num_additional = np.random.randint(min_amenities, max_amenities + 1)
    
    # Randomly select additional amenities
    selected_additional = np.random.choice(
        additional_amenities,
        size=min(num_additional, len(additional_amenities)),
        replace=False
    )
    
    amenities.extend(selected_additional)
    
    # Remove duplicates and return as semicolon-separated string
    amenities = list(set(amenities))
    return ';'.join(sorted(amenities))


def generate_property_size(property_type, neighborhood_row):
    """Generate realistic property size within neighborhood ranges"""
    size_min_col = f"{property_type.lower().replace('br', 'br')}_size_min"
    size_max_col = f"{property_type.lower().replace('br', 'br')}_size_max"
    
    size_min = neighborhood_row[size_min_col]
    size_max = neighborhood_row[size_max_col]
    
    # Use normal distribution slightly skewed toward average size
    size_mean = (size_min + size_max) / 2
    size_std = (size_max - size_min) / 5
    
    size = np.random.normal(size_mean, size_std)
    return int(np.clip(size, size_min, size_max))


def generate_property_listings(neighborhoods, property_types, num_listings=2500):
    """Generate synthetic property listings"""
    print(f"\n[INFO] Generating {num_listings} property listings...")
    
    listings = []
    
    # Distribution of property types (weighted toward common types)
    type_weights = {
        'Studio': 0.20,
        '1BR': 0.35,
        '2BR': 0.30,
        '3BR': 0.15
    }
    
    for i in range(num_listings):
        # Select random neighborhood
        neighborhood_row = neighborhoods.sample(n=1, weights=neighborhoods['tier'].map({
            'Luxury': 0.15,
            'Premium': 0.25,
            'Mid-Market': 0.35,
            'Budget': 0.25
        })).iloc[0]
        
        # Select property type based on weights
        property_type = np.random.choice(
            list(type_weights.keys()),
            p=list(type_weights.values())
        )
        
        property_type_row = property_types[property_types['property_type'] == property_type].iloc[0]
        
        # Generate property size
        size_sqft = generate_property_size(property_type, neighborhood_row)
        
        # Calculate rent
        annual_rent = calculate_rent(neighborhood_row, property_type, size_sqft)
        monthly_rent = round(annual_rent / 12, -2)
        
        # Assign amenities
        amenities = assign_amenities(annual_rent, property_type_row, neighborhood_row['tier'])
        
        # Generate listing metadata
        days_ago = np.random.randint(1, 90)
        posted_date = datetime.now() - timedelta(days=days_ago)
        
        # Create listing
        listing = {
            'listing_id': f'PF{str(i+1).zfill(6)}',
            'neighborhood': neighborhood_row['neighborhood'],
            'property_type': property_type,
            'bedrooms': property_type_row['bedrooms'],
            'bathrooms': property_type_row['bathrooms'],
            'size_sqft': size_sqft,
            'annual_rent': int(annual_rent),
            'monthly_rent': int(monthly_rent),
            'price_per_sqft': round(annual_rent / size_sqft, 2),
            'furnished': np.random.choice(['Furnished', 'Unfurnished', 'Semi-Furnished'],
                                         p=[0.3, 0.5, 0.2]),
            'amenities': amenities,
            'has_metro': neighborhood_row['has_metro'],
            'beach_accessible': neighborhood_row['beach_accessible'],
            'floor_number': np.random.randint(1, 45) if property_type != '3BR' else np.random.randint(10, 40),
            'building_age_years': np.random.randint(0, 20),
            'posted_date': posted_date.strftime('%Y-%m-%d'),
            'agent_name': fake.name(),
            'agent_company': np.random.choice([
                'Property Finder', 'Bayut', 'Dubizzle', 'Allsopp & Allsopp',
                'Haus & Haus', 'Driven Properties', 'Espace Real Estate'
            ]),
            'tier': neighborhood_row['tier']
        }
        
        listings.append(listing)
        
        if (i + 1) % 500 == 0:
            print(f"[PROGRESS] Generated {i + 1}/{num_listings} listings...")
    
    df = pd.DataFrame(listings)
    print(f"[SUCCESS] Generated {len(df)} property listings")
    return df


def generate_tenant_profiles(num_profiles=1000):
    """Generate synthetic tenant profile data"""
    print(f"\n[INFO] Generating {num_profiles} tenant profiles...")
    
    profiles = []
    
    for i in range(num_profiles):
        # Generate tenant demographics
        age = np.random.normal(35, 10)
        age = int(np.clip(age, 22, 65))
        
        # Profession categories
        professions = [
            'IT Professional', 'Finance Professional', 'Healthcare Worker',
            'Teacher', 'Engineer', 'Sales & Marketing', 'Hospitality',
            'Manager', 'Consultant', 'Entrepreneur'
        ]
        
        profession = np.random.choice(professions)
        
        # Income based on profession (monthly in AED)
        income_ranges = {
            'IT Professional': (15000, 45000),
            'Finance Professional': (20000, 60000),
            'Healthcare Worker': (12000, 35000),
            'Teacher': (8000, 18000),
            'Engineer': (15000, 40000),
            'Sales & Marketing': (10000, 35000),
            'Hospitality': (6000, 20000),
            'Manager': (20000, 55000),
            'Consultant': (18000, 50000),
            'Entrepreneur': (15000, 80000)
        }
        
        income_min, income_max = income_ranges[profession]
        monthly_income = int(np.random.normal((income_min + income_max) / 2, (income_max - income_min) / 4))
        monthly_income = np.clip(monthly_income, income_min, income_max)
        
        # Family size
        family_size = np.random.choice([1, 2, 3, 4, 5], p=[0.25, 0.35, 0.20, 0.15, 0.05])
        
        # Preferred property type based on family size
        if family_size == 1:
            preferred_type = np.random.choice(['Studio', '1BR'], p=[0.4, 0.6])
        elif family_size == 2:
            preferred_type = np.random.choice(['1BR', '2BR'], p=[0.3, 0.7])
        elif family_size in [3, 4]:
            preferred_type = np.random.choice(['2BR', '3BR'], p=[0.5, 0.5])
        else:
            preferred_type = '3BR'
        
        # Budget (30-40% of monthly income as standard)
        budget_percentage = np.random.uniform(0.25, 0.45)
        max_monthly_rent = int(monthly_income * budget_percentage)
        
        profile = {
            'tenant_id': f'T{str(i+1).zfill(5)}',
            'age': age,
            'profession': profession,
            'monthly_income': int(monthly_income),
            'family_size': family_size,
            'preferred_property_type': preferred_type,
            'max_monthly_rent': max_monthly_rent,
            'max_annual_rent': max_monthly_rent * 12,
            'nationality': fake.country(),
            'move_in_timeline': np.random.choice(['Immediate', 'Within 1 month', 'Within 3 months', 'Flexible']),
            'pets': np.random.choice(['Yes', 'No'], p=[0.2, 0.8])
        }
        
        profiles.append(profile)
    
    df = pd.DataFrame(profiles)
    print(f"[SUCCESS] Generated {len(df)} tenant profiles")
    return df


def export_datasets(listings_df, tenants_df):
    """Export generated datasets to CSV files"""
    print("\n[INFO] Exporting datasets...")
    
    # Export synthetic listings
    listings_df.to_csv(config.FILE_SYNTHETIC_LISTINGS, index=False)
    print(f"[SUCCESS] Exported property listings to {config.FILE_SYNTHETIC_LISTINGS}")
    
    # Export tenant profiles
    tenants_df.to_csv(config.FILE_TENANT_PROFILES, index=False)
    print(f"[SUCCESS] Exported tenant profiles to {config.FILE_TENANT_PROFILES}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("DATA GENERATION SUMMARY")
    print("="*60)
    print(f"\nProperty Listings: {len(listings_df)}")
    print(f"  - Studios: {len(listings_df[listings_df['property_type'] == 'Studio'])}")
    print(f"  - 1BR: {len(listings_df[listings_df['property_type'] == '1BR'])}")
    print(f"  - 2BR: {len(listings_df[listings_df['property_type'] == '2BR'])}")
    print(f"  - 3BR: {len(listings_df[listings_df['property_type'] == '3BR'])}")
    print(f"\nRent Range: {listings_df['annual_rent'].min():,} - {listings_df['annual_rent'].max():,} AED/year")
    print(f"Average Rent: {listings_df['annual_rent'].mean():,.0f} AED/year")
    print(f"\nTenant Profiles: {len(tenants_df)}")
    print(f"Average Budget: {tenants_df['max_annual_rent'].mean():,.0f} AED/year")
    print("\n" + "="*60)


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("HOMEVISTA SYNTHETIC DATA GENERATOR")
    print("="*60)
    
    # Load reference data
    neighborhoods, property_types = load_reference_data()
    
    # Generate property listings
    listings_df = generate_property_listings(
        neighborhoods,
        property_types,
        num_listings=config.NUM_SYNTHETIC_LISTINGS
    )
    
    # Generate tenant profiles
    tenants_df = generate_tenant_profiles(
        num_profiles=config.NUM_TENANT_PROFILES
    )
    
    # Export datasets
    export_datasets(listings_df, tenants_df)
    
    print("\n[SUCCESS] Data generation completed successfully!\n")


if __name__ == "__main__":
    main()
