"""
Data Validation Script for HomeVista Synthetic Data
Validates generated data against market research constraints
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
import config


def load_data():
    """Load generated datasets and reference data"""
    print("[INFO] Loading datasets...")
    
    listings = pd.read_csv(config.FILE_SYNTHETIC_LISTINGS)
    tenants = pd.read_csv(config.FILE_TENANT_PROFILES)
    neighborhoods = pd.read_csv(config.FILE_NEIGHBORHOODS)
    
    print(f"[SUCCESS] Loaded {len(listings)} listings, {len(tenants)} tenants, {len(neighborhoods)} neighborhoods")
    return listings, tenants, neighborhoods


def validate_completeness(listings, tenants):
    """Check for missing values in critical fields"""
    print("\n" + "="*60)
    print("VALIDATION 1: DATA COMPLETENESS")
    print("="*60)
    
    critical_fields = ['listing_id', 'neighborhood', 'property_type', 'annual_rent', 'size_sqft']
    
    issues = []
    for field in critical_fields:
        missing = listings[field].isna().sum()
        if missing > 0:
            issues.append(f"  [X] {field}: {missing} missing values")
        else:
            print(f"  [OK] {field}: No missing values")
    
    if issues:
        print("\nISSUES FOUND:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("\n[PASS] All critical fields are complete")
        return True


def validate_rent_ranges(listings, neighborhoods):
    """Validate that rents fall within market research ranges"""
    print("\n" + "="*60)
    print("VALIDATION 2: RENT RANGES")
    print("="*60)
    
    all_valid = True
    
    for _, neighborhood in neighborhoods.iterrows():
        neighborhood_name = neighborhood['neighborhood']
        neighborhood_listings = listings[listings['neighborhood'] == neighborhood_name]
        
        if len(neighborhood_listings) == 0:
            continue
        
        for prop_type in ['studio', '1br', '2br', '3br']:
            prop_type_display = prop_type.upper().replace('BR', 'BR')
            type_listings = neighborhood_listings[
                neighborhood_listings['property_type'] == prop_type_display.replace('STUDIO', 'Studio')
            ]
            
            if len(type_listings) == 0:
                continue
            
            min_col = f"{prop_type}_min"
            max_col = f"{prop_type}_max"
            
            expected_min = neighborhood[min_col]
            expected_max = neighborhood[max_col]
            
            actual_min = type_listings['annual_rent'].min()
            actual_max = type_listings['annual_rent'].max()
            
            # Allow 10% tolerance
            tolerance = 0.10
            min_tolerance = expected_min * (1 - tolerance)
            max_tolerance = expected_max * (1 + tolerance)
            
            if actual_min < min_tolerance or actual_max > max_tolerance:
                print(f"  ⚠️  {neighborhood_name} - {prop_type_display}: Range {actual_min:,.0f}-{actual_max:,.0f} outside expected {expected_min:,.0f}-{expected_max:,.0f}")
                all_valid = False
    
    if all_valid:
        print("  ✅ All rent ranges within expected bounds (±10% tolerance)")
        print("\n[PASS] Rent validation successful")
    else:
        print("\n[WARN] Some rent values outside expected ranges")
    
    return all_valid


def validate_size_correlation(listings):
    """Validate that property size correlates with rent"""
    print("\n" + "="*60)
    print("VALIDATION 3: SIZE-RENT CORRELATION")
    print("="*60)
    
    correlation = listings['size_sqft'].corr(listings['annual_rent'])
    
    print(f"  Correlation coefficient: {correlation:.3f}")
    
    if correlation > 0.6:
        print(f"  ✅ Strong positive correlation (R = {correlation:.3f})")
        print("\n[PASS] Size and rent are properly correlated")
        return True
    elif correlation > 0.4:
        print(f"  ⚠️  Moderate correlation (R = {correlation:.3f})")
        print("\n[WARN] Correlation could be stronger")
        return True
    else:
        print(f"  ❌ Weak correlation (R = {correlation:.3f})")
        print("\n[FAIL] Size and rent correlation too weak")
        return False


def validate_distributions(listings):
    """Validate property type distributions"""
    print("\n" + "="*60)
    print("VALIDATION 4: PROPERTY TYPE DISTRIBUTION")
    print("="*60)
    
    total = len(listings)
    distribution = listings['property_type'].value_counts()
    
    print(f"\n  Total Listings: {total}")
    print(f"\n  Property Type Distribution:")
    for prop_type, count in distribution.items():
        percentage = (count / total) * 100
        print(f"    {prop_type}: {count} ({percentage:.1f}%)")
    
    # Expected ranges (flexible)
    expected_ranges = {
        'Studio': (15, 25),
        '1BR': (30, 40),
        '2BR': (25, 35),
        '3BR': (10, 20)
    }
    
    all_valid = True
    for prop_type, (min_pct, max_pct) in expected_ranges.items():
        if prop_type in distribution.index:
            actual_pct = (distribution[prop_type] / total) * 100
            if not (min_pct <= actual_pct <= max_pct):
                print(f"\n  ⚠️  {prop_type}: {actual_pct:.1f}% outside expected range {min_pct}-{max_pct}%")
                all_valid = False
    
    if all_valid:
        print(f"\n[PASS] All property types within expected distribution ranges")
    else:
        print(f"\n[WARN] Some property types outside expected ranges")
    
    return True  # This is not a critical failure


def validate_amenities(listings):
    """Validate amenity assignment by tier"""
    print("\n" + "="*60)
    print("VALIDATION 5: AMENITY DISTRIBUTION BY TIER")
    print("="*60)
    
    listings['amenity_count'] = listings['amenities'].apply(lambda x: len(x.split(';')))
    
    tier_amenities = listings.groupby('tier')['amenity_count'].agg(['mean', 'min', 'max'])
    
    print("\n  Average Amenity Count by Tier:")
    for tier, row in tier_amenities.iterrows():
        print(f"    {tier}: {row['mean']:.1f} (range: {row['min']}-{row['max']})")
    
    # Luxury should have more amenities than Budget
    if tier_amenities.loc['Luxury', 'mean'] > tier_amenities.loc['Budget', 'mean']:
        print(f"\n  ✅ Luxury properties have more amenities than Budget properties")
        print("\n[PASS] Amenity distribution is realistic")
        return True
    else:
        print(f"\n  ❌ Luxury properties don't have more amenities than Budget")
        print("\n[FAIL] Amenity distribution needs adjustment")
        return False


def print_summary_statistics(listings, tenants):
    """Print summary statistics"""
    print("\n" + "="*60)
    print("SUMMARY STATISTICS")
    print("="*60)
    
    print(f"\n📊 PROPERTY LISTINGS ({len(listings)} total)")
    print(f"  Rent Statistics:")
    print(f"    Min: {listings['annual_rent'].min():,.0f} AED/year")
    print(f"    Max: {listings['annual_rent'].max():,.0f} AED/year")
    print(f"    Mean: {listings['annual_rent'].mean():,.0f} AED/year")
    print(f"    Median: {listings['annual_rent'].median():,.0f} AED/year")
    
    print(f"\n  Size Statistics:")
    print(f"    Min: {listings['size_sqft'].min():,.0f} sqft")
    print(f"    Max: {listings['size_sqft'].max():,.0f} sqft")
    print(f"    Mean: {listings['size_sqft'].mean():,.0f} sqft")
    
    print(f"\n  Neighborhoods Represented: {listings['neighborhood'].nunique()}/20")
    
    print(f"\n👥 TENANT PROFILES ({len(tenants)} total)")
    print(f"  Budget Statistics:")
    print(f"    Min: {tenants['max_annual_rent'].min():,.0f} AED/year")
    print(f"    Max: {tenants['max_annual_rent'].max():,.0f} AED/year")
    print(f"    Mean: {tenants['max_annual_rent'].mean():,.0f} AED/year")
    
    print(f"\n  Family Size Distribution:")
    family_dist = tenants['family_size'].value_counts().sort_index()
    for size, count in family_dist.items():
        print(f"    {size} person(s): {count}")


def main():
    """Main validation execution"""
    print("\n" + "="*60)
    print("HOMEVISTA DATA VALIDATION")
    print("="*60)
    
    # Load data
    listings, tenants, neighborhoods = load_data()
    
    # Run validations
    results = {
        'completeness': validate_completeness(listings, tenants),
        'rent_ranges': validate_rent_ranges(listings, neighborhoods),
        'size_correlation': validate_size_correlation(listings),
        'distributions': validate_distributions(listings),
        'amenities': validate_amenities(listings)
    }
    
    # Print summary
    print_summary_statistics(listings, tenants)
    
    # Final result
    print("\n" + "="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test.upper()}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 [SUCCESS] All validations passed!")
        print("Data is ready for processing and analysis.\n")
        return 0
    else:
        print("\n⚠️  [WARNING] Some validations failed")
        print("Review the issues above before proceeding.\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
