__version__ = '0.2.2'

import requests
import tabulate
import re

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

    def get_internal_account_id(self,search_param):
        """Searches across id/accountName/accountNumber/portfolioName
        Best use is to pass a full custodian accout number
        Returns the internal system id used by the Eclipse API
        Returns the first result. This might not be expected"""
        res = self.search_accounts(search_param)
        return res[0]['id']

    def search_accounts(self,search_param):
        res = self.api_request(f"{self.base_url}/account/accounts/simple?search={search_param}")
        return res.json()

    def search_accounts_number_and_name(self,acct_num_portion, name_portion):
        """Searches accounts based on the trailing digits of the custodial account number
        and a string contained in the name"""
        from_acct = re.sub(r"\D", "", acct_num_portion)

        accounts = self.search_accounts(from_acct)

        num_match = [account for account in accounts if account['accountNumber'].endswith(from_acct)]
        name_match = [account for account in accounts if name_portion.lower() in account['name'].lower()]

        # intersection of name_match and num_match
        matching_accounts = [account for account in num_match if account in name_match]

        if len(matching_accounts) == 1:
            return matching_accounts[0]['id'], matching_accounts[0]['accountNumber']

        if len(matching_accounts) == 0:
            E = Exception(f"No accounts found for acct# {acct_num_portion} and {name_portion}")
            print("accounts matching digits: ", [{key: account[key] for key in ['id','name','accountId','accountNumber','accountType']} for account in num_match])
            print("accounts matching last name: ", [{key: account[key] for key in ['id','name','accountId','accountNumber','accountType']} for account in name_match])
            raise E
        else:
            E = Exception(f"Multiple accounts found for {acct_num_portion} and {name_portion}")
            print("matching accounts: ", [{key: account[key] for key in ['id','name','accountId','accountNumber','accountType']} for account in matching_accounts])
            raise E
        
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
                "cashAmount": float(amount),
                'minCashAmount': float(min_amount),
                'maxCashAmount': float(max_amount),
                "expirationTypeId": expire_type,
                "expirationValue": expire_value,
                "toleranceValue": expire_trans_tol,
                "description": "TESTING Aside Cash",
                "percentCalculationTypeId": percent_calc_type,
            })
        return res.json()

    def get_account_details(self,internal_id):
        res = self.api_request(f"{self.base_url}/account/accounts/{internal_id}")
        return res.json()
    
    def get_account_cash_available(self,internal_id):
        res = self.get_account_details(internal_id)
        return res['summarySection']['cashAvailable']
