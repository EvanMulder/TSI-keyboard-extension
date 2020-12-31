"""
Created on Tue Oct 27 13:36:58 2020

@author: Evan Mulder

Purpose of TSI-keyboard extension is to generate virtual keyboard presses
by converting fNIRS data, analyzed by Turbo Satori (TSI), to self-chosen commands.
This program is able to generate virtual keypresses without you touching
the keyboard. It uses the fNIRS data from TSI an when the oxygenated hemoglobin
concentration values reaches a certain threshold value, a output is given consisting
of a keypress. This program will not run when TSI is not opened.
---------------------------------------------------------------------------
Strongly advice to read the Read me file in the TSI-extension map folder before
usage."""

import tkinter as tk
from tkinter import messagebox
from timeit import default_timer as timer
import time
from pynput.keyboard import Controller, KeyCode
import xlsxwriter
import pandas as pd
import List_Pycommands
import expyriment_stash.extras.expyriment_io_extras.turbosatorinetworkinterface\
    ._turbosatorinetworkinterface as BCI

keyboard = Controller()
BCIConnected = False

try:
    myBCI = BCI.TurbosatoriNetworkInterface('127.0.0.1', 55555)  # rename class
    BCIConnected = True
except (RuntimeError, TypeError, NameError):
    print("Can't connect to TurboSatori")
"""Try to connect to TSI
    If connection is not found return "Can't connect to TurboSatori" """

root = tk.Tk()  # Tkinter window
root.title("BCI Control")  # title
# root.geometry("300x200") #size
frame = tk.LabelFrame(root)  # label for frame window
frame.grid(row=0, column=0)  # grid the frame window
"""Creation of the BCI window for input variables"""

output = False  # give output a starting value
"""Output function is set to False.
    Output must be True to generate a keyboard press command"""

start_timer = 0
timepassed = 0
hemoglobin = 2
"""start_timer and timepassed function are set a starting value of 0.
    Both functions are needed for measuring elapsed time for continuous command
    start_timer will be set to the timepoint at which portocol matrix starts
    and timepassed measured the time past since ths timepoint
    hemoglobin value is set to 2 because it has to have a value for running the
    the binair and continuous command"""

samplerate = myBCI.get_sampling_rate()[0]
"""creates integer value of sampling at which rate the data at TSI is processed.
    This is used for time.sleep command in run_program to run 1 frame each time"""

Pycommands = List_Pycommands.Pycommands
"""renaming the Pycommand list from the imported file"""


def Current_Time():
    """Get the current timepoint from TSI """
    return myBCI.get_current_time_point()[0] - 1
    """returns current time point with one frame delay """


def protocol_condition():
    """ Get protocol conditions at current time point  """
    return myBCI.get_protocol_condition(myBCI.get_current_time_point()[0] - 1)[0]
    """Returns:
        protocol condition 0-based: int.
        The current protocol condition at the current time point."""


def start_protocol():
    """Function for retrieving the starting point at which the protocol condition
    changes from 0 to 1."""
    global start_timer
    if myBCI.get_protocol_condition(myBCI.get_current_time_point()[0] - 2)[0] == 0\
        and protocol_condition() == 1:
        start_timer = Current_Time()
    else:
        pass
    return start_timer
    """Returns: start_timer: int.
        When protocol condition is 0, start_timer is starting value of 0
        If condition is met when Current_Time has protocol value of 1 and
        Current_Time - 1 has protocol value of 0 returns stat_timer as Current_time."""


def deoxy_data(S_channel):
    """ Get oxygenetad blood value from TSI"""
    return myBCI.get_data_deoxy(myBCI.get_selected_channels()[0][S_channel],\
                                myBCI.get_current_time_point()[0] - 1)[0] *\
        myBCI.get_oxy_data_scale_factor()[0]
    """ Parameter:
    S_channel: int
        The selected channels in TSI

    Returns:
    get_data_deoxy: int
         The value of deoxygenated blood from each channels at current time point."""


