from itertools import count
from tkinter import *
from tkinter import ttk
import sqlite3
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from tkcalendar import *

root = Tk()

windowWidth = root.winfo_reqwidth()
windowHeight = root.winfo_reqheight()

positionRight = int(root.winfo_screenwidth()/2 - windowWidth/2)
positionDown = int(root.winfo_screenheight()/2 - windowHeight/2)

root.title('Winelist')
root.geometry("1200x890")


#Database###################

#create or connect to database
conn = sqlite3.connect('tree_crm.db')

#create a cursor
c = conn.cursor()

#create a table
c.execute("""CREATE TABLE if not exists wines (
name text,
type text,
id integer,
price integer,
quantity integer)
""")

#commit changes
conn.commit()

#close connection
conn.close()

########## Sales Database############

#create or connect to database
conn = sqlite3.connect('tree_crm.db')

#create a cursor
c = conn.cursor()

#create a table
c.execute("""CREATE TABLE if not exists sales (
quantity integer,
date text,
name text
)
""")
#commit changes
conn.commit()

#close connection
conn.close()

############# QUERY DATABASE #####################

def query_database():
    #create or connect to database
    conn = sqlite3.connect('tree_crm.db')

    #create a cursor
    c = conn.cursor()

    c.execute("SELECT rowid, * FROM wines")
    records = c.fetchall()
    
    #add our data to the screen
    global count
    count = 0

    for record in records:
        if count % 2 ==0:
            my_tree.insert(parent='', index='end', iid=count, text='', values=(record[1], record[2], record[0], record[4], record[5]), tags=('evenrow',))
        else:
            my_tree.insert(parent='', index='end', iid=count, text='', values=(record[1], record[2], record[0], record[4], record[5]), tags=('oddrow',))
        #increment counter
        count +=1

    #commit changes
    conn.commit()

    #close connection
    conn.close()

# add style
style = ttk.Style()

# pick a theme

style.theme_use('clam')

#configure treeviw colours

style.configure('Treview')

# change selected colour
style.map('Treview')


######## CREATE NOTEBOOK FOR TABS
noteb = ttk.Notebook(root) 

#### TAB 1
t1 = Frame(noteb) 

#### TAB 2
t2 = Frame(noteb) 

#### NAME AND PACK TABS
noteb.add(t1, text ='Statistics') 
noteb.add(t2, text ='Inventory') 
noteb.pack(pady=55, expand=True) 

# treeview frame
tree_frame = Frame(t2)
tree_frame.pack(pady=10, padx=0, side=TOP, expand=True)

#create a treeview scrollbar
tree_scroll = Scrollbar(tree_frame)
tree_scroll.pack(side=RIGHT, fill=Y)

#create the treeview
my_tree = ttk.Treeview(tree_frame, yscrollcommand=tree_scroll.set, selectmode='extended', height=25)
my_tree.pack(pady=10, padx=0, fill='both', side=TOP)

#configure scrollbar
tree_scroll.config(command=my_tree.yview)

#define our columns
my_tree['columns'] = ('Name', 'Type', 'ID', 'Price', 'Quantity')

#format our columns
my_tree.column('#0', width=0, stretch=NO)
my_tree.column("Name", anchor=W, width=270)
my_tree.column("Type", anchor=W, width=200)
my_tree.column("ID", anchor=CENTER, width=120)
my_tree.column("Price", anchor=CENTER, width=210)
my_tree.column("Quantity", anchor=CENTER, width=210)

#create headings
my_tree.heading("#0", text="", anchor=W)
my_tree.heading("Name", text="Name", anchor=W)
my_tree.heading("Type", text="Type", anchor=W)
my_tree.heading("ID", text="ID", anchor=CENTER)
my_tree.heading("Price", text="Price", anchor=CENTER)
my_tree.heading("Quantity", text="Quantity", anchor=CENTER)

# create  striped row tags
my_tree.tag_configure('oddrow', background= 'white')
my_tree.tag_configure('evenrow', background='pink')

# add record entry boxes
data_frame = LabelFrame(t2, text="Information")
data_frame.pack(pady=0, padx=20, side=TOP)

name_label = Label(data_frame, text="Name")
name_label.grid(row=0, column=0, padx=10, pady=10)
name_entry = ttk.Entry(data_frame)
name_entry.grid(row=0, column=1, padx=10, pady=10)

type_label = Label(data_frame, text="Type")
type_label.grid(row=0, column=2, padx=10, pady=10)
type_entry = ttk.Entry(data_frame)
type_entry.grid(row=0, column=3, padx=10, pady=10)

id_label = Label(data_frame, text="ID")
id_label.grid(row=0, column=4, padx=10, pady=10)
id_entry = ttk.Entry(data_frame)

id_entry.grid(row=0, column=5, padx=10, pady=10)

