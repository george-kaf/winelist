from tkinter import messagebox 
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
from matplotlib import dates as mpl_dates
import tkinter as tk
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import Listbox
from tkinter import filedialog
import os

try:
    from ctypes import windll
except:
    pass

try:
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

conn = sqlite3.connect('winelist.db')
c = conn.cursor()

c.execute("""CREATE TABLE if not exists wines (
name text,
type text,
variety text,
price real,
quantity real,
notes text)
""")

c.execute("""CREATE TABLE if not exists sales (
quantity real,
date blob,
drink text
)
""")

conn.commit()
conn.close()

##########  DASHBOARD FUNCTIONS ######################
def sale(button_press):
    date_str = cal.entry.get()
    date_object = datetime.strptime(date_str, '%d/%m/%Y').date()

    sel_item = my_tree.focus()
    sel_item_data = (my_tree.item(sel_item))
    sel_item_values = sel_item_data['values']

    sel_wine_id = str(sel_item_values[0])
    type_to_remove = str(sel_item_values[1])
    variety_to_remove = str(sel_item_values[2])
    name_to_remove = str(sel_item_values[3])

    drink = str(sel_item_values[1])+" ~ "+str(sel_item_values[3])+" ~ "+str(sel_item_values[2])

    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT rowid, quantity FROM wines WHERE type=? AND variety=? AND name=? ", (type_to_remove, variety_to_remove, name_to_remove))
    quan = c.fetchall()

    if button_press == "Bottle":
        quan2 = quan[0]
        quan3 = quan2[1]
        new_quan = round((quan3-1), 2)
        quantity_to_save = 1
    else:
        quan2 = quan[0]
        quan3 = quan2[1]
        new_quan = (quan3-0.2)
        new_quan = round(new_quan, 2)
        quantity_to_save = 0.2       

    c.execute("INSERT INTO sales (quantity, drink, date) VALUES (?, ?, ?)", (quantity_to_save, drink, date_object))

    if new_quan >= 0 :
        c.execute("""UPDATE wines SET
        quantity = :quantity
        WHERE rowid = :rowid""",
        {
            'quantity':new_quan,
            'rowid':quan2[0],})
        
        conn.commit()
        conn.close()  
        my_inv_tree.delete(*my_inv_tree.get_children())
        query_database()

        validationMessage = ttk.Label(recordSaleLabelFrame, text=' Submitted succesfully!', bootstyle=SUCCESS)
        validationMessage.pack(pady=(0,20), padx=20, fill=X)
        validationMessage.after(2000, validationMessage.destroy)

        selected_iid = my_tree.focus()
        item_index = my_tree.index(selected_iid)            
        my_tree.delete(*my_tree.get_children())
        query_sales_stock()
        my_tree.focus(item_index)
        my_tree.selection_set(item_index)

        values = my_tree.item(selected_iid, "values")
        quan_label.set("Bottles: "+str(values[4]))
        progg_value = values[4]
        progg['value'] = progg_value
        hist_list_update()


    else:
        messagebox.showinfo("Oops!", "You are trying to set the remaining quantity to a negative number. Check your inventory and try again.", parent=app)
        conn.commit()
        conn.close()

def low_quants():
    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM wines")
    records = c.fetchall() 
    quan_list = []
    for record in records:
        try:
            if record[5] < 3  :
                if record[4] < 100 :
                    quan_list.append(record)
        except:
            continue

    if quan_list:
        messagebox.showinfo("Low Stock!", "Press OK to check which wines are running low on stock!")
        low_quantities = ttk.Toplevel(app)
        low_quantities.geometry("700x700")
        low_quantities.title("Wines that are in low quantity")


        quan_lb = Listbox(low_quantities, font=('Calibri', 14))
        quan_lb.pack(expand=True, fill='both', padx=20, pady=20, side=RIGHT)
        quant_progg = ttk.Frame(low_quantities)
        quant_progg.pack(fill=X, side=LEFT, anchor=N, pady=20, padx=(20,0))

        for q in quan_list:
            x = 0
            quan_lb.insert(x, q[1]+"  "+q[2]+"  "+str(q[4]))
            progg = ttk.Progressbar(quant_progg, bootstyle="danger", length=100, orient=HORIZONTAL)
            progg.pack(pady=(10), padx=5,)
            progg['value'] += 10
            x+1

    conn.commit()
    conn.close()

