from tkinter import *
from itertools import count
from tkinter import ttk
import sqlite3
from tkinter import messagebox 
import matplotlib.pyplot as plt
from tkcalendar import *
import tkinter.font as font
from matplotlib import dates as mpl_dates
from datetime import *
import pandas as pd
from tkinter import filedialog


app = Tk()
app.title("Winelist")
app.state('zoomed') 

conn = sqlite3.connect('winelist.db')
c = conn.cursor()

c.execute("""CREATE TABLE if not exists wines (
name text,
type text,
id integer,
price integer,
quantity integer)
""")

c.execute("""CREATE TABLE if not exists sales (
quantity integer,
date blob,
name text
)
""")

conn.commit()
conn.close()

def query_database():
    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM wines")
    records = c.fetchall()
    global count
    count = 0

    for record in records:   
        if count % 2 ==0:
            my_tree.insert(parent='', index='end', iid=count, text='', values=(record[0], record[1], record[2], record[4], record[5]), tags=('evenrow',))
        else:
            my_tree.insert(parent='', index='end', iid=count, text='', values=(record[0], record[1], record[2], record[4], record[5]), tags=('oddrow',))
            
        count +=1

    conn.commit()
    conn.close()

def clear_entries():
    name_entry.delete(0, END)
    type_entry.delete(0, END)
    id_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)

def remove_one():
    MsgBox = messagebox.askquestion ('Delete Wine','Are you sure you want to delete this wine?',icon = 'warning')
    if MsgBox == 'yes':
        x = my_tree.selection()[0]
        my_tree.delete(x)
        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute("DELETE from wines WHERE oid=" + id_entry.get())
        conn.commit()
        conn.close()
        clear_entries()
        messagebox.showinfo("Deleted!", "Your Wine Has Been Deleted!")
    else:
        pass

def select_record(e):
    
    clear_entries()

    selected = my_tree.focus()
    values = my_tree.item(selected, "values")

    name_entry.insert(0, values[1])
    type_entry.insert(0, values[2])
    id_entry.insert(0, values[0])
    price_entry.insert(0, values[3])
    quantity_entry.insert(0, values[4])

def update_record():
    MsgBox = messagebox.askquestion ('Update Wine','Are you sure about the changes?')
    if MsgBox == 'yes':
        selected = my_tree.focus()
        my_tree.item(selected, text='', values=( id_entry.get(), name_entry.get(),type_entry.get(),price_entry.get(), quantity_entry.get(),))

        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute("""UPDATE wines SET
            name = :name,
            type = :type,
            price = :price,
            quantity = :quantity

            WHERE oid = :oid""",
            {
                'name':name_entry.get(),
                'type':type_entry.get(),
                'price':price_entry.get(),
                'quantity':quantity_entry.get(),
                'oid':id_entry.get(),
            }
        )

        conn.commit()
        conn.close()

        name_entry.delete(0, END)
        type_entry.delete(0, END)
        id_entry.delete(0, END)
        price_entry.delete(0, END)
        quantity_entry.delete(0, END)
    else:
        pass

def add_record():

    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("INSERT INTO wines VALUES (:name, :type, :id, :price, :quantity)",
    {
        'name':name_entry.get(),
        'type':type_entry.get(),
        'id':id_entry.get(),
        'price':price_entry.get(),
        'quantity':quantity_entry.get(),
    }
    )

    conn.commit()
    conn.close()   

    #clear entry boxes
    name_entry.delete(0, END)
    type_entry.delete(0, END)
    id_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)

    my_tree.delete(*my_tree.get_children())

    query_database()

def sale():

    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("INSERT INTO sales (quantity, name, date) VALUES (?, ?, ?)", (spin.get(), combo.get(), cal.get_date()))

    combo_id = (combo.get()).split(".)  ")
    wine_id_for_reduction = combo_id[0]

    c.execute("SELECT quantity FROM wines WHERE rowid=?", (wine_id_for_reduction,) )

    quan = c.fetchall()
    quan2 = quan[0]
    quan3 = quan2[0]
    new_quan = quan3 - int(spin.get())

    c.execute("""UPDATE wines SET
    quantity = :quantity

    WHERE rowid = :rowid""",
    {
        'quantity':new_quan,
        'rowid':wine_id_for_reduction,
    }
    )
    
    conn.commit()
    conn.close()  

    my_hist_tree.delete(*my_hist_tree.get_children())
    query_history()
    my_tree.delete(*my_tree.get_children())
    query_database()
    low_quants()