def oxy_data(S_channel):
    """ Get oxygenetad blood value from TSI"""
    return myBCI.get_data_oxy(myBCI.get_selected_channels()[0][S_channel], \
                              myBCI.get_current_time_point()[0] - 1)[0] *\
        myBCI.get_oxy_data_scale_factor()[0]

    """ Parameter:
    S_channel: int.
    The selected channels in TSI.

    Returns:
    get_data_oxy: int.
         The value of oxygenated blood from each channel at current time point."""


def beta_data(S_channel):
    """"Get Beta value from TSI."""
    return myBCI.get_beta_of_channel\
        (myBCI.get_selected_channels()[0][S_channel], Predictor, hemoglobin)[0]\
            * myBCI.get_value_of_design_matrix(Predictor, Current_Time(), hemoglobin)[0]
    """ Parameter:
    S_channel: int.
        The selected channels in TSI.

    Returns:
    get_beta_of_channel: int.
         The beta value from each channel at current time point based on
         the chromophore of interest (1 = Oxy, 0 = DeOxy)."""


def Predicted_Value(S_channel):
    """Provides the predicted signal as a 4-byte float value of the channel specified by
    the parameter “channel”. The given “chromophore” parameter is jused to define
    the chromophore of interest (Oxy/DeOxy:1/0)."""
    return myBCI.get_prediction_of_channel(myBCI.get_selected_channels()[0][S_channel],\
                                           hemoglobin)[0]
    """ Parameter:
    S_channel: int
        The selected channels in TSI.

    Returns:
     get_prediction_of_channel: int.
         The predicted value from each channel at current time point based on
         the chromophore of interest (1 = Oxy, 0 = DeOxy)."""


def TSI_data(S_channel):
    """"Returns selected input data from TSI"""
    if Input_Variable.get() == "oxygenated":
        return oxy_data(S_channel)
    if Input_Variable.get() == "deoxygenated":
        return deoxy_data(S_channel)
    if Input_Variable.get() == "beta value":
        return beta_data(S_channel)
    if Input_Variable.get() == "Predictor":
        return Predicted_Value(S_channel)
        """ Parameter:
    S_channel: int
        The selected channels in TSI.

    Returns the input data from TSI depending on the chosen Input_Variable
    in the Tkinter window"""


def keycode_from_command(index):
    """"Returns Keycode"""
    return KeyCode.from_vk(Pycommands[1][Pycommands[0].index(command[index].get())])

    """Parameters: index: int
    command(index) is linked to a specific channels chosen in TSI
    Returns the Keycode value for each command[index] which is chosen from
    the first list of Pycommand in Binair or Continuous function and converter
    to the corresponding placement in the second list of Pycommands"""


def elaps_time():
    """Function for measurement of elapsed time since start_protocol."""
    if start_protocol() != 0:
        timepassed = Current_Time() - start_protocol()
    else:
        timepassed = 0
    return timepassed

    """ Returns timepassed: int.
    timepassed is set to 0 if start_protocol = 0.
    When start_protocol is != 0 elaps_time returns timepassed which will
    only reset at the start of a new protocol."""


def keycode_from_elaps_time():
    """Virtual keycode converte which depends on the elapsed time and
    interval_length variable chosen in continuous window and used for
    continuous command"""
    for i in range(interval_numbers):
        if (i * interval_length) < (elaps_time() - 20) <= ((i + 1) * interval_length):
            return keycode_from_command(i)

    """ Returns keycode_from_command depending on the current value of elaps_time
    which is in range of a multiply of the chosen interval_length"""