def query_sales_stock():
    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM wines")
    records = c.fetchall()
    records.sort(reverse=True)

    global count
    count = 0

    for record in records:
        if count % 2 == 0:

            my_tree.insert(parent='', index='end', iid=count, text='', values=(record[0], record[2], record[3], record[1], record[5]), tags=('evenrow'))
        else:
            my_tree.insert(parent='', index='end', iid=count, text='', values=(record[0], record[2], record[3], record[1], record[5]), tags=('oddrow'))
        count +=1
 
    conn.commit()
    conn.close()

def delete_sale():
    MsgBox = messagebox.askquestion ('Delete Sale','Are you sure you want to delete this sale?')
    if MsgBox == 'yes':
        cs = hist_listbox.curselection()[0]
        cs_name = hist_listbox.get(cs)
        cs_name = cs_name.split(" ~ ")
        oid_to_delete = cs_name[4]

        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute("DELETE FROM sales WHERE oid=?", (oid_to_delete,))

        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted!", "Your Sale Has Been Deleted! Check your inventory for correct quantities.")
        hist_list_update()
    else:
        pass 

def hist_list_update():
    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT rowid, * from sales")
    hist = c.fetchall()
    hist_listbox.delete(0, END)
    for hi in hist:
        x=0
        if hi[1] > 0.5:
            hist_listbox.insert(x, str("Bottle of ")+" ~ "+str(hi[3])+" ~ "+str(hi[0]))
        else:
            hist_listbox.insert(x, str("Glass of ")+" ~ "+str(hi[3])+" ~ "+str(hi[0]))

        x +=1
    conn.commit()
    conn.close()

############  INVENTORY FUNCTIONS  ######################
def query_database():
    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM wines")
    records = c.fetchall()
    records.sort(key=lambda a: a[2])
    global count
    count = 0

    for record in records:   
        if count % 2 ==0:
            my_inv_tree.insert(parent='', index='end', iid=count, text='', values=(record[0], record[2], record[3], record[1], record[4], record[5]), tags=('evenrow',))
        else:
            my_inv_tree.insert(parent='', index='end', iid=count, text='', values=(record[0], record[2], record[3], record[1], record[4], record[5]), tags=('oddrow',))
            
        count +=1

    conn.commit()
    conn.close()

def select_record(e):
    try:
        clear_entries()

        selected = my_inv_tree.focus()
        values = my_inv_tree.item(selected, "values")

        name_entry.insert(0, values[3])
        type_entry.insert(0, values[1])
        var_entry.insert(0, values[2])
        price_entry.insert(0, values[4])
        quantity_entry.insert(0, values[5])
    except:
        pass

def sel_item_for_quanity(e):
    try:
        selected = my_tree.focus()
        values = my_tree.item(selected, "values")
        quan_label.set("Bottles: "+str(values[4]))
        progg_value = values[4]
        progg['value'] = progg_value
    except:
        pass 

def select_record_notes(e):
    try:
        selected = my_inv_tree.focus()
        values = my_inv_tree.item(selected, "values")

        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute("SELECT notes FROM wines WHERE rowid=?", (str(values[0]),))
        n = c.fetchall()
        n1 = n[0]
        n2 = n1[0]
        notes_var.set(n2)
        conn.commit()
        conn.close()
    except:
        pass

