import requests
import time
from tkinter import *
from tkinter import simpledialog
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

########
    # Done
    #1: organize code
    #2: stop over spending
    #3: long buttons
    #2 choose collateral for shorts
    #4implement MA signaler

    # To Do
    #3 implement p/l % counter
    #5 implement settings
    #######

global price_history 
global ma5_history
global ma20_history
global ma50_history
price_history = []
ma5_history = []
ma20_history = []
ma50_history = []

global capital
global original_balance
original_balance = 100.0
capital = 100.0
short_investment_increment = 100.0
global invested_long
invested_long = 0.0
open_short_positions = []
stop_loss_button_pressed = False

def percent_change(entry_price, current_price):
    return ((current_price - entry_price) / entry_price) * 100.0


def get_bitcoin_price():
    url = 'https://api.coinbase.com/v2/prices/spot?currency=USD'
    response = requests.get(url)
    data = response.json()
    return float(data['data']['amount'])  # Convert to float to handle numerical operations


def calculate_moving_average(window_size):
    if len(price_history) < window_size:
        return None
    return sum(price_history[-window_size:]) / window_size

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


def long_indicator(button):
    if len(price_history) > 50 and float(ma20_history[-2]) <= float(ma50_history[-2]) and float(ma20_history[-1]) >= float(ma50_history[-1]):
       button.config(bg='green')
       print("long indicator green")
    else: button.config(bg='red')

def short_indicator(button):
    if len(price_history) > 50 and float(ma20_history[-2]) >= float(ma50_history[-2]) and float(ma20_history[-1]) <= float(ma50_history[-1]):
        button.config(bg='green')
        print("Short indicator green Green")
    else: button.config(bg='red')

        
       
def enter_long(investment_increment, stop_loss_button_pressed):
    global capital
    global invested_long
    print("entered long at " + str(price_history[-1]))
    capital = capital - float(investment_increment.get())
    invested_long = invested_long + (float(investment_increment.get()) / price_history[-1])
    if stop_loss_button_pressed:   
        trailing_stop_loss_for_long()
    

def exit_long(price_to_exit, amount):
    global capital
    global invested_long
    print("Exiting long position.")
    invested_long = invested_long - amount
    capital = capital + (price_to_exit * amount)
    print(invested_long)
        


def trailing_stop_loss_for_long(entry_price, percent_tolerance):
    price_history
    
    current_price = price_history[-1]

    #calculate max change in price from peak for stop loss
    tolerance = entry_price * percent_tolerance

    # Track the lowest price since entering the position
    max_price = max(price_history[price_history.index(entry_price):])

    # Calculate trailing stop loss level
    trailing_stop = max_price + tolerance

    # Check if current price has crossed the trailing stop loss level
    if current_price <= trailing_stop:
        exit_long()
    else:
        print(f"Current price: {current_price}, Trailing stop loss: {trailing_stop}")




    
position_id_count = 0
button_tracker = []
def enter_short(window, position_id, price, stop_loss_button_pressed, collateral, scale_update_function):
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
        print(capital)
        
    
    
    

    def trailing_stop_loss_for_short(entry_price, percent_tolerance):
        price_history
        
        current_price = price_history[-1]

        #calculate max change in price from peak for stop loss
        tolerance = entry_price * percent_tolerance

        # Track the lowest price since entering the position
        lowest_price = min(price_history[price_history.index(entry_price):])

        # Calculate trailing stop loss level
        trailing_stop = lowest_price + tolerance

        # Check if current price has crossed the trailing stop loss level
        if current_price >= trailing_stop:
            exit_short(button_tracker[position_id_count] , trailing_stop)
        else:
            print(f"Current price: {current_price}, Trailing stop loss: {trailing_stop}")

    #run enter short code
    if capital >= collateral:
        position_id_count = position_id_count + 1
        print(f"Entered short {position_id} at {price}")
        price_sold = price
        capital = capital - collateral 
        open_short_positions.append([position_id, price_sold, collateral])
        # Create tkinter exit_short_button that references itself when pressed to destroy itself
        exit_short_button = Button(window, text=f"Close Short {position_id} Position at Price {price}", command=lambda: exit_short(exit_short_button, get_bitcoin_price()))
        button_tracker.append(exit_short_button)
        exit_short_button.pack(side=TOP, pady=10)
        scale_update_function()
    else:
        print("not enough capital for trade")
        
    
    if stop_loss_button_pressed:
        trailing_stop_loss_for_short()  # Assuming this function handles trailing stop loss


def profit_loss_calc():
    short_balance = 0
    
    for short in open_short_positions:
        short_balance+=short[2] + ((short[1] - price_history[-1]) *  ((short[2] * 2) / short[1]))

    percent_dec = (capital + short_balance + (invested_long * price_history[-1]) - original_balance) / original_balance
    return str(round((percent_dec * 100), 3)) + "%"

def update_scale(scale_widget, new_to_value):
    scale_widget.config(to=new_to_value)


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

def update_gui(window, price_label, balance_label, canvas, ax, shortLabel, longLabel, profit_loss_label):
    if price_history:
        current_price = price_history[-1]  # Get the latest price
        price_label.config(text=f"Current Bitcoin Price: ${current_price:.3f}")
        balance_label.config(text=f"Your Simulated Balance: {capital:.3f}")
        profit_loss_label.config(text=f"% Gain    {profit_loss_calc()}")
    update_graph(canvas, ax)
    short_indicator(shortLabel)
    long_indicator(longLabel)
    # Schedule the next update after 5 seconds
    window.after(5000, update_gui, window, price_label, balance_label, canvas, ax, shortLabel, longLabel, profit_loss_label)

