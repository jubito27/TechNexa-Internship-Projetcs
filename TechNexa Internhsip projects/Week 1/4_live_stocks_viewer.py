import requests
import json
from tkinter import *
import pandas as pd
import matplotlib.pyplot as plt


ALPHA_VINTAGE_API_KEY = "1FT8S5UBK5RFK6YN"
url = 'https://www.alphavantage.co/query'


def extract_keys(json_object):
    
    if isinstance(json_object, dict):
        return list(json_object.keys()) # Convert the view object to a list

    else:
        print("Error: Input is not a dictionary.")
        return None
    
def extract_values(json_object):

    if isinstance(json_object , dict):
        return list(json_object.values())
    
    else:
        print("Error: Input is not a dictionary.")
        return None
    


def latest_daily_close(symbol):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": ALPHA_VINTAGE_API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        data = r.json()
        with open("stocks.json" , "a" , encoding="utf-8") as f:
            json.dump(data , f)
            f.write("\n-" *50 ,"\n")

    except TimeoutError as e:
        print("error" , e)
    except Exception as e:
        print("another error" , e)
    

def show_stocks():
    with open("stocks.json" , "r" , encoding='utf-8') as f:
        data = json.load(f)
        encode = json.dumps(data["Time Series (Daily)"], sort_keys=True , indent=4)
        dict_load = json.loads(encode)
        final = extract_keys(dict_load)
        print(f"date         |   prices")
        date_list = []
        price_list = []
        for i in range(len(final)):
            date = final[i]
            price = json.dumps(data["Time Series (Daily)"][date]['4. close'], sort_keys=True , indent=4)
            print(f"{date}   |   {price}")
            date_list.append(date)
            price_list.append(price)
        print(price_list , date_list)
        return date_list , price_list
    
def plot_stocks():
    x_axis , y_axis = show_stocks()
    plt.plot(x_axis , y_axis )
    plt.ylabel("Stocks Price")
    plt.xlabel("Date")
    plt.show()

def download_csv():
    with open("stocks.json" , "r" , encoding='utf-8') as f:
        data = json.load(f)
        encode = json.dumps(data["Time Series (Daily)"], sort_keys=True , indent=4)
        dict_load = json.loads(encode)
        final = extract_keys(dict_load)
        date_list = []
        open_list = []
        low_list = []
        high_list = []
        close_list = []
        volume_list = []
        for i in range(len(final)):
            date = final[i]
            
            open_ =  json.dumps(data["Time Series (Daily)"][date]['1. open'], sort_keys=True , indent=4)
            high  = json.dumps(data["Time Series (Daily)"][date]['2. high'], sort_keys=True , indent=4)
            low  = json.dumps(data["Time Series (Daily)"][date]['3. low'], sort_keys=True , indent=4)
            close = json.dumps(data["Time Series (Daily)"][date]['4. close'], sort_keys=True , indent=4)
            volume = json.dumps(data["Time Series (Daily)"][date]['5. volume'], sort_keys=True , indent=4)
            date_list.append(date)
            open_list.append(open_)
            low_list.append(low)
            high_list.append(high)
            close_list.append(close)
            volume_list.append(volume)

        csv_data = {
            'TimeStamp' : date_list,
            'open' : open_list,
            'high' : high_list,
            'low' : low_list,            
            'close' : close_list,
            'volume' : volume_list
        }
        db = pd.DataFrame(csv_data)
        print(db)
        db.to_csv("IBM_STOCKS.csv" , index=False )

def main():
    root = Tk()
    root.title("IBM Stocks Overview")
    root.geometry("400x300")
    Label(root , text="Welcome to Daily IBM Stocks Merchandize" , font="Serif 20 bold").place(x=20 , y = 100)
    plotButton = Button(root , text= 'Plot Graph' , command=plot_stocks)
    plotButton.place(x=150 , y=150 , width=60 , height=30)

    downloadcsvButton = Button(root , text="Downlaod CSV" , command=download_csv)
    downloadcsvButton.place(x=150 , y=180 , width=60 , height=30)

    root.mainloop()


if __name__=="__main__":
    latest_daily_close("IBM")
    main()




# class StockTracker:
#     def __init__(self):datda
#         self.watched_stocks = {}
#         self.price_history = {}
#         self.alerts = []
#         self.root = Tk()
#         self.root.title("Stocks Viewer")
#         self.root.geometry("800x600")

#     def setup_gui(self):

        
#     def fetch_stock_data(self, symbol):
#         ALPHA_VINTAGE_API_KEY = "1FT8S5UBK5RFK6YN"
#         urls = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&apikey=1FT8S5UBK5RFK6YN&datatype=csv']            

       
        
#     def monitor_prices(self):
#         # Real-time monitoring with threading
#         pass
        
#     def check_alerts(self, symbol, current_price):
#         # Alert system logic
#         pass
        
#     def visualize_trends(self):
#         # Matplotlib integration
#         pass
        
#     def export_data(self):
#         # CSV/JSON export functionality
#         pass