def add_record():
    def clear_entries():
        name_entry.delete(0, END)
        var_entry.delete(0, END)
        price_entry.delete(0, END)
        quantity_entry.delete(0, END)
        notes_entry.delete(0, END)
        
    def clear_entries_and_selection():
        clear_entries()
        for item in my_inv_tree.selection():
            my_inv_tree.selection_remove(item)


    def add_one():
        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute("INSERT INTO wines VALUES (:name, :type, :variety, :price, :quantity, :notes)",
        {
            'name':name_entry.get().capitalize(),
            'type':type_entry.get().capitalize(),
            'variety':var_entry.get().capitalize(),
            'price':price_entry.get(),
            'quantity':quantity_entry.get(),
            'notes':notes_entry.get()
        }
        )

        conn.commit()
        conn.close()   

        name_entry.delete(0, END)
        var_entry.delete(0, END)
        price_entry.delete(0, END)
        quantity_entry.delete(0, END)
        notes_entry.delete(0, END)

        my_inv_tree.delete(*my_inv_tree.get_children())
        query_database()
        my_tree.delete(*my_tree.get_children())
        query_sales_stock()
        add.destroy()

    add = ttk.Toplevel()
    add.title("Add a drink")

    add_main = ttk.Frame(add)
    add_main.pack(fill=X, expand=1, padx=20, pady=20)

    input_frame = ttk.Frame(add_main)
    input_frame.pack(padx=(20, 20), pady=10, fill=X)

    name_frame = ttk.Frame(input_frame)
    name_frame.pack(fill=X, expand=True, pady=3)

    name_label = ttk.Label(name_frame, text="Name : ")
    name_label.pack(side=LEFT)

    name_entry = ttk.Entry(name_frame)
    name_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    type_frame = ttk.Frame(input_frame)
    type_frame.pack(fill=X, expand=True, pady=3)

    type_label = ttk.Label(type_frame, text="Type : ")
    type_label.pack(side=LEFT)

    type_values = ["Red", "White", "Rose", "Sparkling", "Other"]
    type_entry = ttk.Combobox(type_frame, values=type_values, state=READONLY)
    type_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)
    type_entry.set("Red")

    var_frame = ttk.Frame(input_frame)
    var_frame.pack(fill=X, expand=True, pady=3)

    var_label = ttk.Label(var_frame, text="Variety : ")
    var_label.pack(side=LEFT)

    var_entry = ttk.Entry(var_frame)
    var_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    price_frame = ttk.Frame(input_frame)
    price_frame.pack(fill=X, expand=True, pady=3)

    price_label = ttk.Label(price_frame, text="Price : ")
    price_label.pack(side=LEFT)

    price_entry = ttk.Entry(price_frame)
    price_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    quantity_frame = ttk.Frame(input_frame)
    quantity_frame.pack(fill=X, expand=True, pady=3)

    quantity_label = ttk.Label(quantity_frame, text="Quantity : ")
    quantity_label.pack(side=LEFT)

    quantity_entry = ttk.Entry(quantity_frame)
    quantity_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    notes_frame = ttk.Frame(input_frame)
    notes_frame.pack(fill=X, expand=True, pady=3)

    notes_label = ttk.Label(notes_frame, text="Notes : ")
    notes_label.pack(side=LEFT)

    notes_entry = ttk.Entry(notes_frame)
    notes_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    add_wine_button = ttk.Button(add_main, text='Done', bootstyle=SUCCESS, command=add_one)
    add_wine_button.pack(side=LEFT, padx=20, pady=20, fill=X, expand=1)

    clear_text_button = ttk.Button(add_main, text='Clear', command=clear_entries_and_selection, bootstyle=DANGER)
    clear_text_button.pack(side=LEFT, padx=(0, 20), pady=20, fill=X, expand=1)

    add.mainloop()

