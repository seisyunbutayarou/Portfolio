import tkinter as tk
from tkinter import ttk

window = tk.Tk()

window.title('電卓')

window.geometry("500x600+1+1")

display = tk.Entry(window, width=13, font=("Arial", 40))
display.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

buttons = [
    ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
    ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
    ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
    ('0', 4, 0), ('.', 4, 1), ('+', 4, 2), ('=', 4, 3),
    ('C', 5, 0)
]

for btn in buttons:
    text, row, col = btn
    tk.Button(window, text=text, width=7, height=2, font=("Arial", 18),
              command=lambda value=text: calculator(value)).grid(row=row, column=col)

def calculator(value):
    if value == "=":
        try:
            expression = display.get()
            if "=" in expression:
                expression = expression.replace("=", "")
            result = convert_number(eval(expression))
            display.delete(0, tk.END)
            display.insert(0, result)
        except Exception as e:
            display.delete(0, tk.END)
            display.insert(0, "エラー:"+str(e))
    elif value == "C":
        display.delete(0, tk.END)
    else:
        display.insert(tk.END, value)

def key_press(event):
    key = event.char
    if key in '0123456789+-*/.':
        display.insert(tk.END, key)
    elif key == '\r':
        calculator('=')
    elif key == '\x08':  # バックスペースキー
        display.delete(len(display.get())-1)

def convert_number(num):
    if num.is_integer():  # 小数点以下が0の場合
        return int(num)
    else:
        return num

window.bind("<KeyPress>", key_press)

window.mainloop()