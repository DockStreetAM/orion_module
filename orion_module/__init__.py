__version__ = '0.1.0'

import requests

class OrionAPI(object):
    def __init__(self, usr=None, pwd=None):
        pass

    def login(self,usr,pwd):
        pass

    def query(self,id,params=None):
        pass
""" 
res = requests.get(
    "https://api.orionadvisor.com/api/v1/security/token",
    auth=(
        os.environ["ORION_USER"],
        os.environ["ORION_PASS"]
    )    
)
orion_token = res.json()['access_token']

query_id = 4790

res = requests.post(
    f"https://api.orionadvisor.com/api/v1/Reporting/Custom/{query_id}/Generate/Table",
    headers={'Authorization': 'Session '+orion_token},
    json={"prompts": [{
      "id": 16806,
      "code": "@asOf",
      "defaultValue": (datetime.date.today()-datetime.timedelta(days=1)).strftime("%m/%d/%Y"),
        },
        {
      "id": 49140,
      "code": "@m",
      "defaultValue": 2,
    }
    ]}
)
orion_households_df = pandas.read_json(res.text) """