def delete_sale():
    MsgBox = messagebox.askquestion ('Delete Sale','Are you sure you want to delete this sale?')
    if MsgBox == 'yes':
        x = my_hist_tree.selection()
        y = my_hist_tree.item(x)['values']
        my_hist_tree.delete(x)

        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute("DELETE from sales WHERE oid=?",  (y[0],))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted!", "Your Sale Has Been Deleted!")

    else:
        pass
    
conn = sqlite3.connect('winelist.db')
c = conn.cursor()
c.execute("SELECT rowid, name, type FROM wines")
wines_stock = []
for i in c.fetchall():
    wines_stock.append(str(i[0])+".)  "+i[1]+"  ("+i[2]+")")
conn.commit()
conn.close()

def query_history():

    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM sales")
    records = c.fetchall()
    records.sort(reverse=True)

    global count
    count = 0

    for record in records:
        dates_list2 = record[2].split('-')
        dates_list =  dates_list2[2]+'-'+dates_list2[1]+'-'+dates_list2[0]

        if count % 2 ==0:
            my_hist_tree.insert(parent='', index='end', iid=count, text='', values=(record[0], dates_list, record[3], record[1]), tags=('evenrow',))
        else:
            my_hist_tree.insert(parent='', index='end', iid=count, text='', values=(record[0], dates_list, record[3], record[1]), tags=('oddrow',))
        count +=1

    conn.commit()
    conn.close()

def export_data():
    conn = sqlite3.connect('winelist.db')
    df = pd.read_sql_query("SELECT quantity, date, name FROM sales ", conn)
    df.to_csv(r'sales.csv')
    df = pd.read_sql_query("SELECT * FROM wines ", conn)
    df.to_csv(r'wines.csv')

    messagebox.showinfo("Saved!", "Your Database Has Been Saved in a CSV inside the folder!")


def import_sales():
    MsgBox = messagebox.askquestion ('Update Database','Database update will erase the saved information. Are you sure you want to update your database?')
    if MsgBox == 'yes':
        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute("DROP TABLE sales")

        c.execute("""CREATE TABLE if not exists sales (
        quantity integer,
        date blob,
        name text
        )
        """)

        app.filename_sales = filedialog.askopenfilename(initialdir="C:\\Users\\Kafetzo\\Desktop\\winelist_copy", title='Select CSV', filetype=(("csv files", "*.csv"), ("all files", "*.*")))
        
        sales = pd.read_csv(app.filename_sales, names =['quantity', 'date', 'name'])
        new_header = sales.iloc[0] #grab the first row for the header
        sales = sales[1:] #take the data less the header row
        sales.columns = new_header #set the header row as the df header
        sales.to_sql('sales', conn, if_exists='append', index=FALSE)

        my_hist_tree.delete(*my_hist_tree.get_children())
        query_history()

        conn.commit()
        conn.close()
        messagebox.showinfo("Updated!", "Your Sales Have Been Updated!")

    else:
        pass
    
def import_wines():
    MsgBox = messagebox.askquestion ('Update Database','Database update will erase the saved information. Are you sure you want to update your database?')

    if MsgBox == 'yes':
        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute("DROP TABLE wines")

        c.execute("""CREATE TABLE if not exists wines (
            name text,
            type text,
            id integer,
            price integer,
            quantity integer)
            """)

        app.filename_wines = filedialog.askopenfilename(initialdir="C:\\Users\\Kafetzo\\Desktop", title='Select CSV', filetype=(("csv files", "*.csv"), ("all files", "*.*")))

        wines = pd.read_csv(app.filename_wines, names =['name', 'type', 'id', 'price', 'quantity'])
        new_header2 = wines.iloc[0] #grab the first row for the header
        wines = wines[0:] #take the data less the header row
        wines.columns = new_header2 #set the header row as the df header
        wines.to_sql('wines', conn, if_exists='append', index=FALSE)


        my_tree.delete(*my_tree.get_children())
        query_database()
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated!", "Your Wines Have Been Updated!")

    else:
        pass