price_label = Label(data_frame, text="Price")
price_label.grid(row=0, column=6, padx=10, pady=10)
price_entry = ttk.Entry(data_frame)
price_entry.grid(row=0, column=7, padx=10, pady=10)

quantity_label = Label(data_frame, text="Quantity")
quantity_label.grid(row=0, column=8, padx=10, pady=10)
quantity_entry = ttk.Entry(data_frame)
quantity_entry.grid(row=0, column=9, padx=10, pady=10)

id_caution_label = Label(data_frame, text="*ALWAYS LEAVE ID BOX EMPTY !")
id_caution_label.grid(row=1, column= 5)
#remove one record
def remove_one():
    x = my_tree.selection()[0]
    my_tree.delete(x)

        #create or connect to database
    conn = sqlite3.connect('tree_crm.db')

    #create a cursor
    c = conn.cursor()

    #delete from database
    c.execute("DELETE from wines WHERE oid=" + id_entry.get())
    
    #commit changes
    conn.commit()

    #close connection
    conn.close()

    #clear entry boxes
    clear_entries()

    #add a little message box for fun
    messagebox.showinfo("Deleted!", "Your Wine Has Been Deleted!")



#clear entry boxes
def clear_entries():
    name_entry.delete(0, END)
    type_entry.delete(0, END)
    id_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)
    
#select record
def select_record(e):
    #clear entry boxes
    name_entry.delete(0, END)
    type_entry.delete(0, END)
    id_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)

    #grab record number
    selected = my_tree.focus()
    #grab record values
    values = my_tree.item(selected, "values")

    #output to entry boxes
    name_entry.insert(0, values[0])
    type_entry.insert(0, values[1])
    id_entry.insert(0, values[2])
    price_entry.insert(0, values[3])
    quantity_entry.insert(0, values[4])

def update_record():
    #grab the record numer
    selected = my_tree.focus()
    my_tree.item(selected, text='', values=(name_entry.get(),type_entry.get(), id_entry.get(), price_entry.get(), quantity_entry.get(),))

    #update the databse
    #create or connect to database
    conn = sqlite3.connect('tree_crm.db')

    #create a cursor
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

    #commit changes
    conn.commit()

    #close connection
    conn.close()

    #clear entry boxes
    name_entry.delete(0, END)
    type_entry.delete(0, END)
    id_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)

#add new record to database
def add_record():
    conn = sqlite3.connect('tree_crm.db')

    #create a cursor
    c = conn.cursor()

    #add new record
    c.execute("INSERT INTO wines VALUES (:name, :type, :id, :price, :quantity)",
    {
        'name':name_entry.get(),
        'type':type_entry.get(),
        'id':id_entry.get(),
        'price':price_entry.get(),
        'quantity':quantity_entry.get(),
    }
     )

    #commit changes
    conn.commit()

    #close connection
    conn.close()   

    #clear entry boxes
    name_entry.delete(0, END)
    type_entry.delete(0, END)
    id_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)

    #clear the treeview table
    my_tree.delete(*my_tree.get_children())

    #run to pull date from database from start
    query_database()

###### GRAPH FUNCTION
def graph():

  #create or connect to database
  conn = sqlite3.connect('tree_crm.db')
  c = conn.cursor()
  c.execute('SELECT date, quantity FROM sales WHERE name=?', (combo.get(),))
  results = c.fetchall()
  dates = []
  quantities = []

  for i in results:
    dates.append(i[0])
    quantities.append(i[1])
  
    # plt.bar to plot a bar graph
  # with given values
  plt.bar(dates, quantities, width=0.5)
  
  # Setting count of values in
  # y-axis
  plt.ylim(0, 15)
  
  # setting xlabel of graph
  plt.xlabel("Dates")
  # setting ylabel of graph
  plt.ylabel("Quantities")
  # setting tile of graph
  plt.title("Wine Graph")
  # show() method to display the graph
  plt.show()

  conn.commit()
  conn.close()

#####  FUNCTION TO DELETE ITEM IN HISTORY
def delete_sale():
    global records
    delete_selected_wine = listb.get(listb.curselection())
    idToDelete = delete_selected_wine[3]+delete_selected_wine[4]+delete_selected_wine[5]
    conn = sqlite3.connect('tree_crm.db')
    c = conn.cursor()
    c.execute("DELETE from sales WHERE oid=?", (idToDelete,))

    conn.commit()
    conn.close()
    listb.delete(0, END)
    query_history()


#add buttons 
button_frame = Frame(t2)
button_frame.pack(pady=0, padx=10, side=TOP )

add_button = ttk.Button(button_frame, text='Add Wine', command=add_record, width=38)
add_button.grid(row=0, column=0, padx=10 , pady=30)

update_button = ttk.Button(button_frame, text='Update Wine', command=update_record, width=38)
update_button.grid(row=0, column=1, padx=10, pady=30)