def Input_Data():
    """Creates an new window  for the selection of the input data
    Consist of a Label and a Option Menu"""
    global Input_Variable
    global Top
    Top = tk.Toplevel()
    Top.grab_set()
    Input_List = ["oxygenated", "deoxygenated", "beta value", "Predictor"]
    Input_Variable = tk.StringVar()
    Input_Variable.set(Input_List[0])
    drop_Input = tk.OptionMenu(Top, Input_Variable, *Input_List)
    drop_Input.grid(row=0, column=1)
    Label_Input = tk.Label(Top, text="Input Data", borderwidth=2, relief="groove")
    Label_Input.grid(row=0, column=0)
    Close_window = tk.Button(Top, text="Save & Close", command=Close_Input, height=1, width=24)
    Close_window.grid(row=1, column=0, columnspan=2)


def Input_Beta():
    """Opens the begta window for the selection of the protocol and chromophore"""
    global B_value
    global Oxy_List
    global Oxy_Value
    global Protocol_list
    global Top2
    Top2 = tk.Toplevel()
    Protocol_list = [0, 1, 2, 3]
    Oxy_List = [["Oxy Value", "Deoxy Value"], [1, 0]]
    B_value = tk.IntVar()
    B_value.set(Protocol_list[0])
    Oxy_Value = tk.StringVar()
    Oxy_Value.set(Oxy_List[0][0])
    drop5 = tk.OptionMenu(Top2, B_value, *Protocol_list)
    drop5.grid(row=0, column=1)
    Label5 = tk.Label(Top2, text="protocol", borderwidth=2, relief="groove")
    Label5.grid(row=0, column=0)
    drop6 = tk.OptionMenu(Top2, Oxy_Value, *Oxy_List[0])
    drop6.grid(row=1, column=1)
    Label6 = tk.Label(Top2, text="Chromophore", borderwidth=2, relief="groove")
    Label6.grid(row=1, column=0)
    Close = tk.Button(Top2, text="Save & Close", command=Close_Beta, height=1, width=26)
    Close.grid(row=3, column=0, columnspan=2)


def Close_Beta():
    """Close the Beta window for the selection of the input data and renames
    the selected varaibles in the window.
    When closing the window, the label in BCI window will be updated"""
    global Predictor
    global hemoglobin
    if Input_Variable.get() == "beta value":
        Predictor = B_value.get()
        hemoglobin = int(Oxy_List[1][Oxy_List[0].index(Oxy_Value.get())])
        Label1.configure(text=Input_Variable.get() + "\n" + "Protocol: " + str(Predictor) \
                         + "\n" + "Chromophore: " + Oxy_Value.get())
    Top2.destroy()


def Input_Predictor():
    """Opens the predictor window for the selection of the chromophore"""
    global Oxy_List
    global Oxy_Value
    global Top2
    Top2 = tk.Toplevel()
    Top2.grab_set()
    Oxy_List = [["Oxy Value", "Deoxy Value"], [1, 0]]
    Oxy_Value = tk.StringVar()
    Oxy_Value.set(Oxy_List[0][0])
    drop6 = tk.OptionMenu(Top2, Oxy_Value, *Oxy_List[0])
    drop6.grid(row=1, column=1)
    Label6 = tk.Label(Top2, text="Chromophore", borderwidth=2, relief="groove")
    Label6.grid(row=1, column=0)
    Close = tk.Button(Top2, text="Save & Close", command=Close_Predictor, height=1, width=26)
    Close.grid(row=3, column=0, columnspan=2)


def Close_Predictor():
    """Close the Predictor window for the selection of the input data and renames
    the selected varaibles in the window.
    When closing the window, the label in BCI window will be updated"""
    global hemoglobin
    hemoglobin = int(Oxy_List[1][Oxy_List[0].index(Oxy_Value.get())])
    Label1.configure(text=Input_Variable.get() + "\n" + "Chromophore: " + Oxy_Value.get())
    Top2.destroy()


def Close_Input():
    """Close the input window for the selection of the input data
    It will open another window when beta value or Predictor is selcted in the
    Option Menu. When closing the window, the label in BCI window will be updated"""
    if Input_Variable.get() == "beta value":
        Top.destroy()
        Input_Beta()
    elif Input_Variable.get() == "Predictor":
        Top.destroy()
        Input_Predictor()
    else:
        Label1.configure(text=Input_Variable.get())
        Top.destroy()