def graph_hist():

    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute('SELECT date, quantity FROM sales WHERE name=?', (combo2.get(),))

    results = c.fetchall()
    dates = []
    dates.sort()
    quantities = []

    conn.commit()
    conn.close()

    for i in results:

        today = date.today()
        today_str = today.strftime("%Y/%m/%d")
        current_year_slice = today_str.split('/')
        current_year = int(current_year_slice[0])

        d = i[0]
        d2 = d.split('-')
        sales_year = int(d2[0])
        if sales_year == current_year:
            quantities.append(i[1])
            dates.append(d)

    dates_list = [datetime.strptime(date, '%Y-%m-%d').date() for date in dates]
    plt.bar(dates_list, quantities, width=1)
    plt.gcf().autofmt_xdate()
    date_format = mpl_dates.DateFormatter('%b-%d-%Y')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.ylim(0, 11)
    plt.xlabel("Dates")
    plt.ylabel("Quantities")
    plt.title("Wine Graph")
    plt.tight_layout()
    plt.show()

def graph_sel_wine():

    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute('SELECT date, quantity FROM sales WHERE name=?', (combo2.get(),))

    results = c.fetchall()
    results_sorted = sorted(results)

    dates = []
    quantities = []
    fromDate = from_cal.get_date()
    toDate = to_cal.get_date()


    for res in results_sorted:
        if (datetime.strptime(res[0], '%Y-%m-%d').date()) >= fromDate and (datetime.strptime(res[0], '%Y-%m-%d').date()) <= toDate :
            dates.append((datetime.strptime(res[0], '%Y-%m-%d').date()))
            quantities.append(res[1])

    conn.commit()
    conn.close()

    sum = {}
    for item in results_sorted:
        if not item[2] in sum:
            sum[ item[2] ] = 0
        sum[ item[2] ] += item[0]
    
    if dates:
        plt.bar(dates, quantities)
        plt.gcf().autofmt_xdate()
        date_format = mpl_dates.DateFormatter('%b-%d-%Y')
        plt.gca().xaxis.set_major_formatter(date_format)
        plt.ylim(0, 11)
        plt.xlabel("Dates")
        plt.ylabel("Quantities")
        plt.title("Wine Graph")
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showinfo("Error!", "There Are No Sales In These Dates!")

def low_quants():

    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM wines")
    records = c.fetchall() 

    quan_list = []

    for record in records:
        i = 0
        if record[5] < 2  :
            if record[4] < 100 :
                quan_list.append(record)

    if quan_list:
        messagebox.showinfo("LOW STOCK !!!", "You Have Low Stock On Wines!")
        low_quantities = Tk()
        low_quantities.geometry("700x700")
        low_quantities.title("Wines that are in low quantities")
        
        quan_lb = Listbox(low_quantities, font=('Cambria', 15))
        quan_lb.pack(expand=True, fill='both')

        for q in quan_list:
            x = 0
            quan_lb.insert(x, str(q[0])+".)  "+q[1]+"  "+q[2]+"  "+str(q[5]))
            x+1

    conn.commit()
    conn.close()

def graph_sel_dates():
    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sales')
    r = c.fetchall()

    c.execute('SELECT rowid, name, type FROM wines')
    names = c.fetchall()

    date_from = from_cal.get_date()
    date_to = to_cal.get_date()

    wine_list = []
    wine_list.sort()

    conn.commit()
    conn.close()

    for res in r:
        d = (datetime.strptime(res[1], '%Y-%m-%d').date())
        if d >= date_from and d <= date_to:
            wine_list.append(res)

    sum = {}
    for item in wine_list:
        if not item[2] in sum:
            sum[ item[2] ] = 0
        sum[ item[2] ] += item[0]

    names = list(sum.keys())
    values = list(sum.values())

    plt.bar(range(len(sum)), values, tick_label=names)
    plt.gcf().autofmt_xdate()
    plt.ylabel("Quantities")
    plt.title("Wine Sales On Selected Dates")
    plt.tight_layout()
    plt.show()

