import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.geometry("1000x600")
root.title("모션캡쳐를 이용한 프로젠테이션")
tabControl = ttk.Notebook(root)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text='발표시')
tabControl.add(tab2, text='발표 연습')
tabControl.pack(expand=1, fill="both")

ttk.Label(tab1,
          text="Welcome to \
          GeeksForGeeks").grid(column=0,
                               row=0,
                               padx=30,
                               pady=30)
ttk.Label(tab2,
          text="Lets dive into the\
          world of computers").grid(column=0,
                                    row=0,
                                    padx=30,
                                    pady=30)

root.mainloop()