def Input_Commands():
    """Opens the command window for the selection of the binair or continuous option"""
    global Command_Variable
    global Top
    Top = tk.Toplevel()
    Top.grab_set()
    Command_List = ["Binair", "Continuous"]
    Command_Variable = tk.StringVar()
    Command_Variable.set(Command_List[0])
    drop_Command = tk.OptionMenu(Top, Command_Variable, *Command_List)
    drop_Command.grid(row=0, column=1)
    Label_Command = tk.Label(Top, text="Input Data", borderwidth=2, relief="groove")
    Label_Command.grid(row=0, column=0)
    Close_window = tk.Button(Top, text="Save & Close", command=Close_Input_Command,\
                             height=1, width=24)
    Close_window.grid(row=1, column=0, columnspan=2)


def Close_Input_Command():
    """"Closes the command window and update the label in BCI window"""
    Label2.configure(text=Command_Variable.get())
    Top.destroy()


def Variables():
    """ Creates interval window for command depending on seleciton
    Binair will open just threshold and Continuous will open
    interval_length and interval_numbers variables and close button
    will run CLose_Variables """
    global interval2
    global interval
    global Threshold
    global Top
    try:
        Command_Variable
        Top = tk.Toplevel()
        Top.grab_set()
        if Command_Variable.get() == "Continuous":
            interval = tk.Entry(Top, width=25)
            interval.insert(0, 80)
            interval.grid(row=0, column=1)
            Interval_Label = tk.Label(Top, text="Length of interval", width=15)
            Interval_Label.grid(row=0, column=0)
            interval2 = tk.Entry(Top, width=25)
            interval2.insert(0, 4)
            interval2.grid(row=1, column=1)
            Interval_Label2 = tk.Label(Top, text="Amount of intervals", width=15)
            Interval_Label2.grid(row=1, column=0)
        Threshold = tk.Entry(Top, width=25)
        Threshold.insert(0, 0.3)
        Threshold.grid(row=2, column=1)
        Interval_Label3 = tk.Label(Top, text="Threshold value", width=15)
        Interval_Label3.grid(row=2, column=0)
        Closebtn2 = tk.Button(Top, text="Save & Next", command=Close_Variables, height=1, width=41)
        Closebtn2.grid(row=3, column=0, columnspan=3)
    except NameError:
        messagebox.showerror("Command", "Please select Binair/Continuous")


def Interval_Variables():
    """ Runs when interval window is closed.
    Renames interval and interval2 variables to integer interval_length
    and integer interval_numbers.
    Closes interval window."""
    global interval_length
    global interval_numbers
    global Threshold_value
    interval_length = int(interval.get())
    interval_numbers = int(interval2.get())
    Threshold_value = float(Threshold.get())


def Close_Variables():
    """"CLoses Interval window and update Label in BCI window"""
    global Threshold_value
    if Command_Variable.get() == "Continuous":
        Interval_Variables()
        Label3.configure(text="Length of interval: " + interval.get() + "\n" +\
                         "Amount of intervals: " + interval2.get() + "\n" +\
                         "Threshold value: " + Threshold.get())
    else:
        Threshold_value = float(Threshold.get())
        Label3.configure(text="Threshold value: " + Threshold.get())
    Top.destroy()


