__version__ = '0.1.4'

import requests
import tabulate

class OrionAPI(object):
    def __init__(self, usr=None, pwd=None):
        self.token = None
        self.usr = usr
        self.pwd = pwd
        self.base_url = "https://api.orionadvisor.com/api/v1/"

        if self.usr is not None:
            self.login(self.usr,self.pwd)

    def login(self,usr=None,pwd=None):
        res = requests.get(
            f"{self.base_url}/security/token",
            auth=(usr,pwd)
        )
        self.token = res.json()['access_token']

    def api_request(self,url,req_func=requests.get,**kwargs):
        return req_func(url,
            headers={'Authorization': 'Session '+self.token},**kwargs)

    def check_username(self):
        res = self.api_request(f"{self.base_url}/authorization/user")
        return res.json()['loginUserId']

    def get_query_payload(self,id):
        return self.api_request(f"{self.base_url}/Reporting/Custom/{id}").json()

    def get_query_params(self,id):
        return self.get_query_payload(id)['prompts']

    def get_query_params_description(self,id):
        param_list = self.get_query_params(id)
        header = param_list[0].keys()
        rows = [x.values() for x in param_list]
        print(tabulate.tabulate(rows, header))
            

    def query(self,id,params=None):
        # Get the query to get list of params
        default_params = self.get_query_params(id)

        # Match param dict with params to constructut payload
        payload_template = {
            "runTo": 'null',
            "databaseIdList": 'null',
            "prompts": [],
            }
        run_params = []
        for p in default_params:
            if p['code'] in params.keys():
                p['defaultValue'] = params[p['code']]
            run_params.append(p)

        payload = payload_template.copy()
        payload['prompts'] = run_params

        # Put request to run query
        res = self.api_request(f"{self.base_url}/Reporting/Custom/{id}/Generate/Table",
            requests.post, json=payload)
        return res.json()        

