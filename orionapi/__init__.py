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

    def get_closed_trades(self):
        """Get all closed/executed trade orders.

        Returns:
            list: List of closed trade order dicts with account, security, action, etc.
        """
        return self.api_request(f"{self.base_url}/tradeorder/closedtrades").json()

    def get_trade_instances(self, start_date, end_date):
        """Get trade instances (batches of trades) within a date range.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            list: List of trade instance dicts with id, orderCount, executeStatus, etc.
        """
        return self.api_request(
            f"{self.base_url}/tradeorder/instances?startDate={start_date}&endDate={end_date}"
        ).json()

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

    def add_model(self, name, name_space="Default", description=None, tags=None, status_id=1,
                  management_style_id=2, is_community_model=False, is_dynamic=False,
                  exclude_rebalance_sleeve=False):
        """Create a new model.

        Args:
            name: Name of the model (required)
            name_space: Namespace of the model (default "Default")
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
            "nameSpace": name_space or "Default",
            "description": description or "",
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

    def update_security_set(self, set_id, name, securities, description=None,
                            tolerance_type="ABSOLUTE", tolerance_type_value=0):
        """Update an existing security set.

        Args:
            set_id: ID of the security set to update
            name: Name of the security set
            securities: List of security dicts with:
                - id: Security ID
                - targetPercent: Target percentage
                - rank: Rank order
                - lowerModelTolerancePercent: Lower tolerance %
                - upperModelTolerancePercent: Upper tolerance %
            description: Description of the security set
            tolerance_type: "ABSOLUTE" or "BAND" (default "ABSOLUTE")
            tolerance_type_value: Tolerance value (default 0)

        Returns:
            dict with updated security set details
        """
        payload = {
            "name": name,
            "description": description,
            "toleranceType": tolerance_type,
            "toleranceTypeValue": tolerance_type_value,
            "securities": securities
        }

        res = self.api_request(
            f"{self.base_url}/security/securityset/{set_id}",
            requests.put,
            json=payload
        )
        return res.json()

    def search_securities(self, search, top=20, exclude_cash=True):
        """Search for securities by ticker symbol, name, or ID.

        Args:
            search: Search string (ticker, name, or ID)
            top: Maximum number of results (default 20)
            exclude_cash: Exclude cash securities (default True)

        Returns:
            list: List of matching security dicts with id, name, symbol, price, etc.
        """
        params = {
            "search": search,
            "top": top,
            "excludeCashSecurity": str(exclude_cash).lower()
        }
        res = self.api_request(f"{self.base_url}/security/securities", params=params)
        return res.json()

    def get_security_by_ticker(self, ticker):
        """Get a security by its ticker symbol.

        Args:
            ticker: The ticker symbol (e.g., "AAPL")

        Returns:
            dict: Security details including id, name, symbol, price

        Raises:
            NotFoundError: If no security matches the ticker
        """
        results = self.search_securities(ticker, top=10)
        # Find exact ticker match
        for sec in results:
            if sec.get('symbol', '').upper() == ticker.upper():
                return sec
        raise NotFoundError(f"No security found with ticker: {ticker}")

    # Security Set Sync Helpers

    def parse_security_set_file(self, file_path):
        """Parse a security set definition file.

        File format:
            # Security Set: Name Here
            # Description: Optional description
            # Lines starting with # are comments
            # Ticker  Lower%  Target%  Upper%
            AAPL      5       10       20
              = AAPL2    # Equivalent security
            MSFT      3       8        15

        Where Lower and Upper are absolute percentage bounds (not relative to target).
        Lines starting with "= " (indented) are equivalent securities for the previous ticker.

        Args:
            file_path: Path to the security set definition file

        Returns:
            dict with 'name', 'description', and 'securities' list (each with optional 'equivalents')
        """
        name = None
        description = None
        securities = []

        with open(file_path, 'r') as f:
            for line in f:
                raw_line = line
                line = line.strip()
                if not line:
                    continue

                # Parse header comments
                if line.startswith('#'):
                    if line.lower().startswith('# security set:'):
                        name = line.split(':', 1)[1].strip()
                    elif line.lower().startswith('# description:'):
                        description = line.split(':', 1)[1].strip()
                    continue

                # Parse equivalent security line (indented, starts with =)
                if line.startswith('='):
                    equiv_ticker = line[1:].strip()
                    if securities and equiv_ticker:
                        if 'equivalents' not in securities[-1]:
                            securities[-1]['equivalents'] = []
                        securities[-1]['equivalents'].append(equiv_ticker)
                    continue

                # Parse security line: TICKER LOWER TARGET UPPER
                parts = line.split()
                if len(parts) >= 4:
                    ticker = parts[0]
                    lower = float(parts[1].rstrip('%'))
                    target = float(parts[2].rstrip('%'))
                    upper = float(parts[3].rstrip('%'))

                    securities.append({
                        'ticker': ticker,
                        'lower_bound': lower,
                        'target': target,
                        'upper_bound': upper
                    })

        return {
            'name': name,
            'description': description,
            'securities': securities
        }

    def convert_to_eclipse_tolerances(self, securities):
        """Convert absolute bounds to Eclipse tolerance format.

        Eclipse stores tolerances as offsets from target:
        - lowerModelTolerancePercent: subtracted from target for lower bound
        - upperModelTolerancePercent: added to target for upper bound

        Args:
            securities: List of dicts with 'ticker', 'lower_bound', 'target', 'upper_bound',
                       and optional 'equivalents' list of ticker strings

        Returns:
            list: Securities with Eclipse tolerance format, resolved IDs, and equivalences
        """
        result = []
        for i, sec in enumerate(securities):
            security_info = self.get_security_by_ticker(sec['ticker'])

            # Convert absolute bounds to relative tolerances
            lower_tolerance = sec['target'] - sec['lower_bound']
            upper_tolerance = sec['upper_bound'] - sec['target']

            sec_data = {
                'id': security_info['id'],
                'targetPercent': sec['target'],
                'lowerModelTolerancePercent': lower_tolerance,
                'upperModelTolerancePercent': upper_tolerance,
                'rank': i
            }

            # Add equivalences if present
            if sec.get('equivalents'):
                equivalences = []
                for equiv_ticker in sec['equivalents']:
                    try:
                        equiv_info = self.get_security_by_ticker(equiv_ticker)
                        equivalences.append({'id': equiv_info['id']})
                    except NotFoundError:
                        # Skip equivalents that can't be found
                        pass
                if equivalences:
                    sec_data['equivalences'] = equivalences

            result.append(sec_data)

        return result

    def preview_security_set_changes(self, file_path):
        """Preview changes between a security set file and Eclipse.

        Compares the local file to the existing Eclipse security set (if any)
        and returns a detailed diff showing what would change.

        Args:
            file_path: Path to the security set definition file

        Returns:
            dict with:
                - action: 'create' or 'update'
                - name: Security set name
                - existing_id: ID if updating, None if creating
                - changes: List of change descriptions
                - new_securities: List of securities from file
                - old_securities: List of securities from Eclipse (if updating)
        """
        parsed = self.parse_security_set_file(file_path)

        if not parsed['name']:
            raise ValueError("Security set file must have '# Security Set: Name' header")

        existing = self.find_security_set_by_name(parsed['name'])

        result = {
            'action': 'update' if existing else 'create',
            'name': parsed['name'],
            'existing_id': existing['id'] if existing else None,
            'changes': [],
            'new_securities': [],
            'old_securities': []
        }

        # Build new securities list with bounds
        for sec in parsed['securities']:
            sec_info = {
                'ticker': sec['ticker'],
                'lower': sec['lower_bound'],
                'target': sec['target'],
                'upper': sec['upper_bound'],
                'equivalents': sec.get('equivalents', [])
            }
            result['new_securities'].append(sec_info)

        if existing:
            # Get current Eclipse data
            eclipse_ss = self.get_security_set(existing['id'])

            # Build old securities lookup
            old_by_ticker = {}
            for sec in eclipse_ss.get('securities', []):
                ticker = sec.get('symbol', '')
                target = sec.get('targetPercent', 0)
                lower_tol = sec.get('lowerModelTolerancePercent', 0)
                upper_tol = sec.get('upperModelTolerancePercent', 0)
                equiv_tickers = [e.get('symbol', '') for e in sec.get('equivalences', [])]

                old_info = {
                    'ticker': ticker,
                    'lower': target - lower_tol,
                    'target': target,
                    'upper': target + upper_tol,
                    'equivalents': equiv_tickers
                }
                result['old_securities'].append(old_info)
                old_by_ticker[ticker.upper()] = old_info

            # Compare and find changes
            new_tickers = set()
            for new_sec in result['new_securities']:
                ticker = new_sec['ticker'].upper()
                new_tickers.add(ticker)
                old_sec = old_by_ticker.get(ticker)

                if not old_sec:
                    result['changes'].append(f"+ ADD {new_sec['ticker']}: {new_sec['lower']}/{new_sec['target']}/{new_sec['upper']}")
                else:
                    changes = []
                    if old_sec['lower'] != new_sec['lower']:
                        changes.append(f"lower {old_sec['lower']} -> {new_sec['lower']}")
                    if old_sec['target'] != new_sec['target']:
                        changes.append(f"target {old_sec['target']} -> {new_sec['target']}")
                    if old_sec['upper'] != new_sec['upper']:
                        changes.append(f"upper {old_sec['upper']} -> {new_sec['upper']}")

                    # Compare equivalents
                    old_equiv = set(old_sec.get('equivalents', []))
                    new_equiv = set(new_sec.get('equivalents', []))
                    added_equiv = new_equiv - old_equiv
                    removed_equiv = old_equiv - new_equiv
                    if added_equiv:
                        changes.append(f"+equiv: {', '.join(added_equiv)}")
                    if removed_equiv:
                        changes.append(f"-equiv: {', '.join(removed_equiv)}")

                    if changes:
                        result['changes'].append(f"~ {new_sec['ticker']}: {', '.join(changes)}")

            # Check for removed securities
            for old_sec in result['old_securities']:
                if old_sec['ticker'].upper() not in new_tickers:
                    result['changes'].append(f"- REMOVE {old_sec['ticker']}: {old_sec['lower']}/{old_sec['target']}/{old_sec['upper']}")

        return result

    def sync_security_set_from_file(self, file_path, set_id=None):
        """Sync a security set from a definition file to Eclipse.

        If set_id is provided, updates the existing security set.
        Otherwise, creates a new security set.

        Args:
            file_path: Path to the security set definition file
            set_id: Optional ID of existing security set to update

        Returns:
            dict: Created or updated security set details
        """
        parsed = self.parse_security_set_file(file_path)

        if not parsed['name']:
            raise ValueError("Security set file must have '# Security Set: Name' header")

        eclipse_securities = self.convert_to_eclipse_tolerances(parsed['securities'])

        if set_id:
            return self.update_security_set(
                set_id=set_id,
                name=parsed['name'],
                securities=eclipse_securities,
                description=parsed['description']
            )
        else:
            return self.create_security_set(
                name=parsed['name'],
                securities=eclipse_securities,
                description=parsed['description']
            )

    def find_security_set_by_name(self, name):
        """Find a security set by name.

        Args:
            name: Name of the security set

        Returns:
            dict: Security set if found, None otherwise
        """
        all_sets = self.get_all_security_sets()
        for ss in all_sets:
            if ss.get('name', '').lower() == name.lower():
                return ss
        return None

    def sync_security_set_from_file_by_name(self, file_path):
        """Sync a security set from file, auto-detecting create vs update.

        If a security set with the same name exists, it will be updated.
        Otherwise, a new security set will be created.

        Args:
            file_path: Path to the security set definition file

        Returns:
            tuple: (result dict, 'created' or 'updated')
        """
        parsed = self.parse_security_set_file(file_path)

        if not parsed['name']:
            raise ValueError("Security set file must have '# Security Set: Name' header")

        existing = self.find_security_set_by_name(parsed['name'])

        if existing:
            result = self.sync_security_set_from_file(file_path, set_id=existing['id'])
            return result, 'updated'
        else:
            result = self.sync_security_set_from_file(file_path)
            return result, 'created'

    def export_security_set_to_file(self, set_id, file_path):
        """Export a security set to a definition file.

        Converts Eclipse tolerance format back to absolute bounds.
        Includes equivalent securities indented under primary security.

        Args:
            set_id: ID of the security set to export
            file_path: Path to write the definition file
        """
        ss = self.get_security_set(set_id)

        lines = [
            f"# Security Set: {ss.get('name', 'Unknown')}",
            f"# Description: {ss.get('description', '')}",
            "",
            "# Ticker  Lower%  Target%  Upper%"
        ]

        for sec in ss.get('securities', []):
            ticker = sec.get('symbol', sec.get('name', f"ID:{sec.get('id')}"))
            target = sec.get('targetPercent', 0)
            lower_tol = sec.get('lowerModelTolerancePercent', 0)
            upper_tol = sec.get('upperModelTolerancePercent', 0)

            # Convert back to absolute bounds
            lower_bound = target - lower_tol
            upper_bound = target + upper_tol

            lines.append(f"{ticker:<8} {lower_bound:<7.2f} {target:<7.2f} {upper_bound:<7.2f}")

            # Add equivalent securities
            for equiv in sec.get('equivalences', []):
                equiv_symbol = equiv.get('symbol', equiv.get('name', ''))
                if equiv_symbol:
                    lines.append(f"  = {equiv_symbol}")

        with open(file_path, 'w') as f:
            f.write('\n'.join(lines) + '\n')

    # Model Sync Helpers

    def update_model_detail(self, model_id, model_detail):
        """Update model detail/structure for an existing model.

        Args:
            model_id: ID of the model to update
            model_detail: Dict with model structure (same format as add_model_detail)

        Returns:
            dict with updated model details
        """
        res = self.api_request(
            f"{self.base_url}/modeling/models/{model_id}/modelDetail",
            requests.put,
            json={"modelDetail": model_detail}
        )
        return res.json()

    def find_model_by_name(self, name):
        """Find a model by name.

        Args:
            name: Name of the model

        Returns:
            dict: Model if found, None otherwise
        """
        all_models = self.get_all_models()
        for m in all_models:
            if m.get('name', '').lower() == name.lower():
                return m
        return None

    def parse_model_file(self, file_path):
        """Parse a model definition file.

        File format:
            # Model: Model Name
            # Description: Optional description
            # Lines starting with # are comments
            # Component (Security Set name)  Lower%  Target%  Upper%
            Equity                           5       100      200
            Cash Funds                       0       0        5

        Where Lower and Upper are absolute percentage bounds (not relative to target).

        Args:
            file_path: Path to the model definition file

        Returns:
            dict with 'name', 'description', and 'components' list
        """
        name = None
        description = None
        components = []

        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse header comments
                if line.startswith('#'):
                    if line.lower().startswith('# model:'):
                        name = line.split(':', 1)[1].strip()
                    elif line.lower().startswith('# description:'):
                        description = line.split(':', 1)[1].strip()
                    continue

                # Parse component line: NAME LOWER TARGET UPPER
                # Handle names with spaces by splitting from the right
                parts = line.rsplit(None, 3)
                if len(parts) >= 4:
                    # Last 3 parts are numbers, rest is the name
                    component_name = parts[0]
                    lower = float(parts[1].rstrip('%'))
                    target = float(parts[2].rstrip('%'))
                    upper = float(parts[3].rstrip('%'))

                    components.append({
                        'name': component_name,
                        'lower_bound': lower,
                        'target': target,
                        'upper_bound': upper
                    })

        return {
            'name': name,
            'description': description,
            'components': components
        }

    def convert_model_to_eclipse_format(self, components, existing_model=None, model_name=None):
        """Convert parsed model components to Eclipse modelDetail format.

        Args:
            components: List of dicts with 'name', 'lower_bound', 'target', 'upper_bound'
            existing_model: Optional existing model dict to preserve IDs
            model_name: Name for the root node (required for new models)

        Returns:
            dict: modelDetail structure for Eclipse API
        """
        # Build a lookup of existing children by name if we have an existing model
        existing_children = {}
        root_info = {}
        model_detail = existing_model.get('modelDetail') if existing_model else None
        if model_detail:
            root_info = {
                'id': model_detail.get('id'),
                'modelDetailId': model_detail.get('modelDetailId'),
                'name': model_detail.get('name'),
                'nameSpace': model_detail.get('nameSpace'),
            }
            for child in model_detail.get('children', []):
                existing_children[child.get('name', '').lower()] = child

        children = []
        for i, comp in enumerate(components):
            # Look up security set by name
            ss = self.find_security_set_by_name(comp['name'])
            if not ss:
                raise NotFoundError(f"Security set not found: {comp['name']}")

            # Convert absolute bounds to relative tolerances
            lower_tolerance = comp['target'] - comp['lower_bound']
            upper_tolerance = comp['upper_bound'] - comp['target']

            child = {
                'name': comp['name'],
                'modelTypeId': 4,  # Security Set
                'securityAsset': {'id': ss['id']},
                'targetPercent': comp['target'],
                'lowerModelTolerancePercent': lower_tolerance,
                'upperModelTolerancePercent': upper_tolerance,
                'rank': i,
                'children': []
            }

            # Preserve existing IDs if updating
            existing = existing_children.get(comp['name'].lower())
            if existing:
                if 'id' in existing:
                    child['id'] = existing['id']
                if 'modelDetailId' in existing:
                    child['modelDetailId'] = existing['modelDetailId']

            children.append(child)

        # For updates with existing detail, include root node info
        if model_detail:
            return {
                'id': root_info.get('id'),
                'modelDetailId': root_info.get('modelDetailId'),
                'name': root_info.get('name'),
                'nameSpace': root_info.get('nameSpace'),
                'children': children
            }
        else:
            # For new models or models with null detail, include name and nameSpace
            return {
                'name': model_name or 'Model',
                'nameSpace': 'Default',
                'children': children
            }

    def preview_model_changes(self, file_path):
        """Preview changes between a model file and Eclipse.

        Compares the local file to the existing Eclipse model (if any)
        and returns a detailed diff showing what would change.

        Args:
            file_path: Path to the model definition file

        Returns:
            dict with:
                - action: 'create' or 'update'
                - name: Model name
                - existing_id: ID if updating, None if creating
                - changes: List of change descriptions
                - new_components: List of components from file
                - old_components: List of components from Eclipse (if updating)
        """
        parsed = self.parse_model_file(file_path)

        if not parsed['name']:
            raise ValueError("Model file must have '# Model: Name' header")

        existing = self.find_model_by_name(parsed['name'])

        result = {
            'action': 'update' if existing else 'create',
            'name': parsed['name'],
            'existing_id': existing['id'] if existing else None,
            'changes': [],
            'new_components': [],
            'old_components': []
        }

        # Build new components list with bounds
        for comp in parsed['components']:
            comp_info = {
                'name': comp['name'],
                'lower': comp['lower_bound'],
                'target': comp['target'],
                'upper': comp['upper_bound']
            }
            result['new_components'].append(comp_info)

        if existing:
            # Get current Eclipse data
            eclipse_model = self.get_model(existing['id'])
            model_detail = eclipse_model.get('modelDetail', {})

            # Build old components lookup
            old_by_name = {}
            for child in model_detail.get('children', []):
                name = child.get('name', '')
                target = child.get('targetPercent', 0) or 0
                lower_tol = child.get('lowerModelTolerancePercent', 0) or 0
                upper_tol = child.get('upperModelTolerancePercent', 0) or 0

                old_info = {
                    'name': name,
                    'lower': target - lower_tol,
                    'target': target,
                    'upper': target + upper_tol
                }
                result['old_components'].append(old_info)
                old_by_name[name.lower()] = old_info

            # Compare and find changes
            new_names = set()
            for new_comp in result['new_components']:
                name_key = new_comp['name'].lower()
                new_names.add(name_key)
                old_comp = old_by_name.get(name_key)

                if not old_comp:
                    result['changes'].append(f"+ ADD {new_comp['name']}: {new_comp['lower']}/{new_comp['target']}/{new_comp['upper']}")
                else:
                    changes = []
                    if old_comp['lower'] != new_comp['lower']:
                        changes.append(f"lower {old_comp['lower']} -> {new_comp['lower']}")
                    if old_comp['target'] != new_comp['target']:
                        changes.append(f"target {old_comp['target']} -> {new_comp['target']}")
                    if old_comp['upper'] != new_comp['upper']:
                        changes.append(f"upper {old_comp['upper']} -> {new_comp['upper']}")

                    if changes:
                        result['changes'].append(f"~ {new_comp['name']}: {', '.join(changes)}")

            # Check for removed components
            for old_comp in result['old_components']:
                if old_comp['name'].lower() not in new_names:
                    result['changes'].append(f"- REMOVE {old_comp['name']}: {old_comp['lower']}/{old_comp['target']}/{old_comp['upper']}")

        return result

    def sync_model_from_file(self, file_path, model_id=None):
        """Sync a model from a definition file to Eclipse.

        If model_id is provided, updates the existing model.
        Otherwise, creates a new model.

        Args:
            file_path: Path to the model definition file
            model_id: Optional ID of existing model to update

        Returns:
            dict: Created or updated model details
        """
        parsed = self.parse_model_file(file_path)

        if not parsed['name']:
            raise ValueError("Model file must have '# Model: Name' header")

        if model_id:
            # Update existing model
            existing_model = self.get_model(model_id)
            model_detail = self.convert_model_to_eclipse_format(
                parsed['components'], existing_model
            )
            # Use PUT if model has detail, POST if not
            if existing_model.get('modelDetail'):
                return self.update_model_detail(model_id, model_detail)
            else:
                return self.add_model_detail(model_id, model_detail)
        else:
            # Create new model
            new_model = self.add_model(
                name=parsed['name'],
                description=parsed['description']
            )
            # For new models, use POST (add_model_detail)
            model_detail = self.convert_model_to_eclipse_format(parsed['components'])
            return self.add_model_detail(new_model['id'], model_detail)

    def sync_model_from_file_by_name(self, file_path):
        """Sync a model from file, auto-detecting create vs update.

        If a model with the same name exists, it will be updated.
        Otherwise, a new model will be created.

        Args:
            file_path: Path to the model definition file

        Returns:
            tuple: (result dict, 'created' or 'updated')
        """
        parsed = self.parse_model_file(file_path)

        if not parsed['name']:
            raise ValueError("Model file must have '# Model: Name' header")

        existing = self.find_model_by_name(parsed['name'])

        if existing:
            result = self.sync_model_from_file(file_path, model_id=existing['id'])
            return result, 'updated'
        else:
            result = self.sync_model_from_file(file_path)
            return result, 'created'

    def export_model_to_file(self, model_id, file_path):
        """Export a model to a definition file.

        Converts Eclipse tolerance format back to absolute bounds.

        Args:
            model_id: ID of the model to export
            file_path: Path to write the definition file
        """
        model = self.get_model(model_id)

        lines = [
            f"# Model: {model.get('name', 'Unknown')}",
            f"# Description: {model.get('description', '')}",
            "",
            "# Component                      Lower%  Target%  Upper%"
        ]

        model_detail = model.get('modelDetail', {})
        for child in model_detail.get('children', []):
            name = child.get('name', f"ID:{child.get('id')}")
            target = child.get('targetPercent', 0) or 0
            lower_tol = child.get('lowerModelTolerancePercent', 0) or 0
            upper_tol = child.get('upperModelTolerancePercent', 0) or 0

            # Convert back to absolute bounds
            lower_bound = target - lower_tol
            upper_bound = target + upper_tol

            lines.append(f"{name:<32} {lower_bound:<7.2f} {target:<7.2f} {upper_bound:<7.2f}")

        with open(file_path, 'w') as f:
            f.write('\n'.join(lines) + '\n')