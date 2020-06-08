import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
from tkinter.ttk import Progressbar
import time
from model import *
import datetime
import sys

import matplotlib.pyplot as plt


dc = DeviceController()
# dc.start()
examinator = Examinator()
dc.set_examinator_callback(examinator.get_callback())


DATE_TIME_FORMAT = '%Y-%m-%d %H:%M'


def data_txt_line_to_date_object(line):
    s_line = line.split()
    return datetime.datetime.strptime(s_line[0] +' '+ s_line[1],DATE_TIME_FORMAT) , float(s_line[2][:-1])


after_activation_fun = None

test_list= [('17.02','36.7C'),('18.02','36.6C'),('19.02','37.5C'),('20.02','38.8C')]

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=12, weight="bold", slant="italic")

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
    COMS_PROGRESS_BAR_MAGNIFIER = 50
    def __init__(self, parent, controller):
        self.button_to_page_one_enabled=False
        self.button_to_page_two_enabled=False
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is the start page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.coms_len = dc.get_com_length()
        print(self.coms_len)
        self.progress = Progressbar(self, orient=tk.HORIZONTAL,
                               length=self.coms_len*StartPage.COMS_PROGRESS_BAR_MAGNIFIER, mode='determinate')

        self.progress['value'] = 0
        self.update_idletasks()
        dc.set_scanner_callback(self.animate_progress_bar)

        progres_infrom_label = tk.Label(self, text="Scanning for device...     ", font=controller.title_font)

        self.go_to_page_one_button = tk.Button(self, text="Make test",
                            command=self._go_to_page_one_func,fg='grey28',bg='gray63')
        self.go_to_page_two_button = tk.Button(self, text="View results",
                            command=self._go_to_page_two_func,fg='grey28',bg='gray63')
        progres_infrom_label.pack()
        self.progress.pack()
        self.go_to_page_one_button.pack()
        self.go_to_page_two_button.pack()



        progres_infrom_label.config(text = "Scanning for device... done")
        self.enable_go_to_page_one_button()
        self.enable_go_to_page_two_button()
        self.update_idletasks()
        print('self.progress[\'value\'] = {} '.format(self.progress['value']))
        global after_activation_fun
        after_activation_fun = self.late_activation


    def animate_progress_bar(self):
        self.progress['value'] =   self.progress['value'] +StartPage.COMS_PROGRESS_BAR_MAGNIFIER
        self.update_idletasks()

    def _go_to_page_one_func(self):
        if self.button_to_page_one_enabled:
            return self.controller.show_frame("PageOne")

    def enable_go_to_page_one_button(self):
        self.button_to_page_one_enabled=True
        self.go_to_page_one_button.config(fg='black', bg=self.cget('background'))

    def _go_to_page_two_func(self):
        if self.button_to_page_two_enabled:
            return self.controller.show_frame("PageTwo")

    def enable_go_to_page_two_button(self):
        self.button_to_page_two_enabled=True
        self.go_to_page_two_button.config(fg='black', bg=self.cget('background'))

    def late_activation(self):
        dc.com_scanner()
        self.progress['value'] = self.coms_len * StartPage.COMS_PROGRESS_BAR_MAGNIFIER
        dc.start()

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
        button1 = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        #button.pack()
        button1.grid(row = 1, column = 0)
        button2 = tk.Button(self, text="show graph",
                           command=self.show_graph)
        # button.pack()
        button2.grid(row = 1, column = 1)
        self.lines = None
        self.last_n = 5

    def activation(self):
        self.lines = []
        with open('data.txt','r') as f:
            self.lines = list(f)
        self.lines.reverse()
        for i in range(len(self.lines)):
            if i >= 10:
                break
            split_line = self.lines[i].split()

            b = tk.Label(self, text=split_line[0] +' '+ split_line[1])
            b.grid(row=i + PageTwo.NON_TABLE_ELEMS, column=0)
            b = tk.Label(self, text=split_line[2] + 'C')
            b.grid(row=i + PageTwo.NON_TABLE_ELEMS, column=1)
        # for i in range(len(test_list)):
        #     for j in range(2):
        #         b=tk.Label(self,text=test_list[i][j])
        #         b.grid(row=i+PageTwo.NON_TABLE_ELEMS,column=j)

    def show_graph(self):
        zipped_vals = list(map(data_txt_line_to_date_object,self.lines))
        unzipped = list(zip(*zipped_vals))
        if len(unzipped[0]) > 10:
            plt.plot(unzipped[0][:10], unzipped[1][:10])
        else:
            plt.plot(unzipped[0],unzipped[1])
        plt.xlabel('time')
        plt.ylabel('temperature')
        counter = 0
        for elem in zipped_vals:
            if counter>=10:
                break
            print(elem)
            plt.plot(elem[0],elem[1],'bo')
            plt.annotate(str(elem[1]),(elem[0],elem[1]))
            counter+=1
        plt.show()




class PageOne(tk.Frame):

    PROGRESSBAR_MAX_TICKS = 200
    def __init__(self, parent, controller):
        self._enable_save_button= False
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Tempartue Page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.label_temp = tk.Label(self, text="Temparature")
        self.label_temp.pack()
        self.label_time = tk.Label(self, text="Time")
        self.label_time.pack()

        self.progress_bar_real_max_ticks= examinator.progress_bar_max_ticks()
        self.progress_bar_current_ticks  =0
        button_back = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))


        button_test = tk.Button(self, text="Start_test",
                           command=lambda: self.start_examination_button())
        # button_test.pack()

        self.progress = Progressbar(self, orient=tk.HORIZONTAL,
                                    length=PageOne.PROGRESSBAR_MAX_TICKS, mode='determinate')

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
            f.write(str(time_val.strftime(DATE_TIME_FORMAT))+str(" {:.2f}".format(examinator.get_res()))+'\n')
        self.disable_save_button()

    def inc_progress_bar(self):
        # print('inc progress bar called')
        self.progress_bar_current_ticks+=1
        self.progress['value'] = int((self.progress_bar_current_ticks/float(self.progress_bar_real_max_ticks))*PageOne.PROGRESSBAR_MAX_TICKS)
        self.update_idletasks()
        print(self.progress['value'])

    def finished_callback(self):
        if not examinator.f_ended_with_timeout():
            self.label_temp.config(text=str(examinator.get_res())+' C',bg='green')
        else:
            self.label_temp.config(text=str(examinator.get_res()) + ' C', bg='red')
        self.label_time.config(text=str(examinator.get_elapsed_time())+ ' s')
        self.progress['value'] = PageOne.PROGRESSBAR_MAX_TICKS
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
    app.after(1,after_activation_fun)
    app.mainloop()
