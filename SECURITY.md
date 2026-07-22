# Security

Never commit real credentials to GitHub.

Use GitHub repository secrets for automated workflows and Streamlit Community
Cloud Secrets for the hosted app.

Required secret names:

- `FRED_API_KEY`
- `APP_PASSWORD`

If a secret is exposed, revoke or rotate it immediately, replace it in GitHub
and Streamlit, and reboot the app.
