import assist_Functions as aF
import pandas as pd
import asyncio
from tabulate import tabulate

def swap_rows(df, i1, i2, row): # Possible Error
# Swap the names of the first and second artifacts
    df = df.loc[i1, row], df.loc[i2, row] = df.loc[i2, row], df.loc[i1, row]
    return df

def main():
    # Asking the user for basic information
    uid = int(input("What is your in-game UID: "))
    character_Name = str(input(f"Hello {asyncio.run(aF.userName(uid))}, what character are you requesting: "))

    # Utilizing assist_Functions.py to sort all the data into readable tables
    asyncio.run(aF.userInfo(uid))
    characterDict = asyncio.run(aF.artifact_Extractor(uid, character_Name))

    # Creating Artifact DataFrame
    artifact_Retrieve = characterDict[character_Name]
    ArtifactsDF = pd.DataFrame(artifact_Retrieve, columns=['Artifacts'])
    print(tabulate(ArtifactsDF, headers='keys', tablefmt='pretty'))

    # Creating Stats Data Frame
    mainStat_Retireve = asyncio.run(aF.artifact_MainStat(uid, character_Name))
    mainStatDF = pd.DataFrame(mainStat_Retireve, columns=['Stat', 'Value'])
    print(tabulate(mainStatDF, headers='keys', tablefmt='pretty'))

    # Merging the df
    # Still fixing issue here
    mergedDF = pd.concat([ArtifactsDF.reset_index(drop=True), mainStatDF.reset_index(drop=True)], axis=1)
    mergeDF = swap_rows(mergeDF, 1, 4, 'Artifacts')
    print(tabulate(mergedDF, headers='keys', tablefmt='pretty'))




if __name__ == "__main__":
    main()
