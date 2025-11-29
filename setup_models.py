"""
Model Download Script for Streamlit Cloud.

This script downloads pre-trained model files from Google Drive
to enable deployment on Streamlit Cloud (which has GitHub file size limits).

Usage:
    python setup_models.py
"""

import os
import sys
from pathlib import Path

def download_models():
    """Download model files from Google Drive."""
    models_dir = Path(__file__).parent / 'models'
    models_dir.mkdir(exist_ok=True)
    
    # Check if models already exist
    required_files = [
        'model_suite.pkl',
        'ensemble_weights.pkl',
        'feature_engineer.pkl',
        'best_hyperparameters.pkl'
    ]
    
    missing_files = [f for f in required_files if not (models_dir / f).exists()]
    
    if not missing_files:
        print("✓ All model files already exist. Skipping download.")
        return True
    
    print(f"📥 Missing {len(missing_files)} model file(s). Starting download...")
    
    try:
        import gdown
    except ImportError:
        print("❌ Error: 'gdown' package not found.")
        print("   Install it with: pip install gdown")
        return False
    
    # Google Drive file ID (TO BE UPDATED BY USER)
    # Get this from your shareable Google Drive link
    # Example: https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view?usp=sharing
    # The file ID is: 1a2b3c4d5e6f7g8h9i0j
    
    GDRIVE_FILE_ID = "1ZlEQDDhDCMSZXexuhSo2yg31jSZ7Ggfe"
    
    if GDRIVE_FILE_ID == "YOUR_GOOGLE_DRIVE_FILE_ID_HERE":
        print("\n" + "="*70)
        print("⚠️  SETUP REQUIRED")
        print("="*70)
        print("\nPlease follow these steps:\n")
        print("1. Upload your 'models' folder (as a ZIP) to Google Drive")
        print("2. Right-click → Share → Set to 'Anyone with the link can view'")
        print("3. Copy the shareable link")
        print("4. Extract the FILE_ID from the link")
        print("5. Open setup_models.py and replace 'YOUR_GOOGLE_DRIVE_FILE_ID_HERE'")
        print("   with your actual file ID")
        print("\nExample link format:")
        print("https://drive.google.com/file/d/1a2b3c4d5e6f7g8h9i0j/view?usp=sharing")
        print("                                  ^^^^^^^^^^^^^^^^^^^^")
        print("                                  This is your FILE_ID")
        print("="*70)
        return False
    
    # Download the ZIP file
    output_path = models_dir / 'models.zip'
    url = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"
    
    print(f"\n📦 Downloading models from Google Drive...")
    print(f"   URL: {url}")
    
    try:
        gdown.download(url, str(output_path), quiet=False)
        
        # If downloaded file is a ZIP, extract it
        if output_path.exists() and output_path.suffix == '.zip':
            print("\n📂 Extracting files...")
            import zipfile
            with zipfile.ZipFile(output_path, 'r') as zip_ref:
                zip_ref.extractall(models_dir)
            
            # Remove the ZIP file
            output_path.unlink()
            print("✓ Extraction complete")
        
        # Verify all files are present
        missing_after = [f for f in required_files if not (models_dir / f).exists()]
        
        if missing_after:
            print(f"\n❌ Error: Still missing files: {missing_after}")
            print("   Please check your Google Drive ZIP structure.")
            print("   Expected structure: models.zip containing all .pkl files directly")
            return False
        
        print("\n✅ All model files downloaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading models: {e}")
        print("\nTroubleshooting:")
        print("1. Verify the Google Drive link is set to 'Anyone with the link can view'")
        print("2. Check that the file ID is correct")
        print("3. Ensure you have internet connection")
        return False

def main():
    """Main entry point."""
    print("HomeVista Model Setup")
    print("=" * 70)
    
    success = download_models()
    
    if success:
        print("\n🎉 Setup complete! You can now run the app:")
        print("   streamlit run app.py")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please resolve the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
