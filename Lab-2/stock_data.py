# Summary: This module contains the functions used by both console and GUI programs to manage stock data.

import sqlite3
from selenium import webdriver
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
from utilities import clear_screen, sortDailyData
from stock_class import Stock, DailyData

# Create the SQLite database
def create_database():
    stockDB = "stocks.db"
    conn = sqlite3.connect(stockDB)
    cur = conn.cursor()
    createStockTableCmd = """CREATE TABLE IF NOT EXISTS stocks (
                            symbol TEXT NOT NULL PRIMARY KEY,
                            name TEXT,
                            shares REAL
                        );"""
    createDailyDataTableCmd = """CREATE TABLE IF NOT EXISTS dailyData (
                                symbol TEXT NOT NULL,
                                date TEXT NOT NULL,
                                price REAL NOT NULL,
                                volume REAL NOT NULL,
                                PRIMARY KEY (symbol, date)
                        );"""   
    cur.execute(createStockTableCmd)
    cur.execute(createDailyDataTableCmd)

# Save stocks and daily data into database
def save_stock_data(stock_list):
    stockDB = "stocks.db"
    conn = sqlite3.connect(stockDB)
    cur = conn.cursor()
    insertStockCmd = """INSERT INTO stocks
                            (symbol, name, shares)
                            VALUES
                            (?, ?, ?); """
    insertDailyDataCmd = """INSERT INTO dailyData
                                    (symbol, date, price, volume)
                                    VALUES
                                    (?, ?, ?, ?);"""
    for stock in stock_list:
        insertValues = (stock.symbol, stock.name, stock.shares)
        try:
            cur.execute(insertStockCmd, insertValues)
            cur.execute("COMMIT;")
        except:
            pass
        for daily_data in stock.DataList: 
            insertValues = (stock.symbol,daily_data.date.strftime("%m/%d/%y"),daily_data.close,daily_data.volume)
            try:
                cur.execute(insertDailyDataCmd, insertValues)
                cur.execute("COMMIT;")
            except:
                pass
    
# Load stocks and daily data from database
def load_stock_data(stock_list):
    stock_list.clear()
    stockDB = "stocks.db"
    conn = sqlite3.connect(stockDB)
    stockCur = conn.cursor()
    stockSelectCmd = """SELECT symbol, name, shares
                    FROM stocks; """
    stockCur.execute(stockSelectCmd)
    stockRows = stockCur.fetchall()
    for row in stockRows:
        new_stock = Stock(row[0],row[1],row[2])
        dailyDataCur = conn.cursor()
        dailyDataCmd = """SELECT date, price, volume
                        FROM dailyData
                        WHERE symbol=?; """
        selectValue = (new_stock.symbol)
        dailyDataCur.execute(dailyDataCmd,(selectValue,))
        dailyDataRows = dailyDataCur.fetchall()
        for dailyRow in dailyDataRows:
            daily_data = DailyData(datetime.strptime(dailyRow[0],"%m/%d/%y"),float(dailyRow[1]),float(dailyRow[2]))
            new_stock.add_data(daily_data)
        stock_list.append(new_stock)
    sortDailyData(stock_list)

# Get stock price history from web using Web Scraping
def retrieve_stock_web(dateStart, dateEnd, stock_list):
    # Convert dates to Unix timestamp for Yahoo Finance
    try:
        dateFrom = str(int(time.mktime(time.strptime(dateStart, "%m/%d/%y"))))
        dateTo = str(int(time.mktime(time.strptime(dateEnd, "%m/%d/%y"))))
    except ValueError:
        print("Invalid Date Format. Please use m/d/yy")
        return 0

    recordCount = 0

    for stock in stock_list:
        stockSymbol = stock.symbol
        # URL construction
        url = "https://finance.yahoo.com/quote/" + stockSymbol + "/history?period1=" + dateFrom + "&period2=" + dateTo + "&interval=1d&filter=history&frequency=1d"
        
        # Setup Chrome options
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.implicitly_wait(60)
            driver.get(url)
        except:
            raise RuntimeWarning("Chrome Driver Not Found")

        # Parse Page
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        # Find data rows
        dataRows = soup.find_all('tr')
        
        for row in dataRows:
            td = row.find_all('td')
            rowList = [i.text for i in td]
            columnCount = len(rowList)
            
            # Standard data row has 7 columns (Date, Open, High, Low, Close, Adj Close, Volume)
            if columnCount == 7: 
                try:
                    # Parse Data: Date[0], Close[5], Volume[6]
                    date_obj = datetime.strptime(rowList[0], "%b %d, %Y")
                    close_price = float(rowList[5].replace(',', ''))
                    volume = float(rowList[6].replace(',', ''))
                    
                    daily_data = DailyData(date_obj, close_price, volume)
                    stock.add_data(daily_data)
                    recordCount += 1
                except ValueError:
                    continue 

    return recordCount

# Get price and volume history from Yahoo! Finance using CSV import.
def import_stock_web_csv(stock_list, symbol, filename):
    for stock in stock_list:
        if stock.symbol == symbol:
            try:
                with open(filename, newline='') as stockdata:
                    datareader = csv.reader(stockdata, delimiter=',')
                    next(datareader) # Skip header
                    for row in datareader:
                        # CSV: Date[0], Close[4], Volume[6]
                        try:
                            date_obj = datetime.strptime(row[0], "%Y-%m-%d")
                            close_price = float(row[4])
                            volume = float(row[6])
                            daily_data = DailyData(date_obj, close_price, volume)
                            stock.add_data(daily_data)
                        except (ValueError, IndexError):
                            continue
            except Exception as e:
                print(f"Error reading CSV: {e}")

def main():
    clear_screen()
    print("This module will handle data storage and retrieval.")

if __name__ == "__main__":
    main()