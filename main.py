import tkinter as tk
import customtkinter as ctk
import notify2 as notify
from calendar import monthcalendar
from time import strftime
from json import loads, dumps
from os import path, mkdir, getenv
from uuid import uuid4
from datetime import date, timedelta
from PIL import Image

class Window:
    # window_initializer
    def __init__(self,_title: str,height: int,width: int,theme: str="system"):
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
        
    def setPosition(self,x: int,y: int) -> None:
        self.checkbox.place(relx=x,rely=y,anchor=tk.CENTER)

def calendarWidget(root,date: str,height: int,width: int) -> None:
    Months = [
       "January","February","March","April","May","June",
       "July","August","September","October","November","December"
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
    d_x, d_y = init_x, init_y
    for days_ in days_of_week:
        label = ctk.CTkLabel(root,text=days_,font=('sans-serif',28,'bold'))
        label.grid(padx=2,pady=2)
        label.place(relx=d_x/width*100,rely=init_y,anchor=tk.CENTER)
        d_x += spaceing_factor
    d_y = init_y + 2.2
    d_x = init_x
    for weeks in calendarChart:
        for dates in weeks:
            date_label = ctk.CTkLabel(
              root,text="" if dates == 0 else dates,
              font=('sans-serif', 26),
              text_color="#0af011" if date[2] == dates else "#fff"
            )
            date_label.grid(padx=2,pady=2)
            date_label.place(relx=d_x/width*100,rely=d_y/width*100,anchor=tk.CENTER)
            d_x += spaceing_factor
        d_x = init_x
        d_y += spaceing_factor
    return

def getMoonPhase(_date: str) -> tuple:
    lunar_cycle = 29.53088  # lunar cycle is approximately 29.5308 days
    _date = list(map(int, _date.split("-")))
    lastnew_moon = date(year=2018,month=12,day=7)
    current = date(year=_date[0],month=_date[1],day=_date[2])
    difference = (current-lastnew_moon).total_seconds()/(60*60*24)
    number_of_newmoons = difference/lunar_cycle
    phase_diff = number_of_newmoons - round(number_of_newmoons)
    age, phase_image,name = phase_diff*lunar_cycle, None, None
    if age >= 0 and age < 0.5:
        phase_image = path.join("assets", "newmoon.png")
        name = "New Moon"
    elif age >= 0.5 and age <= 7.1:
        phase_image = path.join("assets", "waxing_cresent.png")
        name = "Waxing Crescent"
    elif age > 7.1 and age <= 7.99:
        phase_image = path.join("assets","first_quarter.png")
        name = "First Quarter"
    elif age > 7.99 and age <= 13.9:
        phase_image = path.join("assets","waxing_gibbous.png")
        name = "Waxing Gibbous"
    elif age >= 14 and age <= 15.1:
        phase_image =  path.join("assets","full_moon.png")
        name = "Full Moon"
    elif age > 15.1 and age <= 21.9:
        phase_image = path.join("assets","wanning_gibbous.jpeg")
        name = "Wanning Gibbous"
    elif age > 21.9 and age <= 23.3:
        phase_image = path.join("assets","last_quarter.png")
        name = "Last Quarter"
    elif age > 23.3 and age <= 28.9:
        phase_image = path.join("assets","wanning_cresent.png")
        name = "Wanning Crescent"
    elif age > 28.9 and age <= lunar_cycle:
        phase_image = path.join("assets","newmoon.png")
        name = "New Moon"
    return (age, phase_image, name)

def renderMoonPhase(root) -> None:
    # find the next occurring full moon! 
    def getNextFullMoon(initdate: str) -> int:
        parsed, full_moon_age = list(map(int, initdate.split("-"))), 13.8 # days
        phase, dayselapsed = getMoonPhase(initdate)[0], None
        if (full_moon_age-phase) < 0:
            dayselapsed = ((29.5308 - phase) + full_moon_age)
        else:
            dayselapsed = full_moon_age - phase
        next_full_moon = date(year=parsed[0],month=parsed[1],day=parsed[2])
        return next_full_moon + timedelta(days=round(dayselapsed))
    # render moon phases!
    def renderer() -> None:
        local_time = strftime("%Y-%m-%d")
        age, phase, name = getMoonPhase(local_time)
        _image = ctk.CTkImage(
          light_image=Image.open(phase),dark_image=Image.open(phase),
          size=(500,500)
        )
        imagelabel = ctk.CTkLabel(root,text="",image=_image)
        imagelabel.place(relx=0.5,rely=0.3,anchor=tk.CENTER)
        moonphaselabel = ctk.CTkLabel(
          root,text=f"{name}",font=('monospace',36,'bold')
        )
        moon_agelabel = ctk.CTkLabel(
          root,text=f"Age: {round(age,3)} days",font=('monospace',35)
        )
        next_full_moon = ctk.CTkLabel(
          root,text=f"Next Full Moon: {getNextFullMoon(local_time)}",
          font=('monospace',30)
        )
        next_full_moon.place(relx=0.49,rely=0.89,anchor=tk.CENTER)
        moonphaselabel.place(relx=0.49,rely=0.7,anchor=tk.CENTER)
        moon_agelabel.place(relx=0.49,rely=0.8,anchor=tk.CENTER)
        root.after(1200000, renderer)
        return
    renderer()
    return
    
def renderTime(root, height: int, width: int) -> None:
    # time renderer 
    def renderCall() -> None:
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

def createCheckBoxLis(parent,height: int,width: int,datalist: dict[str])-> None:
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
def saveFormData(parent, datalist: dict[str]) -> None:
    # perform form data validation
    if "days" not in datalist:
        datalist["days"] = "repeat everyday"
    hours, minute = datalist["hours"].get(), datalist["minute"].get()
    isValidTime = lambda hour,minute:(hour <= 23 and hour >= 0) and (minute >= 0 and minute <= 59)
    if (not hours.isdigit() or not minute.isdigit()):
        messagebox = tk.messagebox.showerror("Error", "The inputs you gave are not valid Time stamp!")
        return  # display error message
    elif not isValidTime(int(hours), int(minute)):
        messagebox = tk.messagebox.showerror("Error", "Input Overflow!")
        return
    currentdata = [{"hours":hours,"minute":minute,"days-to-repeat":datalist["days"]}]
    currentdata[0]["id"] = str(uuid4())  # create a unique id for alarms
    _dirname_, config_file = "My-Clock-utils", "alarms.json"
    if path.exists(_dirname_) == False:  # if directory doesn't exist or is deleted then create it
        mkdir(_dirname_)  # create configuration directory!
    if path.exists(path.join(_dirname_, config_file)) == False:  
        # and if config json file doesnt exist then create it!
        with open(path.join(_dirname_, config_file), "w") as f2:
            f2.write(dumps(currentdata))   # dump json string
            parent.destroy()              # terminate the parent window!
        return  # exit
    fetched_json = None
    with open(path.join(_dirname_, config_file), "r") as f1:
        fetched_json = f1.read()  # read the existing file and fetch the buffer!
    with open(path.join(_dirname_,config_file), "w") as f2:
    # if file has not json add the new list to existing otherwise concatenate the existing with new!
        fetched_json = currentdata if fetched_json == "" else loads(fetched_json) + currentdata
        f2.write(dumps(fetched_json))
    parent.destroy()   # terminate the parent window after storing the data!
    return

# render and Handle Alarm Input from user!
def alarmInputForm() -> None:
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

def subtractTime(inittimestring: str) -> tuple[int]:
    target = list(map(int, inittimestring.split(":"))) 
    now = list(map(int, strftime("%H:%M").split(":")))
    if target[0] == now[0]:
        if (target[1]-now[1] < 0):
            return (23, abs(target[1]-now[1]))
        return (0, target[1]-now[1])
    elif target[0] < now[0]:
        hour_diff = (24-now[0]) + target[0]
        if now[1] > target[1]:
            return (hour_diff-1,(60-now[1] + target[1]))
        else:
            return (hour_diff, target[1]-now[1])
    hour_diff = target[0] - now[0]
    minute_diff = target[1] - now[1]
    if minute_diff < 0:
        return (23,abs(minute_diff))
    return (hour_diff, minute_diff)

def alarmMenu(parent, parent_height: int,parent_width: int) -> None:
    newAlarmBtn = ctk.CTkButton(
      parent,text="new alarm",height=50,width=80,
      font=('monospace',18,'bold'),command=alarmInputForm
    )
    alarmsMenu = ctk.CTkScrollableFrame(
      parent,width=parent_width*0.89,
      height=parent_height*0.62
    )
    alarmsMenu.grid(padx=3,pady=3)
    alarmsMenu.place(relx=0.5,rely=0.63,anchor=tk.CENTER)
    json_folder = path.join("My-Clock-utils", "alarms.json")
    no_data_label = ctk.CTkLabel(
      parent,text="No Alarms here!",
      font=('monospace',40),text_color="yellow"
    )
    if path.exists("My-Clock-utils") == False or path.exists(json_folder) == False:
        no_data_label.place(relx=0.5,rely=0.2,anchor=tk.CENTER)
    else:
        json_dump = ""    # fetched data from file!
        with open(json_folder, "r") as f2:
            json_dump = f2.read()
        if json_dump == "":
            no_data_label.place(relx=0.5,rely=0.2,anchor=tk.CENTER)       
        else:
            no_data_label.destroy()   # destroy the not_data_label to display saved data
            json_dump = loads(json_dump)
            for data in json_dump:
                timestring = f"{data["hours"]}:{data["minute"]}"
                hour_diff, min_diff = subtractTime(timestring)
                tablist = ctk.CTkTabview(
                  alarmsMenu,height=120,width=parent_width*0.76,
                  border_width=3,corner_radius=8,fg_color="#696a6b"
                )
                alarmTime_label = ctk.CTkLabel(
                  tablist,text=timestring,font=('monospace',43)
                )
                deleteAlarmBtn = ctk.CTkButton(
                  tablist,text="delete",height=30,width=37,
                  fg_color="#ff295b",command=lambda: deleteAlarmWithId(data["id"])
                )
                alarmNote =  ctk.CTkLabel(
                  tablist,text=f"{hour_diff} hours {min_diff} minutes to go!",
                  font=('sans-serif',15),text_color="#b4b8b5"
                )
                fireAlarmNotification(parent,timestring)
                tablist.grid(padx=4,pady=4)
                alarmNote.place(relx=0.23,rely=0.75,anchor=tk.CENTER)
                deleteAlarmBtn.place(relx=0.88,rely=0.5,anchor=tk.CENTER)
                alarmTime_label.place(relx=0.2,rely=0.5,anchor=tk.CENTER)
    # widget display-positions
    newAlarmBtn.grid(padx=3,pady=3)
    newAlarmBtn.place(relx=0.48,rely=0.089,anchor=tk.CENTER)
    return

# delete the alarm with an id
def deleteAlarmWithId(alarm_id):
    confirm_dialog = tk.messagebox.askquestion(
      "alarms","Do you really want to delete this alarm?"
    )  # confirm from user if he wants to delete the alarm or not
    if confirm_dialog == "no":
        return   # if no then just exit
    alarmlist = None
    config_path = path.join("My-Clock-utils", "alarms.json")
    with open(config_path, "r") as f2:
        alarmlist = loads(f2.read())  # parse stringified json!
    # find the alarm with id and delete it!
    for i in range(len(alarmlist)):
        if alarmlist[i]["id"] == alarm_id:
            alarmlist.remove(alarmlist[i])  # delete the data
            break
    with open(config_path, "w") as f2:
        f2.write(dumps(alarmlist))   # stringify and save the updated buffer
    return

def fireAlarmNotification(root, time: str):
    notify.init("My Clock")
    notification = notify.Notification(f"its {time}")
    newYearNotification = notify.Notification(
      f"Happy New Year {getenv("USER")}", 
      '''Every new year brings an new 
      opportuinity. Hope you have a Great New Year!'''
    )
    def helper():
        if time == strftime("%H:%M"):
            notification.show()  # display notification!
        if strftime("%m-%d") == "01-01":
            newYearNotification.show()
        root.after(10000, helper)
    helper()
    return

def displayTab(app,_height: int,_width: int):
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
    renderMoonPhase(tabview.tab(tablist[1]))
    alarmMenu(tabview.tab(tablist[2]),_height*0.86,_width*0.96)
    settings(app, tabview.tab(tablist[3]))
    return

def settings(window, parent) -> None:
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

def main() -> None:
    app = Window("My Clock",900,760,"dark")
    root = app.root
    displayTab(root,app.dim["height"],app.dim["width"])
    root.mainloop()
    return

if __name__ == "__main__":
    main()    # run application
