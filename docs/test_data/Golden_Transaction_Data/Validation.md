## Validating that the app imports correctly and calculates all the metrics correctly

1. This folder has a set of xlsx files from brokerage accounts with all transactions for the time period.
2. The py files process these files to extract and transform the transactions to fit the requirements of the app.
3. I imported Foolish_Buys.csv into Golden-Buys-2025-07-15. Note, there was one line with an incorrect value in the amount column. I fixed this manually. 
./Fidelity_CraigRoth_2024_Transactions.csv:MSFT,BUY,2024-02-12,417.40,2.4550
./Foolish_Transactions.csv:MSFT,BUY,2024-02-12,417.4,2.8247,154.2977536
./Robinhood_Roth_Transactions.csv:MSFT,BUY,2024-02-12,417.4,0.369664,154.2977536
4. I exported the data from the db and verified that the data matches the foolish_buys.csv data and the amount is $84,204.98 in both the db and the source csv. 
5. Data import for buys seems to work as expected.
6. Next will calculate the total value of the portfolio (without splits) and compare that to the app. 
    1. Found a small difference in the current stock price data. After fixing that manually, the numbers match. 
    Mismatches in Current Price column:
    Date: 2024-05-28, Ticker: SMCI, Golden: 53.45000076293945, XIRR: 53.16999816894531
    Date: 2025-06-30, Ticker: META, Golden: 711.9000244140625, XIRR: 710.3900146484375
7. After doing all of that, I re-calculated XIRR in Foolish_XIRR_Calculations.csv and found the XIRR to be 25.403, where as the app reports 25.42%

### The file Foolish_XIRR_Calculations_Manual.csv matches with the database after importing from Foolish_Transactions.csv. 
Both of these files and this md are being put under source control. 