def delete_wines():
    MsgBox = messagebox.askquestion ('DELETE WINES','Are you sure you want to delete ALL WINES ?')

    if MsgBox == 'yes':
        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute('DROP TABLE wines')
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated!", "Your Wines Have Been Deleted! Please restart the application for the changed to take effect.")

    else:
        pass


def delete_sales():
    MsgBox = messagebox.askquestion ('DELETE SALES','Are you sure you want to delete ALL SALES ?')

    if MsgBox == 'yes':
        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute('DROP TABLE sales')
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated!", "Your Sales Have Been Deleted! Please restart the application for the changed to take effect.")

    else:
        pass



s = ttk.Style()
s.theme_use('clam')

note_frame = Frame(app, background="white")
note_frame.pack(fill='both', expand=True)

s.configure('TNotebook', background="white")
s.configure('TNotebook.Tab', background="white", font=('Cambria', 13), width=12)
notebook = ttk.Notebook(note_frame)
notebook.pack(pady=25, padx=25, expand=True, fill='both')

frame_sale = Frame(master=app, background='#FFFFFF')
frame_inv= Frame(master=app, background='#FFFFFF')
imp_exp= Frame(master=app, background='#FFFFFF')

frame_sale.pack(pady=20, padx=0, fill="both", expand=True)
frame_inv.pack(pady=0, padx=0, fill="both", expand=True)
imp_exp.pack(pady=0, padx=0, fill="both", expand=True)

notebook.add(frame_sale, text='Sales')
notebook.add(frame_inv, text='Inventory')
notebook.add(imp_exp, text='Import/Export')
############### SALES TAB ##############################
frame_top2 = Frame(frame_sale, background='white')
frame_top2.pack( pady=0, padx=0, fill='both',  side=TOP)

frame_top3 = Frame(frame_sale, background='#FFFFFF')
frame_top3.pack( pady=0, padx=20, fill='both', expand=True, side=BOTTOM)

frame_top4 = Frame(frame_sale, background='white')
frame_top4.pack( pady=0, padx=0, fill='both', expand=True, side=BOTTOM)

frame_top_left = Frame(frame_top3, background='white')
frame_top_left.pack(side=LEFT, fill='both', expand=True)

frame_top_right = Frame(frame_top3, background='#FFFFFF')
frame_top_right.pack(fill='both', expand=True, side=RIGHT, pady=20)

combo_lbl_frame = Frame(frame_top2, background='white') 
combo_lbl_frame.pack(padx=0, pady=30, fill='x', expand=True)

combo_lbl_frame2 = Frame(combo_lbl_frame, background='white') 
combo_lbl_frame2.pack( padx=0, pady=20, fill='x', expand=True)

input_frame2 = Frame(frame_top3, background='white')
input_frame2.pack(fill='both', expand=True)

sales_input_frame = Frame(frame_top_left, background='#F5F5F5')
sales_input_frame.pack(side=TOP, fill='both', expand=True, pady=20)

sales_input_frame2 = Frame(sales_input_frame, background='#F5F5F5')
sales_input_frame2.pack(side=TOP, pady=40)

combo_lbl = Label(combo_lbl_frame2, text="Maître Corbeau - Stock Management and Sales Analysis", bg='white', fg='grey3', font=('Cambria', 23))
combo_lbl.pack(padx=40, side=LEFT)

combo_lbl2 = Label(combo_lbl_frame, text="Sales History", bg='white', fg='grey3', font=('Cambria', 18))
combo_lbl2.pack(padx=40, side=LEFT)

sales_inp_label = Label(sales_input_frame2, text='Record A Wine Sale', bg='#F5F5F5' , font=('Cambria', 19, 'bold'))
sales_inp_label.pack(pady=20)

combo_label = Label(sales_input_frame2, text='Wine Name :', bg='#F5F5F5' , font=('Cambria', 14))
combo_label.pack(pady=5)

fontExample = ("Cambria", 14)
app.option_add("*TCombobox*Listbox*Font", fontExample)
s.map('TCombobox', fieldbackground=[('readonly', 'white')])
combo = ttk.Combobox(sales_input_frame2, values=wines_stock, state="readonly", width=40, font=('Cambria', 15))
try:
    combo.set(wines_stock[0])
except:
    pass
combo.pack(pady=5)

