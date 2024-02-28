import enka
import asyncio
import string
# ---------------------------------------------------- #
# Afif UID: 607566990
# Pheu UID: 701473745
# Andrew UID: 602115277
# Edison UID: 602114999
# Ichigo UID: 601179564
# Okami UID: 600383198
# Sora UID: 606380789
# ---------------------------------------------------- #

"""
This function prints basic information
of the request user

Parameters:
uid (int) The players UID

Returns:
None
"""
async def userInfo(uid) -> None:
   await connection_Test(uid)
   async with enka.EnkaAPI() as api:
      response = await api.fetch_showcase(uid)
      print("=== Player Info ===")
      print(f"Nickname: {response.player.nickname}")
      print(f"Level: {response.player.level}")
      print(f"Signature: {response.player.signature}")
      print(f"Achievements: {response.player.achievements}")
      print(f"Abyss Floor: {response.player.abyss_floor}")
      
      characters = [character.name for character in response.characters]
      print(f"Characters: {characters}")
      print("===================")

"""
This function returns the players
in-game name

Parameters:
uid (int) The players UID

Returns:
string
"""    
async def userName(uid) -> None:
   await connection_Test(uid)
   async with enka.EnkaAPI() as api:
      response = await api.fetch_showcase(uid)
      return response.player.nickname

"""
This function returns character
information is a general basis

Parameters:
uid (int) The players UID
name (string) The character to be viewed

Returns:
None
"""
async def characterInfo(uid, name):
   await connection_Test(uid)
   async with enka.EnkaAPI() as api:
      response = await api.fetch_showcase(uid)
      for character in response.characters:
         if character.name.lower() == name.lower():
            return character
   return None


"""
This function returns information
of each artifact from the specified
character that's requested

Parameters:
uid (int) The players UID
name (string) The character to be viewed

Returns:
combined_info (dict) A dictionary of all the artifact information
"""
async def artifact_Extractor(uid, name):
   await connection_Test(uid)
   async with enka.EnkaAPI() as api:
      response = await api.fetch_showcase(uid)
      for characters in response.characters:    
         if(characters.name.lower() == name.lower()):
            artifactName = {characters.name: {artifact.name.replace("'", "") for artifact in characters.artifacts}}  
            artifactMainStat = {f"{artifact.name}": [artifact.main_stat.name, artifact.main_stat.formatted_value] for artifact in characters.artifacts} #Main Stats
            artifactSubStat = {f"{artifact.name} ss": [(substat.name, substat.formatted_value) for substat in artifact.sub_stats] for artifact in characters.artifacts} #Sub Stats
            combined_info = {**artifactName, **artifactMainStat, **artifactSubStat}
            return combined_info      

"""
This function returns the main
stats of a artifact in a tuple

Parameters:
uid (int) The players UID
name (string) The character to be viewed

Returns:
List object
"""
async def artifact_MainStat(uid, name):
   await connection_Test(uid)
   async with enka.EnkaAPI() as api:
      response = await api.fetch_showcase(uid)
      for characters in response.characters:
         if(characters.name.lower() == name.lower()):
            aMS = [(artifact.main_stat.name, artifact.main_stat.formatted_value) for artifact in characters.artifacts] #Main Stats
      return aMS
"""
This function returns information
of the weapon from the specified
character that's requested

Parameters:
uid (int) The players UID
name (string) The character to be viewed

Returns:
combined_info (DoL) A dictionary of List that stores information on the weapon
"""
async def weapon_Extractor(uid, name):
   await connection_Test(uid)
   weaponInfo = {}
   async with enka.EnkaAPI() as api:
      response = await api.fetch_showcase(uid)
      for character in response.characters:
        if(character.name.lower() == name.lower()):
            weapon = character.weapon
            weaponInfo = {weapon.name: [weapon.level, weapon.rarity, weapon.refinement]}
            return weaponInfo

"""
This function makes sure that
EnkaNetwork is up and running
in-order to retrieve data

Parameters:
uid (int) The players UID

Returns:
combined_info (DoL) A dictionary of List that stores information on the weapon
"""
async def connection_Test(uid) -> None:
    async with enka.EnkaAPI() as api:
        try:
            response = await api.fetch_showcase(uid)
        except enka.exceptions.PlayerDoesNotExistError:
            return print("Player does not exist.")
        except enka.exceptions.GameMaintenanceError:
            return print("Game is in maintenance.")

# ==========================
# How to test code Below
# test = asyncio.run(userInfo(606380789))
# print(test)
# ==========================