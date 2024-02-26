import assist_Functions as aF
import pandas as pd
import asyncio

# Utilizing assist_Functions to sort all the data into readable tables
asyncio.run(aF.userInfo(607566990))
test = asyncio.run(aF.artifact_Extractor(607566990, 'Xiao'))

XiaoTest = pd.DataFrame.from_dict(test)
XiaoTest