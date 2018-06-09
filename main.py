import tkinter as tk
from service import *
from DBhelper import DBhelper


def click_event():
    global my_rases
    global all_rases
    global yscroll
    global db_helper
    print("click")
    db_helper = DBhelper()
    prev_all_rases = db_helper.get("rase")
    print(time_away.get())
    print(city_from.get(city_from.curselection()))
    print(city_to.get(city_to.curselection()))
    print(company.get())
    print(plane.get())
    t_away = time_away.get()
    c_from = city_from.get(city_from.curselection())
    c_to = city_to.get(city_to.curselection())
    com = company.get()
    pl = plane.get()
    main(t_away, c_from, c_to, com, pl)
    all_rases = tk.Listbox(root, width=90, height=10)
    all_rases.grid(row=6, column=1)

    yscroll = tk.Scrollbar(command=all_rases.yview, orient=tk.VERTICAL)
    yscroll.grid(row=6, column=2, sticky='ns')
    all_rases.configure(yscrollcommand=yscroll.set)

    db_helper = DBhelper()
    my_rases = db_helper.get("rase")
    print(my_rases)
    i = 0
    while i < len(my_rases) - 1:
        item_rase = []
        for it in my_rases[i]:
            item_rase.append(copy.deepcopy(str(it)))
        if prev_all_rases[i][1] != my_rases[i][1]:
            all_rases.insert(tk.END, str(item_rase))
            all_rases.itemconfig(i, {'bg': 'yellow'})
        else:
            all_rases.insert(tk.END, str(item_rase))
        i += 1
    item_rase = []
    for it in my_rases[i]:
        item_rase.append(copy.deepcopy(str(it)))
    all_rases.insert(tk.END, str(item_rase))
    all_rases.itemconfig(i, {'bg': 'light green'})

    lines = len(my_rases)
    all_rases.yview_scroll(lines, 'units')


root = tk.Tk()
tk.Label(root, text="Время вылета", relief=tk.RIDGE, anchor='s', width=12).grid(row=0)
tk.Label(root, text="Точка вылета", relief=tk.RIDGE, anchor='s', width=12).grid(row=1)
tk.Label(root, text="Точка прилета", relief=tk.RIDGE, anchor='s', width=12).grid(row=2)
tk.Label(root, text="Компания", relief=tk.RIDGE, anchor='s', width=12).grid(row=3)
tk.Label(root, text="Самолет", relief=tk.RIDGE, anchor='s', width=12).grid(row=4)
tk.Label(root, text="Рейсы", relief=tk.RIDGE, anchor='s', width=12).grid(row=6)

time_away = tk.Entry(root, width=50)
time_away.insert(0, '2018-05-05 12:30:00')
time_away.grid(row=0, column=1)

city_from = tk.Listbox(root, width=50, height=2, exportselection=0)
city_from.grid(row=1, column=1)

company = tk.Entry(root, width=50)
company.grid(row=3, column=1)

plane = tk.Entry(root, width=50)
plane.grid(row=4, column=1)

b1 = tk.Button(root, text='Добавить', command=click_event)
b1.grid(row=5, column=1)



for item in ["St.Petersberg, Pulkovo", "Moscow, Sheremetyevo"]:
    city_from.insert(tk.END, item)

city_to = tk.Listbox(root, width=50, height=2, exportselection=0)
city_to.grid(row=2, column=1)
for item in ["St.Petersberg, Pulkovo", "Moscow, Sheremetyevo"]:
    city_to.insert(tk.END, item)

all_rases = tk.Listbox(root, width=90, height=10)
all_rases.grid(row=6, column=1)

yscroll = tk.Scrollbar(command=all_rases.yview, orient=tk.VERTICAL)
yscroll.grid(row=6, column=2, sticky='ns')
all_rases.configure(yscrollcommand=yscroll.set)

db_helper = DBhelper()
my_rases = db_helper.get("rase")
print(my_rases)
for rase in my_rases:
    item_rase = []
    for it in rase:
        item_rase.append(copy.deepcopy(str(it)))
    all_rases.insert(tk.END, str(item_rase))

lines = len(my_rases)
all_rases.yview_scroll(lines, 'units')

root.geometry("650x350")
root.resizable(width=False, height=False)
root.mainloop()
