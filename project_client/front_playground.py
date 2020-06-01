import tkinter as tk                # python 3
from tkinter import font  as tkfont # python 3
from tkinter.ttk import Progressbar
import time
#import Tkinter as tk     # python 2
#import tkFont as tkfont  # python 2


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
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is page 2", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(self, text="Go to the start page",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def activation(self):
        pass

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()