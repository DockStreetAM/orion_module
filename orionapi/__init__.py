__version__ = '0.1.7'

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
        # TODO: allow params to be optional. Right now {} must be passed for some reason
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
        self.usr = usr
        self.pwd = pwd
        self.orion_token = orion_token

        if orion_token is None and usr is None:
            raise Exception("Pass either usr/pwd or an Orion Connect token, not both")
        pass

        if usr is not None:
            res = requests.get(
                f"{self.base_url}/admin/token",
                auth=(usr,pwd)
                )
            self.eclipse_token = res.json()['eclipse_access_token']

        if self.orion_token is not None:
            res = requests.get(
                f"{self.base_url}/admin/token",
                headers={'Authorization': 'Session '+self.orion_token})
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

    
    def get_all_accounts(self):
        res = self.api_request(f"{self.base_url}/account/accounts/simple")
        accounts = res.json()
        return accounts

    def get_set_asides_v2(self):
        res = self.api_request(f"{self.base_url}/api/v2/Account/Accounts/SetAsideCashSettings")
        return res.json()

    def get_set_asides(self,account_id):
        account_id = self.get_internal_account_id(account_id)
        res = self.api_request(f"{self.base_url}/account/accounts/{account_id}/asidecash")
        return res.json()

    def get_internal_account_id(self,account_id):
        """Takes account_id, which is shown in the app and Orion Connect
        Returns the internal system id used by the Eclipse API"""
        res = self.api_request(f"{self.base_url}/account/accounts/simple?search={account_id}")
        return res.json()[0]['id']
        
    def create_set_aside(self, account_id, amount, min_amount=None, max_amount=None,description=None, 
                         min=None, max=None, cash_type='$',start_date=None,
                         expire_type='None',expire_date=None,expire_trans_tol=0,
                         expire_trans_type=1,percent_calc_type=0):
        
        account_id = self.get_internal_account_id(account_id)

        cash_type_map = {
            # end point account/accounts/asideCashAmountType
            '$': 1,
            '%': 2,
        }
        if type(cash_type) == str:
            cash_type = cash_type_map[cash_type]

        expire_type_map = {
            # end point account/accounts/asideCashExpirationType
            'Date': 1,
            'Transaction': 2,
            'None': 3,
        }
        if type(expire_type) == str:
            print("mapping expire type")
            expire_type = expire_type_map[expire_type]
        print(f"Expire type is {expire_type}")
        print(f"Type of expire type is {type(expire_type)}")

        expire_trans_type_map = {
            # end point account/accounts/asideCashTransactionType
            'Distribution / Merge Out': 1,
            'Fee': 3,
        }
        if type(expire_trans_type) == str:
            expire_trans_type = expire_type_map[expire_trans_type]
            
        if expire_type == 1:
            expire_value = expire_date
        elif expire_type == 2:
            expire_value = expire_trans_type
        elif expire_type == 3:
            expire_value = 0

        percent_calc_type_map = {
            'Use Default/Managed Value': 0,
            'Use Total Value': 1,
            'Use Excluded Value': 2,
        }
        if type(percent_calc_type) == str:
            percent_calc_type = percent_calc_type_map[percent_calc_type]
            
        res = self.api_request(f"{self.base_url}/account/accounts/{account_id}/asidecash",
            requests.post, json={
                "cashAmountTypeId": cash_type,
                "cashAmount": amount,
                'minCashAmount': min_amount,
                'maxCashAmount': max_amount,
                "expirationTypeId": expire_type,
                "expirationValue": expire_value,
                "toleranceValue": expire_trans_tol,
                "description": "TESTING Aside Cash",
                "percentCalculationTypeId": percent_calc_type,
})
        return res.json()
