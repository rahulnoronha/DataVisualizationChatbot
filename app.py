from tkinter import *
from tkinter import filedialog
from chat import get_response, bot_name
from db import get_csvtodb
from pathlib import Path
from sqlalchemy import create_engine
from pathlib import Path
from matplotlib import pyplot as plt
import pandas as pd
import keyring
import matplotlib
import webbrowser
import seaborn as sns

# Colours
BG_GRAY = "#A9A9A9" #dark gray
BG_COLOUR = "#FF8C00" #dark orange
BG_COLOUR1 = "#FFFFFF" #White
BG_COLOUR2 = "#FF0000" #red
TEXT_COLOUR = "#000000" #Black

# Fonts
FONT = "Helvetica 14"
FONT_BOLD = "Helvetica 13 bold"

# To store a list of already imported Dataset CSVs
imported_files = []

#Main Function
def main():
    app = ChatApplication()
    app.run()


#Restart Function
def restart():
    import sys
    print("argv was",sys.argv)
    print("sys.executable was", sys.executable)
    print("restart now")
    import os
    os.execv(sys.executable, ['python','app.py'])     
    
    
class ChatApplication:
    def __init__(self):
        self.window = Tk()
        self._setup_main_window()

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        self.window.title("Chat")
        self.window.resizable(width=True, height=True)
        self.window.configure(width=470, height=550, bg=BG_COLOUR1)
        # head label
        head_label = Label(self.window, bg=BG_COLOUR1, fg=TEXT_COLOUR,
                           text="Welcome", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)
        # tiny divider
        line = Label(self.window, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)
        # text widget
        self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOUR, fg=TEXT_COLOUR,
                                font=FONT, padx=5, pady=5)
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
        self.msg_entry = Entry(
            bottom_label, bg=BG_COLOUR1, fg=TEXT_COLOUR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06,
                             rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)

        # send button
        send_button = Button(bottom_label, text="Send", font=FONT_BOLD, width=10, bg=BG_GRAY,
                             command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.70, rely=0.008, relheight=0.06, relwidth=0.22)

        # Input csv button
        input_button = Button(bottom_label, text="Input CSV",
                              font=FONT_BOLD, width=10, bg=BG_GRAY, command=encode)
        input_button.place(relx=0.48, rely=0.008,
                           relheight=0.06, relwidth=0.22)
        # Help Button
        help_button = Button(bottom_label,text="Help",
                             font=FONT_BOLD, width=4, bg=BG_GRAY,command=help)
        help_button.place(relx=0.92, rely=0.008,
                           relheight=0.06, relwidth=0.08)
    
    
    def _setup_visual(self,headers,df):
        self._headers = headers
        self._df = df
        self.sub = Toplevel()
        self.sub.title("Data Visualizations")
        self.sub.resizable(width=True, height=True)
        self.sub.configure(width=470, height=550, bg=BG_COLOUR1)
        # head label
        head_label1 = Label(self.sub, bg=BG_COLOUR1, fg=TEXT_COLOUR,
                           text="Graphs", font=FONT_BOLD, pady=10)
        head_label1.place(relwidth=1)
        # tiny divider
        line1 = Label(self.sub, width=450, bg=BG_GRAY)
        line1.place(relwidth=1, rely=0.07, relheight=0.012)
        # text widget
        self.text_widget1 = Text(self.sub, width=20, height=2, bg=BG_COLOUR, fg=TEXT_COLOUR,
                                font=FONT, padx=5, pady=5)
        self.text_widget1.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget1.configure(cursor="arrow", state=NORMAL)
        # bottom label
        bottom_label1 = Label(self.sub, bg=BG_GRAY, height=80)
        bottom_label1.place(relwidth=1, rely=0.825)
        # scroll bar
        scrollbar1 = Scrollbar(self.text_widget1)
        scrollbar1.place(relheight=1, relx=0.974)
        scrollbar1.configure(command=self.text_widget1.yview)
        msg1 = f"Enter a number\n1. Pairplot\n2.Bar chart\n3.Pie chart\n4. Scatterplot\nfollowed by the number of independent variables followed by parameters space separated\n\n"
        msg1+="The headers in the data are\n\n"
        for i,j in enumerate(headers):
            msg1+=f"{i} {j}\n"
        self.text_widget1.insert(END, msg1)
        # message entry box
        self.msg_entry1 = Entry(
            bottom_label1, bg=BG_COLOUR1, fg=TEXT_COLOUR, font=FONT)
        self.msg_entry1.place(relwidth=0.74, relheight=0.06,
                             rely=0.008, relx=0.011)
        self.msg_entry1.focus()
        self.msg_entry1.bind("<Return>", self._on_enter_vis)
        # send button
        send_button1 = Button(bottom_label1, text="Visualize", font=FONT_BOLD, width=10, bg=BG_GRAY,
                             command=lambda: self._on_enter_vis(None))
        send_button1.place(relx=0.70, rely=0.008, relheight=0.06, relwidth=0.22)
        #help button
        help_button1 = Button(bottom_label1,text="Help",
                             font=FONT_BOLD, width=10, bg=BG_GRAY,command=help)
        help_button1.place(relx=0.92, rely=0.008,
                           relheight=0.06, relwidth=0.08)
        self.sub.mainloop()
        
        
    def _on_enter_vis(self,event):
        parameters = self.msg_entry1.get()
        a = list(parameters.split())
        headers = self._headers
        chart_type = int(a[0])
        num = int(a[1])
        print(a)
        b=a[num+2:]
        flag=0
        for i in b:
            if i not in headers:
                self.sub.destroy()
                flag = 1
                
                
        if flag!=1:    
            ind_variable = a[2:2+num]
            dep_variable = a[num+2:]
            df = self._df
            try:
                if chart_type==1:
                    fig = sns.pairplot(x_vars=ind_variable,y_vars=dep_variable,data=df)
                    for ax in fig.axes.flat[:2]:
                        ax.tick_params(axis='x', labelrotation=90)
                        fig.fig.set_size_inches(20,20)
                    plt.title('PAIRPLOT')
                    plt.show()     
                    print("The independent variables are\n",ind_variable)
                    print("The dependent variables are \n",dep_variable)
                elif chart_type==2:
                    if len(ind_variable)==len(dep_variable) and len(ind_variable)==1:
                        data_x = df[ind_variable[0]]
                        data_y = df[dep_variable[0]]
                        plt.xlabel(ind_variable[0])
                        plt.ylabel(dep_variable[0])
                        plt.title("BAR PLOT")
                        plt.bar(data_x, data_y, color='blue')
                        plt.show()
                    else:
                        pass
                elif chart_type==3:
                    df[ind_variable].value_counts().plot.pie(autopct='%0.2f%%',radius=2)
                    plt.show()
                elif chart_type==4:
                    for i in ind_variable:
                        for j in dep_variable:
                            plt.scatter(df[i],df[j])
                            plt.title(f'{i} vs {j}')
                            plt.show()
            except error as e:
                print(error)
            else:
                pass
        else:
            pass
        
    
    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "You")


    def _insert_message(self, msg, sender):
        if not msg:
            return

        self.msg_entry.delete(0, END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_widget.configure(state=NORMAL)
        self.text_widget.insert(END, msg1)
        self.text_widget.configure(state=DISABLED)

        reply = get_response(msg)
        if reply[-13:] != 'Visual_Create':
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
            text = "postgresql+psycopg2:///?user="+user + \
                "&password="+passw+"&database="+database
            postgreSQLconnection = create_engine(text)
            postgreSQLconnection = postgreSQLconnection.connect()
            df1 = pd.read_sql(
                f"SELECT * from \"{name}\"", postgreSQLconnection)
            print(df1)
            headers = df1.columns.values
            print(headers)
            postgreSQLconnection.close()
            self._setup_visual(headers,df1)

        
def encode():
    """
    On clicking input_csv button this function is called. It takes in no parameters.
    Use a filedialog.askopenfile method to get the file name of the input csv.
    Then using the get_csvtodb method pass the input file path and store the csv as a Table in the
    database called Visual_Chatbot_Database, and name the table according to the csv file imported.
    Then add the intents to intents.json using file methods open, read, write.
    Store the table name in a text file called imported_file.txt.
    """
    file1 = filedialog.askopenfile(defaultextension='.csv', filetypes=[
                                   ('Comma Separated Value', '*.csv'),('All Files', '*.*')])
    input_file_path = file1.name
    get_csvtodb(input_file_path)
    print(input_file_path)
    file_name = Path(input_file_path).stem
    imported_files.append(file_name)

    # Check if the Database Table exists in the json file
    flag = 0
    with open('intents.json', 'r') as f:
        read = f.readlines()
        for sentence in read:
            line = sentence.split()
            if(f'"{file_name}Visual_Create"' in line):
                flag = 1
                break
            else:
                pass
                

    # Add intents.json entry for imported Data Table if it doesn't exists in the json file already
    if flag == 0:
        # Write the json data to intents.json using open, write, seek, truncate, read, readlines, writelines methods
        with open('intents.json', 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            f.writelines(lines[0:-2])
            f.write(',{\n')
            f.write('      "tag" : "{0}",\n'.format(file_name))
            f.write('      "patterns" : [\n')
            f.write('        "{0} data",\n '.format(file_name))
            f.write(
                '        "Show me a visualization of {0}"\n      ],'.format(file_name))
            f.write('      "responses" : [\n')
            f.write('        "{0}Visual_Create"\n'.format(file_name))
            f.write('      ]\n')
            f.write('    }\n')
            f.write('\n')
            f.write('  ]\n')
            f.write('}')
            f.write('\n')
        # Store imported csv dataset names in a file
        with open('imported_file.txt', 'a') as f:
            f.write(imported_files[-1])
            f.write(' ')
        import train
        restart()
    else:
        pass


def help():
    link = "https://rahuldatavisualization.blogspot.com/2021/07/data-visualization-bot-help.html"
    webbrowser.open(link)



if __name__ == "__main__":
    main()
    
