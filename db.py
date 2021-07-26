import sqlalchemy
from sqlalchemy import create_engine
from pathlib import Path
import pandas as pd
import keyring
#Database used name = "Visual_Chatbot_Database" 

def get_csvtodb(filename):
    #Connect to the Database
    """
    Connect to the local host Database and add the input csv to the localhost PostgreSQL database as a table with all headings as lowercase, and underscore separated formatted strings. 
    Returns -1 or -2 on different errors.
    """
    name = filename[:-4]
    name = Path(filename).stem
    passw = keyring.get_password("Visual_Chatbot_Database", "rahul")
    user="postgres"
    database="Visual_Chatbot_Database"
    text = "postgresql+psycopg2:///?user="+user+"&password="+passw+"&database="+database
    postgreSQLconnection = create_engine(text)
    postgreSQLconnection = postgreSQLconnection.connect()
    try:
        df = pd.read_csv(filename)
    except Exception as e:    
        df = pd.read_csv(filename,encoding='Latin-1')
    #Cleaning the DataFrame
    #Making headers consistent using list comprehension
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
  
    try:
        dbase = df.to_sql(name,postgreSQLconnection,if_exists='fail')
    except ValueError as vx:
        print(vx)
    except Exception as ex:
        print(ex)
        return -2
        
    else:
        print(f"PostgreSQL Table {name} has been created successfully.")
    
    df1 = pd.read_sql(f"SELECT * from \"{name}\"",postgreSQLconnection)
    print(df1)
    headers = df1.columns.values
    print(headers)
    postgreSQLconnection.close()
    
    
#Usage get_csvtodb("Datasets/Sales.csv")