# Summary: This module contains helper functions for sorting and charting.

import matplotlib.pyplot as plt
from datetime import datetime
from os import system, name

# Function to Clear the Screen
def clear_screen():
    if name == "nt": # User is running Windows
        _ = system('cls')
    else: # User is running Linux or Mac
        _ = system('clear')

# Function to sort the stock list (alphabetical by symbol)
def sortStocks(stock_list):
    stock_list.sort(key=lambda x: x.symbol)

# Function to sort the daily stock data (oldest to newest) for all stocks
def sortDailyData(stock_list):
    for stock in stock_list:
        stock.DataList.sort(key=lambda x: x.date)

# Function to create stock chart
def display_stock_chart(stock_list, symbol):
    date = []
    price = []
    volume = []
    company = ""
    
    # Find the selected stock and extract data
    found = False
    for stock in stock_list:
        if stock.symbol == symbol:
            found = True
            company = stock.name
            # Ensure data is sorted before plotting
            stock.DataList.sort(key=lambda x: x.date)
            for daily_data in stock.DataList:
                date.append(daily_data.date)
                price.append(daily_data.close)
                volume.append(daily_data.volume)
    
    # Check if data exists
    if not found:
        print(f"Stock {symbol} not found.")
        return
        
    if not date:
        print(f"No daily data available for {symbol}")
        return

    # Create the plot
    try:
        plt.figure(figsize=(10, 6))
        plt.plot(date, price, label='Close Price')
        plt.title(f"{company} ({symbol}) Stock Price")
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
    except Exception as e:
        print(f"Error displaying chart: {e}")