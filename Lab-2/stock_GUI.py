# Summary: This module contains the user interface and logic for a graphical user interface version of the stock manager program.

from datetime import datetime
from os import path
from tkinter import *
from tkinter import ttk
from tkinter import messagebox, simpledialog, filedialog
import csv
import stock_data
from stock_class import Stock, DailyData
from utilities import clear_screen, display_stock_chart, sortStocks, sortDailyData

class StockApp:
    def __init__(self):
        self.stock_list = []
        #check for database, create if not exists
        if path.exists("stocks.db") == False:
            stock_data.create_database()

        # This section creates the user interface

        # Create Window
        self.root = Tk()
        self.root.title("(myname) Stock Manager") 

        # Add Menubar
        self.menubar = Menu(self.root)

        # Add File Menu
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label="Load Data", command=self.load)
        self.filemenu.add_command(label="Save Data", command=self.save)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        # Add Web Menu 
        self.webmenu = Menu(self.menubar, tearoff=0)
        self.webmenu.add_command(label="Scrape Data from Yahoo! Finance...", command=self.scrape_web_data)
        self.webmenu.add_command(label="Import CSV from Yahoo! Finance...", command=self.importCSV_web_data)
        self.menubar.add_cascade(label="Web", menu=self.webmenu)

        # Add Chart Menu
        self.chartmenu = Menu(self.menubar, tearoff=0)
        self.chartmenu.add_command(label="Display Stock Chart", command=self.display_chart)
        self.menubar.add_cascade(label="Chart", menu=self.chartmenu)

        # Add menus to window       
        self.root.config(menu=self.menubar)

        # Add heading information
        self.headingLabel = Label(self.root, text="No Stock Selected")
        self.headingLabel.grid(column=0, row=0, columnspan=3)

        # Add stock list
        self.stockList = Listbox(self.root)
        self.stockList.grid(column=0, row=1, padx=5, pady=5, rowspan=2)
        self.stockList.bind('<<ListboxSelect>>', self.update_data)
        
        # Add Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(column=1, row=1, padx=5, pady=5)
        
        self.mainTab = ttk.Frame(self.notebook)
        self.historyTab = ttk.Frame(self.notebook)
        self.reportTab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.mainTab, text="Manage")
        self.notebook.add(self.historyTab, text="History")
        self.notebook.add(self.reportTab, text="Report")

        # Set Up Main Tab
        self.addSymbolLabel = Label(self.mainTab, text="Symbol")
        self.addSymbolLabel.grid(column=0, row=0)
        self.addSymbolEntry = Entry(self.mainTab)
        self.addSymbolEntry.grid(column=1, row=0)
        
        self.addNameLabel = Label(self.mainTab, text="Name")
        self.addNameLabel.grid(column=0, row=1)
        self.addNameEntry = Entry(self.mainTab)
        self.addNameEntry.grid(column=1, row=1)
        
        self.addSharesLabel = Label(self.mainTab, text="Shares")
        self.addSharesLabel.grid(column=0, row=2)
        self.addSharesEntry = Entry(self.mainTab)
        self.addSharesEntry.grid(column=1, row=2)
        
        self.addStockButton = Button(self.mainTab, text="Add Stock", command=self.add_stock)
        self.addStockButton.grid(column=0, row=3, columnspan=2)
        
        self.deleteStockButton = Button(self.mainTab, text="Delete Stock", command=self.delete_stock)
        self.deleteStockButton.grid(column=0, row=4, columnspan=2)
        
        self.updateSharesLabel = Label(self.mainTab, text="Update Shares")
        self.updateSharesLabel.grid(column=0, row=5)
        self.updateSharesEntry = Entry(self.mainTab)
        self.updateSharesEntry.grid(column=1, row=5)
        
        self.buyButton = Button(self.mainTab, text="Buy", command=self.buy_shares)
        self.buyButton.grid(column=0, row=6)
        
        self.sellButton = Button(self.mainTab, text="Sell", command=self.sell_shares)
        self.sellButton.grid(column=1, row=6)

        # Setup History Tab
        self.dailyDataList = Text(self.historyTab, width=40, height=15)
        self.dailyDataList.grid(column=0, row=0)
        
        # Setup Report Tab
        self.stockReport = Text(self.reportTab, width=40, height=15)
        self.stockReport.grid(column=0, row=0)

        ## Call MainLoop
        self.root.mainloop()

