import assist_Functions as aF
import pandas as pd
import asyncio
import ast
import sqlite3
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from tabulate import tabulate

def main():
    uid = input("What is your in-game UID: ")
    if(len(uid) > 9 or not uid.isnumeric()):
        print("Not a Valid UID")
        return -1
    
    # Edgecase if player has no characters
    if(asyncio.run(aF.userInfo(uid)) == "ERROR"):
        print("Error: No Characters Found")
        return -1
    
    character = input("What character are you requesting for: ")
    #------------------------------------------------------------#
    # Creating Player Info Table
    playerInfo = asyncio.run(aF.userInfo(uid))
    lines = playerInfo.split('\n')[2:-2]

    # Create a dictionary from the lines
    data = {}
    for line in lines:
        key, value = line.split(': ')
        if key == 'Characters':
            value = ast.literal_eval(value)  # Convert string representation of list to actual list
        elif key in ['Level', 'Achievements', 'Abyss Floor']:
            value = int(value)  # Convert string representation of integer to actual integer
        data[key] = [value]

    # Insert 'uid' at the top of the dictionary
    data = {'UID': [uid]} | data

    playerInfoDF = pd.DataFrame(data)

    # Converting data into cleaned DataFrame
    playerInfoDF = playerInfoDF.T
    playerInfoDF.columns = ['Player Info']

    # Remove 'Characters' index from the DataFrame
    playerInfoDF = playerInfoDF.drop('        Characters', errors='ignore')

    # To De-Bug
    # print(tabulate(playerInfoDF, headers='keys', tablefmt='psql'))


    #------------------------------------------------------------#
    #CharactersDF
    # Find the start and end of the characters list
    start = playerInfo.find('[')
    end = playerInfo.find(']')
    characters_str = playerInfo[start:end+1]
    characters = ast.literal_eval(characters_str)
    charactersDF = pd.DataFrame({'UID': uid, 'Character': characters})


    # To De-Bug
    # print(tabulate(charactersDF, headers='keys', tablefmt='psql'))



    #------------------------------------------------------------#

    artifactInfo = asyncio.run(aF.artifact_Extractor(uid, character))

    rows = []
    for key, value in artifactInfo.items():
        if isinstance(value, set):
            for item in value:
                rows.append({'Character': character, 'Artifact': item})
        elif isinstance(value, list):
            if all(isinstance(i, tuple) for i in value):
                for stat, amount in value:
                    rows.append({'Character': character, 'Artifact': key, 'Stat': stat, 'Amount': amount})
            else:
                stat = value[0]
                amount = value[1] if len(value) > 1 else None  # Check if value has more than one element
                rows.append({'Character': character, 'Artifact': key, 'Stat': stat, 'Amount': amount})

    artifactDF = pd.DataFrame(rows)

    # DataFrame with both MainStat and SubStat values (Messy Data)
    artifactDF = artifactDF.dropna(subset=['Stat', 'Amount'])

    # Seperating the mainstat values and the substat values into their own df
    main_stats_df = artifactDF[~artifactDF['Artifact'].str.endswith(' ss')].copy()
    substats_df = artifactDF[artifactDF['Artifact'].str.endswith(' ss')].copy()

    # Removing the 'ss' since its already in a substat dataframe
    substats_df['Artifact'] = substats_df['Artifact'].str.replace(' ss', '')

    # Add IDs to the DataFrames (helps to identify it in a SQL DB)
    main_stats_df.insert(0, 'Artifact ID', range(1, len(main_stats_df) + 1))
    substats_df.insert(0, 'Substat ID', range(1, len(substats_df) + 1))

    # Add the Artifact IDs to the substats DataFrame (helps to identify it in a SQL DB)
    artifact_id_map = main_stats_df[['Artifact', 'Artifact ID']].set_index('Artifact').to_dict()['Artifact ID']
    substats_df['Artifact ID'] = substats_df['Artifact'].map(artifact_id_map)

    print(tabulate(main_stats_df, headers='keys', tablefmt='psql'))
    print(tabulate(substats_df, headers='keys', tablefmt='psql'))
    #------------------------------------------------------------#

    # Weapons DF
    weapon_info = asyncio.run(aF.weapon_Extractor(uid, character))
    weapon_stat_df = pd.DataFrame(weapon_info, index=['Level', 'Refinement', 'Ascension'])
    weapon_stat_df['Character'] = character
    weaponDF = weapon_stat_df.reset_index()
    columns = weaponDF.columns.tolist()

    # Changing the columns to my liking
    weaponDF = weaponDF[['Character'] + columns[:-1]]

    # Rename the columns
    weaponDF.columns = ['Character', 'Stat', 'Value']

    # Add a column for the Weapon Name
    weaponDF['Weapon'] = list(weapon_info.keys())[0]

    # To De-Bug
    # print(tabulate(weaponDF, headers='keys', tablefmt='psql'))


    #-------------------------------------------#
    #              All Tables                   #
    #                                           #
    # - playerInfoDF : Info of Player           #
    # - charactersDF : Table of Characters      #
    # - main_stats_df : main artifact stat info #
    # - substats_df : artifact substat info     #
    # - weaponDF : character Weapon Info        #
    #-------------------------------------------#

    #------------------------------------------------------------#
    #                                                            #
    #                Creating the Data Base                      #
    #                                                            #
    #------------------------------------------------------------#


    engine = create_engine('sqlite:///GenshinPlayerStats.db')
    metadata = MetaData()

    # Defining the Tables
    Users = Table('Users', metadata,
        Column('UID', String, primary_key=True),
        Column('Nickname', String),
        Column('Level', String),
        Column('Signature', String),
        Column('Achievements', String),
        Column('AbyssFloor', String)
    )

    Characters = Table('Characters', metadata,
        Column('UID', String, ForeignKey('Users.UID')),
        Column('CharacterName', String)
    )

    Artifacts = Table('Artifacts', metadata,
        Column('ArtifactID', String, primary_key=True),
        Column('Character', String, ForeignKey('Characters.CharacterName')),
        Column('Artifact', String),
        Column('Stat', String),
        Column('Amount', String)
    )

    Substats = Table('Substats', metadata,
        Column('SubstatID', String, primary_key=True),
        Column('Character', String, ForeignKey('Characters.CharacterName')),
        Column('Artifact', String, ForeignKey('Artifacts.Artifact')),
        Column('Stat', String),
        Column('Amount', String),
        Column('ArtifactID', String, ForeignKey('Artifacts.ArtifactID'))
    )

    Weapons = Table('Weapons', metadata,
        Column('Character', String, ForeignKey('Characters.CharacterName')),
        Column('Stat', String),
        Column('Value', String),
        Column('Weapon', String)
    )

    # Create the tables
    metadata.create_all(engine)
    charactersDF.columns = ['UID', 'CharacterName']
    main_stats_df.columns = ['ArtifactID', 'Character', 'Artifact', 'Stat', 'Amount']
    substats_df.columns = ['SubstatID', 'Character', 'Artifact', 'Stat', 'Amount', 'ArtifactID']
    
    # Errors here (Fix Later)
    # # Drop duplicates based on 'ArtifactID'
    # playerInfoDF.drop_duplicates(keep='first', inplace=True)
    # charactersDF.drop_duplicates(keep='first', inplace=True)
    # main_stats_df.drop_duplicates(subset='ArtifactID', keep='first', inplace=True)
    # substats_df.drop_duplicates(keep='first', inplace=True)
    # weaponDF.drop_duplicates(keep='first', inplace=True)


    # Write dataframes to SQL
    playerInfoDF.to_sql('Users', engine, if_exists='replace', index=True) #Users Database shows basic player info
    charactersDF.to_sql('Characters', engine, if_exists='append', index=False) #Character Database
    main_stats_df.to_sql('Artifacts', engine, if_exists='append', index=False) #Main Stat Artifacts
    substats_df.to_sql('Substats', engine, if_exists='append', index=False) #Substats for Main Artifacts
    weaponDF.to_sql('Weapons', engine, if_exists='append', index=False) #Weapon Stats





if __name__ == "__main__":
    main()
