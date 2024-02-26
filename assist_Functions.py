import enka
import asyncio
import pprint

# Afif UID: 607566990
# Pheu UID: 701473745
# Andrew UID: 602115277
# Edison UID: 602114999
# Ichigo UID: 601179564
# Okami UID: 600383198
# Sora UID: 606380789
# ---------------------------------------------------- #
async def userInfo(uid) -> None:
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
      

async def characterInfo(uid, name):
   async with enka.EnkaAPI() as api:
      response = await api.fetch_showcase(uid)
      for character in response.characters:
         if character.name.lower() == name.lower():
            return character
   return None

async def artifact_Extractor(uid, name): #Working on this
   async with enka.EnkaAPI() as api:
      response = await api.fetch_showcase(uid)
      for characters in response.characters:    #
         if(characters.name.lower() == name.lower()):
            # squared_values = {key: value**2 for key, value in dict_example.items()} # Example
            artifactName = {characters.name: {artifact.name for artifact in characters.artifacts}}  
            artifactMainStat = {f"{artifact.name} Stats": [artifact.main_stat.name, artifact.main_stat.formatted_value] for artifact in characters.artifacts}
            artifactSubStat = {f"{artifact.name} Sub Stats": [(substat.name, substat.formatted_value) for substat in artifact.sub_stats] for artifact in character.artifacts}

            combined_info = {**artifactName, **artifactMainStat, **artifactSubStat}
            return combined_info      



uid = 602115277
pp = pprint.PrettyPrinter(indent=2)
asyncio.run(userInfo(uid))
character = asyncio.run(characterInfo(uid, 'Furina'))

artifact = asyncio.run(artifact_Extractor(uid, 'Qiqi'))
pp.pprint(artifact)