def update_record():
    def edit_one():
        if my_inv_tree.item(my_inv_tree.focus())  == "":
            pass
        else:
            MsgBox = messagebox.askquestion ('Update Wine','Are you sure about the changes?')
            if MsgBox == 'yes':
                try:
                    curItem = my_inv_tree.focus()
                    item_data = (my_inv_tree.item(curItem))
                    item_values = item_data['values']
                    id_from_selection = str(item_values[0])
                except:
                    pass

                conn = sqlite3.connect('winelist.db')
                c = conn.cursor()
                c.execute("""UPDATE wines SET
                    name = :name,
                    type = :type,
                    variety = :variety,
                    price = :price,
                    quantity = :quantity,
                    notes = :notes

                    WHERE oid = :oid""",
                    {
                        'name':name_entry.get().capitalize(),
                        'type':type_entry.get().capitalize(),
                        'variety':var_entry.get().capitalize(),
                        'price':price_entry.get(),
                        'quantity':quantity_entry.get(),
                        'notes':notes_entry.get().capitalize(),
                        'oid':id_from_selection
                    }
                )

                conn.commit()
                conn.close()

                my_inv_tree.delete(*my_inv_tree.get_children())
                query_database()
                my_tree.delete(*my_tree.get_children())
                query_sales_stock()
                edit.destroy()

    def close():
        edit.destroy()        

    edit = ttk.Toplevel()
    edit.title("Edit a drink")

    add_main = ttk.Frame(edit)
    add_main.pack(fill=X, expand=1, padx=20, pady=20)

    input_frame = ttk.Frame(add_main)
    input_frame.pack(padx=(20, 20), pady=10, fill=X)

    name_frame = ttk.Frame(input_frame)
    name_frame.pack(fill=X, expand=True, pady=3)

    name_label = ttk.Label(name_frame, text="Name : ")
    name_label.pack(side=LEFT)

    name_entry = ttk.Entry(name_frame)
    name_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    type_frame = ttk.Frame(input_frame)
    type_frame.pack(fill=X, expand=True, pady=3)

    type_label = ttk.Label(type_frame, text="Type : ")
    type_label.pack(side=LEFT)

    type_values = ["Red", "White", "Rose", "Sparkling", "Other"]
    type_entry = ttk.Combobox(type_frame, values=type_values, state=READONLY)
    type_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    var_frame = ttk.Frame(input_frame)
    var_frame.pack(fill=X, expand=True, pady=3)

    var_label = ttk.Label(var_frame, text="Variety : ")
    var_label.pack(side=LEFT)

    var_entry = ttk.Entry(var_frame)
    var_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    price_frame = ttk.Frame(input_frame)
    price_frame.pack(fill=X, expand=True, pady=3)

    price_label = ttk.Label(price_frame, text="Price : ")
    price_label.pack(side=LEFT)

    price_entry = ttk.Entry(price_frame)
    price_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    quantity_frame = ttk.Frame(input_frame)
    quantity_frame.pack(fill=X, expand=True, pady=3)

    quantity_label = ttk.Label(quantity_frame, text="Quantity : ")
    quantity_label.pack(side=LEFT)

    quantity_entry = ttk.Entry(quantity_frame)
    quantity_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    notes_frame = ttk.Frame(input_frame)
    notes_frame.pack(fill=X, expand=True, pady=3)

    notes_label = ttk.Label(notes_frame, text="Quantity : ")
    notes_label.pack(side=LEFT)

    notes_entry = ttk.Entry(notes_frame)
    notes_entry.pack(side=LEFT, padx=(20,0), fill=X, expand=True)

    edit_wine_button = ttk.Button(add_main, text='Done', bootstyle=SUCCESS, command=edit_one)
    edit_wine_button.pack(side=LEFT, padx=20, pady=20, fill=X, expand=1)

    close_text_button = ttk.Button(add_main, text='Close', command=close, bootstyle=DANGER)
    close_text_button.pack(side=LEFT, padx=(0, 20), pady=20, fill=X, expand=1)

    selected = my_inv_tree.focus()
    values = my_inv_tree.item(selected, "values")

    wine_id = values[0]

    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT * FROM wines WHERE rowid=?", (wine_id,))
    wine_to_edit = c.fetchall()

    wine_to_edit = wine_to_edit[0]
    wine_to_edit = wine_to_edit[5]

    name_entry.insert(0, values[3])
    type_entry.set(values[1])
    var_entry.insert(0, values[2])
    price_entry.insert(0, values[4])
    quantity_entry.insert(0, values[5])
    notes_entry.insert(0, wine_to_edit)
    conn.commit()
    conn.close()

    edit.mainloop()

def remove_one():
    try:
        curItem = my_inv_tree.focus()
        item_data = (my_inv_tree.item(curItem))
        item_values = item_data['values']
        id_from_selection = str(item_values[0])

        MsgBox = messagebox.askquestion ('Delete Record','Are you sure you want to delete this record?',icon = 'warning', parent=inventory)
        if MsgBox == 'yes':


            conn = sqlite3.connect('winelist.db')
            c = conn.cursor()
            c.execute("DELETE from wines WHERE oid=" + id_from_selection)
            conn.commit()
            conn.close()

            my_inv_tree.delete(*my_inv_tree.get_children())
            query_database()
            my_tree.delete(*my_tree.get_children())
            query_sales_stock()
            messagebox.showinfo("Deleted!", "Your Wine Has Been Deleted!")

    except:
        pass    

######### NAVBAR FUNCTIONS
def inv():
    inventory.pack(fill=BOTH, expand=1, padx=20, pady=20)
    background.pack_forget()
    settings.pack_forget()
    reports.pack_forget()


def dash():
    background.pack(fill='both', expand=True)
    inventory.pack_forget()
    settings.pack_forget()
    reports.pack_forget()