def Binair():
    """Creates the binair window in the interface and show the chosen channels
    and corresponding output from Pycommands"""
    global command
    global myList
    global channel
    global Top
    drop, MyLabel = [], []
    Top = tk.Toplevel()
    myList = []
    command = []
    Top.grab_set()
    for channel in myBCI.get_selected_channels()[0]:
        myList.append("Channel " + str(channel))
        command.append("00")

    for i in range(len(command)):
        command[i] = tk.StringVar()
        command[i].set(str(Pycommands[0][i + 23]))
        drop.append("Drop " + str(i))
        MyLabel.append("MyLabel " + str(i))
        drop[i] = tk.OptionMenu(Top, command[i], *Pycommands[0])
        MyLabel[i] = tk.Label(Top, text=myList[i], borderwidth=2, relief="groove")
        drop[i].grid(row=i, column=1)
        MyLabel[i].grid(row=i, column=0)
        x = len(command) + 1
        Close = tk.Button(Top, text="Save & Close", command=Close_Output, height=1, width=24)
        Close.grid(row=x, column=0, columnspan=2)

    """ Function creates 2 list, MyList and command.
    Both length of list are dependent on the number of chosen channels.
    Each channel[i] is linked to command[i] which is set to a string value.
    drop function creation option menu in interface from where Pycommands are
    chosen and linked to command[i].
    Mylabel creates labels for each channel consisting of MyList[i].
    Close button closen binair window in interface"""


def Continuous():
    """Creates the continuous window in Tkinter and show the chosen channels
    and corresponding output from Pycommands"""
    global command
    global myList
    global Top
    Top = tk.Toplevel()
    myList = []
    command = []
    MyCLabel, Cdrop = [], []
    for channel in range(interval_numbers):
        myList.append("Channel " + str(myBCI.get_selected_channels()[0][0]))
        command.append("00")
    for i in range(interval_numbers):
        command[i] = tk.StringVar()
        command[i].set(str(Pycommands[0][i + 23]))
        Cdrop.append("Drop " + str(i))
        MyCLabel.append("MyLabel " + str(i))
        Cdrop[i] = tk.OptionMenu(Top, command[i], *Pycommands[0])
        MyCLabel[i] = tk.Label(Top, text=myList[i], borderwidth=2, relief="groove")
        Cdrop[i].grid(row=i, column=1)
        MyCLabel[i].grid(row=i, column=0)
        x = len(command) + 1
        Closebtn = tk.Button(Top, text="Save & Close", command=Close_Output, height=1, width=24)
        Closebtn.grid(row=x, column=0, columnspan=2)

    """ Function creates 4 list: MyCLabel, Cdrop, MyList and command.
    Length of all lists are dependent on the number of chosen intervals.
    Each interval is linked to command[i] which is set to string value.
    Cdrop function creation option menu in interface from where Pycommands are
    chosen and linked to command[i].
    CMylabel creates labels for each interval consisting of MyList[i]
    Close button closen continuous window in interface"""


def Command_Output():
    """"Opens Control window depended on the selected command input
    Opens error window when no command is selected"""
    try:
        Threshold
        if Command_Variable.get() == "Binair":
            Binair()
        elif Command_Variable.get() == "Continuous":
            Continuous()
        else:
            pass
    except NameError:
        messagebox.showerror("Title", "Please select Variable Settings")


def Close_Output():
    """"Closes Control window depended and update the Label depended on
    the selected command"""
    Command_Label = ''
    for i in range(len(command)):
        Command_Label += str("command " + str(i + 1) + ": " + str(command[i].get() + "\n"))
    Command_ = Command_Label[:-1]  # delete last \n command
    Label4.configure(text=Command_)
    Top.destroy()


def Excel_output_Binair(i):
    """"Creates the correct char value for Pandas for binary command"""
    return chr(int(str(keycode_from_command(i))[1: -1]))

    """"Parameters: i: int
    i is chosen in the keycode_from_command function"""


