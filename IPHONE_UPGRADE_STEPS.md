# Upgrade the existing iPhone app to V2

1. Download and unzip the V2 package.
2. In the existing GitHub repository, upload all V2 files to the repository root.
3. Allow GitHub to replace duplicate files such as `app.py`, `requirements.txt`, and workflow files.
4. Commit directly to `main` with:
   `Deploy enhanced Streamlit V2`
5. Open GitHub Actions and confirm **Validate V2 Application** passes.
6. Streamlit should automatically redeploy from the updated repository.
7. Open the existing `.streamlit.app` address and refresh Safari.
8. Use the same `APP_PASSWORD` stored in Streamlit Secrets.
9. Open **Setup & Health** and run a data refresh.
10. On iPhone, keep the existing Home Screen shortcut; it will open V2 at the same URL.

Important: do not commit real API keys or passwords to GitHub.