def reports():
    reports.pack(fill='both', expand=True)
    inventory.pack_forget()
    background.pack_forget()
    settings.pack_forget()


def settings():
    settings.pack()
    background.pack_forget()
    reports.pack_forget()
    inventory.pack_forget()

###########  REPORTS FUNCTIONS  ######################
def graph_sel_dates_quantities():

    date_f = from_cal.entry.get()
    date_from = datetime.strptime(date_f, '%d/%m/%Y').date()

    date_t = to_cal.entry.get()
    date_to = datetime.strptime(date_t, '%d/%m/%Y').date()

    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sales')
    r = c.fetchall()

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

    if not names:
        messagebox.showinfo("No info!", "No sales in this period")    

    else: 
        plt.bar(range(len(sum)), values, tick_label=names)
        plt.gcf().autofmt_xdate()
        plt.ylabel("Quantities")
        plt.title("Wine Sales On Selected Dates")
        plt.tight_layout()
        plt.show()

def graph_hist():
    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute('SELECT * FROM sales')
    r = c.fetchall()

    wine_list = []
    wine_list.sort()

    conn.commit()
    conn.close()

    for i in r:
        d = i[1]
        d2 = d.split('-')
        sales_year = int(d2[0])

        year_sel = int(year_selection.get())
        if sales_year == year_sel:
            wine_list.append(i)

    sum = {}
    for item in wine_list:
        if not item[2] in sum:
            sum[ item[2] ] = 0
        sum[ item[2] ] += item[0]

    names = list(sum.keys())
    values = list(sum.values())

    if not names:
        messagebox.showinfo("No info!", "No sales in this period")    

    else: 
        plt.bar(range(len(sum)), values, tick_label=names)
        plt.gcf().autofmt_xdate()
        plt.ylabel("Quantities")
        plt.title("Wine Sales On Selected Dates")
        plt.tight_layout()
        plt.show()



############  SETTINGS FUNCTIONS  ######################
def export_data():
    MsgBox = messagebox.askquestion ('Export Data',"Make sure there are no other wines.csv or sales.csv files on the program's folder")
    if MsgBox == 'yes':
        MsgBox = messagebox.showinfo ('Success',"Check the program's folder for a wines.csv and sales.csv files")
        conn = sqlite3.connect('winelist.db')
        df = pd.read_sql_query("SELECT * FROM sales ", conn)
        df.to_csv(r'sales.csv')
        df = pd.read_sql_query("SELECT * FROM wines ", conn)
        df.to_csv(r'wines.csv')
        conn.commit()
        conn.close()
    else:
        pass 

def import_wines():
    MsgBox = messagebox.askquestion ('DELETE WINES','All existing wines will be deleted before importing the new wines. Are you sure you would like to proceed?', parent=settings)


    if MsgBox == 'yes':
        #try:
        conn = sqlite3.connect('winelist.db')
        c = conn.cursor()
        c.execute('DROP TABLE wines')

        c.execute("""CREATE TABLE if not exists wines (
        name text,
        type text,
        variety text,
        price real,
        quantity real,
        notes text)
        """)

        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 
        filename_wines = filedialog.askopenfilename(initialdir=desktop, title='Select CSV', filetypes=(("csv files", "*.csv"), ("all files", "*.*")), header=None)

        wines = pd.read_csv(filename_wines, names =['name', 'type', 'variety', 'price', 'quantity', 'notes'])
        # new_header2 = wines.iloc[0] #grab the first row for the header
        # wines = wines[0:] #take the data less the header row
        # wines.columns = new_header2 #set the header row as the df header
        wines.to_sql('wines', conn, if_exists='append', index=FALSE)

        conn.commit()
        conn.close()
        messagebox.showinfo("Success!", "Your Wines Have Been Updated! Please restart the application for the changes to take effect.")

        #except:
           #messagebox.showinfo("Error!", "Error while trying to import wines")

