import requests
import time
from tkinter import *
from tkinter import simpledialog
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

global price_history 
global ma5_history
global ma20_history
global ma50_history
global capital
global original_balance
global invested_long
price_history = [] #contains price_history of btc since user opened program/since time interval of updates was changed
ma5_history = [] #contains ma5 of btc since user opened program/since time interval of updates was changed
ma20_history = [] #contains ma20 of btc since user opened program/since time interval of updates was changed
ma50_history = [] #contains ma50 of btc since user opened program/since time interval of updates was changed
original_balance = 1000.0  #original balance doesnt change trade to trade, used to calculate P/L
capital = 1000.0 #balance that changes trade to trade, displayed on top of screen
invested_long = 0.0 #tracks size of long position in btc
open_short_positions = [] #tracks all short position, array of array, [position_id, price_sold, collateral]

#calculates percent change for two prices
def percent_change(entry_price, current_price):
    return ((current_price - entry_price) / entry_price) * 100.0

#Gets live bitcoin price from coinbase
def get_bitcoin_price():
    url = 'https://api.coinbase.com/v2/prices/spot?currency=USD'
    response = requests.get(url)
    data = response.json()
    return float(data['data']['amount'])  # Convert to float to handle numerical operations

#calculates moving average of bitcoin price history based on how often the window updates
def calculate_moving_average(window_size):
    if len(price_history) < window_size:
        return None
    return sum(price_history[-window_size:]) / window_size

#uses get_bitcoin_price to fill price history and MA data
update_time = 5
def fetch_bitcoin_data():
    global ma5_history
    global ma20_history
    global ma50_history
    global update_time
    while True:
        price = get_bitcoin_price()
        price_history.append(price)
    
        # Calculate moving averages
        ma_5 = calculate_moving_average(5)
        ma5_history.append(ma_5)
        ma_20 = calculate_moving_average(20)
        ma20_history.append(ma_20)
        ma_50 = calculate_moving_average(50)
        ma50_history.append(ma_50)

        # Wait for a while before fetching again (simulating real-time behavior)
        time.sleep(update_time)  # Adjust as needed

#indicates trend that supports entry of long position. if the 20MA crosses the 50MA going upwards, it indentifies this to the user
def long_indicator(button):
    if len(price_history) > 50 and float(ma20_history[-2]) >= float(ma50_history[-2]) and float(ma20_history[-1]) <= float(ma50_history[-1]):
       button.config(bg='green')
       print("long indicator green")
    else: button.config(bg='red')

#indicates trend that supports entry of short sale. if the 20MA crosses the 50MA going downwards, it indentifies this to the user
def short_indicator(button):
    if len(price_history) > 50 and float(ma20_history[-2]) <= float(ma50_history[-2]) and float(ma20_history[-1]) >= float(ma50_history[-1]):
        button.config(bg='green')
        print("Short indicator green Green")
    else: button.config(bg='red')

        
#enter and exit long take current price data to accurately measure amount of btc you are getting or inversly how much the btc you are selling is worth
def enter_long(investment_increment):
    global capital
    global invested_long
    print("entered long at " + str(price_history[-1]))
    capital = capital - float(investment_increment.get())
    invested_long = invested_long + (float(investment_increment.get()) / price_history[-1])
    
def exit_long(price_to_exit, amount):
    global capital
    global invested_long
    print("Exiting long position.")
    invested_long = invested_long - amount
    capital = capital + (price_to_exit * amount)
        





#enter short, tracks the price it was sold, the collateral put up, and the function to update the scales.
position_id_count = 0
button_tracker = []
def enter_short(window, position_id, price, collateral, scale_update_function):
    global capital
    global position_id_count
    collateral = float(collateral.get())
    
    # Function to handle closing the short position
    def exit_short(exit_short_button, price_to_exit):
        global capital
        print(f"Closing short {position_id} position at ${price_to_exit}")
        exit_short_button.destroy()
        open_short_positions.remove([position_id, price_sold, collateral])
        capital = capital + collateral + ((price_sold - price_to_exit) *  ((collateral * 2) / price_sold)) 
        scale_update_function()
        
    #run enter short code
    if capital >= collateral:
        position_id_count = position_id_count + 1
        print(f"Entered short {position_id} at {price}")
        price_sold = price
        capital = capital - collateral 
        open_short_positions.append([position_id, price_sold, collateral])
        # Create tkinter exit_short_button that references itself when pressed to destroy itself
        exit_short_button = Button(window, text=f"Close Short {position_id} Position at Price {price}", command=lambda: exit_short(exit_short_button, get_bitcoin_price()), width=30, height=2)
        button_tracker.append(exit_short_button)
        exit_short_button.pack(side=TOP, pady=10)
        scale_update_function()
    else:
        print("not enough capital for trade")
        