quan_label = Label(sales_input_frame2, text='Quantity :', bg='#F5F5F5' , font=('Cambria', 14))
quan_label.pack(pady=5)

s.configure('My.TSpinbox', arrowsize=15,  fieldbackground='#FFFFFF')
spin = ttk.Spinbox(sales_input_frame2, style='My.TSpinbox',from_=1, to_=10, width=5,font=font.Font(family='Cambria', size=15))
spin.set(1)
spin.pack(pady=5, fill='x')

sale_date_label = Label(sales_input_frame2, text='Date :', bg='#F5F5F5' , font=('Cambria', 14))
sale_date_label.pack(pady=5)

cal = DateEntry(sales_input_frame2,background='#FFFFFF',
            foreground='black', borderwidth=2, style='my.DateEntry', locale='el_GR', date_pattern='dd/mm/yyyy', font=('Cambria', 15))
cal.pack(pady=5, fill='x')

sales_but = Button(sales_input_frame2, text="Wines Sold", command=sale, background='#751824',fg='white', font=('Cambria',13, 'bold'))
sales_but.pack(pady=20, ipadx=14, anchor=CENTER)

hist_tree_frame = Frame(frame_top4, background='white')
hist_tree_frame.pack(pady=0, padx=0, fill='both', expand=True)

hist_tree_frame2 = Frame(hist_tree_frame, bg='white')
hist_tree_frame2.pack(pady=0, padx=20, side=TOP, fill='both', expand=True)
hist_tree_scroll = Scrollbar(hist_tree_frame2)
hist_tree_scroll.pack(side=LEFT, fill='y', pady=0)

delete_sale_button = Button(combo_lbl_frame, text='Delete Selected Sale', command=delete_sale, height=1, background='#751824',fg='white', font=('Cambria',13, 'bold'))
delete_sale_button.pack(pady=0, padx=20, ipadx=20, side=RIGHT, anchor=E)

my_hist_tree = ttk.Treeview(hist_tree_frame2, yscrollcommand=hist_tree_scroll.set, selectmode='extended', height=6)
my_hist_tree.pack(pady=0, padx=0, side=LEFT, expand=True, fill='both')


hist_tree_scroll.config(command=my_hist_tree.yview)

my_hist_tree['columns'] = ('ID', 'Date', 'Name', 'Quantity')

my_hist_tree.column('#0', width=0, stretch=NO)
my_hist_tree.column("ID", anchor=CENTER, width=20)
my_hist_tree.column("Date", anchor=CENTER)
my_hist_tree.column("Name", anchor=CENTER, width=400)
my_hist_tree.column("Quantity", anchor=CENTER)

my_hist_tree.heading("#0", text="", anchor=CENTER)
my_hist_tree.heading("ID", text="ID", anchor=CENTER)
my_hist_tree.heading("Date", text="Date", anchor=CENTER)
my_hist_tree.heading("Name", text="Name", anchor=CENTER)
my_hist_tree.heading("Quantity", text="Quantity", anchor=CENTER)

my_hist_tree.tag_configure('oddrow', background= 'white', foreground='black', font=('Cambria', 16))
my_hist_tree.tag_configure('evenrow',background='#EEE9ED', foreground='black', font=('Cambria', 16))
my_hist_tree.tag_configure('lowrow',background='red', foreground='white', font=('Cambria', 16))

from_to_cal_frame = Frame(frame_top_right, background='#FFFFFF')
from_to_cal_frame.pack(pady=20)

graph_label = Label(from_to_cal_frame, text='Create A Graph', background='#FFFFFF', font=('Cambria', 19, 'bold'))
graph_label.pack(pady=20)

sel_wine_label = Label(from_to_cal_frame, text='Select Wine:', background='#FFFFFF', font=('Cambria', 14) )
sel_wine_label.pack(pady=5)

fontExample = ("Cambria", 14)
app.option_add("*TCombobox*Listbox*Font", fontExample)
combo2 = ttk.Combobox(from_to_cal_frame, values=wines_stock, state = "readonly", width=40, font=('Cambria', 15), background='red')
try:
    combo2.set(wines_stock[0])
except:
    pass
combo2.pack(pady=5, padx=5)

from_label = Label(from_to_cal_frame, text='From:', background='#FFFFFF', font=('Cambria', 14))
from_label.pack(pady=5)

