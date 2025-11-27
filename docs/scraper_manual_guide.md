# Bayut Web Scraper - Manual Execution Guide

## Prerequisites

Before running the scraper, ensure you have Selenium and ChromeDriver installed:

### Step 1: Install Selenium
```bash
pip install selenium
```

### Step 2: Install ChromeDriver

**Option A - Automatic (Recommended)**:
```bash
pip install webdriver-manager
```

Then add this to `scraper.py` at line 14:
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
```

And update `setup_driver()` function line 43:
```python
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
```

**Option B - Manual**:
1. Download ChromeDriver from: https://chromedriver.chromium.org/downloads
2. Match your Chrome browser version
3. Extract and add to PATH

---

## Running the Scraper

### Test Run (RECOMMENDED FIRST)

Start with a test run to verify everything works:

```bash
cd e:\Work\Amir\antigravity\HomeVista_RealEstate
python src/scraper.py --test
```

**What this does:**
- Scrapes only 5 listings (fast test)
- Browser stays visible (`SCRAPE_HEADLESS = False`)
- Saves to `data/raw/test_scraped_listings.csv`
- Takes ~2-3 minutes

**Expected output:**
```
============================================================
BAYUT WEB SCRAPER - HOMEVISTA PROJECT
============================================================

[TEST MODE] Will scrape only 5 listings for testing
[INFO] Setting up Chrome WebDriver...
[SUCCESS] WebDriver initialized

[INFO] Searching for 1BR in Dubai Marina...
  URL: https://www.bayut.com/to-rent/property/dubai/dubai-marina/?beds=1
  [SUCCESS] Found 10 listings

  [1/5] Scraping: https://www.bayut.com/property/details-...
    ✓ 1BR - 95000 AED/year
...
```

### Full Scraping Run

Once test works, run the full scraper:

```bash
python src/scraper.py --count 100
```

**Parameters:**
- `--count 100`: Scrape 100 listings (adjust as needed)
- Default targets 5 neighborhoods with mixed property types
- Takes ~15-20 minutes for 100 listings

**For headless mode** (browser runs in background):
Edit `src/config.py` line 109:
```python
SCRAPE_HEADLESS = True  # Change to True
```

---

## Monitoring Progress

Watch the terminal output:

```
[1/100] Scraping: https://www.bayut.com/property/details-12345...
  ✓ 1BR - 95,000 AED/year

[2/100] Scraping: https://www.bayut.com/property/details-67890...
  ✓ Studio - 65,000 AED/year
```

**Progress indicators:**
- `✓` = Successfully scraped
- `[WARN]` = Minor issue (continues)
- `[ERROR]` = Failed to scrape that listing (skips)

---

## Troubleshooting

### Issue 1: "ChromeDriver not found"
**Solution**: Install webdriver-manager (see Prerequisites Step 2)

### Issue 2: Bot detection / CAPTCHA
**Solutions**:
1. Increase delays in `config.py`:
   ```python
   SCRAPE_DELAY_MIN = 5
   SCRAPE_DELAY_MAX = 10
   ```
2. Run in non-headless mode (already default)
3. Try again later (IP may be temporarily blocked)

### Issue 3: No listings found
**Check**:
1. Is Bayut accessible in browser?
2. Are neighborhood names correct? (check Bayut URL structure)
3. Try test mode first to debug

### Issue 4: Missing data fields
**This is normal** - some listings may not have all fields
- Scraper marks missing fields as `None`
- We'll clean this in data processing phase

---

## After Scraping Completes

### 1. Check Output File

```bash
# View first few rows
python -c "import pandas as pd; df = pd.read_csv('data/raw/scraped_listings.csv'); print(df.head())"

# Check data quality
python -c "import pandas as pd; df = pd.read_csv('data/raw/scraped_listings.csv'); print(f'Total: {len(df)}'); print(df.info())"
```

### 2. Validate Data Quality

I'll create a validation script for you - but first, let me know how the scraping goes!

### 3. Next Steps

Once you have scraped data:
1. Run validation (I'll guide you)
2. Merge with synthetic data
3. Move to Phase 3: Data Processing

---

## Expected Timeline

- **Test run**: 2-3 minutes
- **100 listings**: 15-20 minutes
- **400 listings**: 60-80 minutes

**Recommendation**: Start with 50-100 listings, validate, then do more if needed.

---

## Tips for Best Results

✓ Run during off-peak hours (late night UAE time)
✓ Start with test mode
✓ Monitor first 10-20 listings to ensure quality
✓ If you see many errors, stop and troubleshoot
✓ Keep browser visible (non-headless) for first run
✓ You can press `Ctrl+C` to stop anytime (data saves automatically)

---

## What to Do If Something Goes Wrong

1. **Stop the scraper**: Press `Ctrl+C`
2. **Check what was scraped**: Open `data/raw/scraped_listings.csv` or test CSV
3. **Report the issue**: Tell me what error you saw
4. **Try test mode**: `python src/scraper.py --test` to debug

---

## Ready to Start?

**Recommended first command:**
```bash
python src/scraper.py --test
```

Let me know when you've run this and I'll help with the next steps!