# This section provides the functionality
       
    # Load stocks and history from database.
    def load(self):
        self.stockList.delete(0,END)
        stock_data.load_stock_data(self.stock_list)
        sortStocks(self.stock_list)
        for stock in self.stock_list:
            self.stockList.insert(END,stock.symbol)
        messagebox.showinfo("Load Data","Data Loaded")

    # Save stocks and history to database.
    def save(self):
        stock_data.save_stock_data(self.stock_list)
        messagebox.showinfo("Save Data","Data Saved")

    # Refresh history and report tabs
    def update_data(self, evt):
        self.display_stock_data()

    # Display stock price and volume history.
    def display_stock_data(self):
        try:
            symbol = self.stockList.get(self.stockList.curselection())
            for stock in self.stock_list:
                if stock.symbol == symbol:
                    self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
                    self.dailyDataList.delete("1.0",END)
                    self.stockReport.delete("1.0",END)
                    self.dailyDataList.insert(END,"- Date -   - Price -   - Volume -\n")
                    self.dailyDataList.insert(END,"=================================\n")
                    for daily_data in stock.DataList:
                        row = daily_data.date.strftime("%m/%d/%y") + "   " +  '${:0,.2f}'.format(daily_data.close) + "   " + str(daily_data.volume) + "\n"
                        self.dailyDataList.insert(END,row)
        except TclError:
            pass # No selection

    
    # Add new stock to track.
    def add_stock(self):
        try:
            new_stock = Stock(self.addSymbolEntry.get(),self.addNameEntry.get(),float(str(self.addSharesEntry.get())))
            self.stock_list.append(new_stock)
            self.stockList.insert(END,self.addSymbolEntry.get())
            self.addSymbolEntry.delete(0,END)
            self.addNameEntry.delete(0,END)
            self.addSharesEntry.delete(0,END)
        except ValueError:
             messagebox.showerror("Error", "Invalid shares or missing data")

    # Buy shares of stock.
    def buy_shares(self):
        try:
            symbol = self.stockList.get(self.stockList.curselection())
            for stock in self.stock_list:
                if stock.symbol == symbol:
                    stock.buy(float(self.updateSharesEntry.get()))
                    self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
            messagebox.showinfo("Buy Shares","Shares Purchased")
            self.updateSharesEntry.delete(0,END)
        except:
             messagebox.showerror("Error", "Select a stock and enter valid shares")

    # Sell shares of stock.
    def sell_shares(self):
        try:
            symbol = self.stockList.get(self.stockList.curselection())
            for stock in self.stock_list:
                if stock.symbol == symbol:
                    stock.sell(float(self.updateSharesEntry.get()))
                    self.headingLabel['text'] = stock.name + " - " + str(stock.shares) + " Shares"
            messagebox.showinfo("Sell Shares","Shares Sold")
            self.updateSharesEntry.delete(0,END)
        except:
            messagebox.showerror("Error", "Select a stock and enter valid shares")

    # Remove stock and all history from being tracked.
    def delete_stock(self):
        try:
            symbol = self.stockList.get(self.stockList.curselection())
            idx = self.stockList.curselection()[0]
            for i, stock in enumerate(self.stock_list):
                if stock.symbol == symbol:
                    del self.stock_list[i]
            self.stockList.delete(idx)
            messagebox.showinfo("Deleted", "Stock Deleted")
        except:
             messagebox.showerror("Error", "Select a stock to delete")

    # [cite_start]Get data from web scraping. [cite: 188-202]
    def scrape_web_data(self):
        dateFrom = simpledialog.askstring("Starting Date", "Enter Starting Date (m/d/yy)")
        dateTo = simpledialog.askstring("Ending Date", "Enter Ending Date (m/d/yy)")
        
        if not dateFrom or not dateTo:
            return 
            
        try:
            stock_data.retrieve_stock_web(dateFrom, dateTo, self.stock_list)
            self.display_stock_data()
            messagebox.showinfo("Get Data From Web", "Data Retrieved")
        except Exception as e:
            messagebox.showerror("Cannot Get Data from Web", f"Check Path for Chrome Driver. Error: {e}")

    # [cite_start]Import CSV stock history file. [cite: 258-272]
    def importCSV_web_data(self):
        try:
            symbol = self.stockList.get(self.stockList.curselection())
        except:
            messagebox.showwarning("Selection Error", "Please select a stock first.")
            return

        filename = filedialog.askopenfilename(
            title="Select " + symbol + " File to Import",
            filetypes=[('Yahoo Finance! CSV', '*.csv')]
        )
        
        if filename != "":
            try:
                stock_data.import_stock_web_csv(self.stock_list, symbol, filename)
                self.display_stock_data()
                messagebox.showinfo("Import Complete", symbol + " Import Complete")
            except Exception as e:
                messagebox.showerror("Import Failed", str(e))
    
    # Display stock price chart.
    def display_chart(self):
        try:
            symbol = self.stockList.get(self.stockList.curselection())
            display_stock_chart(self.stock_list,symbol)
        except:
            messagebox.showwarning("Chart", "Select a stock first")


def main():
        app = StockApp()
        

if __name__ == "__main__":
    # execute only if run as a script
    main()