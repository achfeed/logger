from log2json import logger
import pandas as pd

data = [10, 20, 30, 40, 50, 60]
logger.info("Dataframe creation step : data's generated")

df = pd.DataFrame(data, columns=['Numbers'])
logger.info("Dataframe creation step : DataFrame populated")

print(df)