def import_sales():
    MsgBox = messagebox.askquestion ('DELETE SALES','All existing sales will be deleted before importing the new wines. Are you sure you would like to proceed?')

    if MsgBox == 'yes':
        try:
            conn = sqlite3.connect('winelist.db')
            c = conn.cursor()
            c.execute('DROP TABLE sales')
            c.execute("""CREATE TABLE if not exists sales (
            quantity real,
            date blob,
            drink text
            )
            """)

            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            settings.filename_sales = filedialog.askopenfilename(initialdir=desktop, title='Select CSV', filetypes=(("csv files", "*.csv"), ("all files", "*.*")))

            sales = pd.read_csv(settings.filename_sales, names =['quantity', 'date', 'drink'])
            new_header = sales.iloc[0] #grab the first row for the header
            sales = sales[1:] #take the data less the header row
            sales.columns = new_header #set the header row as the df header
            sales.to_sql('sales', conn, if_exists='append', index=FALSE)

            conn.commit()
            conn.close()
            messagebox.showinfo("Success!", "Your Sales Have Been Updated")
        except:
            messagebox.showinfo("Error!", "Please check that the file name is sales.csv and retry.")

# Insert wines to combobox
try:
    conn = sqlite3.connect('winelist.db')
    c = conn.cursor()
    c.execute("SELECT rowid, name, type, variety FROM wines")
    w_sorted = c.fetchall()
    w_sorted.sort(key=lambda a: a[2])
    wines_stock = []
    for i in w_sorted:
        wines_stock.append(str(i[2])+" ~ "+i[1]+" ~ "+i[3])
    conn.commit()
    conn.close()
except:
   pass 

app = ttk.Window()
app.title("Winelist")
app.update()
app.state("zoomed")
app.style.theme_use("superhero")

navbar = ttk.Frame(app)
navbar.pack(fill='x', pady=(40, 20))

menuButtons = ttk.Frame(navbar, bootstyle=PRIMARY)
menuButtons.pack(fill=X, pady=0, padx=20)

menuButton3 = ttk.Button(menuButtons, text='Settings', width=17, command=settings)
menuButton3.pack(side=RIGHT, pady=0, padx=(0))

menuButton2 = ttk.Button(menuButtons, text='Reports', width=17, command=reports)
menuButton2.pack(side=RIGHT, padx=0)

menuButton1 = ttk.Button(menuButtons, text='Inventory', width=17, command=inv)
menuButton1.pack(side=RIGHT, pady=0, padx=0)

menuButton0 = ttk.Button(menuButtons, text='Dashboard', width=17, command=dash)
menuButton0.pack(side=RIGHT, pady=0, padx=0)

winelist_label = ttk.Label(menuButtons, text="WINELIST", bootstyle=PRIMARY)
winelist_label.pack(side=LEFT, fill=Y, ipadx=10)

background = ttk.Frame(app)
background.pack(fill='both', expand=True)

sale_and_search_frame = ttk.Frame(background)
sale_and_search_frame.pack(padx=20, pady=20, fill=BOTH, side=LEFT, anchor=N)

recordSaleLabelFrame = ttk.LabelFrame (sale_and_search_frame,text='Record Sales')
recordSaleLabelFrame.pack(fill=BOTH, side=LEFT, anchor=N)

s = ttk.Style()
s.map('TCombobox', fieldbackground=[('readonly', 'white')])

cal = ttk.DateEntry(master=recordSaleLabelFrame, dateformat='%d/%m/%Y' )
cal.pack(padx=20, pady=20)

progg_and_label = ttk.Frame(recordSaleLabelFrame)
progg_and_label.pack(pady=(0,20), fill=X, padx=20)

quan_label = tk.StringVar()
q_label = ttk.Label(progg_and_label, textvariable=quan_label)
q_label.pack(side=LEFT, padx=(0,10))

progg = ttk.Progressbar(progg_and_label, maximum=10)
progg.pack(side=RIGHT, fill=X, expand=1)

bottle_sold_btn = ttk.Button(recordSaleLabelFrame, text='Bottle', bootstyle=SUCCESS, width=15, command=lambda m="Bottle": sale(m))
bottle_sold_btn.pack(padx=(20), pady=(0), fill=X)

glass_sold_btn = ttk.Button(recordSaleLabelFrame, text='Glass', bootstyle=PRIMARY, width=15, command=lambda m="Glass": sale(m))
glass_sold_btn.pack(padx=(20), pady=20, fill=X)

hist_label = ttk.Label(recordSaleLabelFrame, text='Sale History')
hist_label.pack(padx=20, fill=X)

hist_listbox = Listbox(recordSaleLabelFrame, width=35)
hist_listbox.pack(fill=X, pady=(5,20), padx=20)

