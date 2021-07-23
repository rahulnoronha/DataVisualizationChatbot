import train
import tkinter
import pandas as pd
import matplotlib
import webbrowser
import seaborn as sns
import json
import keyring
import os
import sys
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from matplotlib.widgets import Slider
from chat import get_response, bot_name
from db import get_csvtodb
from pathlib import Path
from sqlalchemy import create_engine
from pathlib import Path
from matplotlib import pyplot as plt




# Colours
# The colours used in the GUI front-end
BG_GRAY = "#A9A9A9"  # dark gray
BG_COLOUR = "#87CEEB"  # sky blue
BG_COLOUR1 = "#FFFFFF"  # White
BG_COLOUR2 = "#F5F5DC"  # beige
BG_COLOUR3 = "#7F87CE" #Slightly Saturated blue
BG_COLOUR4 = "#000000" #Black
TEXT_COLOUR = "#000000"  # Black

# Fonts
# Font used to display text onto tkinter GUI
FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

# To store a list of already imported Dataset CSVs
imported_files = []
# To store a list of the possible visualization types
charts = ["Pairplot", "Bar_chart", "Pie_chart", "Scatterplot"]

# Main Function
def main():
    """
    Create object of class ChatApplication which is created by __init__
    Use the run method of the app to create the main window.
    """
    app = ChatApp()
    app.run()


# Restart Function
def restart():
    """
    This function helps to restart the GUI, namely app.py using sys and os modules.
    """
    print("argv was", sys.argv)
    print("sys.executable was", sys.executable)
    print("Restarting application now")
    os.execv(sys.executable, ["python", "app.py"])


# To check if a string is in json format
def check_json(json_text):
    try:
        json.loads(json_text)
        return True
    except Exception as ex:
        return False


