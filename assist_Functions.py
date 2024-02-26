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

def artifact_Extractor(character): #Error Here
    artifact_info = {}
    for artifact in character.artifacts:
        artifact_info[artifact.name] = {
            'item_id': artifact.item_id,
            'main_stat': {
                'type': artifact.main_stat.type,
                'value': artifact.main_stat.value,
                'name': artifact.main_stat.name
            },
            'sub_stats': [{
                'type': stat.type,
                'value': stat.value,
                'name': stat.name
            } for stat in artifact.sub_stats],
            'set_name': artifact.set_name
        }
    return artifact_info



uid = 602115277
pp = pprint.PrettyPrinter(indent=4)
asyncio.run(userInfo(uid))
character = asyncio.run(characterInfo(uid, 'Furina'))
artifact = asyncio.run(artifact_Extractor(character))

print(artifact)