tree_frame = ttk.Frame(background)
tree_frame.pack(fill='both', expand=1, padx=20, pady=20, side=RIGHT)

tree_frame2 = ttk.Frame(tree_frame)
tree_frame2.pack(pady=0, padx=0, side=LEFT,fill='both', expand=1)

tree_scroll = ttk.Scrollbar(tree_frame2)
tree_scroll.pack(side=RIGHT, fill='y', pady=0)

s = ttk.Style()
s.configure('Treeview.Heading',font=('Calibri', 13, 'bold'), height=15)
s.configure('Treeview', rowheight=35, font=('Calibri', 15 ))

my_tree = ttk.Treeview(tree_frame2, yscrollcommand=tree_scroll.set, selectmode='extended')
my_tree.pack(fill='both', expand=1)
tree_scroll.config(command=my_tree.yview)

my_tree['columns'] = ('ID', 'Type', 'Variety', 'Name', 'Quantity')

my_tree.column('#0', width=0, stretch=NO)
my_tree.column("ID", width=40, stretch=NO, anchor=W)
my_tree.column("Type", anchor=CENTER)
my_tree.column("Variety", anchor=CENTER)
my_tree.column("Name", anchor=CENTER)
my_tree.column("Quantity", anchor=CENTER, width=60)

my_tree.heading("#0", text="", anchor=CENTER)
my_tree.heading("ID", text="ID", anchor=W)
my_tree.heading("Type", text="Type", anchor=CENTER)
my_tree.heading("Variety", text="Variety", anchor=CENTER)
my_tree.heading("Name", text="Name", anchor=CENTER)
my_tree.heading("Quantity", text="Quantity", anchor=CENTER)

my_tree.tag_configure('evenrow',background='#263D51')

s = ttk.Style()
s.configure('Treeview.Heading',font=('Calibri', 13, 'bold'), height=15)
s.configure('Treeview', rowheight=35, font=('Calibri', 15 ))

delete_button = ttk.Button (recordSaleLabelFrame, text='Delete', bootstyle=DANGER, command=delete_sale)
delete_button.pack(anchor=W, padx=20, pady=(0,20), ipadx=15)

###############  INVENTORY  ############################
inventory = ttk.Frame(app)

inv_tree_frame = ttk.Frame(inventory)
inv_tree_frame.pack(fill='both', expand=1, padx=20, pady=(0,10))

inv_tree_frame2 = ttk.Frame(inv_tree_frame)
inv_tree_frame2.pack(pady=0, padx=0, side=LEFT,fill='both', expand=1)

inv_tree_scroll = ttk.Scrollbar(inv_tree_frame2)
inv_tree_scroll.pack(side=RIGHT, fill='y', pady=0)

s = ttk.Style()
s.configure('Treeview.Heading',font=('Calibri', 13, 'bold'), height=15)
s.configure('Treeview', rowheight=35, font=('Calibri', 15 ))

my_inv_tree = ttk.Treeview(inv_tree_frame2, yscrollcommand=inv_tree_scroll.set, selectmode='extended')
my_inv_tree.pack(fill='both', expand=1)
inv_tree_scroll.config(command=my_inv_tree.yview)

my_inv_tree['columns'] = ('ID', 'Type','Variety', 'Name', 'Price', 'Quantity')

my_inv_tree.column('#0', width=0, stretch=NO)
my_inv_tree.column("ID", width=0, stretch=NO)
my_inv_tree.column("Type", anchor=CENTER)
my_inv_tree.column("Variety", anchor=CENTER)
my_inv_tree.column("Name", anchor=CENTER)
my_inv_tree.column("Price", anchor=CENTER)
my_inv_tree.column("Quantity", anchor=CENTER)

my_inv_tree.heading("#0", text="", anchor=CENTER)
my_inv_tree.heading("ID", text="ID", anchor=CENTER)
my_inv_tree.heading("Type", text="Type", anchor=CENTER)
my_inv_tree.heading("Variety", text="Variety", anchor=CENTER)
my_inv_tree.heading("Name", text="Name", anchor=CENTER)
my_inv_tree.heading("Price", text="Price", anchor=CENTER)
my_inv_tree.heading("Quantity", text="Quantity", anchor=CENTER)

