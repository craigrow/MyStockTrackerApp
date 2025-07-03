# Feature Gaps Log

Features identified during testing that need to be addressed:

1. When dividends are recorded, they should be shown in the Recent Activity box.
2. In addition to total gain, total invested, and cash balance, there should be a Total Dividends Received indicator.
3. If there is not price data for a specific stock, do not include it in the portfolio and show an error to the user.
4. Enable users to edit and/or delete transactions. (UI placeholders implemented, backend functionality needed)
5. ✅ IMPLEMENTED: ETF performance comparisons with time-period matching from actual purchase dates (vs QQQ and vs VOO columns).
6. ✅ IMPLEMENTED: The user needs a way of viewing all of the transactions (buy, sell, dividend) that are in the portfolio. Comprehensive transactions page with performance calculations and ETF comparisons.
7. Large CSV imports (100+ rows) cause production timeouts due to extensive price fetching during import. Need to implement asynchronous import or batch processing.
8. ✅ FIXED: Today vs Market box was showing incorrect date range (Friday-to-yesterday instead of yesterday-to-now when market open). Fixed date calculation logic.
9. ✅ FIXED: Portfolio Value and Total Gain/Loss now show closing prices when market is closed instead of stale intraday prices.
10. Application error on initial page load after deployment - requires page reload to fix. Possible Heroku dyno cold start or database connection issue.
11. Need to incorporate stock splits.
12. When we switch between views; from dashboard to transactions for example; we should persiste the portfolio that is being viewed, not switch portfolios.
13. We should have settings to determine which ETFs to use as comparisons on a per portfolio basis.
14. Let's create a cash log. It will show all of the assumed cash inflows and outflows for the portfolio. Then, we should enable the user to manually enter inflows and outflows.
15. App load is still a bad experience. What we want is, first, load the app with whatever cached data we have. Display a message: showing cached data from [DATE/time], refreshing data. Then, when you have fresh data, update everything and change the message to say, up to date as of [Date/time].
16. **CRITICAL: Heroku Deployment Reliability** - Frequent transient problems when deploying code to Heroku, including cold start issues causing 30+ second response times and apparent "down" status. Need to implement: health checks, dyno keep-alive mechanism, deployment monitoring, and consider upgrading from Basic dynos to prevent sleep mode. Goal: Zero deployment incidents.
17. **Individual Transaction Duplicate Detection** - Web UI allows entering the same transaction multiple times without validation. Need to implement duplicate detection for manual transaction entry (similar to CSV import validation) to prevent accidental duplicate entries through the web interface.
18. Let's create an immutable transaction log. Any time a user adds, modifies or delets a transaction or a dividend, we should record that in the log for auditability and debugging purposes.
