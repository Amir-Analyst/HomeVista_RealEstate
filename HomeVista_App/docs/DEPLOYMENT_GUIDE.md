# Deployment Guide

## 1. Push Changes to GitHub
Open your terminal in the project root and run these commands to save the reorganization:

```bash
git add .
git commit -m "Refactor: Reorganize project structure into HomeVista_App"
git push origin main
```

## 2. Update Streamlit Cloud Settings
**CRITICAL STEP**: Since `app.py` has moved, Streamlit Cloud needs to know where to find it.

1.  Go to your [Streamlit Cloud Dashboard](https://share.streamlit.io).
2.  Find your app (**HomeVista_RealEstate**).
3.  Click the **three dots menu (⋮)** next to the app and select **Settings**.
4.  Locate the **"Main file path"** field.
5.  Change it from `app.py` to:
    ```text
    HomeVista_App/app.py
    ```
6.  Click **Save**.

The app will automatically redeploy with the new structure.
