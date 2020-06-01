import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
from tkinter.ttk import Progressbar
import time
from model import *
import datetime


dc = DeviceController()
dc.start()
examinator = Examinator()
dc.set_callback(examinator.get_callback())



test_list= [('17.02','36.7C'),('18.02','36.6C'),('19.02','37.5C'),('20.02','38.8C')]

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.activation()
        frame.tkraise()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is the start page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.progress = Progressbar(self, orient=tk.HORIZONTAL,
                               length=100, mode='determinate')
        self.progress.pack()

        button1 = tk.Button(self, text="Make test",
                            command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="View results",
                            command=lambda: controller.show_frame("PageTwo"))
        button3 = tk.Button(self,text="scan for device",command = self.animate_progress_bar)
        button1.pack()
        button2.pack()
        button3.pack()

    def animate_progress_bar(self):
        self.progress['value']= 0
        self.update_idletasks()
        for i in range(1,10+1):
            time.sleep(1)
            self.progress['value']= 10*i
            self.update_idletasks()

    def activation(self):
        pass

class PageTwo(tk.Frame):
    NON_TABLE_ELEMS = 2
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 1", font=controller.title_font)
        #label.pack(side="top", fill="x", pady=10)
        label.grid()
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        #button.pack()
        button.grid()

    def activation(self):
        for i in range(len(test_list)):
            for j in range(2):
                b=tk.Label(self,text=test_list[i][j])
                b.grid(row=i+PageOne.NON_TABLE_ELEMS,column=j)

class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        self._enable_save_button= False;
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Tempartue Page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.label_temp = tk.Label(self, text="Temparature")
        self.label_temp.pack()
        self.label_time = tk.Label(self, text="Time")
        self.label_time.pack()
        button_back = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))


        button_test = tk.Button(self, text="Start_test",
                           command=lambda: self.start_examination_button())
        # button_test.pack()

        self.progress = Progressbar(self, orient=tk.HORIZONTAL,
                                    length=examinator.progress_bar_max_ticks(), mode='determinate')

        self.button_save = tk.Button(self,text='save result',command=self.save_result)

        self.progress.pack()
        self.button_save.pack()
        self.disable_save_button()
        button_test.pack()
        button_back.pack()

        self.progress['value'] = 0
        self.update_idletasks()

    def enable_save_button(self):
        self._enable_save_button =True
        self.button_save.config(fg='black', bg=self.cget('background'))
        self.update_idletasks()

    def disable_save_button(self):
        self._enable_save_button =False
        self.button_save.config(fg='grey28',bg='gray63')
        self.update_idletasks()

    def save_result(self):
        if not self._enable_save_button:
            return
        with open('data.txt','a+')as f:
            time_val = datetime.datetime.now()
            f.write('( '+str(time_val.strftime('%Y-%m-%d %H:%M'))+' ) '+str(examinator.get_res())+'\n')
        self.disable_save_button()

    def inc_progress_bar(self):
        # print('inc progress bar called')
        self.progress['value'] = self.progress['value'] + 1
        self.update_idletasks()

    def finished_callback(self):
        if not examinator.f_ended_with_timeout():
            self.label_temp.config(text=str(examinator.get_res())+' C',bg='green')
        else:
            self.label_temp.config(text=str(examinator.get_res()) + ' C', bg='red')
        self.label_time.config(text=str(examinator.get_elapsed_time())+ ' s')
        self.progress['value'] = examinator.progress_bar_max_ticks()
        self.button_save.config(state=tk.NORMAL)
        self.enable_save_button()
        self.update_idletasks()
        pass

    def start_examination_button(self):
        if examinator.f_examination_started() and not examinator.f_examination_finished():
            return
        self.disable_save_button()
        self.progress['value'] = 0
        self.label_temp.config(text='temperature',bg = self.cget('background'))
        self.label_time.config(text='time')
        self.update_idletasks()
        examinator.clear()
        examinator.set_finished_callback(self.finished_callback)
        examinator.set_progress_callback(self.inc_progress_bar)
        examinator.start_examination()

    def activation(self):
        pass


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()