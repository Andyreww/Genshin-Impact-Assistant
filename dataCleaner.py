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
pp.pprint(artifact_Retrieve)
ArtifactsDF = pd.DataFrame.from_dict(artifact_Retrieve)
ArtifactsDF = ArtifactsDF.rename({0: 'Artifacts'}, axis='columns')

# Allows us to view the artifact pandas Data Frame
print(tabulate(ArtifactsDF, headers='keys', tablefmt='psql'))

#Creating Stats Data Frame
stats_Retrieve = characterDict[] #Stopped here for the day
