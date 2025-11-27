"""
Web Scraper for Bayut Dubai Rental Listings
Collects real property data for HomeVista project
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import config

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random
from datetime import datetime
import re


def setup_driver(headless=True):
    """
    Set up Selenium WebDriver with anti-detection measures
    """
    print("[INFO] Setting up Chrome WebDriver...")
    
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument('--headless=new')
    
    # Anti-detection measures
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f'user-agent={random.choice(config.USER_AGENTS)}')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    print("[SUCCESS] WebDriver initialized")
    return driver


def human_delay():
    """Random delay to simulate human behavior"""
    delay = random.uniform(config.SCRAPE_DELAY_MIN, config.SCRAPE_DELAY_MAX)
    time.sleep(delay)


def clean_price(price_text):
    """Extract numeric price from formatted text"""
    # Remove AED, commas, /year, /month, etc.
    numbers = re.findall(r'[\d,]+', price_text)
    if numbers:
        price = int(numbers[0].replace(',', ''))
        
        # Convert monthly to annual if needed
        if '/month' in price_text.lower() or 'per month' in price_text.lower():
            price = price * 12
        
        return price
    return None


def clean_size(size_text):
    """Extract size in sqft from text"""
    # Look for sqft or sqm
    numbers = re.findall(r'[\d,]+', size_text)
    if numbers:
        size = int(numbers[0].replace(',', ''))
        
        # Convert sqm to sqft if needed (1 sqm = 10.764 sqft)
        if 'sqm' in size_text.lower() or 'm²' in size_text.lower():
            size = int(size * 10.764)
        
        return size
    return None


def close_popups(driver):
    """
    Close pop-ups and overlays that may appear on Bayut
    """
    try:
        # Wait a moment for pop-ups to appear
        time.sleep(2)
        
        # Try to close TruBroker ad pop-up
        try:
            close_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']")
            close_button.click()
            print("  [INFO] Closed ad pop-up")
            time.sleep(1)
        except:
            pass
        
        # Try to close any modal overlays
        try:
            modal_close = driver.find_element(By.CSS_SELECTOR, "button[class*='close'], button[class*='dismiss']")
            modal_close.click()
            print("  [INFO] Closed modal overlay")
            time.sleep(1)
        except:
            pass
        
        # Press ESC key to dismiss any overlays
        try:
            from selenium.webdriver.common.keys import Keys
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
            time.sleep(1)
        except:
            pass
            
    except Exception as e:
        # It's okay if we can't close pop-ups, continue anyway
        pass


def extract_property_type(title, bedrooms=None):
    """Extract property type from title or bedrooms count"""
    title_lower = title.lower()
    
    # Check for studio
    if 'studio' in title_lower:
        return 'Studio'
    
    # Check for bedroom counts in title
    if '3 bed' in title_lower or '3br' in title_lower or 'three bed' in title_lower or '3-bed' in title_lower:
        return '3BR'
    elif '2 bed' in title_lower or '2br' in title_lower or 'two bed' in title_lower or '2-bed' in title_lower:
        return '2BR'
    elif '1 bed' in title_lower or '1br' in title_lower or 'one bed' in title_lower or '1-bed' in title_lower:
        return '1BR'
    
    # Fallback to using bedrooms count from property facts
    if bedrooms is not None:
        if bedrooms == 0:
            return 'Studio'
        elif bedrooms == 1:
            return '1BR'
        elif bedrooms == 2:
            return '2BR'
        elif bedrooms == 3:
            return '3BR'
    
    return 'Unknown'


def scrape_listing_details(driver, url, neighborhood=None):
    """
    Scrape details from a single listing page
    
    Args:
        driver: Selenium WebDriver
        url: Listing URL
        neighborhood: Neighborhood name (passed from search context)
    """
    try:
        driver.get(url)
        human_delay()
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        
        listing_data = {}
        
        # Extract listing ID from URL
        listing_data['listing_id'] = url.split('-')[-1].replace('.html', '')
        
        # Title
        try:
            title = driver.find_element(By.TAG_NAME, "h1").text
            listing_data['title'] = title
        except:
            listing_data['title'] = None
        
        # Neighborhood - use the one passed from search context (most reliable)
        listing_data['neighborhood'] = neighborhood if neighborhood else 'Unknown'
        
        # Property facts (beds, baths, size) - extract BEFORE property_type
        try:
            facts = driver.find_elements(By.CSS_SELECTOR, "span[aria-label*='Bed'], span[aria-label*='Bath'], span[aria-label*='Area']")
            
            listing_data['bedrooms'] = None
            listing_data['bathrooms'] = None
            listing_data['size_sqft'] = None
            
            for fact in facts:
                label = fact.get_attribute('aria-label')
                text = fact.text
                
                if 'Bed' in label:
                    # Extract number
                    bed_num = re.findall(r'\d+', text)
                    listing_data['bedrooms'] = int(bed_num[0]) if bed_num else 0
                elif 'Bath' in label:
                    bath_num = re.findall(r'\d+', text)
                    listing_data['bathrooms'] = int(bath_num[0]) if bath_num else 0
                elif 'Area' in label:
                    listing_data['size_sqft'] = clean_size(text)
        except Exception as e:
            print(f"  [WARN] Error extracting facts: {e}")
        
        # Now extract property_type using title AND bedrooms as fallback
        listing_data['property_type'] = extract_property_type(
            listing_data.get('title', ''), 
            listing_data.get('bedrooms')
        )
        
        # Price
        try:
            price_elem = driver.find_element(By.CSS_SELECTOR, "[aria-label='Price']")
            listing_data['annual_rent'] = clean_price(price_elem.text)
        except:
            listing_data['annual_rent'] = None
        
        # Amenities
        try:
            amenity_elems = driver.find_elements(By.CSS_SELECTOR, "span[aria-label*='amenity']")
            amenities = [elem.text for elem in amenity_elems if elem.text]
            listing_data['amenities'] = ';'.join(amenities) if amenities else ''
        except:
            listing_data['amenities'] = ''
        
        # Furnished status - check amenities or description
        furnished_keywords = ['furnished', 'furnish']
        listing_data['furnished'] = 'Unfurnished'
        if any(keyword in listing_data['amenities'].lower() for keyword in furnished_keywords):
            listing_data['furnished'] = 'Furnished'
        
        # Agent name
        try:
            agent_elem = driver.find_element(By.CSS_SELECTOR, "a[aria-label*='Agent']")
            listing_data['agent_name'] = agent_elem.text
        except:
            listing_data['agent_name'] = None
        
        # Posted date
        try:
            date_elem = driver.find_element(By.CSS_SELECTOR, "span[aria-label*='Verified']")
            listing_data['posting_date'] = datetime.now().strftime('%Y-%m-%d')  # Placeholder
        except:
            listing_data['posting_date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Metro and beach - mark as unknown for now
        listing_data['has_metro'] = 'Unknown'
        listing_data['beach_accessible'] = 'Unknown'
        
        return listing_data
        
    except Exception as e:
        print(f"  [ERROR] Failed to scrape {url}: {e}")
        return None


def get_listing_urls(driver, neighborhood, property_type, max_listings=50):
    """
    Get listing URLs from Bayut search results for a specific neighborhood and property type
    """
    print(f"\n[INFO] Searching for {property_type} in {neighborhood}...")
    
    # Build search URL
    # Format: https://www.bayut.com/to-rent/property/dubai/{neighborhood}/
    neighborhood_slug = neighborhood.lower().replace(' ', '-').replace('(', '').replace(')', '')
    search_url = f"{config.BAYUT_BASE}/to-rent/property/dubai/{neighborhood_slug}/"
    
    # Add property type filter if not Studio
    if property_type== '1BR':
        search_url += "?beds=1"
    elif property_type == '2BR':
        search_url += "?beds=2"
    elif property_type == '3BR':
        search_url += "?beds=3"
    
    print(f"  URL: {search_url}")
    
    try:
        driver.get(search_url)
        
        # Close any pop-ups that appear
        close_popups(driver)
        
        # Wait for listings to load
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except:
            pass
        
        # Try multiple CSS selectors for listing links
        listing_links = []
        
        # Try different selectors
        selectors = [
            "a[aria-label*='Listing link']",
            "a[href*='/property/details/']",
            "article a[href*='/property/']",
            "div[aria-label*='Listing'] a"
        ]
        
        for selector in selectors:
            try:
                links = driver.find_elements(By.CSS_SELECTOR, selector)
                if links:
                    listing_links = links
                    print(f"  [INFO] Found links using selector: {selector}")
                    break
            except:
                continue
        
        # Extract URLs
        urls = []
        for link in listing_links[:max_listings]:
            url = link.get_attribute('href')
            if url and '/property/' in url:  # Relaxed filter - any property URL
                # Avoid duplicates
                if url not in urls:
                    urls.append(url)
        
        # Debug: print first few URLs found
        if urls:
            print(f"  [DEBUG] Sample URLs found:")
            for url in urls[:3]:
                print(f"    - {url[:80]}...")
        
        print(f"  [SUCCESS] Found {len(urls)} listings")
        return urls
        
    except TimeoutException:
        print(f"  [WARN] Timeout loading {search_url}")
        return []
    except Exception as e:
        print(f"  [ERROR] Failed to get listings: {e}")
        return []


def main(target_count=100, test_mode=False):
    """
    Main scraping function
    
    Args:
        target_count: Total number of listings to scrape
        test_mode: If True, only scrape 5 listings for testing
    """
    print("\n" + "="*60)
    print("BAYUT WEB SCRAPER - HOMEVISTA PROJECT")
    print("="*60)
    
    if test_mode:
        print("\n[TEST MODE] Will scrape only 5 listings for testing")
        target_count = 5
    
    driver = setup_driver(headless=config.SCRAPE_HEADLESS)
    
    all_listings = []
    
    # Define targets per neighborhood (simplified for manual run)
    targets = [
        {"neighborhood": "Dubai Marina", "property_type": "1BR", "count": 10},
        {"neighborhood": "Jumeirah Beach Residence JBR", "property_type": "1BR", "count": 10},
        {"neighborhood": "Downtown Dubai", "property_type": "2BR", "count": 10},
        {"neighborhood": "Business Bay", "property_type": "Studio", "count": 10},
        {"neighborhood": "Jumeirah Lake Towers JLT", "property_type": "1BR", "count": 10},
        # Additional neighborhoods for more listings
        {"neighborhood": "Al Barsha", "property_type": "2BR", "count": 10},
        {"neighborhood": "Barsha Heights", "property_type": "1BR", "count": 10},
        {"neighborhood": "Discovery Gardens", "property_type": "1BR", "count": 10},
        {"neighborhood": "Deira", "property_type": "2BR", "count": 10},
        {"neighborhood": "Motor City", "property_type": "2BR", "count": 10},
    ]
    
    if test_mode:
        targets = targets[:1]  # Only first target in test mode
        targets[0]['count'] = 5
    
    try:
        for target in targets:
            if len(all_listings) >= target_count:
                break
            
            # Get listing URLs
            urls = get_listing_urls(
                driver,
                target['neighborhood'],
                target['property_type'],
                max_listings=target['count']
            )
            
            # Scrape each listing
            for i, url in enumerate(urls, 1):
                if len(all_listings) >= target_count:
                    break
                
                print(f"\n  [{len(all_listings)+1}/{target_count}] Scraping: {url[:80]}...")
                
                listing_data = scrape_listing_details(driver, url, target['neighborhood'])
                
                if listing_data:
                    all_listings.append(listing_data)
                    print(f"    ✓ {listing_data['property_type']} - {listing_data['annual_rent']} AED/year")
                
                # Don't delay on last item
                if i < len(urls):
                    human_delay()
        
        # Save to CSV
        if all_listings:
            df = pd.DataFrame(all_listings)
            
            output_file = config.FILE_SCRAPED_LISTINGS if not test_mode else Path(config.RAW_DATA_DIR) / 'test_scraped_listings.csv'
            df.to_csv(output_file, index=False)
            
            print("\n" + "="*60)
            print("SCRAPING COMPLETE")
            print("="*60)
            print(f"\nTotal listings scraped: {len(df)}")
            print(f"Output file: {output_file}")
            print(f"\nProperty type distribution:")
            print(df['property_type'].value_counts())
            print(f"\nNeighborhood distribution:")
            print(df['neighborhood'].value_counts())
        else:
            print("\n[WARN] No listings were scraped")
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Scraping interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Scraping failed: {e}")
    finally:
        driver.quit()
        print("\n[INFO] Browser closed")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape Bayut rental listings')
    parser.add_argument('--test', action='store_true', help='Run in test mode (5 listings only)')
    parser.add_argument('--count', type=int, default=100, help='Target number of listings')
    
    args = parser.parse_args()
    
    main(target_count=args.count, test_mode=args.test)