class ChatApp:
    """
    Chat Application class: Has its own set of attributes and methods which are part of the tkinter GUI
    """

    def __init__(self):
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        """
        Creates the mainloop of the main window on start by call from main()
        """
        self.window.mainloop()

    def _setup_main_window(self):
        """
        Creates the wigdets of the main window and waits for Buttons to be pressed. Help button opens
        up html local host help.html and run.html, Feedback button allows user to enter query they
        need answer to the json file for future improvement of answers. On press of Input CSV button
        we have the option to import a csv file and store it in local Database using db.py. On pressing
        enter or sent the text is sent to the torch model created in train.py and the app replies to the message
        using the model. In case a data visualization command has been entered then it takes user
        to visualization page.
        """
        self.window.title("Chat")
        self.window.resizable(width=True, height=True)
        self.window.configure(width=470, height=550, bg=BG_COLOUR1)
        # head label
        head_label = Label(
            self.window,
            bg=BG_COLOUR1,
            fg=TEXT_COLOUR,
            text="Welcome",
            font=FONT_BOLD,
            pady=10,
        )
        head_label.place(relwidth=1)
        # tiny divider
        line = Label(self.window, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)
        # text widget
        self.text_widget = Text(
            self.window,
            width=20,
            height=2,
            bg=BG_COLOUR3,
            fg=TEXT_COLOUR,
            font=FONT,
            padx=5,
            pady=5,
        )
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)
        # scroll bar
        scrollbar = Scrollbar(self.text_widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)
        # bottom label
        bottom_label = Label(self.window, bg=BG_GRAY, height=80)
        bottom_label.place(relwidth=1, rely=0.825)
        # message entry box
        self.msg_entry = Entry(bottom_label, bg=BG_COLOUR1, fg=TEXT_COLOUR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)

        # send button
        send_button = Button(
            bottom_label,
            text="Send",
            font=FONT_BOLD,
            width=10,
            bg=BG_GRAY,
            command=lambda: self._on_enter_pressed(None),
        )
        send_button.place(relx=0.70, rely=0.008, relheight=0.06, relwidth=0.22)

        # Input csv button
        input_button = Button(
            bottom_label,
            text="Input CSV",
            font=FONT_BOLD,
            width=10,
            bg=BG_GRAY,
            command=self.encode,
        )
        input_button.place(relx=0.48, rely=0.008, relheight=0.06, relwidth=0.22)
        # Help Button
        help_button = Button(
            bottom_label, text="Help", font=FONT_BOLD, width=4, bg=BG_GRAY, command=help
        )
        help_button.place(relx=0.92, rely=0.008, relheight=0.06, relwidth=0.08)
        # Feedback Button
        feedback_button = Button(
            head_label,
            text="Feedback",
            font=FONT_BOLD,
            width=6,
            bg=BG_GRAY,
            command=self.feedback,
        )
        feedback_button.place(relx=0.62, rely=0.4, relheight=0.4, relwidth=0.3)

    def _setup_visual(self, headers, df):
        """
        Used to create a separate window for visualizations. Here the DataFrame can be viewed using 
        DataFrame button and also Enter button can be used in addition to the Visualize button to enter plaintext
        query and view the visualizations.
        """
        self._headers = headers
        self._df = df
        self.sub = Toplevel()
        self.sub.title("Data Visualizations")
        self.sub.resizable(width=True, height=True)
        self.sub.configure(width=470, height=550, bg=BG_COLOUR1)
        # head label
        head_label1 = Label(
            self.sub,
            bg=BG_COLOUR1,
            fg=TEXT_COLOUR,
            text="Graphs",
            font=FONT_BOLD,
            pady=10,
        )
        head_label1.place(relwidth=1)
        # tiny divider
        line1 = Label(self.sub, width=450, bg=BG_GRAY)
        line1.place(relwidth=1, rely=0.07, relheight=0.012)
        # text widget
        self.text_widget1 = Text(
            self.sub,
            width=20,
            height=2,
            bg=BG_COLOUR,
            fg=TEXT_COLOUR,
            font=FONT,
            padx=5,
            pady=5,
        )
        self.text_widget1.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget1.configure(cursor="arrow", state=NORMAL)
        # bottom label
        bottom_label1 = Label(self.sub, bg=BG_GRAY, height=80)
        bottom_label1.place(relwidth=1, rely=0.825)
        # scroll bar
        scrollbar1 = Scrollbar(self.text_widget1)
        scrollbar1.place(relheight=1, relx=0.974)
        scrollbar1.configure(command=self.text_widget1.yview)
        msg1 = f"Enter the chart type\n1. Pairplot\n2.Bar_chart\n3.Pie_chart\n4. Scatterplot\n\nFollowed by independent parameters which are space separated\n\nFollowed by vs\n\nFollowed by dependent parameters which are space separated and can be index or strings\n\n"
        msg1 += f"Example: Scatterplot {headers[0]} vs {headers[1]}\n\nOR \n\nScatterplot 0 vs 1\n\n"
        msg1 += "The headers in the data are\n\n"
        for i, j in enumerate(headers):
            msg1 += f"{i} {j}\n"
        self.text_widget1.insert(END, msg1)
        # message entry box
        self.msg_entry1 = Entry(bottom_label1, bg=BG_COLOUR1, fg=TEXT_COLOUR, font=FONT)
        self.msg_entry1.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry1.focus()
        self.msg_entry1.bind("<Return>", self._on_enter_vis)
        # send button
        send_button1 = Button(
            bottom_label1,
            text="Visualize",
            font=FONT_BOLD,
            width=10,
            bg=BG_GRAY,
            command=lambda: self._on_enter_vis(None),
        )
        send_button1.place(relx=0.70, rely=0.008, relheight=0.06, relwidth=0.22)
        # help button
        help_button1 = Button(
            head_label1, text="Help", font=FONT_BOLD, width=4, bg=BG_GRAY, command=help
        )
        help_button1.place(relx=0.72, rely=0.008, relheight=0.4, relwidth=0.3)
        # CSV view button
        csv_button1 = Button(
            head_label1, text="DataFrame", font=FONT_BOLD, width=4, bg=BG_GRAY, command=self.call_tree
        )
        csv_button1.place(relx=0.12, rely=0.008, relheight=0.4, relwidth=0.2)
        self.sub.mainloop()

    def _setup_feedback(self):
        """
        Used to create a separate window for feedback input. Here the feedback can be provided in the given format
        Send button and also Shift+Enter can be used to enter plaintext feedback query and 
        on success the retraining can be done for the model. Relevant error messages are displayed as necessary.         
        """
        self.feed = Toplevel()
        self.feed.title("Feedback")
        self.feed.resizable(width=True, height=True)
        self.feed.configure(width=470, height=550, bg=BG_COLOUR1)
        # head label
        head_label2 = Label(
            self.feed,
            bg=BG_COLOUR1,
            fg=TEXT_COLOUR,
            text="Feedback",
            font=FONT_BOLD,
            pady=10,
        )
        head_label2.place(relwidth=1)
        # tiny divider
        line2 = Label(self.feed, width=450, bg=BG_GRAY)
        line2.place(relwidth=1, rely=0.07, relheight=0.012)
        # text widget
        self.text_widget2 = Text(
            self.feed,
            width=20,
            height=2,
            bg=BG_COLOUR2,
            fg=TEXT_COLOUR,
            font=FONT,
            padx=5,
            pady=5,
        )
        self.text_widget2.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget2.configure(cursor="arrow", state=NORMAL)
        # bottom label
        bottom_label2 = Label(self.feed, bg=BG_GRAY, height=80)
        bottom_label2.place(relwidth=1, rely=0.825)
        # scroll bar
        scrollbar2 = Scrollbar(self.text_widget2)
        scrollbar2.place(relheight=1, relx=0.974)
        scrollbar2.configure(command=self.text_widget2.yview)
        msg2 = f"Enter your query and the reply you were expecting in the following format and then Press Send button\n\n"
        msg2 += 'Example:\n\n Query: What is your age?\n\n\nReply: I am not that old\n\n\nUser Entry:\n\n\ndescription_tag_of_feeback_without_spaces|\n"What is your age?",\n"How old are you?"|\n"I am not that old","I am quite young"\n\nEnter Send Button after typing message or press Shift Enter'
        self.text_widget2.insert(END, msg2)
        # message entry box
        self.msg_entry2 = Entry(bottom_label2, bg=BG_COLOUR1, fg=TEXT_COLOUR, font=FONT)
        self.msg_entry2.place(relwidth=0.64, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry2.focus()
        self.msg_entry2.bind("<Shift_L><Return>", self._on_enter_fed)
        self.msg_entry2.bind("<Shift_R><Return>", self._on_enter_fed)
        # send button
        send_button1 = Button(
            bottom_label2,
            text="Send",
            font=FONT_BOLD,
            width=10,
            bg=BG_GRAY,
            command=lambda: self._on_enter_fed(None),
        )
        send_button1.place(relx=0.70, rely=0.008, relheight=0.06, relwidth=0.22)
        # help button
        help_button1 = Button(
            head_label2, text="Help", font=FONT_BOLD, width=4, bg=BG_GRAY, command=help
        )
        help_button1.place(relx=0.62, rely=0.4, relheight=0.4, relwidth=0.3)
        self.feed.mainloop()

    def _on_enter_fed(self, event):
        """
        This function is used to get the entry of feedback data on press of the send button
        """
        flag = 0
        msg4 = self.msg_entry2.get()
        if len(msg4) > 0:
            # Get the list of tags from the json file intents.json
            tags = list()
            with open("intents.json", "r") as f:
                intents = json.load(f)
            for intent in intents["intents"]:
                tag = intent["tag"]
                tags.append(tag)
            msg = msg4[0 : msg4.find("|")]
            rem_msg = msg4[msg4.find("|") + 1 :]
            if msg not in tags:
                flag = 0
            else:
                flag = 1
            # Adding tag to json
            msg3 = ",{"
            msg3 += f'"tag" : "{msg}",'
            # Adding patterns to json
            patterns_list = rem_msg[0 : rem_msg.find("|")].strip()
            rem_msg = rem_msg[rem_msg.find("|") + 1 :]
            if len(patterns_list) > 0:
                msg3 += f'"patterns" : [{patterns_list}],'
                responses_list = rem_msg.strip()
                if len(responses_list) > 0:
                    msg3 += f'"responses" :[{responses_list}]'
                    msg3 += "}"
                    print(msg3)
                else:
                    # Done so that message doesn't start with a comma any more
                    msg3 = "." + msg3
            else:
                # Done so that message doesn't start with a comma any more
                msg3 = "." + msg3
            # Adding responses to json

            if (
                check_json(msg3[1:]) == True
                and msg3.startswith(",")
                and msg3.endswith("}")
            ):
                f = open("temp.json", "w")
                f.write('{ "intents" : [')
                f.write(msg3[1:])
                f.write("]}")
                f.close()
                os.remove("temp.json")
                if flag == 0:
                    with open("intents.json", "r+") as f:
                        lines = f.readlines()
                        f.seek(0)
                        f.truncate()
                        f.writelines(lines[0:-2])
                        f.write(msg3)
                        f.write("\n")
                        f.write("  ]\n")
                        f.write("}")
                        f.write("\n")
                    import train

                    restart()
                else:
                    self.text_widget2.delete(1.0, END)
                    msg2 = "Error Tag name already exists, Please Retry!\n\n"
                    msg2 += f"Enter your query and the reply you were expecting in the following format and then Press Send button\n\n\n"
                    msg2 += 'Example:\n\n Query: What is your age?\n\n\nReply: I am not that old\n\n\nUser Entry:\n\n\ndescription_tag_of_feeback_without_spaces|\n"What is your age?",\n"How old are you?"|\n"I am not that old","I am quite young"\n\nEnter Send Button after typing message or press Shift Enter'
                    self.text_widget2.insert(1.0, msg2)

            else:
                messagebox.showerror("Information", f"Incorrect Input format")
                self.text_widget2.delete(1.0, END)
                msg2 = "Error Please Retry!\n\n"
                msg2 += f"Enter your query and the reply you were expecting in the following format and then Press Send button\n\n\n"
                msg2 += 'Example:\n\n Query: What is your age?\n\n\nReply: I am not that old\n\n\nUser Entry:\n\n\ndescription_tag_of_feeback_without_spaces|\n"What is your age?",\n"How old are you?"|\n"I am not that old","I am quite young"\n\nEnter Send Button after typing message or press Shift Enter'
                self.text_widget2.insert(1.0, msg2)
        else:
            self.text_widget2.delete(1.0, END)
            msg2 = "Empty tags, patterns or responses not Accepted! Please Retry\n\n"
            msg2 += f"Enter your query and the reply you were expecting in the following format and then Press Send button\n\n\n"
            msg2 += 'Example:\n\n Query: What is your age?\n\n\nReply: I am not that old\n\n\nUser Entry:\n\n\ndescription_tag_of_feeback_without_spaces|\n"What is your age?",\n"How old are you?"|\n"I am not that old","I am quite young"\n\nEnter Send Button after typing message or press Shift Enter'
            self.text_widget2.insert(1.0, msg2)

    def _on_enter_vis(self, event):
        """
        Function is used to get the parameters list and check if it is in the correct format.
        If yes then based on the input, the correct visualization is displayed, else relevant
        error message needs to be displayed.
        
        Plot_name Indep vars list vs Dependent vars list
        """
        parameters = self.msg_entry1.get()
        print(parameters)
        flag1 = 0
        flag = 0
        chart_type = 1
        num_of_independent = 0
        headers = self._headers
        params = list()
        input_vars = list()
        #input_vars = list(parameters.split())
        if "vs" in parameters:
            input_vars += list(parameters.split("vs"))
            input_vars[0] = input_vars[0].strip()
            input_vars[1] = input_vars[1].strip()
            print(input_vars)

        elif "vs" in parameters:
            input_vars += list(parameters.split("Vs"))
            input_vars[0] = input_vars[0].strip()
            input_vars[1] = input_vars[1].strip()
            print(input_vars)
        elif "VS" in parameters:
            input_vars += list(parameters.split("VS"))
            input_vars[0] = input_vars[0].strip()
            input_vars[1] = input_vars[1].strip()
            print(input_vars)
        elif ("Pie_chart" in parameters or '3' in parameters):
            parameters+=" vs "
            input_vars += list(parameters.split("vs"))
            input_vars[0] = input_vars[0].strip()
            print(input_vars)
        else:
            #When the name of the chart type is not given then we try to perform matched with some template formats that we defined.
            if(' by ' in parameters):
                
                input_vars += list(parameters.split("by"))
                temp = input_vars[0].strip()
                input_vars[0] = "Bar_chart "+input_vars[1].strip()
                input_vars[1] = temp.strip()
                parameters = "Bar_chart "+ input_vars[0]+" vs " +input_vars[1]
            elif(' wise ' in parameters):
                if(' where ' in parameters and ' is ' in parameters):
                    parameters1 = parameters[0:parameters.find(' where ')]
                    head = parameters[len(parameters1)+len(' where '):parameters.find(' is ')]
                    query = parameters[parameters.find(' is ')+3:].strip()
                    input_vars += list(parameters1.split("wise"))
                    input_vars[0] = "Bar_chart "+input_vars[0].strip()
                    input_vars[1] = input_vars[1].strip()
                    parameters = input_vars[0]+" vs " +input_vars[1]
                    if head.lower() in headers:
                        self._df=self._df[self._df[head] == query]
                        print(self._df)
                    else:
                        pass
                elif('distribution' in parameters):
                    parameters = parameters[0:parameters.find('distribution')]
                    input_vars += list(parameters.split("wise"))
                    input_vars[0] = "Scatterplot "+input_vars[0].strip()
                    input_vars[1] = input_vars[1].strip()
                    parameters = "Scatterplot "+ input_vars[0]+" vs " +input_vars[1]
                else:
                    input_vars += list(parameters.split("wise"))
                    input_vars[0] = "Bar_chart "+input_vars[0].strip()
                    input_vars[1] = input_vars[1].strip()
                    parameters = "Bar_chart "+ input_vars[0]+" vs " +input_vars[1]
            else:
                flag1=1
        #Check if chart type passed in the first part of input_vars is in charts list
        # Store the number of independent variables in num_of_independent
        #Number of independent variables can be found using the length of variables before vs
        #Subtract 1 since there can be chart_type entered, if not entered chart_type then don't subtract 1 
        if flag1==1:
            pass
        else:
            if(input_vars[0].split()[0].capitalize() in charts): 
                chart_type = charts.index(input_vars[0].split()[0].capitalize())+1
                num_of_independent = len(input_vars[0].split())-1
                params = params+input_vars[0].split()[1:]+input_vars[1].split()
                print(chart_type, charts[chart_type-1]) 
            elif(input_vars[0].split()[0].lower() in ['1','2','3','4']):
                chart_type = int(input_vars[0].split()[0])
                num_of_independent = len(input_vars[0].split())-1
                params = params+input_vars[0].split()[1:]+input_vars[1].split()
                print(chart_type, charts[chart_type-1])  
            elif (input_vars[0].split()[0].lower() in headers):
                #Default chart type is Pairplot
                chart_type = 1
                num_of_independent = len(input_vars[0].split())
                params = params+[input_vars[0].split()[0]]+input_vars[1].split()
                print(chart_type, charts[chart_type-1])  
            else:
                flag1 = 1 
            if flag1==1:
                pass    
            input_vars = [num_of_independent]+[charts[chart_type-1]]+params
            print(input_vars)
            params = [p.lower() for p in params]
            print(params)
            for index, ind_vars in enumerate(params):
                flag = 0
                # Read each character in params[n]
                for char in ind_vars:
                    if char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                        continue
                    else:
                        flag = 1
                        break
                if flag == 0:
                    params[index] = headers[int(ind_vars)]
                    input_vars[index + 2] = headers[int(ind_vars)]
                elif flag == 1:
                    # Case when params[n] is not an Integer
                    if (
                        ind_vars.lower().capitalize() not in headers
                        and ind_vars.lower() not in headers
                        and ind_vars.upper() not in headers
                        and ind_vars not in headers
                    ):
                        flag = 2
                        break
                    else:
                        for index, header in enumerate(headers):
                            if ind_vars.lower() == header.lower():
                                params[params.index(header)] = header
                                input_vars[params.index(header) + 2] = header
                        pass

            if flag != 2:
                ind_variable = input_vars[2 : 2 + num_of_independent]
                dep_variable = input_vars[num_of_independent + 2 :]
                print("The independent variables are\n", ind_variable)
                print("The dependent variables are \n", dep_variable)
                df = self._df
                try:
                    if chart_type == 1:
                        plt.style.use("seaborn")
                        fig = sns.pairplot(
                            x_vars=ind_variable, y_vars=dep_variable, data=df
                        )
                        for ax in fig.axes.flat[:2]:
                            ax.tick_params(axis="x", labelrotation=90)
                            fig.fig.set_size_inches(20, 20)
                        plt.title("PAIRPLOT")
                        plt.tight_layout(pad=10)
                        plt.show()
                    elif chart_type == 2:
                        for ind_vars in ind_variable:
                            for dep_vars in dep_variable:
                                data_x = df[ind_vars]
                                data_y = df[dep_vars]
                                plt.style.use("seaborn")
                                fig = plt.bar(data_x, data_y, color="blue")
                                plt.xlabel(ind_vars)
                                plt.ylabel(dep_vars)
                                plt.title("BAR PLOT")
                                plt.tight_layout(pad=6)
                                plt.show()
                    elif chart_type == 3:
                        for ind_vars in ind_variable:
                            df[ind_vars].value_counts().plot.pie(
                            autopct="%0.2f%%", radius=1.4
                        )
                            plt.title("PIE PLOT")
                            plt.show()
                        for dep_vars in dep_variable:
                            df[dep_vars].value_counts().plot.pie(
                            autopct="%0.2f%%", radius=1.4
                        )
                            plt.title("PIE PLOT")
                            plt.show()
                    elif chart_type == 4:
                        for ind_vars in ind_variable:
                            for dep_vars in dep_variable:
                                plt.style.use("seaborn")
                                plt.scatter(df[ind_vars], df[dep_vars])
                                plt.title(f"{ind_vars} vs {dep_vars}")
                                plt.tight_layout(pad=6)
                                plt.show()
                except Exception as e:
                    print(e)
                else:
                    pass
            else:
                pass

    
    def _setup_treeview(self):
        """
        The Function to Set up the treeview in a new Window and to display DataFrame
        """
        self.tree = Toplevel()
        self.tree.resizable(width=True, height=True) 
        self.tree.configure(width=470, height=550, bg=BG_COLOUR4)        
        df = self._df

        # Frame for TreeView
        frame1 = LabelFrame(self.tree, text="DataFrame Data")
        frame1.place(relx=0.1, rely=0.1, relheight=0.8, relwidth=0.8)
        # Treeview Widget
        tv1 = ttk.Treeview(frame1)
        tv1.place(relheight=1, relwidth=1) 

        treescrolly = Scrollbar(frame1, orient="vertical", command=tv1.yview) 
        treescrollx = Scrollbar(frame1, orient="horizontal", command=tv1.xview) 
        tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set) 
        treescrollx.pack(side="bottom", fill="x") 
        treescrolly.pack(side="right", fill="y") 
        tv1.delete(*tv1.get_children())
        tv1["column"] = list(df.columns)
        tv1["show"] = "headings"
        for column in tv1["columns"]:
            tv1.heading(column, text=column) 

        df_rows = df.to_numpy().tolist() # turns the dataframe into a list of lists
        for row in df_rows:
            tv1.insert("", "end", values=row) # inserts each list into the treeview. 
        self.tree.mainloop()
        

    def call_tree(self):
        """Call the function to Set up the treeview to display DataFrame"""
        self._setup_treeview()
        
    
    def _on_enter_pressed(self, event):
        """
        This function is used to get the response of query on press of the send button or on Enter key
        """
        msg = self.msg_entry.get()
        self._insert_message(msg, "You")

    def _insert_message(self, msg, sender):
        """
        Depending on user input and response from chatbot perform either display of the return message or open relevant window
        """
        if not msg:
            return

        self.msg_entry.delete(0, END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)

        reply = get_response(msg)
        if reply[-13:] != "Visual_Create":
            msg2 = f"{bot_name}: {reply}\n\n"
            self.text_widget.configure(state=NORMAL)
            self.text_widget.insert(END, msg2)
            self.text_widget.configure(state=DISABLED)
            self.text_widget.see(END)

        else:
            name = reply[:-13]
            passw = keyring.get_password("Visual_Chatbot_Database", "rahul")
            user = "postgres"
            database = "Visual_Chatbot_Database"
            text = (
                "postgresql+psycopg2:///?user="
                + user
                + "&password="
                + passw
                + "&database="
                + database
            )
            postgreSQLconnection = create_engine(text)
            postgreSQLconnection = postgreSQLconnection.connect()
            df1 = pd.read_sql(f'SELECT * from "{name}"', postgreSQLconnection)
            print(df1)
            headers = df1.columns.values
            print(headers)
            postgreSQLconnection.close()
            self._setup_visual(headers, df1)

    def feedback(self):
        self._setup_feedback()


    def encode(self):
        """
        On clicking input_csv button this function is called. It takes in no parameters.
        Use a filedialog.askopenfile method to get the file name of the input csv.
        Then using the get_csvtodb method pass the input file path and store the csv as a Table in the
        database called Visual_Chatbot_Database, and name the table according to the csv file imported.
        Then add the intents to intents.json using file methods open, read, write.
        Store the table name in a text file called imported_file.txt.
        """
        try:
            file1 = filedialog.askopenfile(
                defaultextension=".csv",
                filetypes=[("Comma Separated Value", "*.csv"), ("All Files", "*.*")],
            )
            input_file_path = file1.name
            returned = get_csvtodb(input_file_path)
            if (returned==-1):
                print("Can't automatically clean data")
                msg1 = "CSV data is unclean and can't be cleaned automatically.Please do a manual cleaning and retry"
                self.msg_entry.delete(0, END)
                self.text_widget.configure(state=NORMAL)
                self.text_widget.insert(END, msg1)
                self.text_widget.configure(state=DISABLED)
                messagebox.showerror("Information", f"CSV data in {file1.name} is unclean and can't be automatically cleaned")   
            elif (returned==-2):
                print("DB connection error")
                msg1 = "Couldn't connect to DB"
                self.msg_entry.delete(0, END)
                self.text_widget.configure(state=NORMAL)
                self.text_widget.insert(END, msg1)
                self.text_widget.configure(state=DISABLED)
                messagebox.showerror("Information", "Could not connect to to Database")
            else:
                print(input_file_path)
                file_name = Path(input_file_path).stem
                imported_files.append(file_name)

                # Check if the Database Table exists in the json file
                flag = 0
                with open("intents.json", "r") as f:
                    read = f.readlines()
                    for sentence in read:
                        line = sentence.split()
                        if f'"{file_name}Visual_Create"' in line:
                            flag = 1
                            break
                        else:
                            pass

                # Add intents.json entry for imported Data Table if it doesn't exists in the json file already
                if flag == 0:
                    # Write the json data to intents.json using open, write, seek, truncate, read, readlines, writelines methods
                    with open("intents.json", "r+") as f:
                        lines = f.readlines()
                        f.seek(0)
                        f.truncate()
                        f.writelines(lines[0:-2])
                        f.write(",{\n")
                        f.write('      "tag" : "{0}",\n'.format(file_name))
                        f.write('      "patterns" : [\n')
                        f.write('        "{0} data",\n '.format(file_name))
                        f.write(
                            '        "Show me a visualization of {0}"\n      ],'.format(
                                file_name
                            )
                        )
                        f.write('      "responses" : [\n')
                        f.write('        "{0}Visual_Create"\n'.format(file_name))
                        f.write("      ]\n")
                        f.write("    }\n")
                        f.write("\n")
                        f.write("  ]\n")
                        f.write("}")
                        f.write("\n")
                    import train

                    restart()
                else:
                    pass
        except Exception as e:
            messagebox.showerror("Information", "Error reading csv. Retry")
            print(e)


def help():
    link = "help.html"
    link1 = "run.html"
    webbrowser.open(link)
    webbrowser.open(link1)


if __name__ == "__main__":
    main()
