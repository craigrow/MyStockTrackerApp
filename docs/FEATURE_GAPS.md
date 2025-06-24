# Feature Gaps Log

Features identified during testing that need to be addressed:

1. When dividends are recorded, they should be shown in the Recent Activity box.
2. In addition to total gain, total invested, and cash balance, there should be a Total Dividends Received indicator.
3. If there is not price data for a specific stock, do not include it in the portfolio and show an error to the user.
4. Enable users to edit and/or delete transactions.
5. The user needs a way of viewing all of the transactions (buy, sell, dividend) that are in the portfolio.
6. Large CSV imports (100+ rows) cause production timeouts due to extensive price fetching during import. Need to implement asynchronous import or batch processing.
7. ✅ FIXED: Today vs Market box was showing incorrect date range (Friday-to-yesterday instead of yesterday-to-now when market open).
