__version__ = '1.1.0'

import requests
import tabulate
import re
import rapidfuzz
import logging


class OrionAPIError(Exception):
    """Base exception for Orion API errors."""
    pass


class AuthenticationError(OrionAPIError):
    """Raised when authentication fails."""
    pass


class NotFoundError(OrionAPIError):
    """Raised when a requested resource is not found."""
    pass


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
            AuthenticationError: On 401/403 responses
            NotFoundError: On 404 responses
            OrionAPIError: On other 4xx/5xx responses
        """
        headers = kwargs.pop('headers', {})
        headers.update(self._get_auth_header())
        res = req_func(url, headers=headers, **kwargs)

        if not res.ok:
            # Try to get error message from response body
            try:
                error_body = res.json()
                message = error_body.get('message', str(error_body))
            except ValueError:
                message = res.text or res.reason

            if res.status_code in (401, 403):
                raise AuthenticationError(f"{res.status_code} {res.reason}: {message}")
            elif res.status_code == 404:
                raise NotFoundError(f"Resource not found: {message}")
            else:
                raise OrionAPIError(f"{res.status_code} {res.reason}: {message}")

        return res


class OrionAPI(BaseAPI):
    """Client for the Orion Advisor API.

    Provides access to reporting and custom query functionality.

    Args:
        usr: Username for authentication
        pwd: Password for authentication

    Example:
        >>> api = OrionAPI(usr="user@example.com", pwd="password")
        >>> api.check_username()
        'user@example.com'
    """

    def __init__(self, usr=None, pwd=None):
        self.token = None
        self.usr = usr
        self.pwd = pwd
        self.base_url = "https://api.orionadvisor.com/api/v1/"

        if self.usr is not None:
            self.login(self.usr, self.pwd)

    def login(self, usr=None, pwd=None):
        """Authenticate with the Orion API.

        Args:
            usr: Username for authentication
            pwd: Password for authentication

        Raises:
            AuthenticationError: If credentials are invalid
        """
        res = requests.get(
            f"{self.base_url}/security/token",
            auth=(usr, pwd)
        )
        if not res.ok:
            raise AuthenticationError(f"Login failed: {res.status_code} {res.reason}")
        try:
            self.token = res.json()['access_token']
        except (KeyError, ValueError) as e:
            raise AuthenticationError(f"Invalid response from auth endpoint: {e}")

    def _get_auth_header(self):
        return {'Authorization': 'Session ' + self.token}

    def check_username(self):
        """Get the authenticated user's login ID.

        Returns:
            str: The user's login ID
        """
        res = self.api_request(f"{self.base_url}/authorization/user")
        return res.json()['loginUserId']

    def get_query_payload(self, id):
        """Get the full payload for a custom query.

        Args:
            id: The custom query ID

        Returns:
            dict: Query payload including prompts and metadata
        """
        return self.api_request(f"{self.base_url}/Reporting/Custom/{id}").json()

    def get_query_params(self, id):
        """Get the parameters for a custom query.

        Args:
            id: The custom query ID

        Returns:
            list: List of parameter definitions with codes and default values
        """
        return self.get_query_payload(id)['prompts']

    def get_query_params_description(self, id):
        """Print a formatted table of query parameters.

        Args:
            id: The custom query ID
        """
        param_list = self.get_query_params(id)
        header = param_list[0].keys()
        rows = [x.values() for x in param_list]
        print(tabulate.tabulate(rows, header))

    def query(self, id, params=None):
        """Execute a custom query.

        Args:
            id: The custom query ID
            params: Dict of parameter code -> value overrides (optional)

        Returns:
            dict or list: Query results
        """
        default_params = self.get_query_params(id)
        params = params or {}

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

        res = self.api_request(
            f"{self.base_url}/Reporting/Custom/{id}/Generate/Table",
            requests.post,
            json=payload
        )
        return res.json()        

class EclipseAPI(BaseAPI):
    """Client for the Eclipse Trading Platform API.

    Provides access to accounts, portfolios, models, orders, and trade tools.

    Args:
        usr: Username for authentication
        pwd: Password for authentication
        orion_token: Orion session token (alternative to usr/pwd)

    Example:
        >>> api = EclipseAPI(usr="user@example.com", pwd="password")
        >>> api.check_username()
        'user@example.com'
    """

    def __init__(self, usr=None, pwd=None, orion_token=None):
        self.eclipse_token = None
        self.orion_token = orion_token
        self.usr = usr
        self.pwd = pwd
        self.base_url = "https://api.orioneclipse.com/v1"

        if self.usr is not None:
            self.login(self.usr, self.pwd)
        elif self.orion_token is not None:
            self.login(orion_token=self.orion_token)

    def login(self, usr=None, pwd=None, orion_token=None):
        """Authenticate with the Eclipse API.

        Args:
            usr: Username for authentication
            pwd: Password for authentication
            orion_token: Orion session token (alternative to usr/pwd)

        Raises:
            AuthenticationError: If credentials are invalid or missing
        """
        self.usr = usr
        self.pwd = pwd
        self.orion_token = orion_token

        if orion_token is None and usr is None:
            raise AuthenticationError("Must provide either usr/pwd or orion_token")

        if usr is not None:
            res = requests.get(
                f"{self.base_url}/admin/token",
                auth=(usr, pwd)
            )
            if not res.ok:
                raise AuthenticationError(f"Login failed: {res.status_code} {res.reason}")
            try:
                self.eclipse_token = res.json()['eclipse_access_token']
            except (KeyError, ValueError) as e:
                raise AuthenticationError(f"Invalid response from auth endpoint: {e}")

        elif self.orion_token is not None:
            res = requests.get(
                f"{self.base_url}/admin/token",
                headers={'Authorization': 'Session ' + self.orion_token}
            )
            if not res.ok:
                raise AuthenticationError(f"Token exchange failed: {res.status_code} {res.reason}")
            try:
                self.eclipse_token = res.json()['eclipse_access_token']
            except (KeyError, ValueError) as e:
                raise AuthenticationError(f"Invalid response from auth endpoint: {e}")

    def _get_auth_header(self):
        return {'Authorization': 'Session ' + self.eclipse_token}

    def check_username(self):
        """Get the authenticated user's login ID.

        Returns:
            str: The user's login ID
        """
        res = self.api_request(f"{self.base_url}/admin/authorization/user")
        return res.json()['userLoginId']

    def get_all_accounts(self):
        """Get a simplified list of all accounts.

        Returns:
            list: List of account dicts with basic info (id, name, accountNumber, etc.)
        """
        res = self.api_request(f"{self.base_url}/account/accounts/simple")
        return res.json()

    def get_set_asides_v2(self):
        """Get all set-aside cash settings via v2 API.

        Returns:
            list: List of set-aside settings across all accounts
        """
        res = self.api_request(f"{self.base_url}/api/v2/Account/Accounts/SetAsideCashSettings")
        return res.json()

    def get_set_asides(self, account_id):
        """Get set-aside cash settings for a specific account.

        Args:
            account_id: Account ID or account number

        Returns:
            list: List of set-aside settings for the account
        """
        account_id = self.get_internal_account_id(account_id)
        res = self.api_request(f"{self.base_url}/account/accounts/{account_id}/asidecash")
        return res.json()

    def get_internal_account_id(self, search_param):
        """Get internal Eclipse account ID from a search parameter.

        Searches across id, accountName, accountNumber, and portfolioName.
        Best use is to pass a full custodian account number.

        Args:
            search_param: Account number, name, or ID to search for

        Returns:
            int: The internal Eclipse account ID

        Raises:
            NotFoundError: If no matching account is found

        Note:
            Returns the first matching result, which may not be expected
            if multiple accounts match the search parameter.
        """
        res = self.search_accounts(search_param)
        logging.debug("search_accounts result: %s", res)
        if not res:
            raise NotFoundError(f"No account found for search: {search_param}")
        return res[0]['id']

    def search_accounts(self, search_param):
        """Search for accounts by various criteria.

        Args:
            search_param: Search string (matches id, accountName, accountNumber, portfolioName)

        Returns:
            list: List of matching account dicts
        """
        res = self.api_request(f"{self.base_url}/account/accounts/simple?search={search_param}")
        return res.json()

    def normalize_name(self, name):
        """Normalize a name for fuzzy matching (internal helper)."""
        return re.sub(r"[^a-zA-Z0-9]", "", name).lower()

    def search_accounts_number_and_name(self, acct_num_portion, name_portion):
        """Search for an account by trailing account number digits and name.

        Uses fuzzy matching to find the best match when multiple accounts
        share the same trailing digits.

        Args:
            acct_num_portion: Trailing digits of the custodial account number
            name_portion: Partial name to match against

        Returns:
            tuple: (account_id, account_number) of the best match

        Raises:
            NotFoundError: If no accounts match the trailing digits
        """

        from_acct = re.sub(r"\D", "", acct_num_portion)
        name_portion = self.normalize_name(name_portion)

        # First: filter by exact trailing account-number match
        accounts = self.search_accounts(from_acct)
        num_match = [
            a for a in accounts
            if a["accountNumber"].endswith(from_acct)
        ]

        if not num_match:
            raise NotFoundError(f"No accounts found for acct# {acct_num_portion}")

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
        
    def create_set_aside(self, account_number, amount, min_amount=None, max_amount=None,
                         description=None, min=None, max=None, cash_type='$',
                         start_date=None, expire_type='None', expire_date=None,
                         expire_trans_tol=0, expire_trans_type=1, percent_calc_type=0):
        """Create a set-aside cash reservation for an account.

        Args:
            account_number: Full custodial account number
            amount: Cash amount to set aside
            min_amount: Minimum cash amount
            max_amount: Maximum cash amount
            description: Description of the set-aside
            cash_type: '$' for dollar amount, '%' for percentage (default '$')
            start_date: Start date for the set-aside
            expire_type: 'None', 'Date', or 'Transaction' (default 'None')
            expire_date: Expiration date (if expire_type='Date')
            expire_trans_tol: Transaction tolerance value (default 0)
            expire_trans_type: 1='Distribution / Merge Out', 3='Fee' (default 1)
            percent_calc_type: 0='Use Default/Managed Value', 1='Use Total Value',
                              2='Use Excluded Value' (default 0)

        Returns:
            dict: Created set-aside details
        """
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

    def get_account_details(self, internal_id):
        """Get detailed information for a specific account.

        Args:
            internal_id: Internal Eclipse account ID

        Returns:
            dict: Account details including summarySection, holdings, etc.
        """
        res = self.api_request(f"{self.base_url}/account/accounts/{internal_id}")
        return res.json()

    def get_all_account_details(self):
        """Get detailed information for all accounts.

        Returns:
            list: List of account detail dicts
        """
        res = self.api_request(f"{self.base_url}/account/accounts/")
        return res.json()

    def get_account_cash_available(self, internal_id):
        """Get available cash for an account.

        Args:
            internal_id: Internal Eclipse account ID

        Returns:
            float: Available cash amount
        """
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
        """Get all completed (non-pending) trade orders.

        Returns:
            list: List of completed trade order dicts
        """
        return self.api_request(f"{self.base_url}/tradeorder/trades?isPending=false").json()

    def get_orders_pending(self):
        """Get all pending trade orders.

        Returns:
            list: List of pending trade order dicts
        """
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

    # Model Maintenance

    def get_all_models(self):
        """Get all investment models.

        Returns:
            list: List of model dicts with id, name, status, etc.
        """
        res = self.api_request(f"{self.base_url}/modeling/models")
        return res.json()

    def get_model(self, id):
        """Get details for a specific model.

        Args:
            id: Model ID

        Returns:
            dict: Model details including allocations and settings
        """
        res = self.api_request(f"{self.base_url}/modeling/models/{id}")
        return res.json()

    def get_model_allocations(self, id):
        """Get aggregated allocations for a model.

        Args:
            id: Model ID

        Returns:
            list: List of allocation dicts with target percentages
        """
        res = self.api_request(f"{self.base_url}/modeling/models/{id}/allocations?aggregateAllocations=true")
        return res.json()

    def get_all_security_sets(self):
        """Get all security sets.

        Returns:
            list: List of security set dicts
        """
        res = self.api_request(f"{self.base_url}/security/securityset")
        return res.json()

    def get_security_set(self, id):
        """Get details for a specific security set.

        Args:
            id: Security set ID

        Returns:
            dict: Security set details including securities and allocations
        """
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