def binair_command():
    """Creates keyboard presses depending on value of keycode_from_command
     One keypress is genereated when:
    - start of a new protocol condition and
    - Threshold value for oxy_data is reached, inverted for deoxy_data.
    - Only one channel per protocol can generated keypress.
    If keypress is generated, output value changes to false until new protocol is started
    Output, reaction time and Timepoint of output are all saved in the .xlsx file
    File should be closed before running"""
    global output
    start = timer()
    if start_protocol() == Current_Time():
        output = True
    else:
        pass
    for i in range(len(command)):
        if Input_Variable.get() == "deoxygenated" or hemoglobin == 0:
            if output == True and TSI_data(i) < Threshold_value:
                keyboard.press(keycode_from_command(i))
                keyboard.release(keycode_from_command(i))
                output = False
                end = timer()
                print((end - start) * 1000)
                print(Current_Time())
                reaction_time = (end - start) * 1000
                df = pd.read_excel('Data_RT_TSI-Keyboard_Extension.xlsx')
                if df.empty:
                    df = pd.DataFrame(columns=['Output', 'Reaction time', 'Current time'])
                print(Excel_output_Binair(i))
                df = df.append([{'Output': Excel_output_Binair(i), 'Reaction time': reaction_time,\
                                 'Current time': Current_Time()}], ignore_index=True)
                writer = pd.ExcelWriter('Data_RT_TSI-Keyboard_Extension.xlsx', engine='xlsxwriter')
                df.to_excel(writer, header=True, index=False)
                writer.save()
            else:
                pass
        else:
            if output == True and TSI_data(i) > Threshold_value:
                keyboard.press(keycode_from_command(i))
                keyboard.release(keycode_from_command(i))
                output = False
                end = timer()
                print((end - start) * 1000)
                print(Current_Time())
                reaction_time = (end - start) * 1000
                df = pd.read_excel('Data_RT_TSI-Keyboard_Extension.xlsx')
                if df.empty:
                    df = pd.DataFrame(columns=['Output', 'Reaction time', 'Current time'])
                print('0x' + str(keycode_from_command(i)))
                df = df.append([{'Output': Excel_output_Binair(i), 'Reaction time': reaction_time,\
                                 'Current time': Current_Time()}], ignore_index=True)
                writer = pd.ExcelWriter('Data_RT_TSI-Keyboard_Extension.xlsx', engine='xlsxwriter')
                df.to_excel(writer, header=True, index=False)
                writer.save()


def Excel_output_Continuous():
    """"Creates the correct char value for Pandas for continuous command"""
    return chr(int(str(keycode_from_elaps_time())[1: -1]))


def continuous_command():
    """Creates keyboard presses depending on value of keycode_from_elaps_time
     One keypress is genereated when:
    - start of a new protocol condition and
    - Threshold value for TSI_data is reached
    - Only one channel per protocol can generated keypress and is depended
    on value of keycode_from_elaps_time.
    If keypress is generated, output value changes to False until new protocol is started
        Output, reaction time and Timepoint of output are all saved in the .xlsx file
    File should be closed before running."""
    global output
    start = timer()
    if elaps_time() == 1:
        output = True
    else:
        pass
    if Input_Variable.get() == "deoxygenated" or hemoglobin == 0:
        if output == True and TSI_data(0) < Threshold_value:
            keyboard.press(keycode_from_elaps_time())
            keyboard.release(keycode_from_elaps_time())
            end = timer()
            print((end - start) * 1000)
            print(Current_Time())
            output = False
            reaction_time = (end - start) * 1000
            print(Excel_output_Continuous())
            df = pd.read_excel('Data_RT_TSI-Keyboard_Extension.xlsx')
            if df.empty:
                df = pd.DataFrame(columns=['Output', 'Reaction time', 'Current time'])
            df = df.append([{'Output': Excel_output_Continuous(), 'Reaction time': reaction_time,\
                             'Current time': Current_Time()}], ignore_index=True)
            writer = pd.ExcelWriter('Data_RT_TSI-Keyboard_Extension.xlsx', engine='xlsxwriter')
            df.to_excel(writer, header=True, index=False)
            writer.save()
        else:
            pass
    else:
        if output == True and TSI_data(0) > Threshold_value:
            keyboard.press(keycode_from_elaps_time())
            keyboard.release(keycode_from_elaps_time())
            end = timer()
            print((end - start) * 1000)
            print(Current_Time())
            output = False
            reaction_time = (end - start) * 1000
            print(Excel_output_Continuous())
            df = pd.read_excel('Data_RT_TSI-Keyboard_Extension.xlsx')
            if df.empty:
                df = pd.DataFrame(columns=['Output', 'Reaction time', 'Current time'])
            df = df.append([{'Output': Excel_output_Continuous(), 'Reaction time': reaction_time,\
                             'Current time': Current_Time()}], ignore_index=True)
            writer = pd.ExcelWriter('Data_RT_TSI-Keyboard_Extension.xlsx', engine='xlsxwriter')
            df.to_excel(writer, header=True, index=False)
            writer.save()


