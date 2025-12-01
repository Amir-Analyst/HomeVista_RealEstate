"""
Configuration settings for HomeVista project
Centralized paths, constants, and parameters
"""

import os
from pathlib import Path

# Project Root Directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Data Paths
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
REFERENCE_DATA_DIR = DATA_DIR / "reference"

# Specific File Paths
FILE_NEIGHBORHOODS = REFERENCE_DATA_DIR / "neighborhoods.csv"
FILE_PROPERTY_TYPES = REFERENCE_DATA_DIR / "property_types.csv"
FILE_SCRAPED_LISTINGS = RAW_DATA_DIR / "scraped_listings.csv"
FILE_SYNTHETIC_LISTINGS = RAW_DATA_DIR / "synthetic_listings.csv"
FILE_TENANT_PROFILES = RAW_DATA_DIR / "tenant_profiles.csv"
FILE_MERGED_DATA = PROCESSED_DATA_DIR / "merged_listings.csv"
FILE_ANALYTICAL_DATASET = PROCESSED_DATA_DIR / "analytical_dataset.csv"

# Model Paths
MODEL_PRICE_PREDICTOR = MODELS_DIR / "rental_price_model.pkl"
MODEL_SCALER = MODELS_DIR / "feature_scaler.pkl"

# Data Generation Parameters
NUM_SYNTHETIC_LISTINGS = 16000  # 100% coverage of real market (16K-18K listings)
NUM_TENANT_PROFILES = 5000  # Increased proportionally
RANDOM_SEED = 42

# Dubai Neighborhoods (20 areas)
NEIGHBORHOODS = [
    "Dubai Marina",
    "Jumeirah Beach Residence (JBR)",
    "Downtown Dubai",
    "Business Bay",
    "Dubai Internet City",
    "Dubai Media City",
    "Jumeirah Lake Towers (JLT)",
    "Barsha Heights (Tecom)",
    "Al Barsha",
    "Dubai Sports City",
    "Discovery Gardens",
    "International City",
    "Deira",
    "Bur Dubai",
    "Jumeirah",
    "Arabian Ranches",
    "Motor City",
    "Dubai Silicon Oasis",
    "DIFC",
    "Al Nahda"
]

# Property Types
PROPERTY_TYPES = ["Studio", "1BR", "2BR", "3BR", "Villa"]

# Amenities List
AMENITIES = [
    "Parking",
    "Swimming Pool",
    "Gym",
    "Security",
    "Balcony",
    "Maid's Room",
    "Central AC",
    "Built-in Wardrobes",
    "Pets Allowed",
    "Study Room"
]

# Price Ranges (AED per year) - Will be refined with market research
RENT_RANGES = {
    "Studio": (30000, 65000),
    "1BR": (45000, 110000),
    "2BR": (70000, 180000),
    "3BR": (100000, 250000),
    "Villa": (150000, 450000)
}

# Size Ranges (sq ft)
SIZE_RANGES = {
    "Studio": (350, 600),
    "1BR": (600, 950),
    "2BR": (900, 1500),
    "3BR": (1300, 2200),
    "Villa": (2500, 6000)
}

# Model Training Parameters
TEST_SIZE = 0.2  # 80-20 train-test split
CROSS_VALIDATION_FOLDS = 5
RANDOM_FOREST_ESTIMATORS = 100
RANDOM_FOREST_MAX_DEPTH = 20

# Web Scraping Settings
SCRAPE_TARGET_COUNT = 400  # Number of listings to scrape
SCRAPE_DELAY_MIN = 2  # Minimum seconds between requests
SCRAPE_DELAY_MAX = 5  # Maximum seconds between requests
SCRAPE_HEADLESS = False  # Run browser in headless mode (set True for background)
SCRAPE_TIMEOUT = 30  # Page load timeout (seconds)

# Bayut URLs
BAYUT_BASE = "https://www.bayut.com"
BAYUT_SEARCH = f"{BAYUT_BASE}/to-rent/property/dubai/"

# User Agents (rotate to avoid detection)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Dashboard Settings
DASHBOARD_TITLE = "HomeVista: Dubai Rental Intelligence"
DASHBOARD_ICON = "🏙️"

# Create directories if they don't exist
def initialize_directories():
    """Create all necessary project directories"""
    directories = [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        REFERENCE_DATA_DIR,
        MODELS_DIR,
        NOTEBOOKS_DIR,
        REPORTS_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
    
    print("[SUCCESS] Project directories initialized successfully")

if __name__ == "__main__":
    initialize_directories()
