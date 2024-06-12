import google.generativeai as genai
import sqlite3
import os
from dotenv import load_dotenv

print("Gemini Version:", genai.__version__)


#--------------------------------------------------------------------------------#
# Getting data from .env file holding API key
load_dotenv("creds.env")

# Debugging: Print the loaded API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("API key not found. Please check your creds.env file.")
else:
    genai.configure(api_key=api_key) # API key set up
    print("API key loaded successfully.")

#--------------------------------------------------------------------------------#
# Connecting to the SQL Database and getting schema
conn = sqlite3.connect('GenshinPlayerStats.db')
cursor = conn.cursor()

# Fetching Schema of the SQL DB
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

def get_table_names():
    table_names = []
    tables = conn.execute('Select name from sqlite_master where type="table"')
    for table in tables.fetchall():
        table_names.append(table[0])
    return table_names

def get_column_names(table_name):
    column_names = []
    columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()  
    for col in columns:
        column_names.append(col[1])
    return column_names

def get_database_info():
    table_dict = []
    for table_name in get_table_names():
        columns_name = get_column_names(table_name)
        table_dict.append({"table_name": table_name, "column_names": columns_name})
    return table_dict

def execute_sql_query(query):
    try:
        conn = sqlite3.connect('GenshinPlayerStats.db')
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return results
    except sqlite3.Error as e:
        print("An error occurred:", e)
        return None

schema = get_database_info()
schema_str = "\n".join(f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}" for table in schema)

#--------------------------------------------------------------------------------#
#Setting up Model
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
]

model = genai.GenerativeModel(
    model_name = "gemini-pro",
    generation_config=generation_config,
    safety_settings=safety_settings
)
#--------------------------------------------------------------------------------#
# Database AI

prompt_p1 = [
    f"You are an expert in converting English Questions to SQL code! The SQL database has the name GenshinPlayerStats.db and has the following schema {schema_str},\n"
    f"Example 1 - If a user asks about their character artifacts make sure to look into the Artifacts table and the Substats table in order\n"
    f"to distinguish whose artifacts belong to whom. You have an ArtifactID and character column to distinguish it. Once you do find the values, make sure to\n"
    f"only grab the columns pertaining to the character requested for and join both the Artifact table and the Substat table. Most of the time the user\n"
    f"will just ask information pertaining to their character; a name could be something like 'Furina' or 'Hu Tao', pretty much the names of characters within\n"
    f"the game Genshin Impact characters.\n Example 2 - What is the current weapon of my character?, the SQL command will be something like this\n"
    f"SELECT Weapon FROM Weapons WHERE Character = 'character name here' LIMIT 1\n"
    f"Example 2 - What is the current artifacts information for my character?, the SQL command will be something like this\n"
    f"SELECT a.Character, a.Artifact, a.Stat AS MainStat, a.Amount AS MainStatAmount, s.Stat AS SubStat, s.Amount AS SubStatAmount FROM Artifacts a JOIN Substats s ON a.ArtifactID = s.ArtifactID WHERE a.Character = 'character name here'\n"
    f"Example 3 - What is the name of my artifacts for my character?, the SQL command will be something like this\n"
    f"SELECT Artifact FROM Artifacts WHERE Character = 'Furina'",
    f"Just create a SQL Query based on the schema and the user's request and make sure its in 1 line and in the format of a string"
]




question = "How can I improve my Hu Tao to make her stronger"

prompt_parts = [prompt_p1[0], question]
response = model.generate_content(prompt_parts)
# To De-Bug
# print(response.text)
# print(type(response.text))

# Converts AI SQL Query to Readable SQL Code
def make_one_liner(sql_query):
    # Remove newline characters and extra spaces
    one_liner = ' '.join(sql_query.strip().split())
    # Remove ''' and 'sql'
    one_liner = one_liner.replace("```", "").replace("sql", "").replace(";", "")
    return one_liner


one_liner_query = make_one_liner(response.text)

# To De-Bug
#print(one_liner_query)


# Example usage:
results = execute_sql_query(one_liner_query)
#formatted_data = [item[0] for item in results]

# Edge Case if were going into both Artifacts table and Substat table.
# Cleans the response visually
characters = {}
keywords = {"ArtifactID"}

if any(keyword in results for keyword in keywords):
    try:
        for row in results:
            character, artifact, main_stat, main_stat_amount, sub_stat, sub_stat_amount = row
            if character not in characters:
                characters[character] = {}
            if artifact not in characters[character]:
                characters[character][artifact] = {'MainStat': {main_stat: main_stat_amount}, 'SubStats': []}
            characters[character][artifact]['SubStats'].append({sub_stat: sub_stat_amount})
    except Exception:
        pass

# To De-Bug
#print(results)
#print(schema_str)

#--------------------------------------------------------------------------------#
# Answering the Users Question
# Issue here
prompt_final = [
    f"You are a Genshin Impact Assistant aimed to help the user better improve their characters or just help them on their journey\n"
    f"through Genshin Impact. You will be provided the following database information that pertains to information the user is asking for which would\n"
    f"be this: {results}. That is data taken from a SQL Database that contains information of the player who is asking you questions about their Genshin\n"
    f"Impact accounts or either asking about a friends Genshin Impact Account. Your goal here is to digest all of this information and give an answer to the user\n"
    f"by acting like a friend and roleplay as if you are in the world of Teyvat which is the world of Genshin Impact. Please dont be too analytical with your responses,\n"
    f"talk to them like your there to help them in a friendly gesture and keep the responses to about 1-3 sentences in a string format."
]

prompt_parts_f = [prompt_final[0], question]
response2 = model.generate_content(prompt_parts_f)
if not response2._done:
    print("Error occurred during generation.")

    if hasattr(response2, 'error'):
        print(f"Error code: {response2.error.code}")
        print(f"Error message: {response2.error.message}")
    else:
        print("Detailed error information not available.")


print(response2)