def run_program():
    """run the program after the all variables are selected
    Depended on the selected input and command variables runs a different
    keypresscommand function.
    Opens error window when not all variables are selected.
    Time.sleep is depenedent on the samplerate chosen by TSI.
    Will update the root window otherwise the Tkinter window will crash due to
    a double loop"""
    print("start")
    try:
        Input_Variable
        try:
            Command_Variable
            try:
                Threshold,
                try:
                    command
                except NameError:
                    messagebox.showerror("Error", "Please select Choose Commands")
            except NameError:
                messagebox.showerror("Error", "Choose Interval/Treshold")
        except NameError:
            messagebox.showerror("Error", "Please select all variables")
    except NameError:
        messagebox.showerror("Error", "Please select Input Data")
    while True:
        if Command_Variable.get() == "Binair":
            binair_command()
            root.update()
            time.sleep(1 / samplerate)
        elif Command_Variable.get() == "Continuous":
            continuous_command()
            root.update()
            time.sleep(1 / samplerate)
        else:
            pass


Button1 = tk.Button(root, text="Input Data", command=Input_Data, height=1, width=25)
Button1.grid(sticky=tk.W, row=0, column=0)
"""Creates button for Input window"""

Label1 = tk.Label(root, text="Input data", borderwidth=2, relief="groove")
Label1.grid(row=0, column=1, sticky=tk.W + tk.E)
""""Creates label for BCI window"""

Button2 = tk.Button(root, text="Continuous/Binair", command=Input_Commands, height=1, width=25)
Button2.grid(sticky=tk.W, row=1, column=0)
"""Creates button for command window"""

Label2 = tk.Label(root, text="Continuous/Binair", borderwidth=2, relief="groove")
Label2.grid(row=1, column=1, sticky=tk.W + tk.E)
""""Creates label for BCI window"""

Button3 = tk.Button(root, text="Variables settings",\
                    command=Variables, height=2, width=25)
Button3.grid(sticky=tk.W, row=2, column=0)
"""Creates button for Variables window"""

Label3 = tk.Label(root, text="Threshold\ninterval", borderwidth=2, relief="groove")
Label3.grid(row=2, column=1, sticky=tk.W + tk.E)
""""Creates label for BCI window"""

Button4 = tk.Button(root, text="Choose command", command=Command_Output, height=4, width=25)
Button4.grid(sticky=tk.W, row=3, column=0)
"""Creates button for chosen Control window"""

Label4 = tk.Label(root, text="command 1\ncommand 2\ncommand 3\ncommand 4",\
                  borderwidth=2, relief="groove")
Label4.grid(row=3, column=1, sticky=tk.W + tk.E)
""""Creates label for BCI window"""

Run = tk.Button(root, text="run", command=run_program, height=1)
Run.grid(row=4, column=0, columnspan=2, sticky=tk.W + tk.E)
"""Creates button for running the program"""

Save = tk.Button(root, text="Close", command=root.destroy, fg="red", bg="white", height=1)
Save.grid(row=5, column=0, columnspan=2, sticky=tk.W + tk.E)
"""CLoses program"""

root.mainloop()