#calculates profit/loss by summing balance, value of long, and value of short positions
def profit_loss_calc():
    short_balance = 0
    for short in open_short_positions:
        short_balance+=short[2] + ((short[1] - price_history[-1]) *  ((short[2] * 2) / short[1]))

    percent_dec = (capital + short_balance + (invested_long * price_history[-1]) - original_balance) / original_balance
    return round((percent_dec * 100), 3) 

#updates the scales to desired new values
def update_scale(scale_widget, new_to_value):
    scale_widget.config(to=new_to_value)

#updates graph with new price_history every update
def update_graph(canvas, ax):
    ax.clear()
    ax.plot(price_history, label='Bitcoin Price', color='blue')
    if len(price_history) >= 5:
        ax.plot(ma5_history, label='MA 5', color='orange')
    if len(price_history) >= 20:
        ax.plot(ma20_history, label='MA 20', color='green')
    if len(price_history) >= 50:
        ax.plot(ma50_history, label='MA 50', color='red')
    ax.legend()
    canvas.draw()

#updates price_label, current_price label, update_label, balance_label, P/L Label, short indicator, and long indicator
def update_gui(window, price_label, balance_label, canvas, ax, shortLabel, longLabel, profit_loss_label, update_label):
    if price_history:
        current_price = price_history[-1]  # Get the latest price
        price_label.config(text=f"Current Bitcoin Price: ${current_price:.3f}")
        update_label.config(text=f"Update Time approx {update_time} (Sec)")
        balance_label.config(text=f"Your Simulated Balance: {capital:.3f}")
        profit_loss_label.config(text=f"% Gain    {profit_loss_calc()}%")
        if float(profit_loss_calc()) > 0.0:
            profit_loss_label.config(bg="green")
        elif float(profit_loss_calc()) < 0.0:
            profit_loss_label.config(bg="red")
        else:
            profit_loss_label.config(bg="grey")

    update_graph(canvas, ax)
    short_indicator(shortLabel)
    long_indicator(longLabel)
    # Schedule the next update after 5 seconds
    window.after(5000, update_gui, window, price_label, balance_label, canvas, ax, shortLabel, longLabel, profit_loss_label, update_label)

