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
        params = params or {}
        
        # Match param dict with params to constructut payload
        payload_template = {
            "runTo": 'null',
            "databaseIdList": 'null',
            "prompts": [],
            }
        run_params = []
        for p in default_params:
            if p['code'] in params:
                p['defaultValue'] = params[p['code']]
            run_params.append(p)

        payload = payload_template.copy()
        payload['prompts'] = run_params
        print(f"{payload=}")

        # Put request to run query
        res = self.api_request(f"{self.base_url}/Reporting/Custom/{id}/Generate/Table",
            requests.post, json=payload)
        return res.json()        

class EclipseAPI(object):
    def __init__(self, usr=None, pwd=None, orion_token=None):
        self.eclipse_token = None
        self.orion_token = orion_token
        self.usr = usr
        self.pwd = pwd
        self.base_url = "https://api.orioneclipse.com/v1"

        # if one of the params is not None, then login
        if self.usr is not None:
            self.login(self.usr,self.pwd)
        if self.orion_token is not None:
            self.login(orion_token=self.orion_token)

        
    def login(self,usr=None, pwd=None, orion_token=None):
        print("login")
        self.usr = usr
        self.pwd = pwd
        self.orion_token = orion_token

        if orion_token is None and usr is None:
            raise Exception("Pass either usr/pwd or an Orion Connect token, not both")
        pass
# Orion Connect Login
    #def login(self,usr=None,pwd=None):
    #    res = requests.get(
    #        f"{self.base_url}/security/token",
    #        auth=(usr,pwd)
    #    )
    #    self.token = res.json()['access_token']

        if usr is not None:
            print("Requesting with usr: "+f"{self.base_url}/admin/token")
            res = requests.get(
                f"{self.base_url}/admin/token",
                auth=(usr,pwd)
                )
            print(res.text)
            self.eclipse_token = res.json()['eclipse_access_token']

        if self.orion_token is not None:
            print("Requesting with token: "+f"{self.base_url}/admin/token")
            print(f"Orion Connect Token: {self.orion_token[-4:]}") # last 4 characters of token
            res = requests.get(
                f"{self.base_url}/admin/token",
                headers={'Authorization': 'Session '+self.orion_token})
            print("request URL: ",res.request.url)
            print("request Header: ",res.request.headers)
            print("request Body: ",res.request.body)
            print("response Status: ",res.status_code)
            print("response Text: ",res.text)
            print(res.json())
            try:
                self.eclipse_token = res.json()['eclipse_access_token']
            except KeyError:
                return res

    def api_request(self,url,req_func=requests.get,**kwargs):
        return req_func(url,
            headers={'Authorization': 'Session '+self.eclipse_token},**kwargs)

    def check_username(self):
        res = self.api_request(f"{self.base_url}/admin/authorization/user")
        return res.json()['userLoginId']

    def get_set_asides(self):
        res = self.api_request(f"{self.base_url}/api/v2/Account/Accounts/SetAsideCashSettings")
        return res.json()

    def get_all_models(self):
        res = self.api_request(f"{self.base_url}/modeling/models")
        return res.json()
        #https://api.orioneclipse.com/doc/#api-Portfolios-GetPortfolioAllocations

    def get_all_security_sets(self):
        res = self.api_request(f"{self.base_url}/security/securityset")
        return res.json()

    def get_security_set(self,id):
        res = self.api_request(f"{self.base_url}/security/securityset/details/{id}")
        return res.json()