from_cal = DateEntry(from_to_cal_frame, background='#FFFFFF',
            foreground='black', borderwidth=2, style='my.DateEntry', locale='el_GR', date_pattern='dd/mm/yyyy', font=('Cambria', 15))
from_cal.pack(fill='x', expand=True, pady=5, padx=5)

to_label = Label(from_to_cal_frame, text='To:', background='#FFFFFF', font=('Cambria', 14))
to_label.pack(pady=5)

to_cal = DateEntry(from_to_cal_frame, background='#FFFFFF',
            foreground='black', borderwidth=2, style='my.DateEntry', locale='el_GR', date_pattern='dd/mm/yyyy', font=('Cambria', 15))
to_cal.pack(fill='x', expand=True, pady=5, padx=5)

right_button_frame = Frame(frame_top_right, background='#FFFFFF')
right_button_frame.pack(side=TOP, padx=10, pady=0)

wine_graph_button = Button(right_button_frame, text="Selected Wine", background='#751824', command=graph_sel_wine,fg='white', font=('Cambria',13, 'bold'))
wine_graph_button.pack(side=LEFT, padx=5, fill='x', expand=True)

wine_graph_hist_button = Button(right_button_frame, text="Selected Dates", command=graph_sel_dates, background='#751824',fg='white', font=('Cambria',13, 'bold'))
wine_graph_hist_button.pack(side=LEFT, padx=5, fill='x', expand=True)

wine_graph_hist_button = Button(right_button_frame, text="Year Report", command=graph_hist, background='#751824',fg='white', font=('Cambria',13, 'bold'))
wine_graph_hist_button.pack(side=LEFT, padx=5, fill='x', expand=True)


###################### INVENTORY  ###################
s.configure('Treeview.Heading', background="#58181F", foreground='white', font=('Cambria', 15, 'bold'), height=15)
s.configure('Treeview', rowheight=30)

tree_frame = Frame(frame_inv, background='white')
tree_frame.pack(pady=30, padx=0, side=LEFT, fill='both', expand=True)

tree_frame2 = Frame(tree_frame)
tree_frame2.pack(pady=0, padx=0, side=LEFT, fill='both', expand=True)
tree_scroll = Scrollbar(tree_frame2)
tree_scroll.pack(side=LEFT, fill='y', pady=0)

my_tree = ttk.Treeview(tree_frame2, yscrollcommand=tree_scroll.set, selectmode='extended')
my_tree.pack(pady=0, padx=0, side=LEFT, expand=True, fill='both')

tree_scroll.config(command=my_tree.yview)

my_tree['columns'] = ('ID', 'Name', 'Type', 'Price', 'Quantity')

my_tree.column('#0', width=0, stretch=NO)
my_tree.column("ID", anchor=N, width=0)
my_tree.column("Name", anchor=W, width=400)
my_tree.column("Type", anchor=CENTER)
my_tree.column("Price", anchor=CENTER)
my_tree.column("Quantity", anchor=CENTER)

my_tree.heading("#0", text="", anchor=W)
my_tree.heading("ID", text="ID", anchor=N)
my_tree.heading("Name", text="Name", anchor=W)
my_tree.heading("Type", text="Type", anchor=CENTER)
my_tree.heading("Price", text="Price", anchor=CENTER)
my_tree.heading("Quantity", text="Quantity", anchor=CENTER)

my_tree.tag_configure('oddrow', background= 'white', foreground='black', font=('Cambria', 16))
my_tree.tag_configure('evenrow',background='#EEE9ED', foreground='black', font=('Cambria', 16))

rightSideFrame = Frame(frame_inv, background='#58181F', width=390)
rightSideFrame.pack(pady=30, padx=0, expand=True, fill='y')
rightSideFrame.pack_propagate(0)

input_frame = Frame(rightSideFrame, background='#58181F')
input_frame.pack(pady=20, padx=20, side=TOP, fill='both', expand=True)

button_frame = Frame(rightSideFrame, background='#58181F')
button_frame.pack(expand=True, fill='both', side=TOP, padx=33)

