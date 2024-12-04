import tkinter as tk
import customtkinter as ctk
from calendar import monthcalendar
from time import strftime
from requests import get
from json import loads, dumps
from os import path, mkdir
from dotenv import load_dotenv

load_dotenv() 

class Window:
    # window_initializer
    def __init__(self,_title,height,width,theme="system"):
        self.dim = {"height":height,"width":width}
        self.__root = ctk.CTk()
        self.__root.title(f"{_title}")
        self.__root.geometry(f"{height}x{width}")
        self.__root.minsize(height,width)
        self.__root.maxsize(height,width)
        ctk.set_appearance_mode(theme)
        
    @property
    def root(self):
        return self.__root

# check-box interface
class DefaultCheckBox:
    def __init__(self, parent,_text,callback):
        self.checkbox = ctk.CTkCheckBox(
          parent,text=_text,height=40,width=40,
          command=callback,onvalue="on",offvalue="off"
        )
        self.checkbox.grid(padx=4,pady=4)
        
    def setPosition(self,x,y):
        self.checkbox.place(relx=x,rely=y,anchor=tk.CENTER)

def calendarWidget(root,date,height,width):
    Months = [
       "January","February","March","April",
       "May","June","July","August",
       "September","October","November","December"
    ]
    days_of_week = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    date = list(map(int, date.split("-")))
    yearmonth_label = ctk.CTkLabel(
      root,text=f"{Months[date[1]-1]} {date[0]}",
      font=('sans-serif',30),text_color="#0af011"
    )
    yearmonth_label.grid(padx=2,pady=2)
    yearmonth_label.place(relx=0.5,rely=0.19,anchor=tk.CENTER)
    calendarChart = monthcalendar(year=date[0],month=date[1])
    init_x, init_y = 0.85,0.28
    spaceing_factor = 0.85
    Dx, Dy = init_x, init_y
    for days_ in days_of_week:
        label = ctk.CTkLabel(root,text=days_,font=('sans-serif',28,'bold'))
        label.grid(padx=2,pady=2)
        label.place(relx=Dx/width*100,rely=init_y,anchor=tk.CENTER)
        Dx += spaceing_factor
    Dy = init_y + 2.2
    Dx = init_x
    for weeks in calendarChart:
        for dates in weeks:
            date_label = ctk.CTkLabel(
              root,text="" if dates == 0 else dates,
              font=('sans-serif', 26),
              text_color="#0af011" if date[2] == dates else "#fff"
            )
            date_label.grid(padx=2,pady=2)
            date_label.place(relx=Dx/width*100,rely=Dy/width*100,anchor=tk.CENTER)
            Dx += spaceing_factor
        Dx = init_x
        Dy += spaceing_factor
    return
    
def renderTime(root, height, width):
    # time renderer 
    def renderCall():
        local_time = strftime("%H:%M:%S") 
        time_label = ctk.CTkLabel(
          root,text=local_time,font=('monospace',66,"bold"),
          text_color="#0af011"
        )
        time_label.place(relx=0.5,rely=0.09,anchor=tk.CENTER)
        root.after(1000, renderCall)
        del time_label
        return
    def dateRenderer():   # date render will invoke ones every 10 minutes
        date = strftime("%Y-%m-%d")  # formatted date
        calendarWidget(root, date, height, width)
        root.after(600000, dateRenderer)
    renderCall()   # render system time!
    dateRenderer()
    return

def createCheckBoxLis(parent, height, width, datalist):
    def appendData(name):
        if not "days" in datalist:
            datalist["days"] = []
        datalist["days"].append(name)
        return
    createChkbox = lambda name: DefaultCheckBox(
      parent,name,lambda: appendData(name)
    )
    checkboxlist = (
      createChkbox("sunday"),createChkbox("monday"),createChkbox("tuesday"),
      createChkbox("wednesday"),createChkbox("thursday"),createChkbox("friday"),
      createChkbox("saturday")
    )
    # first half row
    x_pos, i = 0.57, 0
    while i < len(checkboxlist)//2 + 1:
        checkboxlist[i].setPosition(x_pos/width*100,0.35)
        x_pos += 0.8
        i += 1
    x_pos = 0.57
    while i < len(checkboxlist):
        checkboxlist[i].setPosition(x_pos/width*100,0.49)
        x_pos += 0.8
        i += 1
    return

