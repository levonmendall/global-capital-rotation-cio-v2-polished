# Data schemas

## current_snapshot.csv

Required columns:

`ticker, group, level, price, move_1d, momentum_3m, momentum_12m, breadth, flow, risk_score, volatility`

## portfolio_holdings.csv

Required columns:

`ticker, description, market_value, cost_basis, account_type, max_weight`

`max_weight` uses decimal form: `0.20` means 20%.

Never include account numbers, Social Security numbers, passwords, or brokerage
credentials in CSV files.
