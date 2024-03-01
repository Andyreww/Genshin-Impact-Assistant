import assist_Functions as aF
import pandas as pd
import asyncio
import pprint
from tabulate import tabulate

# Pretty Print to make
# Dictionary more Readable
pp = pprint.PrettyPrinter(indent=2)

# Asking the user for basic information
# Only for testing (Will Delete Later)
uid = int(input("What is your in-game UID: "))
character_Name = str(input(f"Hello {asyncio.run(aF.userName(uid))} what character are you requesting: "))

# Utilizing assist_Functions.py to sort all the data into readable tables
asyncio.run(aF.userInfo(uid))
characterDict = asyncio.run(aF.artifact_Extractor(uid, character_Name))

# Creating Artifact DataFrame
artifact_Retrieve = characterDict[character_Name]


# Issue on the order this is printing out
# Will cause issues when assigning data
# to the dataframe
print(artifact_Retrieve)
print([key for key in artifact_Retrieve])
ArtifactsDF = pd.DataFrame(artifact_Retrieve, columns=['Artifacts'])# Print the DataFrame
print(tabulate(ArtifactsDF, headers='keys', tablefmt='pretty'))

# Creating Stats Data Frame
# Main Stat DF
mainStat_Retireve = asyncio.run(aF.artifact_MainStat(uid, character_Name)) #Created Workaround

mainStatDF = pd.DataFrame(mainStat_Retireve, columns=['Stat', 'Value'])
print(tabulate(mainStatDF, headers='keys', tablefmt='pretty'))
#Now need to seperate List of Tuple into a pandas DF into seperate columns