remove_one_button = ttk.Button(button_frame, text='Remove Selected', command=remove_one, width=38)
remove_one_button.grid(row=0, column=2, padx=10,  pady=30)

select_record_button = ttk.Button(button_frame, text='Clear Text', command=clear_entries, width=38)
select_record_button.grid(row=0, column=3, padx=10,  pady=30)

#bind the treeview
my_tree.bind("<ButtonRelease-1>", select_record)

#run to pull date from database from start
query_database()

####################  SALES   #####################################
last_sale = []

    # SALE FUNCTION
def sale():
    global last_sale 
    #create a connectiont to the db
    conn = sqlite3.connect('tree_crm.db')
    #create a cursor
    c = conn.cursor()
    #add new sale
    c.execute("INSERT INTO sales (quantity, name, date) VALUES (?, ?, ?)", (tkScale.get(), combo.get(), cal.get()))
    #commit changes
    conn.commit()
    #close connection
    conn.close()  
    # QUERY LISTBOX SALE HISTORY
    listb.delete(0,END)
    query_history()

# GET DATA FOR COMBO BOX TO CHOOSE
#create or connect to database
conn = sqlite3.connect('tree_crm.db')
#create a cursor
c = conn.cursor()
# Get type 
c.execute("SELECT name, type FROM wines")
wines_stock = []
for i in c.fetchall():
    wines_stock.append(str(i[1])+" - "+i[0])
#commit changes
conn.commit()
#close connection
conn.close()

    #############  GET SALE HISTORY
def query_history():
    # GET DATA FOR LISTBOX HISTORY
    conn = sqlite3.connect('tree_crm.db')
    c = conn.cursor()
    c.execute("SELECT rowid, quantity, date, name FROM sales")
    wine_records = c.fetchall()
    records = []
    records.sort(reverse=True)
    for r in wine_records:
        records.append("ID:"+str(r[0])+"      "+str(r[2])+"        -        "+str(r[3])+"  =  "+str(r[1]))
    for record in records:
        x=0
        listb.insert(x,str(record))
        x+1
    conn.commit()
    conn.close()

#### FRAME FOR LISTBOX
frame1 = LabelFrame(t1, text="Record A Sale")
frame1.pack(fill='both', padx=20, pady=30)

##### FRAME FOR TOP THINGS
frame_top = Frame(frame1)
frame_top.pack(side=LEFT, padx=20)

#### FRAME FOR LOGO
logo_frame = Frame(frame1)
logo_frame.pack(side=RIGHT, padx=20)

load= Image.open("home_logo.png")
render = ImageTk.PhotoImage(load)
img = Label(logo_frame, image=render)
img.pack()


#LISTBOX FOR HISTORY
listb = Listbox(frame_top, width=70, height=15)
conn = sqlite3.connect('tree_crm.db')
c = conn.cursor()
c.execute("SELECT rowid, quantity, date, name FROM sales")
wine_records = c.fetchall()
records = []
records.sort(reverse=True)
for r in wine_records:
    records.append("ID:"+str(r[0])+"      "+str(r[2])+"        -        "+str(r[3])+"  =  "+str(r[1]))
for record in records:
    x=0
    listb.insert(x,str(record))
    x+1
conn.commit()
conn.close()
listb.pack(padx=60, pady=50, side=BOTTOM)

# COMBO BOX TO SELECT WINE
combo = ttk.Combobox(frame_top, values=wines_stock, state = "readonly", width=70)
combo.set("Pick an Option")
combo.pack(pady=10, padx=0, side=TOP)

# SCROLLBAR TO CHOSE QUANTITY FOR DB
tkScale = Scale(frame_top, from_=0, to=10, orient=HORIZONTAL, length=440)
tkScale.pack(pady=20, padx=20,side=TOP)

# CALENDAR TO CHOSE DATE FOR DB
cal = DateEntry(frame_top, width=70, background='darkblue',
            foreground='white', borderwidth=2, locale='en_UK', date_pattern='dd/MM/yyyy')
cal.pack(pady=10, padx=20, side=TOP)

#### FRAME FOR GRAPHS
button_frame = Frame(frame_top)
button_frame.pack(side=TOP, pady=20)

### FRAME FOR DELETE BUTTON
button_frame2 = Frame(frame_top)
button_frame2.pack(side=TOP, pady=20)

# BUTTON TO RECORD A SALE FOR DB
sales_but = ttk.Button(button_frame, text="Wines Sold", command=sale, width=30)
sales_but.pack(pady=0, padx=17, side=LEFT)

graph_button = ttk.Button(button_frame, text='Graph', command=graph, width=30)
graph_button.pack(pady=0, padx=17, side=RIGHT)

delete_sale_button = ttk.Button(button_frame2, text='Delete Selected Sale', command=delete_sale, width=70)
delete_sale_button.pack(pady=0, padx=20, side=BOTTOM)

root.mainloop()
