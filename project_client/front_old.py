from model import *
import tkinter as tk


dc = DeviceController()
dc.start()
examinator = Examinator()
dc.set_examinator_callback(examinator.get_callback())


window =tk.Tk()
temp_label = tk.Label(
    text="Temperature goes here",
    fg="white",
    bg="black",
    width=50,
    height=5
)
temp_label.pack()
time_label = tk.Label(
    text="Temperature goes here",
    fg="white",
    bg="black",
    width=50,
    height=5
)
time_label.pack()

def start_test():
    print("button pressed")
    if examinator.f_examination_started() and not examinator.f_examination_finished():
        print("    examination already started")
    else:
        examinator.start_examination(f_clear=True)
        print('    examomination starting')
        temp_label.config(text='0')
        time_label.config(text='0')
    pass


button = tk.Button(
    text="Click me!",
    width=25,
    height=5,
    bg="blue",
    fg="yellow",
    command=start_test
)


button.pack()



def task():
    if examinator.f_examination_finished():
        temp_label.config(text=examinator.get_res())
        time_label.config(text=examinator.get_elapsed_time())
    if examinator.f_examination_started():
        print('    ',end='')
        print(examinator.get_current_test_time())
    window.after(1000, task)

window.after(1000, task)
window.mainloop()
