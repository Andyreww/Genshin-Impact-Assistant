import google.generativeai as genai
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

def load_data(filepaths, encoding='latin1'):
    data_contexts = {}
    for name, path in filepaths.items():
        df = pd.read_csv(path, encoding=encoding)
        data_contexts[name] = df.to_dict(orient='records')
    return data_contexts

def get_api_key():
    load_dotenv("creds.env")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("API key not found. Please check your creds.env file.")
    else:
        genai.configure(api_key=api_key)
        print("API key loaded successfully.")
    return api_key

def get_table_names(conn):
    table_names = []
    tables = conn.execute('SELECT name FROM sqlite_master WHERE type="table"')
    for table in tables.fetchall():
        table_names.append(table[0])
    return table_names

def get_column_names(conn, table_name):
    columns = conn.execute(f"PRAGMA table_info('{table_name}');").fetchall()
    return [col[1] for col in columns]

def get_database_info(conn):
    table_dict = []
    for table_name in get_table_names(conn):
        column_names = get_column_names(conn, table_name)
        table_dict.append({"table_name": table_name, "column_names": column_names})
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

def make_one_liner(sql_query):
    one_liner = ' '.join(sql_query.strip().split())
    one_liner = one_liner.replace("```", "").replace("sql", "").replace(";", "")
    return one_liner

def setup_model():
    generation_config = {
        "temperature": 0.4,
        "top_p": 1,
        "top_k": 32,
        "max_output_tokens": 6000,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        safety_settings=safety_settings
    )
    return model.start_chat(history=[])

def generate_sql_query(chat, prompt_p1, question):
    response = chat.send_message(prompt_p1 + question)
    return make_one_liner(response.text)

def generate_response(chat, assistant_instructions, question, context, weapon_obtainability_context):
    response = chat.send_message(assistant_instructions + question + context + weapon_obtainability_context)
    return response.text.replace("*", "")

def main():
    data_files = {
        "character_info": "C:\\Users\\ajang\\OneDrive\\Desktop\\Genshin-Impact-Assistant\\Context\\genshin.csv",
        "weapon_info": "C:\\Users\\ajang\\OneDrive\\Desktop\\Genshin-Impact-Assistant\\Context\\genshin_weapons_v6.csv",
        "f2p_weapon_info": "C:\\Users\\ajang\\OneDrive\\Desktop\\Genshin-Impact-Assistant\\Context\\F2P_genshin_weapons.csv"
    }

    data_contexts = load_data(data_files)
    api_key = get_api_key()
    if not api_key:
        return

    conn = sqlite3.connect('GenshinPlayerStats.db')
    schema = get_database_info(conn)
    schema_str = "\n".join(f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}" for table in schema)
    
    chat = setup_model()
    
    prompt_p1 = (
        "JUST GIVE ME THE SQL CODE, DONT GIVE AN EXPLANATION ON HOW TO IMPROVE IT JUST GIVE ME THE CODE FOR THE QUERY. "
        "You are an expert in converting English Questions to SQL code! The SQL database has the name GenshinPlayerStats.db and has the following schema " + schema_str + ",\n"
        "Example 1 - If a user asks about their character artifacts make sure to look into the Artifacts table and the Substats table in order\n"
        "to distinguish whose artifacts belong to whom. You have an ArtifactID and character column to distinguish it. Once you do find the values, make sure to\n"
        "only grab the columns pertaining to the character requested for and join both the Artifact table and the Substat table. Most of the time the user\n"
        "will just ask information pertaining to their character; a name could be something like 'Furina' or 'Hu Tao', pretty much the names of characters within\n"
        "the game Genshin Impact characters.\n Example 2 - What is the current weapon of my character?, the SQL command will be something like this\n"
        "SELECT Weapon FROM Weapons WHERE Character = 'character name here' LIMIT 1\n"
        "Example 2 - What is the current artifacts information for my character?, the SQL command will be something like this\n"
        "SELECT a.Character, a.Artifact, a.Stat AS MainStat, a.Amount AS MainStatAmount, s.Stat AS SubStat, s.Amount AS SubStatAmount FROM Artifacts a JOIN Substats s ON a.ArtifactID = s.ArtifactID WHERE a.Character = 'character name here'\n"
        "Example 3 - What is the name of my artifacts for my character?, the SQL command will be something like this\n"
        "SELECT Artifact FROM Artifacts WHERE Character = 'Furina',"
        "Example 4 - Based on my artifacts what would be a good Weapon to match Furina?, the SQL command will be something like this\n"
        "SELECT a.Character, a.Artifact, a.Stat AS MainStat, a.Amount AS MainStatAmount, s.Stat AS SubStat, s.Amount AS SubStatAmount FROM Artifacts a JOIN Substats s ON a.ArtifactID = s.ArtifactID WHERE a.Character = 'character name here'\n"
        "Example 5 - What are all of the names of all of the characters I own?, the SQL command will be something like this\n"
        "SELECT CharacterName FROM Characters,"
        "Example 6 - What are the names of all the Characters I have?, the SQL command will be something like this\n"
        "SELECT CharacterName FROM Characters,"
        "Just create a SQL Query based on the schema and the user's request and make sure its in 1 line."
        "Also the question might be a bit too broad so if the user is asking something such as 'how they can improve their character' then just return information of the Artifacts and Substats table\n"
        "if the user is asking how they can improve their weapon just return data from the Weapons table. What I am trying to say is that if part of the question has no co-relation to the SQL DB then try to approximate what data to search for but remember to follow the schema given"
    )

    assistant_instructions = (
        "IF THE USER IS ASKING A FOLLOW UP QUESTION PLEASE DON'T REFER TO THE DATABASE INFORMATION"
        "You are a Genshin Impact Assistant named 'TeyvMate' here to help users improve their characters and assist them on their Genshin Impact journey.\n"
        f"Here is context for all the characters within Genshin regarding their weapon type and etc {data_contexts['character_info']} in a Dictionary format in Python, and finally here is context about each and every weapon in Genshin Impact {data_contexts['weapon_info']} in a Dictionary format in Python. This data comes from a SQL Database containing information\n"
        "about the player or their friend's Genshin Impact account. Your goal is to digest this information and provide friendly, roleplaying answers\n"
        "as if you are in the world of Teyvat however this time be analytic and provide multiple answers with explanation in a list format, the world of Genshin Impact. Be quirky and fun like Paimon, but don't impersonate her, for reference I named you 'TeyvMate'.\n"
        "Avoid being too analytical; instead, speak to the user in a friendly manner, giving concise responses (MAX 5 sentences).\n"
        "Additionally, try to recommend an improvement in a string format.\n"
        "If you are recommending weapons please be sure to give them F2P(Free to play) which are weapons that are accessible for free and give them another option of a weapon that requires money\n"
    )

    weapon_obtainability_context = (
        f"Here are all the F2P (Free to Play) weapons that players can obtain naturally without spending money in the game: {data_contexts['f2p_weapon_info']}\n"
        "REMINDER: Deathmatch ISN'T FREE"
    )

    while True:
        question = input("Enter your question (or press Enter to exit): ")
        if not question:
            break

        sql_query = generate_sql_query(chat, prompt_p1, question)
        results = execute_sql_query(sql_query)
        context = f"This is the players database information in relation to the question asked: {results}\n. Here is all information of every character in Genshin: {data_contexts['character_info']}. Here is all information of every weapon in Genshin: {data_contexts['weapon_info']}\n"
        response = generate_response(chat, assistant_instructions, question, context, weapon_obtainability_context)
        print("\n")
        print("Question:", question)
        print(response)

if __name__ == "__main__":
    main()
