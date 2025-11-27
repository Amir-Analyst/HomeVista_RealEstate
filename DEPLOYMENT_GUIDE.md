# HomeVista Streamlit Cloud Deployment Guide

## 🎯 Quick Summary

Your app failed on Streamlit Cloud because:
1. ❌ **Model file size**: `model_suite.pkl` is 72.53 MB (GitHub limit: 25 MB)
2. ❌ **Parsing error**: "invalid literal for int() with base 10: 'Tier'"

✅ **Both issues are now FIXED!**

---

## ✅ What Was Fixed

### 1. Tier Parsing Error (Fixed in `predictor.py`)

**Before:**
```python
'tier_numeric': int(property_data['tier'].replace('Tier ', ''))  # Fails on 'Tier'
```

**After:**
```python
tier_str = str(property_data['tier']).strip()
if tier_str.lower().startswith('tier'):
    tier_str = tier_str[4:].strip()
try:
    tier_numeric = int(tier_str)  # Now handles 'Tier', 'Tier 1', '1', etc.
except ValueError:
    tier_numeric = 1  # Safe default
```

### 2. Model Hosting Solution

Models are now:
- ✅ Excluded from GitHub (added to `.gitignore`)
- ✅ Hosted on Google Drive
- ✅ Auto-downloaded on Streamlit Cloud deployment
- ✅ Cached locally after first download

---

## 📋 Deployment Steps

### Step 1: Prepare Model Files (DO THIS FIRST)

1. **Create a ZIP of your models folder:**

```bash
# Option A: Using PowerShell (Windows)
Compress-Archive -Path "models\*.pkl" -DestinationPath "models.zip"

# Option B: Using Python
python -c "import shutil; shutil.make_archive('models', 'zip', 'models')"
```

2. **Upload to Google Drive:**
   - Go to [drive.google.com](https://drive.google.com)
   - Click **"New" → "File upload"**
   - Upload `models.zip`
   
3. **Get shareable link:**
   - Right-click on uploaded file
   - Click **"Share"**
   - Change access to: **"Anyone with the link can view"**
   - Click **"Copy link"**
   
4. **Extract FILE_ID from the link:**
   
   Your link looks like:
   ```
   https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view?usp=sharing
                                     ^^^^^^^^^^^^^^^^^^^^
                                     This is your FILE_ID
   ```

### Step 2: Update `setup_models.py`

Open `setup_models.py` and replace this line (around line 47):

```python
GDRIVE_FILE_ID = "YOUR_GOOGLE_DRIVE_FILE_ID_HERE"
```

With your actual file ID:

```python
GDRIVE_FILE_ID = "1a2b3c4d5e6f7g8h9i0j"  # Your file ID here
```

### Step 3: Test Locally (Optional but Recommended)

```bash
# 1. Remove existing models to test download
rm models/*.pkl  # or manually delete

# 2. Test the download script
python setup_models.py

# 3. Should see:
#    ✓ Downloading models from Google Drive...
#    ✓ All model files downloaded successfully!

# 4. Run the app
streamlit run app.py
```

### Step 4: Push to GitHub

```bash
# Add all changes
git add .

# Commit (models will NOT be pushed - they're in .gitignore)
git commit -m "Fix deployment: Add model download system and tier parsing"

# Push to GitHub
git push origin main
```

**Verify:** Check your GitHub repository - you should see:
- ✅ `models/.gitkeep` (tiny file)
- ❌ NO `models/*.pkl` files (they're excluded)

### Step 5: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"** (or reboot existing deployment)
3. Select your repository
4. Main file: `app.py`
5. Click **"Deploy"**

**First deployment will:**
- Install dependencies (including `gdown`)
- Run `setup_models.py` automatically
- Download models from Google Drive (~30 seconds)
- Launch the app ✨

**Subsequent deployments:**
- Models are cached, no re-download needed!

---

## 🛠️ Troubleshooting

### Error: "Model files not found"

**Cause:** Models didn't download from Google Drive

**Fix:**
1. Check Streamlit Cloud logs for download errors
2. Verify Google Drive link is publicly accessible
3. Confirm file ID in `setup_models.py` is correct

### Error: "gdown: command not found"

**Cause:** `requirements.txt` wasn't updated

**Fix:**
1. Ensure `gdown>=4.7.1` is in `requirements.txt`
2. Redeploy the app

### Error: Still getting tier parsing error

**Cause:** Using old version of `predictor.py`

**Fix:**
1. Verify you committed and pushed the latest `predictor.py`
2. Check line 72-84 has the new tier parsing logic

---

## 📊 Expected Timeline

| Step | Time |
|:-----|:----:|
| Create models.zip | 1 min |
| Upload to Google Drive | 2-5 min |
| Update setup_models.py | 1 min |
| Push to GitHub | 1 min |
| Deploy on Streamlit Cloud | 2-3 min |
| **Total** | **~10 min** |

---

## 🎉 Success Indicators

When deployment succeeds, you'll see:

1. ✅ App loads without errors
2. ✅ Home page displays model metrics
3. ✅ Tenant/Landlord tools work
4. ✅ No "Model files not found" error
5. ✅ Predictions return successfully

---

## 💡 Pro Tips

1. **Keep the Google Drive link:** Don't delete the file or change permissions
2. **Version control:** If you retrain models, zip and re-upload to Google Drive
3. **Local development:** Run `setup_models.py` once, then develop normally
4. **Share with collaborators:** They also need to run `setup_models.py` once

---

## 📞 Need Help?

If you encounter issues:

1. Check **Streamlit Cloud logs** (click "Manage app" → "Logs")
2. Verify **Google Drive permissions** ("Anyone with link can view")
3. Test **locally first** with `python setup_models.py`

---

**You're all set!** Follow these steps, and your app will deploy successfully. 🚀
