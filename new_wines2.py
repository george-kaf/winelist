from tkinter import *
from itertools import count
from tkinter import ttk
import sqlite3
from tkinter import messagebox
from PIL import ImageTk, Image  
import matplotlib.pyplot as plt
from tkcalendar import *
import tkinter.font as font
from matplotlib import dates as mpl_dates
from datetime import *

splash_app = Tk()
splash_app.title('Winelist')
splash_app.state('zoomed')

splash_frame = Frame(splash_app, background='#751824')
splash_frame.pack(fill='both', expand=True, anchor=S, side=TOP)

splash_frame2 = Frame(splash_frame, background='#751824')
splash_frame2.pack(fill='both', expand=True, anchor=S, side=TOP, pady=100, padx=100)

splash_label = Label(splash_frame2, text='Welcome to', background='#751824', font=("Great Vibes", 60), fg='white' )
splash_label.pack(pady=0)

img = ImageTk.PhotoImage(Image.open("C://Users//Kafetzo//Desktop//winelist_copy//home_logo.png"))
panel = Label(splash_frame2, image = img)
panel.pack(pady=0, anchor=CENTER)

def main_window():
    splash_app.destroy()
    app = Tk()
    app.title("Winelist")
    app.state('zoomed') 

    # CREATE TABLES
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
                my_tree.insert(parent='', index='end', iid=count, text='', values=(record[1], record[2], record[0], record[4], record[5]), tags=('evenrow',))
            else:
                my_tree.insert(parent='', index='end', iid=count, text='', values=(record[1], record[2], record[0], record[4], record[5]), tags=('oddrow',))

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
        name_entry.delete(0, END)
        type_entry.delete(0, END)
        id_entry.delete(0, END)
        price_entry.delete(0, END)
        quantity_entry.delete(0, END)

        selected = my_tree.focus()
        values = my_tree.item(selected, "values")

        name_entry.insert(0, values[0])
        type_entry.insert(0, values[1])
        id_entry.insert(0, values[2])
        price_entry.insert(0, values[3])
        quantity_entry.insert(0, values[4])

    def update_record():
        MsgBox = messagebox.askquestion ('Update Wine','Are you sure about the changes?')
        if MsgBox == 'yes':
            selected = my_tree.focus()
            my_tree.item(selected, text='', values=(name_entry.get(),type_entry.get(), id_entry.get(), price_entry.get(), quantity_entry.get(),))

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

            #clear entry boxes
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
        pass

    def import_data():
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
        plt.bar(dates_list, quantities, width=6)
        plt.gcf().autofmt_xdate()
        date_format = mpl_dates.DateFormatter('%b-%d-%Y')
        plt.gca().xaxis.set_major_formatter(date_format)
        plt.ylim(0, 11)
        plt.xlabel("Dates")
        plt.ylabel("Quantities")
        plt.title("Wine Graph")
        plt.tight_layout()
        plt.show()

    def graph_sel():

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

    frame_sale.pack(pady=20, padx=0, fill="both", expand=True)
    frame_inv.pack(pady=20, padx=0, fill="both", expand=True)

    notebook.add(frame_sale, text='Sales')
    notebook.add(frame_inv, text='Inventory')

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
    combo_lbl_frame.pack(side=LEFT, padx=20, pady=20, fill='x', expand=True)

    input_frame2 = Frame(frame_top3, background='white')
    input_frame2.pack(fill='both', expand=True)

    sales_input_frame = Frame(frame_top_left, background='#F5F5F5')
    sales_input_frame.pack(side=TOP, fill='both', expand=True, pady=20)

    sales_input_frame2 = Frame(sales_input_frame, background='#F5F5F5')
    sales_input_frame2.pack(side=TOP, pady=40)

    combo_lbl = Label(combo_lbl_frame, text="Maître Corbeau - Stock Management and Sales Analysis", bg='white', fg='grey3', font=('Cambria', 23))
    combo_lbl.pack(padx=40, side=LEFT)

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

    cal = DateEntry(sales_input_frame2, background='white',
                foreground='black', borderwidth=2, width=25, style='my.DateEntry', state = "readonly", locale='el_GR', date_pattern='d/M/yy', font=('Cambria', 15))
    cal.pack(pady=5, fill='x')

    sales_but = Button(sales_input_frame2, text="Wines Sold", command=sale, background='#751824',fg='white', font=('Cambria',13, 'bold'))
    sales_but.pack(pady=20, ipadx=14, anchor=CENTER)



    #export_btn = Button(input_button_frame, text='Export Data', width=16, background='lightgrey',fg='black', font=('Cambria',13, 'bold'), command=export_data)
    ##export_btn.grid(column=0, row=0, sticky=W, ipadx=20)

    #import_btn = Button(input_button_frame, text='Import Data', width=16, background='lightgrey',fg='black', font=('Cambria',13, 'bold'), command=import_data)
    ##import_btn.grid(column=1, row=0, pady=0, sticky=W, padx=20)

    hist_tree_frame = Frame(frame_top4, background='white')
    hist_tree_frame.pack(pady=0, padx=0, fill='both', expand=True)

    hist_tree_frame2 = Frame(hist_tree_frame, bg='white')
    hist_tree_frame2.pack(pady=0, padx=20, side=TOP, fill='both', expand=True)
    hist_tree_scroll = Scrollbar(hist_tree_frame2)
    hist_tree_scroll.pack(side=LEFT, fill='y', pady=0)

    delete_sale_button = Button(combo_lbl_frame, text='Delete Selected Sale', command=delete_sale, height=1, background='#751824',fg='white', font=('Cambria',13, 'bold'))
    delete_sale_button.pack(pady=0, padx=20, ipadx=20, side=RIGHT, anchor=E)

    my_hist_tree = ttk.Treeview(hist_tree_frame2, yscrollcommand=hist_tree_scroll.set, selectmode='extended')
    my_hist_tree.pack(pady=0, padx=0, side=LEFT, expand=True, fill='both')


    hist_tree_scroll.config(command=my_hist_tree.yview)

    my_hist_tree['columns'] = ('ID', 'Date', 'Name', 'Quantity')

    my_hist_tree.column('#0', width=0, stretch=NO)
    my_hist_tree.column("ID", anchor=CENTER, width=50)
    my_hist_tree.column("Date", anchor=CENTER, width=140)
    my_hist_tree.column("Name", anchor=CENTER, width=400)
    my_hist_tree.column("Quantity", anchor=CENTER, width=50)

    my_hist_tree.heading("#0", text="", anchor=CENTER)
    my_hist_tree.heading("ID", text="ID", anchor=CENTER)
    my_hist_tree.heading("Date", text="Date", anchor=CENTER)
    my_hist_tree.heading("Name", text="Name", anchor=CENTER)
    my_hist_tree.heading("Quantity", text="Quantity", anchor=CENTER)

    my_hist_tree.tag_configure('oddrow', background= 'white', foreground='black', font=('Cambria', 16))
    my_hist_tree.tag_configure('evenrow',background='#EEE9ED', foreground='black', font=('Cambria', 16))

    myFont = font.Font(family=('Cambria'))

    from_to_cal_frame = Frame(frame_top_right, background='#FFFFFF')
    from_to_cal_frame.pack(pady=20)

    graph_label = Label(from_to_cal_frame, text='Select Info For Your Graph', background='#FFFFFF', font=('Cambria', 19, 'bold'))
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

    wine_graph_button = Button(right_button_frame, text="Selected Graph", width=21, background='#751824', command=graph_sel,fg='white', font=('Cambria',13, 'bold'))
    wine_graph_button.pack(pady=10, padx=10, side=LEFT, fill='x', expand=True)

    wine_graph_hist_button = Button(right_button_frame, text="Yearly Graph", width=21, command=graph_hist, background='#751824',fg='white', font=('Cambria',13, 'bold'))
    wine_graph_hist_button.pack(pady=0, padx=10, side=RIGHT, fill='x', expand=True)

    ###################### INVENTORY  ###################
    s.configure('Treeview.Heading', background="#58181F", foreground='white', font=('Cambria', 15, 'bold'), height=15)
    s.configure('Treeview', rowheight=30)

    tree_frame = Frame(frame_inv, background='white')
    tree_frame.pack(pady=30, padx=30, side=LEFT, fill='both', expand=True)

    tree_frame2 = Frame(tree_frame)
    tree_frame2.pack(pady=0, padx=0, side=LEFT, fill='both', expand=True)
    tree_scroll = Scrollbar(tree_frame2)
    tree_scroll.pack(side=LEFT, fill='y', pady=0)

    my_tree = ttk.Treeview(tree_frame2, yscrollcommand=tree_scroll.set, selectmode='extended')
    my_tree.pack(pady=0, padx=0, side=LEFT, expand=True, fill='both')

    tree_scroll.config(command=my_tree.yview)

    my_tree['columns'] = ('Name', 'Type', 'ID', 'Price', 'Quantity')

    my_tree.column('#0', width=0, stretch=NO)
    my_tree.column("Name", anchor=W, width=400)
    my_tree.column("Type", anchor=W)
    my_tree.column("ID", anchor=CENTER)
    my_tree.column("Price", anchor=CENTER)
    my_tree.column("Quantity", anchor=CENTER)

    my_tree.heading("#0", text="", anchor=W)
    my_tree.heading("Name", text="Name", anchor=W)
    my_tree.heading("Type", text="Type", anchor=W)
    my_tree.heading("ID", text="ID", anchor=CENTER)
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

    id_label = Label(input_frame, text="ID: (Always leave empty)", background='#58181F', foreground='white')
    id_label.pack(pady=0, side=TOP)
    id_label.config(font=('Cambria',13, 'bold'))

    id_entry = Entry(input_frame, font=('Cambria', 15))
    id_entry.pack(pady=10, side=TOP, ipady=6, fill='x', padx=10)

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

    my_tree.bind("<ButtonRelease-1>", select_record)

    query_history()
    query_database()

splash_app.after(3000, main_window)

mainloop()