def main():
    #Create window and its title
    window = Tk()
    window.title("Bitcoin Trading Simulator With Custom MA Signals")
    # Set the window to fullscreen immediately
    window.attributes("-fullscreen", True)
    #Bind escape to exit fullscreen
    def end_fullscreen(event=None):
        window.attributes("-fullscreen", False)
        window.geometry("800x600")
        return "break"
    window.bind("<Escape>", end_fullscreen)


    # Create a label for displaying the Bitcoin price
    menubutton = Menubutton(window, text="options")
    menubutton.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=0)  # Adjust x and y for padding

    # Creates label for profit loss of paper trades compared to original balance
    profit_loss_label = Label(window, text="% Gain  " + "000.0%",  bg='grey')
    profit_loss_label.place(relx=0.09, rely=0.0, anchor='ne', x=0, y=12)

    # creates label in bottom right that displays how often the price updates
    update_label = Label(window, text="Update Time approx 5 (Sec)",  bg='grey')
    update_label.place(relx=1, rely=.98, anchor='se', x= -9, y=11)

    # Create a Menu widget that is used for options
    menu = Menu(menubutton, tearoff=0)
    menubutton.config(menu=menu)

    #create function that works with option button to reset trades and overall balance
    def new_balance_option():
        global original_balance
        global capital
        global invested_long
        # Prompt the user for input
        user_input = simpledialog.askstring("Input", "Please enter a value for your new balance:")
        if user_input is not None:  # If the user didn't cancel the dialog
            original_balance = float(user_input)
            capital = float(user_input)
            for button in button_tracker:
                button.destroy()
            open_short_positions.clear()
            invested_long = 0 
            update_all_scales()
            print(f"User input: {user_input}")
        else:
            print("User canceled the input dialog.")

    #Function that is used in option menu to chang e how often the price updates, works with update_label shown above
    def new_price_update_option():
        #global variable imports
        global update_time
        global price_history
        global ma5_history
        global ma20_history
        global ma50_history
        # Prompt the user for input
        user_input = simpledialog.askstring("Input", "Please enter a value for how often you want the graph and MA to update (Seconds)")
        if user_input is not None:  # If the user didn't cancel the dialog
            update_time = int(user_input)
            #resets all price histories so graph doesnt break etc.
            price_history = []
            ma5_history = []
            ma20_history = []
            ma50_history = []
            print(f"User input: {user_input}")
        else:
            print("User canceled the input dialog.")

    #adding above functions to menu
    menu.add_command(label="Input New Balance", command=new_balance_option)
    menu.add_command(label="Change Price Update Interval", command=new_price_update_option)
    
    #displays bitcoin price at top of UI, updates with respect to update_label
    price_label = Label(window, text="Current Bitcoin Price: $....")
    price_label.pack(pady=10)

    #displays users paper trading balance at top of screen, should not go below 0
    balance_label = Label(window, text=f"Your Simulated Balance: {capital:.3f}")
    balance_label.pack(pady=10)

    #initiliazing graph
    fig, ax = plt.subplots(figsize=(4, 2))  # Set the size of the graph here
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().pack_forget()
    # Set smaller font size for axis labels
    ax.tick_params(axis='x', labelsize=4)  # Adjust font size for x-axis ticks
    ax.tick_params(axis='y', labelsize=4)  # Adjust font size for y-axis ticks

    #function that is called by show graph button, shows graph and unhides hide graph button
    def show_graph():
        graph_button.pack_forget()
        hide_graph_button.pack(side=BOTTOM)
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

    #function that is called by hide graph button, hides graph and unhides show graph button  
    def hide_graph():
        hide_graph_button.pack_forget()
        canvas.get_tk_widget().pack_forget()
        graph_button.pack(side=BOTTOM)

    #buttons that control viewing of graph
    graph_button = Button(window, text="Show Graph",command=show_graph, width=7, height=2)
    graph_button.pack(side=BOTTOM, pady=10)
    hide_graph_button = Button(window, text ="Hide Graph", command=hide_graph, width=7, height=2)
    hide_graph_button.pack_forget()

    #function that condenses all update_scale calls, update_scale updates the sliders used to measure size of trades
    def update_all_scales():
        update_scale(sell_long_scale_button, invested_long)
        update_scale(buy_long_scale_button, capital)
        update_scale(collateral_scale_button, capital)
        
    #function used to encapsulate enter_short function for use inside the create short button
    def create_short_position():
        current_price = get_bitcoin_price()
        enter_short(window, position_id_count, current_price,  short_investment_increment, update_all_scales)
        update_gui(window, price_label, balance_label, canvas, ax, short_indicator_label, long_indicator_label, profit_loss_label, update_label)
    
    #function used to encapsulate enter_long function for use inside the create long button
    long_investment_increment = DoubleVar()
    def create_long_position():
        enter_long(long_investment_increment)
        update_all_scales()
        update_gui(window, price_label, balance_label, canvas, ax, short_indicator_label, long_indicator_label, profit_loss_label, update_label)

    #function that interacts with long slider to see how much of the long to sell   
    long_amount_to_sell = DoubleVar()
    def create_exit_long():
        global invested_long
        exit_long(get_bitcoin_price(), float(long_amount_to_sell.get()))
        update_all_scales()


    #Indicator frame to hold indicator labels
    indicator_frame = Frame(window)
    indicator_frame.pack(pady=20)
    short_indicator_label = Label(indicator_frame,text="MA Short Indicator", bg='red', relief=SUNKEN)
    short_indicator_label.pack(side=LEFT, padx=10)
    long_indicator_label = Label(indicator_frame, text= "MA Long Indicator", bg = "red", relief=SUNKEN)
    long_indicator_label.pack(side=LEFT, padx=10)


    # Create a frame to hold the long buttons
    long_button_frame = Frame(window)
    long_button_frame.pack(pady=20)

    buy_long_button = Button(long_button_frame, text="Buy", command=create_long_position, width=2, height=2)
    buy_long_button.pack(side=LEFT, padx=5)

    buy_long_scale_button = Scale(long_button_frame, label="Long Amount", from_=0, to=capital, resolution=0.1, orient=HORIZONTAL, variable=long_investment_increment)
    buy_long_scale_button.pack(side=LEFT, padx=5)

    sell_long_button = Button(long_button_frame, text="sell", command= create_exit_long, width=2, height=2)
    sell_long_button.pack(side=LEFT, padx=5) 

    sell_long_scale_button = Scale(long_button_frame, label="Long Amount", from_=0.0, to=invested_long, resolution=0.00000001, orient=HORIZONTAL, variable=long_amount_to_sell)
    sell_long_scale_button.pack(side=LEFT, padx=5)


    #Create a frame to hold the short buttons
    short_investment_increment = DoubleVar()
    short_button_frame = Frame(window)
    short_button_frame.pack(pady=20)
    addShort_button = Button(short_button_frame, text=f"Add Short Position At Current Price", command=create_short_position, width=22, height=2)
    addShort_button.pack(side=LEFT, pady=10)
    collateral_scale_button = Scale(short_button_frame,label= "50% Collateral", resolution=0.1, from_=0.0, to=capital, orient=HORIZONTAL, variable=short_investment_increment)
    collateral_scale_button.pack(side=LEFT, padx=5)

    
    # Start the thread for fetching Bitcoin data
    fetch_thread = threading.Thread(target=fetch_bitcoin_data)
    fetch_thread.daemon = True  # Daemonize the thread so it will be terminated when the main program exits
    fetch_thread.start()
    
    # Start updating the GUI
    update_gui(window, price_label, balance_label, canvas, ax, short_indicator_label, long_indicator_label, profit_loss_label, update_label)

    # Run the Tkinter main loop
    window.mainloop()



if __name__ == "__main__":
    main()