id_label = Label(input_frame, text="ID: (Leave Empty When Adding A Wine)", background='#58181F', foreground='white')
id_label.pack(pady=0, side=TOP)
id_label.config(font=('Cambria',13, 'bold'))

id_entry = Entry(input_frame, font=('Cambria', 15))
id_entry.pack(pady=10, side=TOP, ipady=6, fill='x', padx=10)

name_label = Label(input_frame, text="Name:", background='#58181F', foreground='white')
name_label.pack(pady=0, side=TOP)
name_label.config(font=('Cambria',13, 'bold'))

name_entry = Entry(input_frame, font=('Cambria', 15), width=25)
name_entry.pack(pady=10, side=TOP, ipady=6, fill='x', padx=10)

type_label = Label(input_frame, text="Type:", background='#58181F', foreground='white')
type_label.pack(pady=0, side=TOP)
type_label.config(font=('Cambria',13, 'bold'))

type_entry = Entry(input_frame, font=('Cambria', 15))
type_entry.pack(pady=10, side=TOP, ipady=6, fill='x', padx=10)

price_label = Label(input_frame, text="Price:", background='#58181F', foreground='white')
price_label.pack(pady=0, side=TOP)
price_label.config(font=('Cambria',13, 'bold'))

price_entry = Entry(input_frame, font=('Cambria', 15))
price_entry.pack(pady=10, side=TOP, ipady=6, fill='x', padx=10)

quantity_label = Label(input_frame, text="Quantity:", background='#58181F', foreground='white')
quantity_label.pack(pady=0, side=TOP)
quantity_label.config(font=('Cambria',13, 'bold'))

quantity_entry = Entry(input_frame, font=('Cambria', 15))
quantity_entry.pack(pady=10, side=TOP, ipady=6, fill='x', padx=10)

add_button = Button(button_frame, text='Add Wine', command=add_record, background='#751824',fg='#EEE9ED', font=('Cambria',13, 'bold'))
add_button.pack(side=TOP, fill='x', ipady=5, pady=20)

update_button = Button(button_frame, text='Update Wine', command=update_record, background='#751824', fg='#EEE9ED', font=('Cambria',13, 'bold'))
update_button.pack(side=TOP, fill='x', ipady=5)

remove_one_button = Button(button_frame, text='Remove Selected', command=remove_one, background='#751824',fg='#EEE9ED', font=('Cambria',13, 'bold'))
remove_one_button.pack(side=TOP, fill='x', ipady=5, pady=20)

select_record_button = Button(button_frame, text='Clear Text', command=clear_entries, background='#751824',fg='#EEE9ED', font=('Cambria',13, 'bold'))
select_record_button.pack(side=TOP, fill='x', ipady=5)

########### IMPORT EXPORT ########

butt_frame_imp = Frame(imp_exp, bg='white')
butt_frame_imp.place(relx=0.5, rely=0.5, anchor=CENTER)

export_btn = Button(butt_frame_imp, text='Export Data', width=16, background='#751824',fg='#EEE9ED', font=('Cambria',13, 'bold'), command=export_data)
export_btn.grid(row=0, columnspan=2, padx=20, pady=20)

import_wines_btn = Button(butt_frame_imp, text='Import Wines', width=16, background='#751824',fg='#EEE9ED', font=('Cambria',13, 'bold'), command=import_wines)
import_wines_btn.grid(row=1, column=0, padx=20, pady=20)

import_sales_btn = Button(butt_frame_imp, text='Import Sales', width=16, background='#751824',fg='#EEE9ED', font=('Cambria',13, 'bold'), command=import_sales)
import_sales_btn.grid(row=1, column=1, padx=20, pady=20)

delete_wines_btn = Button(butt_frame_imp, text='Delete All Wines', width=16, background='#751824',fg='#EEE9ED', font=('Cambria',13, 'bold'), command=delete_wines)
delete_wines_btn.grid(row=2, column=0, padx=20, pady=20)

delete_sales_btn = Button(butt_frame_imp, text='Delete All Sales', width=16, background='#751824',fg='#EEE9ED', font=('Cambria',13, 'bold'), command=delete_sales)
delete_sales_btn.grid(row=2, column=1, padx=20, pady=20)

my_tree.bind("<ButtonRelease-1>", select_record)

query_history()
query_database()
low_quants()


mainloop()
