__version__ = '1.0.0'

import requests
import tabulate
import re
import rapidfuzz
import logging


class BaseAPI:
    """Base class for Orion API clients with shared request handling."""

    base_url = None

    def _get_auth_header(self):
        """Return authorization header dict. Subclasses must implement."""
        raise NotImplementedError("Subclasses must implement _get_auth_header()")

    def api_request(self, url, req_func=requests.get, **kwargs):
        """Make an authenticated API request with error handling.

        Args:
            url: The API endpoint URL
            req_func: The requests function to use (get, post, put, delete)
            **kwargs: Additional arguments passed to the request

        Returns:
            requests.Response object

        Raises:
            requests.exceptions.HTTPError: On 4xx/5xx responses
        """
        headers = kwargs.pop('headers', {})
        headers.update(self._get_auth_header())
        res = req_func(url, headers=headers, **kwargs)
        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Try to include API error message in exception
            try:
                error_body = res.json()
                raise requests.exceptions.HTTPError(
                    f"{e}: {error_body.get('message', error_body)}"
                ) from None
            except ValueError:
                raise
        return res


class OrionAPI(BaseAPI):
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

    def _get_auth_header(self):
        return {'Authorization': 'Session ' + self.token}

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

class EclipseAPI(BaseAPI):
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
            raise Exception("Must provide either usr/pwd or orion_token")

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

    def _get_auth_header(self):
        return {'Authorization': 'Session ' + self.eclipse_token}

    def check_username(self):
        res = self.api_request(f"{self.base_url}/admin/authorization/user")
        return res.json()['userLoginId']

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
        logging.debug("search_accounts result: %s", res)
        return res[0]['id']

    def search_accounts(self,search_param):
        res = self.api_request(f"{self.base_url}/account/accounts/simple?search={search_param}")
        return res.json()

    def normalize_name(self, name):
        return re.sub(r"[^a-zA-Z0-9]", "", name).lower()

    def search_accounts_number_and_name(self,acct_num_portion, name_portion):
        """Searches accounts based on the trailing digits of the custodial account number
        and a string contained in the name"""

        from_acct = re.sub(r"\D", "", acct_num_portion)
        name_portion = self.normalize_name(name_portion)

        # First: filter by exact trailing account-number match
        accounts = self.search_accounts(from_acct)
        num_match = [
            a for a in accounts
            if a["accountNumber"].endswith(from_acct)
        ]

        if not num_match:
            raise Exception(f"No accounts found for acct# {acct_num_portion}")

        # If multiple number matches, log but continue
        if len(num_match) > 1:
            logging.info(
                "Multiple accounts share trailing digits '%s': %s",
                from_acct,
                [
                    {k: a[k] for k in ["id","name","accountId","accountNumber","accountType"]}
                    for a in num_match
                ]
            )

        ### Pick the best fuzzy name match
        best_acct = max(
            num_match,
            key=lambda a: rapidfuzz.fuzz.partial_ratio(
                name_portion,
                self.normalize_name(a["name"])
            )
        )
        return best_acct['id'], best_acct['accountNumber']
        
    def create_set_aside(self, account_number, amount, min_amount=None, max_amount=None,description=None, 
                         min=None, max=None, cash_type='$',start_date=None,
                         expire_type='None',expire_date=None,expire_trans_tol=0,
                         expire_trans_type=1,percent_calc_type=0):
        
        # This function takes the full custodial account number as input
        account_id = self.get_internal_account_id(account_number)

        cash_type_map = {
            # end point account/accounts/asideCashAmountType
            '$': 1,
            '%': 2,
        }
        if isinstance(cash_type, str):
            cash_type = cash_type_map[cash_type]

        expire_type_map = {
            # end point account/accounts/asideCashExpirationType
            'Date': 1,
            'Transaction': 2,
            'None': 3,
        }
        if isinstance(expire_type, str):
            logging.debug("mapping expire type")
            expire_type = expire_type_map[expire_type]
        logging.debug("Expire type is %s (type: %s)", expire_type, type(expire_type))

        expire_trans_type_map = {
            # end point account/accounts/asideCashTransactionType
            'Distribution / Merge Out': 1,
            'Fee': 3,
        }
        if isinstance(expire_trans_type, str):
            expire_trans_type = expire_trans_type_map[expire_trans_type]
            
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
        if isinstance(percent_calc_type, str):
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
                "description": description,
                "percentCalculationTypeId": percent_calc_type,
            })
        return res.json()

    def get_account_details(self,internal_id):
        res = self.api_request(f"{self.base_url}/account/accounts/{internal_id}")
        return res.json()

    def get_all_account_details(self):
        res = self.api_request(f"{self.base_url}/account/accounts/")
        return res.json()
    
    def get_account_cash_available(self,internal_id):
        res = self.get_account_details(internal_id)
        return res['summarySection']['cashAvailable']

    def get_portfolio(self, portfolio_id):
        """Get portfolio details by ID.

        Returns dict with 'general', 'teams', 'issues', 'summary' sections.
        """
        res = self.api_request(f"{self.base_url}/portfolio/portfolios/{portfolio_id}")
        return res.json()

    def get_portfolio_accounts(self, portfolio_id):
        """Get list of accounts for a portfolio.

        Returns list of accounts with cash targets, sleeve settings, and values.
        """
        res = self.api_request(f"{self.base_url}/portfolio/portfolios/{portfolio_id}/accounts")
        return res.json()

    def get_model_tolerance(self, portfolio_id, account_id, account_type="Normal"):
        """Get model tolerance values for a portfolio/account.

        Args:
            portfolio_id: Portfolio ID
            account_id: Account ID
            account_type: "Normal" or "Sleeve"

        Returns target vs current allocation percentages and tolerance bands.
        """
        res = self.api_request(
            f"{self.base_url}/portfolio/portfolios/{portfolio_id}/ModelMACTolerance/{account_id}",
            params={"accountType": account_type}
        )
        return res.json()

    def get_all_portfolios(self, include_value=True, search=None):
        """Get list of all portfolios.

        Args:
            include_value: Include holding values (default True)
            search: Optional search string

        Returns list of portfolios with basic info and optionally values.
        """
        params = {"includevalue": str(include_value).lower()}
        if search:
            params["search"] = search
        res = self.api_request(f"{self.base_url}/portfolio/portfolios/simple", params=params)
        return res.json()

    def get_account_holdings(self, account_id, search=None):
        """Get holdings for a specific account.

        Args:
            account_id: Account ID
            search: Optional search string (id or name)

        Returns list of holdings with values and percentages.
        """
        params = {"inAccountId": account_id}
        if search:
            params["search"] = search
        res = self.api_request(f"{self.base_url}/holding/holdings/simple", params=params)
        return res.json()

    def get_portfolio_holdings(self, portfolio_id, search=None):
        """Get all holdings across a portfolio.

        Args:
            portfolio_id: Portfolio ID
            search: Optional search string (id or name)

        Returns list of holdings with values and percentages.
        """
        params = {"inPortfolioId": portfolio_id}
        if search:
            params["search"] = search
        res = self.api_request(f"{self.base_url}/holding/holdings/simple", params=params)
        return res.json()

    def get_orders(self):
        return self.api_request(f"{self.base_url}/tradeorder/trades?isPending=false").json()

    def get_orders_pending(self):
        return self.api_request(f"{self.base_url}/tradeorder/trades?isPending=true").json()

    def cash_needs_trade(self, portfolio_ids, portfolio_trade_group_ids=None,
                         is_view_only=True, reason="", is_excel_import=False):
        """Rebalance CashNeeds Portfolios.

        Args:
            portfolio_ids: List of portfolio IDs to process
            portfolio_trade_group_ids: List of portfolio trade group IDs (optional)
            is_view_only: If True, preview trades without executing (default True)
            reason: Reason for the trade
            is_excel_import: Whether this is from an Excel import (default False)

        Returns:
            dict with 'issues', 'success', and 'instanceId' fields
        """
        if portfolio_trade_group_ids is None:
            portfolio_trade_group_ids = []

        payload = {
            "portfolioIds": portfolio_ids,
            "portfolioTradeGroupIds": portfolio_trade_group_ids,
            "isViewOnly": is_view_only,
            "reason": reason,
            "isExcelImport": is_excel_import
        }

        res = self.api_request(
            f"{self.base_url}/tradetool/cashneeds/action/generatetrade",
            requests.post,
            json=payload
        )
        return res.json()

    ### Model Maintenance
    def get_all_models(self):
        res = self.api_request(f"{self.base_url}/modeling/models")
        return res.json()
        #https://api.orioneclipse.com/doc/#api-Portfolios-GetPortfolioAllocations

    def get_model(self,id):
        res = self.api_request(f"{self.base_url}/modeling/models/{id}")
        return res.json()

    def get_model_allocations(self,id):
        res = self.api_request(f"{self.base_url}/modeling/models/{id}/allocations?aggregateAllocations=true")
        return res.json()

    def get_all_security_sets(self):
        res = self.api_request(f"{self.base_url}/security/securityset")
        return res.json()

    def get_security_set(self,id):
        res = self.api_request(f"{self.base_url}/security/securityset/details/{id}")
        return res.json()

    def add_model(self, name, name_space=None, description=None, tags=None, status_id=1,
                  management_style_id=2, is_community_model=False, is_dynamic=False,
                  exclude_rebalance_sleeve=False):
        """Create a new model.

        Args:
            name: Name of the model (required)
            name_space: Namespace of the model
            description: Description of the model
            tags: Tags for the model
            status_id: Status ID (default 1)
            management_style_id: Management style ID (default 2)
            is_community_model: Whether model is from community (default False)
            is_dynamic: Whether model is dynamic (default False)
            exclude_rebalance_sleeve: Exclude sleeved accounts from rebalance (default False)

        Returns:
            dict with created model details including 'id'
        """
        payload = {
            "name": name,
            "nameSpace": name_space,
            "description": description,
            "tags": tags,
            "statusId": status_id,
            "managementStyleId": management_style_id,
            "isCommunityModel": is_community_model,
            "isDynamic": 1 if is_dynamic else 0,
            "excludeRebalanceSleeve": exclude_rebalance_sleeve
        }

        res = self.api_request(
            f"{self.base_url}/modeling/models",
            requests.post,
            json=payload
        )
        return res.json()

    def add_model_detail(self, model_id, model_detail):
        """Add model detail/structure to an existing model.

        Args:
            model_id: ID of the model to add detail to
            model_detail: Dict with model structure. Can include:
                - id: ID of submodel
                - name: Name
                - nameSpace: Namespace
                - securityAsset: {"id": asset_id}
                - targetPercent: Target percentage
                - toleranceType: "range" or "fixband%"
                - toleranceTypeValue: Tolerance value
                - rank: Rank order
                - lowerModelTolerancePercent: Lower tolerance %
                - upperModelTolerancePercent: Upper tolerance %
                - lowerModelToleranceAmount: Lower tolerance $
                - upperModelToleranceAmount: Upper tolerance $
                - children: List of child ModelDetail dicts

        Returns:
            dict with updated model details
        """
        res = self.api_request(
            f"{self.base_url}/modeling/models/{model_id}/modelDetail",
            requests.post,
            json={"modelDetail": model_detail}
        )
        return res.json()

    def delete_model(self, model_id):
        """Delete a model (soft delete).

        Args:
            model_id: ID of the model to delete

        Returns:
            dict with success message
        """
        res = self.api_request(
            f"{self.base_url}/modeling/models/{model_id}",
            requests.delete
        )
        return res.json()

    def create_security_set(self, name, securities, description=None,
                            tolerance_type="ABSOLUTE", tolerance_type_value=0):
        """Create a new security set.

        Args:
            name: Name of the security set
            securities: List of security dicts with:
                - id: Security ID
                - targetPercent: Target percentage
                - rank: Rank order
                - lowerModelTolerancePercent: Lower tolerance %
                - upperModelTolerancePercent: Upper tolerance %
                - lowerModelToleranceAmount: Lower tolerance $ (optional)
                - upperModelToleranceAmount: Upper tolerance $ (optional)
            description: Description of the security set
            tolerance_type: "ABSOLUTE" or "BAND" (default "ABSOLUTE")
            tolerance_type_value: Tolerance value (default 0)

        Returns:
            dict with created security set details
        """
        payload = {
            "name": name,
            "description": description,
            "toleranceType": tolerance_type,
            "toleranceTypeValue": tolerance_type_value,
            "securities": securities
        }

        res = self.api_request(
            f"{self.base_url}/security/securityset",
            requests.post,
            json=payload
        )
        return res.json()