Read me
TSI-keyboard extension version 1.0 06/11/2020

GENERAL INFORMATION
-----------------------------------------------------------------------------------
Purpose of TSI-keyboard extension is to generate virtual keyboard presses
by converting fNIRS data, analyzed by Turbo Satori (TSI), to self-chosen commands.
This program is able to generate virtual keypresses without you touching 
the keyboard. It uses the fNIRS data from TSI an when the BOLD signal reaches
a certain threshold value, a output is given consisting of a keypress.
Its main interface consists of a Tkinter window with multiple buttons, 
more information in GENERAL USAGE NOTES.

This program was made with Python 3.6 which includes the libraries below.
This program does not work with Python 2.X.

When using Python 3.3 or older, use the link to download the necessary libraries.
- get-pip.py  (https://bootstrap.pypa.io/get-pip.py)
- time (https://bootstrap.pypa.io/get-pip.py)
- timeit (https://github.com/python/cpython/blob/3.8/Lib/timeit.py)
- Tkinter (https://docs.python.org/3/library/tkinter.html)

Necessary libraries for all Python versions:
- pandas () 
- XLsxwriter ()
- XLrd	 ()
- pip install expyriment ()
- tcpclient ()
Additional library needed for all versions of Python 3.
-Pynput 1.7.1 (https://pypi.org/project/pynput/)

For optimal usage is Turbo-Satori version 2.2.2 or higher needed. 



INSTALLATION OF TSI-KEYBOARD EXTENSION
------------------------------------------------------------------------
Download the Zip file and have python installed at your device
Open program by clicking the TSI-keyboard extension.py file.



GENERAL STEPS
------------------------------------------------------------------------
- Be aware that the program will not run if Turbo Satori is not opened
 and channels are not selected.
- Before running the program, open TSI and run a Localizer.
- At the start of each session, open the program and choose the preferred
variables. An error window will pop up if not all are selected.
- For continuous output, use a single channel
- For binair output, use multiple channels
- All channels are required to have a chosen output otherwise the program 
will not run.  
- When selecting Beta or Predicted value a pop-up window will appear and
will ask for a protocol and chromophore input. 
- Output is generated as virtual keypresses and will be generated in the 
window or program which is opened at that time. Opening a new window
while running the program will result in keypresses in the newly opened
window.
- The generated output at the current time including the time it took to 
generated the output (reaction time) will be printed in the Excel file 
named Data_RT_TSI-Keyboard_Extension located in the same map.
- The Data file must be closed to save your output.
- Recommended to empty the Excel file after each session.
- After each testing, restart program and repeat previous instructions


Input data
------------------------------------------------------------------------
Four options available 
- oxygenated blood value
- deoxygenated blood value
- beta value (uses the beta value and the predicted model)
- Predicted model (uses the Predicted value of the predicted model)
------------------------------------------------------------------------

Continuous/Binair
------------------------------------------------------------------------
Two options available
- Binair (use when multiple channels are selected)
- Continuous (use when a single channel is selected)
------------------------------------------------------------------------

Variables settings
------------------------------------------------------------------------
If binair command is selected
- Threshold value must be selected
If continous command is selected
- Threshold value must be selected
- Number of intervals must be selected (set at 4)
- Length of intervals must be selected (set a 80 frames)
------------------------------------------------------------------------

Choose Command
------------------------------------------------------------------------
If binair command is selected
- Number of commands is depended on the selected channels in TSI
If continous command is selected
- Number of command i depended on the selected number of intervals
------------------------------------------------------------------------

When all previous Variables are selected press Run button to start testing

------------------------------------------------------------------------
TSI-keyboard extension can be reached at:

Website: www.Github.com.....
email:evanmulder@gmail.com

Copyright......