def main():
    #Create window and its geometry
    window = Tk()
    window.title("Bitcoin Trading Simulator With Custom MA Signals")
    window.geometry('1800x1200')


    # Create a label for displaying the Bitcoin price
    menubutton = Menubutton(window, text="options")
    menubutton.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=0)  # Adjust x and y for padding

    # P/L label creation
    profit_loss_label = Label(window, text="% Gain  " + "000.0%",  bg='red')
    profit_loss_label.place(relx=0.08, rely=0.0, anchor='ne', x=0, y=12)


    # Create a Menu widget
    menu = Menu(menubutton, tearoff=0)
    menubutton.config(menu=menu)


    def new_balance_option():
        global original_balance
        global capital
        # Prompt the user for input
        user_input = simpledialog.askstring("Input", "Please enter a value for your new balance:")
        if user_input is not None:  # If the user didn't cancel the dialog
            original_balance = float(user_input)
            capital = float(user_input)
            update_all_scales()
            print(f"User input: {user_input}")
        else:
            print("User canceled the input dialog.")

    def new_price_update_option():
        global update_time
        global price_history
        global ma5_history
        global ma20_history
        global ma50_history
        # Prompt the user for input
        user_input = simpledialog.askstring("Input", "Please enter a value for how often you want the graph and MA to update (Seconds)")
        if user_input is not None:  # If the user didn't cancel the dialog
            update_time = int(user_input)
            price_history = []
            ma5_history = []
            ma20_history = []
            ma50_history = []
            print(f"User input: {user_input}")
        else:
            print("User canceled the input dialog.")


    menu.add_command(label="Input New Balance", command=new_balance_option)
    menu.add_command(label="Change Price Update Interval", command=new_price_update_option)
    
    price_label = Label(window, text="Current Bitcoin Price: $....")
    price_label.pack(pady=10)

    balance_label = Label(window, text=f"Your Simulated Balance: {capital:.3f}")
    balance_label.pack(pady=10)

    
    fig, ax = plt.subplots(figsize=(4, 2))  # Set the size of the graph here
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.get_tk_widget().pack_forget()
    # Set smaller font size for axis labels
    ax.tick_params(axis='x', labelsize=4)  # Adjust font size for x-axis ticks
    ax.tick_params(axis='y', labelsize=4)  # Adjust font size for y-axis ticks


    def show_graph():
        graph_button.pack_forget()
        hide_graph_button.pack(side=BOTTOM)
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        
    def hide_graph():
        hide_graph_button.pack_forget()
        canvas.get_tk_widget().pack_forget()
        graph_button.pack(side=BOTTOM)

    graph_button = Button(window, text="Show Graph",command=show_graph)
    graph_button.pack(side=BOTTOM, pady=10)
    hide_graph_button = Button(window, text ="Hide Graph", command=hide_graph)
    hide_graph_button.pack_forget()

    def update_all_scales():
        update_scale(sell_long_scale_button, invested_long)
        update_scale(buy_long_scale_button, capital)
        update_scale(collateral_scale_button, capital)
   
    def create_short_position():
        current_price = get_bitcoin_price()
        enter_short(window, position_id_count, current_price, stop_loss_button_pressed, short_investment_increment, update_all_scales)
        update_gui(window, price_label, balance_label, canvas, ax, short_indicator_label, long_indicator_label, profit_loss_label)
    
    long_investment_increment = DoubleVar()
    def create_long_position():
        print(invested_long)
        enter_long(long_investment_increment, stop_loss_button_pressed)
        update_all_scales()
        update_gui(window, price_label, balance_label, canvas, ax, short_indicator_label, long_indicator_label, profit_loss_label)
        
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

    buy_long_button = Button(long_button_frame, text="Buy", command=create_long_position)
    buy_long_button.pack(side=LEFT, padx=5)

    buy_long_scale_button = Scale(long_button_frame, label="Long Amount", from_=0, to=capital, resolution=0.1, orient=HORIZONTAL, variable=long_investment_increment)
    buy_long_scale_button.pack(side=LEFT, padx=5)

    sell_long_button = Button(long_button_frame, text="sell", command= create_exit_long)
    sell_long_button.pack(side=LEFT, padx=5) 

    sell_long_scale_button = Scale(long_button_frame, label="Long Amount", from_=0.0, to=invested_long, resolution=0.00000001, orient=HORIZONTAL, variable=long_amount_to_sell)
    sell_long_scale_button.pack(side=LEFT, padx=5)


    #Create a frame to hold the short buttons
    short_investment_increment = DoubleVar()
    short_button_frame = Frame(window)
    short_button_frame.pack(pady=20)
    addShort_button = Button(short_button_frame, text=f"Add Short Position At Current Price", command=create_short_position)
    addShort_button.pack(side=LEFT, pady=10)
    collateral_scale_button = Scale(short_button_frame,label= "50% Collateral", resolution=0.1, from_=0.0, to=capital, orient=HORIZONTAL, variable=short_investment_increment)
    collateral_scale_button.pack(side=LEFT, padx=5)


    



    
    # Start the thread for fetching Bitcoin data
    fetch_thread = threading.Thread(target=fetch_bitcoin_data)
    fetch_thread.daemon = True  # Daemonize the thread so it will be terminated when the main program exits
    fetch_thread.start()
    
    # Start updating the GUI
    update_gui(window, price_label, balance_label, canvas, ax, short_indicator_label, long_indicator_label, profit_loss_label)

    # Run the Tkinter main loop
    window.mainloop()



if __name__ == "__main__":
    main()

