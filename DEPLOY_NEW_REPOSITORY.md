# Deploy polished V2 from a new repository

## Create GitHub repository

Recommended name:

`global-capital-rotation-cio-v2-polished`

Choose **Private** unless you intentionally want the source code public.

## Upload

Upload every item from this package to the repository root.

The root must contain:

- `app.py`
- `engine.py`
- `report_builder.py`
- `storage.py`
- `config.py`
- `auth.py`
- `refresh_all.py`
- `requirements.txt`
- `current_snapshot.csv`
- `portfolio_holdings.csv`

It must also contain:

- `.github/workflows/validate.yml`
- `.github/workflows/daily_refresh.yml`
- `.streamlit/config.toml`
- `.streamlit/secrets.example.toml`

## iPhone note

iPhone uploads may skip hidden folders. The folder `IPHONE_MANUAL_FILES` contains
copies of the exact content needed to create the four hidden files manually.

## GitHub secret

Go to:

`Settings → Secrets and variables → Actions → New repository secret`

Create:

`FRED_API_KEY`

## Validate

Open **Actions** and confirm **Validate Polished V2 Application** turns green.

## Refresh

Run **Daily Polished V2 Market Refresh** manually once.

## Streamlit deployment

Use:

- Repository: the polished V2 repository
- Branch: `main`
- Main file: `app.py`
- Python: `3.11`

Under Streamlit **Advanced settings → Secrets**, enter:

```toml
FRED_API_KEY = "your-active-key"
APP_PASSWORD = "your-private-password"
APP_TITLE = "Global Capital Rotation CIO"
```

The first page should say:

`Chief Investment Officer Command Center`

The sidebar should show:

- Command Center
- My Portfolio
- Capital Rotation
- Risk & Regime
- CIO Committee
- Reports
- System Health
