from pyairtable import Api
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

api = Api(os.getenv("AIRTABLE_TOKEN"))

table = api.table("appfkarmTpUy5nGMQ", "tblYtm6ijHAPfegYr")

data = [
    record["fields"] for record in table.all()
]  # We only need the 'fields' part of each record
df = pd.DataFrame(data)

df.to_csv("htan_airtable.csv")

print(df)