my_inv_tree.tag_configure('evenrow',background='#263D51')

my_inv_tree.bind("<ButtonRelease-1>", select_record)

notes_frame = ttk.Frame(inventory)
notes_frame.pack(pady=20, padx=20, fill=X)

notes_lbl_title = ttk.Label(notes_frame, text="Notes:")
notes_lbl_title.pack(anchor=W)

notes_var = tk.StringVar()
notes_lbl = ttk.Label(notes_frame, textvariable=notes_var)
notes_lbl.pack(anchor=W)
notes_var.set("Click on a drink to see saved notes.")

button_frame = ttk.Frame(inventory)
button_frame.pack(pady=(20, 40), padx=20, fill=X)

add_button = ttk.Button(button_frame, text='Add', width=25, command=add_record, bootstyle=PRIMARY)
add_button.pack(side=LEFT, fill=X)

update_button = ttk.Button(button_frame, text='Edit', width=25, command=update_record, bootstyle=PRIMARY)
update_button.pack(side=LEFT, padx=20, fill=X)

remove_one_button = ttk.Button(button_frame, text='Remove', width=25, command=remove_one, bootstyle=DANGER)
remove_one_button.pack(side=LEFT, fill=X)

##############  REPORTS  ############################
reports = ttk.Frame(app)

graphs_container1 = ttk.LabelFrame(reports, text="Year Report")
graphs_container1.pack(padx=20, pady=(50,20))

graphs_container2 = ttk.LabelFrame(reports, text="Selected Dates Report")
graphs_container2.pack(padx=20, pady=20)

dates_and_labels2 = ttk.Frame(graphs_container1)
dates_and_labels2.pack()

year_frame = ttk.Frame(dates_and_labels2)
year_frame.pack()

from_label = ttk.Label(year_frame, text='Year :')
from_label.pack(pady=20, padx=20, side=LEFT)

years = []

d = datetime.now()
d = str(d).split(" ")

current_year = d[0]
current_year = current_year.split("-")
current_year = int(current_year[0])
years.append(current_year)

while current_year > 2010:
    years.append(current_year)
    current_year = current_year-1

year_selection = ttk.Combobox(year_frame, values=years, state="readonly", width=40 )
year_selection.pack(padx=(0, 20), pady=20, side=LEFT)
year_selection.set(years[0])

wine_graph_hist_button = ttk.Button(year_frame, text="Create", width=18, command=graph_hist)
wine_graph_hist_button.pack(padx=20, pady=20, side=LEFT)

dates_and_labels = ttk.Frame(graphs_container2)
dates_and_labels.pack(pady=20)

from_label = ttk.Label(dates_and_labels, text='From :')
from_label.pack(side=LEFT, padx=(20, 20))

from_cal = ttk.DateEntry(dates_and_labels, dateformat='%d/%m/%Y')
from_cal.pack(side=LEFT)

to_label = ttk.Label(dates_and_labels, text='To :')
to_label.pack(side=LEFT, padx=(20,20))

to_cal = ttk.DateEntry(dates_and_labels, dateformat='%d/%m/%Y')
to_cal.pack(side=LEFT, padx=(0,20))

create_button = ttk.Button(dates_and_labels, text="Create", width=17, command=graph_sel_dates_quantities)
create_button.pack(side=LEFT, pady=20, padx=20)

##############  SETTINGS  ############################
settings = ttk.Frame(app)

settings_frame = ttk.Frame(settings)
settings_frame.pack()

label = ttk.Label(settings_frame, text="App Settings", font=('Calibri', 18))
label.pack(padx=20, pady=20)

exp_sales_button = ttk.Button (settings_frame, text='Export Data', width=20, command=export_data)
exp_sales_button.pack(anchor=W, padx=40, pady=20)

imp_wines_button = ttk.Button (settings_frame, text='Import Wines', width=20, command=import_wines)
imp_wines_button.pack(anchor=W, padx=40, pady=20)

imp_sales_button = ttk.Button (settings_frame, text='Import Sales', width=20, command=import_sales)
imp_sales_button.pack(anchor=W, padx=40, pady=0)


my_inv_tree.bind("<ButtonRelease-1>", select_record_notes)
hist_list_update()
my_tree.bind("<ButtonRelease-1>", sel_item_for_quanity)
query_sales_stock()
query_database()
low_quants()
app.mainloop()