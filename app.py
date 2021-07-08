from tkinter import *
from tkinter import filedialog
from chat import get_response, bot_name
from db import get_csvtodb
from pathlib import Path
from sqlalchemy import create_engine
from pathlib import Path
import pandas as pd
import keyring


# Colours
BG_GRAY = "#A9A9A9" #dark gray
BG_COLOUR = "#FF8C00" #dark orange
BG_COLOUR1 = "#FFFFFF" #White
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
        self.window.configure(width=470, height=550, bg=BG_COLOUR)
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

        self.text_widget.see(END)


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


if __name__ == "__main__":
    main()
    