# save alarm into a file-stream 
def saveFormData(parent, datalist):
    # perform form data validation
    if "days" not in datalist:
        datalist["days"] = "repeat everyday"
    hours, minute = datalist["hours"].get(), datalist["minute"].get()
    isValidTime = lambda hour, minute: (hour <= 23 and hour >= 0) and (minute >= 0 and minute <= 59)
    if (not hours.isdigit() or not minute.isdigit()):
        messagebox = tk.messagebox.showerror("Error", "The inputs you gave are not valid Time stamp!")
        return  # display error message
    elif not isValidTime(int(hours), int(minute)):
        messagebox = tk.messagebox.showerror("Error", "Input Overflow!")
        return
    currentdata = [{"hours":hours,"minute":minute,"days-to-repeat":datalist["days"]}]
    _dirname_, config_file = "My-Clock-utils", "alarms.json"
    if path.exists(_dirname_) == False:  # if directory doesn't exist or is deleted then create it
        mkdir(_dirname_)  # create configuration directory!
    if path.exists(path.join(_dirname_, config_file)) == False:  
        # and if config json file doesnt exist then create it!
        with open(path.join(_dirname_, config_file), "w") as f2:
            f2.write(dumps(currentdata))   # dump json string
            parent.destroy()              # terminate the parent window!
        return  # exit
    with open(path.join(_dirname_, config_file), "r") as f1:
        with open(path.join(_dirname_,config_file), "w") as f2:
            if f1.read() == "":   # if file exists but is empty append the data
                f2.write(dumps(currentdata))
            else:
                extended = loads(f1.read())+currentdata # otherwise parse json to dictionary-list and extend
                f2.write(dumps(extended))
    parent.destroy()   # terminate the parent window after storing the data!
    return

# render and Handle Alarm Input from user!
def alarmInputForm():
    formwindow = Window("set alarm", 550, 422,"dark") # create a small window for a form input
    formroot = formwindow.root               # root tkinter element of Window
    datalist = {"hours":tk.StringVar(formroot),"minute":tk.StringVar(formroot)}
    _hours_input,_minutes_input = ctk.CTkEntry(
      formroot,textvariable=datalist["hours"],
      height=60,width=70,font=('monospace',40)
    ), ctk.CTkEntry(
      formroot,textvariable=datalist["minute"],
      height=60,width=70,font=('monospace',40)
    )
    datalist["hours"].set("06")   # default value for hours time
    datalist["minute"].set("00")      # default value for minutes time
    # save alarm button
    saveAlarmBtn = ctk.CTkButton(
      formroot,text="save",height=57,
      width=100,font=('monospace',27),
      command=lambda: saveFormData(formroot,datalist)
    )
    createCheckBoxLis(
      formroot,formwindow.dim["height"],
      formwindow.dim["width"],datalist
    )
    _hours_input.grid(padx=4,pady=4)   # hour input positioning
    _minutes_input.grid(padx=4,pady=4)  # minute input positioning
    _hours_input.place(relx=0.23,rely=0.18,anchor=tk.CENTER)
    _minutes_input.place(relx=0.42,rely=0.18,anchor=tk.CENTER)
    saveAlarmBtn.grid(padx=5,pady=4)
    saveAlarmBtn.place(relx=0.5,rely=0.81,anchor=tk.CENTER)
    formroot.mainloop()     # form window loop
    return

