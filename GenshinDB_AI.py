import google.generativeai as genai
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv

# De-Bug Gemini Version
# print("Gemini Version:", genai.__version__)
#--------------------------------------------------------------------------------#
# Gathering Data to help AI with context

# All Genshin Impact Characters
character_info_filepath = os.path.join("C:\\Users\\ajang\\OneDrive\\Desktop\\Genshin-Impact-Assistant\\Context", "genshin.csv")
characterInfo_fp = pd.read_csv(character_info_filepath, encoding='latin1')
character_dict_context = characterInfo_fp.to_dict(orient='records')

# All Weapon Information
weapon_info_filepath = os.path.join("C:\\Users\\ajang\\OneDrive\\Desktop\\Genshin-Impact-Assistant\\Context", "genshin_weapons_v6.csv")
weaponInfo_fp = pd.read_csv(weapon_info_filepath, encoding='latin1')
weapon_dict_context = weaponInfo_fp.to_dict(orient='records')

# All Free 2 Play Weapons
F2P_weapons_filepath = os.path.join("C:\\Users\\ajang\\OneDrive\\Desktop\\Genshin-Impact-Assistant\\Context", "F2P_genshin_weapons.csv")
F2P_weaponInfo_fp = pd.read_csv(F2P_weapons_filepath, encoding='latin1')
F2P_weapon_dict_context = F2P_weaponInfo_fp.to_dict(orient='records')
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
    model_name = "gemini-1.5-flash",
    generation_config=generation_config,
    safety_settings=safety_settings
)
chat = model.start_chat(history=[])
#--------------------------------------------------------------------------------#
# Database AI

prompt_p1 = (
    "JUST GIVE ME THE SQL CODE, DONT GIVE AN EXPLANATION ON HOW TO IMPROVE IT JUST GIVE ME THE CODE FOR THE QUERY"
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
    "if the user is asking how they can improve their weapon just return data from the Weapons table. What I am trying to say is that if part of the question has no co-relation to the SQL DB then try to approximate what data to search for but rememer to follow the schema given"
)






question = "Can you compare my Zhongli and Hu Tao Artifacts, which character should I focus on more?"

#prompt_parts = [prompt_p1[0], question]
#response = model.generate_content(prompt_parts)
response = chat.send_message(prompt_p1 + question)

# To De-Bug
# print("SQL Query:",response.text)
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
# print("Through One Liner Function:", one_liner_query)

# To De-Bug
# print(one_liner_query)


# Example usage:
results = execute_sql_query(one_liner_query)

# To De-Bug
# print("SQL INFO:", results)


# To De-Bug
#print(results)
#print(schema_str)

#--------------------------------------------------------------------------------#
# Answering the Users Question

assistant_instructions = (
    "You are a Genshin Impact Assistant named 'TeyvMate' here to help users improve their characters and assist them on their Genshin Impact journey.\n"
    f"You will be provided with the following database information: {results} WHICH IS THE PLAYERS INFORMATION AND RELATED TO THE QUESTION THEY ARE ASKING. Additionally, here is context for all the characters within Genshin regarding their weapon type and etc {character_dict_context} in a Dictionary format in Python, and finally here is context about each and every weapon in Genshin Impact {weapon_dict_context} in a Dictionary format in Python. This data comes from a SQL Database containing information\n"
    "about the player or their friend's Genshin Impact account. Your goal is to digest this information and provide friendly, roleplaying answers\n"
    "as if you are in the world of Teyvat however this time be analytic and provide multiple answers with explanation in a list format, the world of Genshin Impact. Be quirky and fun like Paimon, but don't impersonate her, for reference I named you 'TeyvMate'.\n"
    "Avoid being too analytical; instead, speak to the user in a friendly manner, giving concise responses (MAX 5 sentences).\n"
    "Additionally, try to recommend an improvement in a string format.\n"
    "Here are some example conversations:\n"
    "Example 1 - What weapon do you recommend for Keqing?\n"
    "Keqing, the Thundering Might of the Liyue Qixing, deserves a weapon that matches her swift strikes and electrifying personality! The Lion's Roar is a great choice for amplifying her Electro damage. If you're looking for a more refined option, the Aquila Favonia grants both damage and healing capabilities, making it a versatile companion for Keqing's battles.\n"
    "Example 2 - How should I build artifacts for Venti?\n"
    "Ah, Venti, the Anemo Archon! For the Windborne Bard, focus on artifacts that boost his Anemo damage and Energy Recharge. The Viridescent Venerer set is a top pick, enhancing his Swirl reactions and reducing enemies' Elemental Resistances. Pair it with artifacts that boost Energy Recharge to keep his Elemental Burst flowing like a gentle breeze across Mondstadt!\n"
    "Example 3 - Which weapon is best for Tartaglia in his ranged stance?\n"
    "Tartaglia, the formidable Hydro archer! When he's in his ranged stance, the Rust bow is a splendid choice, increasing his Normal Attack damage and optimizing his Hydro-infused shots. Alternatively, the Skyward Harp provides a mix of Crit Rate and AoE damage, ensuring each arrow sings with precision and power!\n"
    "Example 4 - Can you suggest an optimal team composition for Diluc?\n"
    "Of course! Diluc, the Darknight Hero, shines brightest when surrounded by a synergistic team. Pair him with characters like Bennett for Fire resonance and healing support. Adding an Anemo character such as Sucrose or Venti can enhance Elemental Reactions, while a Hydro character like Xingqiu provides additional Elemental damage and defensive shields.\n"
    "Example 5 - What artifacts should I prioritize for Ganyu?\n"
    "Ganyu, the Liyue Qixing's adeptus of Cryo! Equip her with artifacts that boost Cryo damage, such as the Blizzard Strayer set, to amplify her Frostflake Arrows. Focus on artifacts that increase her Crit Rate and Crit Damage to maximize her burst damage potential. Remember, precision is key when crafting her artifact set!\n"
    "If you are reccomending weapons please be sure to give them F2P(Free to play) which are weapons that are accessible for free and give them another option of a weapon that requires money\n"
)


context = f"This is the players info in relation to the question asked: {results}. Here is all information of every character in Genshin: {character_dict_context}. Here is all information of every weapon in Genshin: {weapon_dict_context}\n"
weapon_obtainability_context = f"Here are all the F2P (Free to Play) weapons that players can obtain naturally without spending money in the game: {F2P_weapon_dict_context}\n REMINDER: Deathmatch ISNT FREE"

response2 = chat.send_message(assistant_instructions + question + context + weapon_obtainability_context)
print("\n")
print("Question:", question)
print(response2.text.replace("*", ""))