def alarmMenu(parent, parent_height,parent_width):
    newAlarmBtn = ctk.CTkButton(
      parent,text="new alarm",height=50,width=80,
      font=('monospace',18,'bold'),command=alarmInputForm
    )
    alarmsMenu = ctk.CTkScrollableFrame(
      parent,width=parent_width*0.89,
      height=parent_height*0.62
    )
    json_folder = path.join("My-Clock-utils", "alarms.json")
    if path.exists("My-Clock-utils") == False or path.exists(json_folder) == False:
        no_data_label = ctk.CTkLabel(
          parent,text="No Alarms here!",
          font=('monospace',40),text_color="yellow"
        )
        no_data_label.place(relx=0.5,rely=0.2,anchor=tk.CENTER)
    else:
        json_dump = ""    # fetched data from file!
        with open(json_folder, "r") as f2:
            json_dump = loads(f2.read())
        y_init = 0.04   # initial y-position of the first widget
        for data in json_dump:
            timestring = f"{data["hours"]}:{data["minute"]}"
            tablist = ctk.Tabview(
              alarmsMenu,height=50,width=parent_width*0.75,
              border_color="#149cfc",border_width="3",corner_radius=8
            )
            alarmTime_label = ctk.CTkLabel(
              tablist,text=timestring,font=('monospace',35)
            )
            tablist.grid(padx=3,pady=3)
            alarmTime.grid(padx=3,pady=3)
            alarmTime.place(relx=0.1,rely=0.3,anchor=tk.CENTER)
            tablist.place(
              relx=0.5,rely=y_init/(parent_height*0.62)*100,
              anchor=tk.CENTER
            )
            y_init += 0.9   # update y_position of the box
    # widget display-positions
    newAlarmBtn.grid(padx=3,pady=3)
    alarmsMenu.grid(padx=3,pady=3)
    alarmsMenu.place(relx=0.5,rely=0.63,anchor=tk.CENTER)
    newAlarmBtn.place(relx=0.48,rely=0.089,anchor=tk.CENTER)
    return

def displayTab(app,_height,_width):
    # navbar button procedure
    navBarBtns = lambda _text: ctk.CTkButton(
      app,text=_text,height=49,width=160,
      font=('monospace',20,'bold'),command=lambda: tabview.set(_text)
    )
    # procudures and initialize positioning for the first button in navbar
    tablist, y_positioning = ["time","moon-phase","alarm","settings"], 0.8
    tabview = ctk.CTkTabview(app, height=_height*0.86,width=_width*0.96)
    tabview.place(relx=0.2,rely=0)
    # create tabs
    for tabs in tablist:
        tabview.add(tabs)
    # create navigation buttons
    buttonlist = (
      navBarBtns(tablist[0]),navBarBtns(tablist[1]),
      navBarBtns(tablist[2]),navBarBtns(tablist[3])
    )
    for button in buttonlist: # position the buttons in contigious manner as Side Navbar
        button.place(relx=0.01,rely=y_positioning/_height*100)
        y_positioning += 0.9
    renderTime(tabview.tab(tablist[0]),_height*0.86,_width*0.96)
    alarmMenu(tabview.tab(tablist[2]),_height*0.86,_width*0.96)
    settings(app, tabview.tab(tablist[3]))
    return

def settings(window, parent):
    header = ctk.CTkLabel(parent,text="Settings", font=('sans-serif',39,'bold'))
    header.grid(padx=3,pady=3)
    header.place(relx=0.2,rely=0.08,anchor=tk.CENTER)
    bgVar,bgmodevar = ctk.StringVar(value="blue"),ctk.StringVar(value="dark")
    changebg_label = ctk.CTkLabel(
      parent,text="Color theme",font=('sans-serif',27)
    )
    changeBgframe = ctk.CTkComboBox(
      parent,values=["green","dark-blue","blue"],variable=bgVar,
      command=lambda choice: window._apply_appearance_mode(choice) # set color theme
    )
    bgModeLabel = ctk.CTkLabel(parent,text="theme",font=('sans-serif',27))
    bgChangeLabel = ctk.CTkComboBox(
      parent,values=["system","white","dark"],variable=bgmodevar,
      command=lambda choice: window._set_appearance_mode(choice) # set background theme
    )
    changebg_label.grid(padx=4,pady=4)
    changebg_label.place(relx=0.17,rely=0.2,anchor=tk.CENTER)
    changeBgframe.grid(padx=4,pady=4)
    changeBgframe.place(relx=0.8,rely=0.2,anchor=tk.CENTER)
    bgModeLabel.grid(padx=4,pady=4)
    bgModeLabel.place(relx=0.17,rely=0.31,anchor=tk.CENTER)
    bgChangeLabel.grid(padx=4,pady=4)
    bgChangeLabel.place(relx=0.8,rely=0.31,anchor=tk.CENTER)
    return

def main():
    app = Window("My Clock",900,760,"dark")
    root = app.root
    displayTab(root,app.dim["height"],app.dim["width"])
    root.mainloop()
    return

if __name__ == "__main__":
    main()    # run application
