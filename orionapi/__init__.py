__version__ = "1.7.0"

import logging
import re
import time
from pathlib import Path
from urllib.parse import urlencode

import rapidfuzz
import requests
import tabulate

# Trade Instance Type mappings (from Orion API documentation)
TRADE_INSTANCE_TYPES = {
    1: "Astro",
    2: "Cash Movements",
    3: "Global Trades",
    4: "Option Trading",
    5: "Quick Trade",
    6: "Rebalance",
    7: "Tactical Tool",
    8: "Tax Harvesting",
    9: "Tax Ticker Swap",
    10: "Trade to Target",
    11: "Liquidate",
}

# Trade Instance SubType mappings (from Orion API documentation)
TRADE_INSTANCE_SUBTYPES = {
    1: "Automated Losses",
    2: "ASTRO",
    3: "Cash Needs",
    4: "Focused Rebalance",
    5: "Full Location Rebalance",
    6: "Global Trades",
    7: "Manual Gains",
    8: "Manual Losses",
    9: "Option Trading",
    10: "Partial Location Rebalance",
    11: "Quick Trade",
    12: "Raise Cash",
    13: "Spend Cash",
    14: "Standard Rebalance",
    15: "Tactical Tool",
    16: "Tax Ticker Swap",
    17: "Trade Import",
    18: "Trade to Target",
    19: "Journal Only Cash",
    20: "Journal Cash and Holdings",
    21: "Money Market Rebalance",
    22: "Liquidate",
}

# Set-Aside Cash Constants (from Eclipse API)
CASH_TYPE_DOLLAR = 1
CASH_TYPE_PERCENT = 2

EXPIRE_TYPE_DATE = 1
EXPIRE_TYPE_TRANSACTION = 2
EXPIRE_TYPE_NONE = 3

EXPIRE_TRANS_DISTRIBUTION = 1
EXPIRE_TRANS_FEE = 3

PERCENT_CALC_DEFAULT = 0
PERCENT_CALC_TOTAL_VALUE = 1
PERCENT_CALC_EXCLUDED_VALUE = 2

MODEL_TYPE_SECURITY_SET = 4

# Billing Constants (from Orion API BillGeneratorInfoDto)
BILLING_RUN_FOR_TYPES = [
    "AllHouseholds",
    "FundFamily",
    "Custodian",
    "Representative",
    "BusinessLine",
    "SingleHHNewBill",
    "SingleHHRerun",
    "Accounts",
    "ImportedHouseholds",
]

BILLING_ACCOUNT_FILTERS = ["ActiveAccounts", "InActiveAccounts", "AllAccounts"]

TRANSACTION_STATUSES = {
    "Complete",
    "Pending",
    "Rejected",
    "Reversed",
    "Inactive",
    "PendingCorpAction",
}

REPORT_GENERATION_STATUSES = {
    "NotGenerated",
    "ErroredReport",
    "OnHold",
    "Generated",
    "PendingGeneration",
    "WillNotBeGenerated",
}

PORTFOLIO_TREE_FILTER_TYPES = {
    "PortfolioTree",
    "PortfolioGroups",
    "RegistrationsOnly",
    "AccountsOnly",
}

CANCEL_TYPES = {"Full", "Partial"}

BILLING_BILL_TYPES = [
    "Unknown",
    "Renewal",
    "NewMoney",
    "NewAccount",
    "FinancialPlanningFee",
    "Performance",
    "AdvanceCreditDebit",
]


class OrionAPIError(Exception):
    """Base exception for Orion API errors."""

    pass


class AuthenticationError(OrionAPIError):
    """Raised when authentication fails."""

    pass


class NotFoundError(OrionAPIError):
    """Raised when a requested resource is not found."""

    pass


class RateLimiter:
    """Simple rate limiter to prevent API abuse.

    Implements a token bucket algorithm to limit requests per second.

    Args:
        calls_per_second: Maximum number of API calls per second (default 10)
    """

    def __init__(self, calls_per_second=10):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second if calls_per_second > 0 else 0
        self.last_call = 0

    def wait(self):
        """Wait if necessary to respect rate limit."""
        if self.calls_per_second <= 0:
            return  # Rate limiting disabled

        now = time.time()
        time_since_last = now - self.last_call

        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_call = time.time()


class BaseAPI:
    """Base class for Orion API clients with shared request handling.

    Args:
        rate_limit: Maximum API calls per second (default 10, set to 0 to disable)
    """

    base_url = None

    def __init__(self, rate_limit=10, verify_ssl=True, ca_bundle=None):
        """Initialize base API with rate limiting and SSL configuration.

        Args:
            rate_limit: Maximum API calls per second (default 10, set to 0 to disable)
            verify_ssl: Verify SSL certificates (default True)
            ca_bundle: Path to custom CA bundle file (optional)
        """
        self._rate_limiter = RateLimiter(calls_per_second=rate_limit)
        self.verify_ssl = verify_ssl
        self.ca_bundle = ca_bundle

    def _get_auth_header(self):
        """Return authorization header dict. Subclasses must implement."""
        raise NotImplementedError("Subclasses must implement _get_auth_header()")

    def _sanitize_for_logging(self, data):
        """Remove sensitive fields from data before logging.

        Args:
            data: Dict or list to sanitize

        Returns:
            Sanitized copy of data with sensitive fields redacted
        """
        if not isinstance(data, (dict, list)):
            return data

        sensitive_keys = {
            "token",
            "password",
            "pwd",
            "access_token",
            "accessToken",
            "eclipse_access_token",
            "session",
            "sessionToken",
            "authorization",
            "api_key",
            "apiKey",
        }

        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                if key.lower() in sensitive_keys or any(
                    s in key.lower() for s in ["token", "password", "secret", "key"]
                ):
                    sanitized[key] = "***REDACTED***"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_for_logging(value)
                else:
                    sanitized[key] = value
            return sanitized
        elif isinstance(data, list):
            return [self._sanitize_for_logging(item) for item in data]

        return data

    def api_request(self, url, req_func=requests.get, timeout=30, **kwargs):
        """Make an authenticated API request with error handling.

        Args:
            url: The API endpoint URL
            req_func: The requests function to use (get, post, put, delete)
            timeout: Request timeout in seconds (default 30)
            **kwargs: Additional arguments passed to the request

        Returns:
            requests.Response object

        Raises:
            AuthenticationError: On 401/403 responses
            NotFoundError: On 404 responses
            OrionAPIError: On other 4xx/5xx responses
        """
        # Apply rate limiting
        self._rate_limiter.wait()

        headers = kwargs.pop("headers", {})
        headers.update(self._get_auth_header())

        # Set default timeout if not provided in kwargs
        if "timeout" not in kwargs:
            kwargs["timeout"] = timeout

        # Set SSL verification if not provided in kwargs
        if "verify" not in kwargs:
            if self.ca_bundle:
                kwargs["verify"] = self.ca_bundle
            else:
                kwargs["verify"] = self.verify_ssl

        res = req_func(url, headers=headers, **kwargs)

        if not res.ok:
            # Try to get error message from response body
            try:
                error_body = res.json()
                message = error_body.get("message", str(error_body))
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
        rate_limit: Maximum API calls per second (default 10, set to 0 to disable)
        verify_ssl: Verify SSL certificates (default True)
        ca_bundle: Path to custom CA bundle file (optional)

    Example:
        >>> api = OrionAPI(usr="user@example.com", pwd="password")
        >>> api.check_username()
        'user@example.com'
    """

    def __init__(self, usr=None, pwd=None, rate_limit=10, verify_ssl=True, ca_bundle=None):
        super().__init__(rate_limit=rate_limit, verify_ssl=verify_ssl, ca_bundle=ca_bundle)
        self.token = None
        self.base_url = "https://api.orionadvisor.com/api/v1/"

        if usr is not None:
            self.login(usr, pwd)
            # Credentials are not stored to prevent memory exposure

    def login(self, usr=None, pwd=None):
        """Authenticate with the Orion API.

        Args:
            usr: Username for authentication
            pwd: Password for authentication

        Raises:
            AuthenticationError: If credentials are invalid
        """
        res = requests.get(f"{self.base_url}/security/token", auth=(usr, pwd))
        if not res.ok:
            raise AuthenticationError(f"Login failed: {res.status_code} {res.reason}")
        try:
            self.token = res.json()["access_token"]
        except (KeyError, ValueError) as e:
            raise AuthenticationError(f"Invalid response from auth endpoint: {e}") from e

    def _get_auth_header(self):
        return {"Authorization": "Session " + self.token}

    def check_username(self):
        """Get the authenticated user's login ID.

        Returns:
            str: The user's login ID
        """
        res = self.api_request(f"{self.base_url}/authorization/user")
        return res.json()["loginUserId"]

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
        return self.get_query_payload(id)["prompts"]

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
            "runTo": "null",
            "databaseIdList": "null",
            "prompts": [],
        }
        run_params = []
        for p in default_params:
            if p["code"] in params:
                p["defaultValue"] = params[p["code"]]
            run_params.append(p)

        payload = payload_template.copy()
        payload["prompts"] = run_params

        res = self.api_request(
            f"{self.base_url}/Reporting/Custom/{id}/Generate/Table", requests.post, json=payload
        )
        return res.json()

    def get_all_queries(self, search_term="", top=100):
        """Get all custom queries/reports available in Orion Connect.

        Args:
            search_term: Optional search term to filter queries by name (default "")
            top: Max results to return (default 100)

        Returns:
            list: Matching queries with id, name, and other metadata
        """
        if not isinstance(search_term, str):
            raise ValueError("search_term must be a string")
        if not isinstance(top, int) or top < 1:
            raise ValueError("top must be a positive integer")

        params = urlencode({"search": search_term, "top": top})
        res = self.api_request(f"{self.base_url}/Reporting/Custom/Simple/Search?{params}")
        return res.json()

    # -------------------------------------------------------------------------
    # Custom Field Definitions
    # -------------------------------------------------------------------------

    _custom_field_cache = {}  # Cache: entity -> {display_name: code}

    def get_custom_field_definitions(self, entity):
        """Get custom field definitions for an entity type.

        Args:
            entity: 'client', 'registration', or 'account'

        Returns:
            list: Field definitions with code, description, type, options, etc.
        """
        res = self.api_request(f"{self.base_url}/Settings/UserDefinedFields/Definitions/{entity}")
        fields = res.json()

        # Cache the display name -> code mapping
        self._custom_field_cache[entity] = {
            f["description"]: f["code"] for f in fields if f.get("description")
        }
        return fields

    def _translate_custom_fields(self, entity, data):
        """Translate custom field display names to codes.

        Args:
            entity: 'client', 'registration', or 'account'
            data: Dict that may contain display names as keys

        Returns:
            dict: Data with display names replaced by udf-prefixed codes
        """
        # Ensure cache is populated
        if entity not in self._custom_field_cache:
            self.get_custom_field_definitions(entity)

        name_to_code = self._custom_field_cache.get(entity, {})
        translated = {}

        for key, value in data.items():
            if key in name_to_code:
                # It's a display name - translate to udf + code
                translated[f"udf{name_to_code[key]}"] = value
            else:
                translated[key] = value

        return translated

    # -------------------------------------------------------------------------
    # Households (Clients)
    # -------------------------------------------------------------------------

    def search_clients(self, search_term, top=20, is_active=True):
        """Search for households/clients by name.

        Args:
            search_term: Name to search for
            top: Max results to return (default 20)
            is_active: Filter to active clients only (default True)

        Returns:
            list: Matching clients with id, name, status
        """
        if not isinstance(search_term, str) or not search_term.strip():
            raise ValueError("search_term must be a non-empty string")
        if not isinstance(top, int) or top < 1:
            raise ValueError("top must be a positive integer")

        params = urlencode({"search": search_term, "top": top, "isActive": str(is_active).lower()})
        res = self.api_request(f"{self.base_url}/Portfolio/Clients/Simple/Search?{params}")
        return res.json()

    def get_client(self, client_id):
        """Get full details for a household/client.

        Args:
            client_id: Client ID

        Returns:
            dict: Client details including custom fields
        """
        res = self.api_request(f"{self.base_url}/Portfolio/Clients/{client_id}")
        return res.json()

    def update_client(self, client_id, data):
        """Update a household/client.

        Args:
            client_id: Client ID
            data: Dict of fields to update. Custom fields can use display names
                  (e.g., "Annual Spending") or codes (e.g., "udf5ANNUALSPE")

        Returns:
            dict: Updated client
        """
        translated = self._translate_custom_fields("client", data)
        res = self.api_request(
            f"{self.base_url}/Portfolio/Clients/{client_id}", requests.put, json=translated
        )
        return res.json()

    def create_client(self, data):
        """Create a new client/household.

        Args:
            data: Dict of client fields. Minimum required: {"name": "Household Name"}.
                Body is a ClientVerboseDto.

        Returns:
            dict: Created client
        """
        if not isinstance(data, dict) or not data:
            raise ValueError("data must be a non-empty dict")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Clients/Verbose", requests.post, json=data
        )
        return res.json()

    def cancel_client(
        self,
        client_id,
        cancel_type="Full",
        account_ids=None,
        as_of_date=None,
        zero_assets=False,
        exclude_download=False,
        create_final_bill=False,
    ):
        """Cancel a client/household (full or partial).

        Args:
            client_id: Client ID
            cancel_type: "Full" or "Partial" (default "Full")
            account_ids: List of account IDs (required if cancel_type is "Partial")
            as_of_date: Optional as-of date (YYYY-MM-DD format)
            zero_assets: Whether to zero out assets (default False)
            exclude_download: Whether to exclude from downloads (default False)
            create_final_bill: Whether to create a final bill (default False)

        Returns:
            dict: Cancellation result
        """
        if not isinstance(client_id, int) or client_id < 1:
            raise ValueError("client_id must be a positive integer")
        if cancel_type not in CANCEL_TYPES:
            raise ValueError(f"cancel_type must be one of {CANCEL_TYPES}")
        if cancel_type == "Partial":
            if not isinstance(account_ids, list) or not account_ids:
                raise ValueError("account_ids must be a non-empty list when cancel_type is Partial")

        payload = {
            "clientId": client_id,
            "cancelType": cancel_type,
            "zeroAssets": zero_assets,
            "excludeDownload": exclude_download,
            "createFinalBill": create_final_bill,
        }
        if account_ids is not None:
            payload["accountIds"] = account_ids
        if as_of_date is not None:
            payload["asOfDate"] = as_of_date

        res = self.api_request(
            f"{self.base_url}/Portfolio/Clients/Action/Cancel", requests.put, json=payload
        )
        return res.json()

    def delete_clients(self, client_ids):
        """Delete clients/households by ID.

        Args:
            client_ids: List of client IDs to delete

        Returns:
            list: Deleted client IDs
        """
        if not isinstance(client_ids, list) or not client_ids:
            raise ValueError("client_ids must be a non-empty list")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Clients/Action/Delete", requests.put, json=client_ids
        )
        return res.json()

    def get_portfolio_tree(
        self, client_id, include_additional=False, include_rep=False, filter_type=None
    ):
        """Get hierarchical portfolio tree for a client.

        Args:
            client_id: Client ID
            include_additional: Include additional info (default False)
            include_rep: Include representative info (default False)
            filter_type: Optional filter - "PortfolioTree", "PortfolioGroups",
                "RegistrationsOnly", or "AccountsOnly"

        Returns:
            dict: Hierarchical client -> registrations -> accounts view
        """
        if not isinstance(client_id, int) or client_id < 1:
            raise ValueError("client_id must be a positive integer")
        if filter_type is not None and filter_type not in PORTFOLIO_TREE_FILTER_TYPES:
            raise ValueError(f"filter_type must be one of {PORTFOLIO_TREE_FILTER_TYPES}")

        params = {
            "includeAdditional": str(include_additional).lower(),
            "includeRep": str(include_rep).lower(),
        }
        if filter_type is not None:
            params["filterType"] = filter_type

        url = f"{self.base_url}/Portfolio/Clients/{client_id}/PortfolioTree?" + urlencode(params)
        res = self.api_request(url)
        return res.json()

    # -------------------------------------------------------------------------
    # Registrations
    # -------------------------------------------------------------------------

    def search_registrations(self, search_term, top=20, is_active=True):
        """Search for registrations by name.

        Args:
            search_term: Name to search for
            top: Max results to return (default 20)
            is_active: Filter to active registrations only (default True)

        Returns:
            list: Matching registrations with id, name, type
        """
        if not isinstance(search_term, str) or not search_term.strip():
            raise ValueError("search_term must be a non-empty string")
        if not isinstance(top, int) or top < 1:
            raise ValueError("top must be a positive integer")

        params = urlencode({"search": search_term, "top": top, "isActive": str(is_active).lower()})
        res = self.api_request(f"{self.base_url}/Portfolio/Registrations/Simple/Search?{params}")
        return res.json()

    def get_registration(self, registration_id):
        """Get full details for a registration.

        Args:
            registration_id: Registration ID

        Returns:
            dict: Registration details including custom fields
        """
        res = self.api_request(f"{self.base_url}/Portfolio/Registrations/{registration_id}")
        return res.json()

    def get_client_registrations(self, client_id, is_active=True):
        """Get all registrations for a household/client.

        Args:
            client_id: Client ID
            is_active: Filter to active registrations only (default True)

        Returns:
            list: Registrations under this client
        """
        res = self.api_request(
            f"{self.base_url}/Portfolio/Clients/{client_id}/Registrations?isActive={str(is_active).lower()}"
        )
        return res.json()

    def update_registration(self, registration_id, data):
        """Update a registration.

        Args:
            registration_id: Registration ID
            data: Dict of fields to update. Custom fields can use display names.

        Returns:
            dict: Updated registration
        """
        translated = self._translate_custom_fields("registration", data)
        res = self.api_request(
            f"{self.base_url}/Portfolio/Registrations/{registration_id}",
            requests.put,
            json=translated,
        )
        return res.json()

    def get_registration_types(self):
        """Get available registration types (IRA, 401k, etc.).

        Returns:
            list: Registration types with id and name
        """
        res = self.api_request(f"{self.base_url}/Portfolio/Registrations/Types")
        return res.json()

    def create_registration(self, data):
        """Create a new registration.

        Args:
            data: Dict of registration fields. Minimum required: name + nested
                portfolio.clientId. Body is a RegistrationVerboseDto.

        Returns:
            dict: Created registration
        """
        if not isinstance(data, dict) or not data:
            raise ValueError("data must be a non-empty dict")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Registrations/Verbose", requests.post, json=data
        )
        return res.json()

    def move_registration(self, registration_ids, target_client_id):
        """Move registrations to a different client/household.

        Args:
            registration_ids: List of registration IDs to move
            target_client_id: Target client ID

        Returns:
            dict: Move result
        """
        if not isinstance(registration_ids, list) or not registration_ids:
            raise ValueError("registration_ids must be a non-empty list")
        if not isinstance(target_client_id, int) or target_client_id < 1:
            raise ValueError("target_client_id must be a positive integer")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Registrations/Action/MoveToClient/{target_client_id}",
            requests.put,
            json=registration_ids,
        )
        return res.json()

    def split_registration(self, registration_id):
        """Split a registration so each active non-sleeved account gets its own registration.

        Args:
            registration_id: Registration ID to split

        Returns:
            dict: Split result
        """
        if not isinstance(registration_id, int) or registration_id < 1:
            raise ValueError("registration_id must be a positive integer")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Registrations/{registration_id}/Action/Split",
            requests.put,
        )
        return res.json()

    def delete_registrations(self, registration_ids):
        """Delete registrations by ID.

        Args:
            registration_ids: List of registration IDs to delete

        Returns:
            list: Deleted registration IDs
        """
        if not isinstance(registration_ids, list) or not registration_ids:
            raise ValueError("registration_ids must be a non-empty list")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Registrations/Action/Delete",
            requests.put,
            json=registration_ids,
        )
        return res.json()

    # -------------------------------------------------------------------------
    # Accounts
    # -------------------------------------------------------------------------

    def search_orion_accounts(self, search_term, top=20, is_active=True):
        """Search for accounts by name or number.

        Args:
            search_term: Name or account number to search for
            top: Max results to return (default 20)
            is_active: Filter to active accounts only (default True)

        Returns:
            list: Matching accounts with id, number, name, custodian
        """
        if not isinstance(search_term, str) or not search_term.strip():
            raise ValueError("search_term must be a non-empty string")
        if not isinstance(top, int) or top < 1:
            raise ValueError("top must be a positive integer")

        params = urlencode({"search": search_term, "top": top, "isActive": str(is_active).lower()})
        res = self.api_request(f"{self.base_url}/Portfolio/Accounts/Simple/Search?{params}")
        return res.json()

    def get_orion_account(self, account_id):
        """Get full details for an account.

        Args:
            account_id: Account ID

        Returns:
            dict: Account details including custom fields
        """
        res = self.api_request(f"{self.base_url}/Portfolio/Accounts/{account_id}")
        return res.json()

    def update_orion_account(self, account_id, data):
        """Update an account.

        Args:
            account_id: Account ID
            data: Dict of fields to update. Custom fields can use display names.

        Returns:
            dict: Updated account
        """
        translated = self._translate_custom_fields("account", data)
        res = self.api_request(
            f"{self.base_url}/Portfolio/Accounts/{account_id}", requests.put, json=translated
        )
        return res.json()

    def create_orion_account(self, data, generate_account_number=False):
        """Create a new account.

        Args:
            data: Dict of account fields. Minimum: name + either number or
                generate_account_number=True. Body is an AccountVerboseDto.
            generate_account_number: Auto-generate account number (default False)

        Returns:
            dict: Created account
        """
        if not isinstance(data, dict) or not data:
            raise ValueError("data must be a non-empty dict")

        params = {}
        if generate_account_number:
            params["generateAccountNumber"] = "true"

        url = f"{self.base_url}/Portfolio/Accounts/Verbose"
        if params:
            url += "?" + urlencode(params)

        res = self.api_request(url, requests.post, json=data)
        return res.json()

    def move_account(self, account_id, target_registration_id):
        """Move an account to a different registration.

        Args:
            account_id: Account ID to move
            target_registration_id: Target registration ID

        Returns:
            dict: AccountBaseDto
        """
        if not isinstance(account_id, int) or account_id < 1:
            raise ValueError("account_id must be a positive integer")
        if not isinstance(target_registration_id, int) or target_registration_id < 1:
            raise ValueError("target_registration_id must be a positive integer")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Accounts/{account_id}/Action/MoveToRegistration/{target_registration_id}",
            requests.put,
        )
        return res.json()

    def merge_accounts(self, merges):
        """Merge accounts.

        Args:
            merges: List of dicts with old/new account ID pairs for merging

        Returns:
            list: Merged account IDs
        """
        if not isinstance(merges, list) or not merges:
            raise ValueError("merges must be a non-empty list")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Accounts/Action/Merge", requests.put, json=merges
        )
        return res.json()

    def convert_account(
        self,
        from_account_id,
        convert_date,
        copy_assets=True,
        copy_billing=True,
        copy_transactions=True,
        old_active=False,
    ):
        """Convert an account (e.g., IRA to Roth conversion).

        Args:
            from_account_id: Source account ID
            convert_date: Conversion date (YYYY-MM-DD format)
            copy_assets: Copy assets to new account (default True)
            copy_billing: Copy billing settings (default True)
            copy_transactions: Copy transactions (default True)
            old_active: Keep old account active (default False)

        Returns:
            dict: AccountBaseDto for the new account
        """
        if not isinstance(from_account_id, int) or from_account_id < 1:
            raise ValueError("from_account_id must be a positive integer")

        payload = {
            "fromAccountId": from_account_id,
            "convertDate": convert_date,
            "copyAssets": copy_assets,
            "copyBilling": copy_billing,
            "copyTransactions": copy_transactions,
            "oldActive": old_active,
        }

        res = self.api_request(
            f"{self.base_url}/Portfolio/Accounts/Action/ConvertAccount",
            requests.post,
            json=payload,
        )
        return res.json()

    def delete_accounts(self, account_ids):
        """Delete accounts by ID.

        Args:
            account_ids: List of account IDs to delete

        Returns:
            list: Deleted account IDs
        """
        if not isinstance(account_ids, list) or not account_ids:
            raise ValueError("account_ids must be a non-empty list")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Accounts/Action/Delete", requests.put, json=account_ids
        )
        return res.json()

    def undo_account_conversion(self, account_id):
        """Undo an account conversion.

        Args:
            account_id: Account ID to undo conversion for

        Returns:
            dict: Result of the undo operation
        """
        if not isinstance(account_id, int) or account_id < 1:
            raise ValueError("account_id must be a positive integer")

        res = self.api_request(
            f"{self.base_url}/Portfolio/Accounts/{account_id}/Action/UndoConversion",
            requests.delete,
        )
        return res.json()

    # -------------------------------------------------------------------------
    # Assets
    # -------------------------------------------------------------------------

    def get_assets(self, account_id, has_value=True):
        """Get assets for a specific account.

        Args:
            account_id: Account ID
            has_value: Filter to assets with current value (default True)

        Returns:
            list: Assets with positions, tickers, values, etc.
        """
        if not isinstance(account_id, int) or account_id < 1:
            raise ValueError("account_id must be a positive integer")
        if not isinstance(has_value, bool):
            raise ValueError("has_value must be a boolean")

        params = urlencode({"accountId": account_id, "hasValue": str(has_value).lower()})
        res = self.api_request(f"{self.base_url}/Portfolio/Assets?{params}")
        return res.json()

    def search_assets(self, search_term, top=20):
        """Search for assets by ticker, CUSIP, or name.

        Args:
            search_term: Ticker, CUSIP, or asset name to search for
            top: Max results to return (default 20)

        Returns:
            list: Matching assets with basic info
        """
        if not isinstance(search_term, str) or not search_term.strip():
            raise ValueError("search_term must be a non-empty string")
        if not isinstance(top, int) or top < 1:
            raise ValueError("top must be a positive integer")

        params = urlencode({"search": search_term, "top": top})
        res = self.api_request(f"{self.base_url}/Portfolio/Assets/Simple/Search?{params}")
        return res.json()

    # -------------------------------------------------------------------------
    # Transactions
    # -------------------------------------------------------------------------

    def get_transactions(
        self,
        account_id=None,
        client_id=None,
        registration_id=None,
        start_date=None,
        end_date=None,
        status=None,
        trans_type_ids=None,
        has_errors=None,
    ):
        """Get transactions, optionally filtered.

        Args:
            account_id: Optional account ID filter
            client_id: Optional client ID filter
            registration_id: Optional registration ID filter
            start_date: Optional start date (YYYY-MM-DD format)
            end_date: Optional end date (YYYY-MM-DD format)
            status: Optional status filter - "Complete", "Pending", "Rejected",
                "Reversed", "Inactive", or "PendingCorpAction"
            trans_type_ids: Optional list of transaction type IDs
            has_errors: Optional boolean to filter by error status

        Returns:
            list: TransactionBaseDto records
        """
        if account_id is not None and (not isinstance(account_id, int) or account_id < 1):
            raise ValueError("account_id must be a positive integer")
        if client_id is not None and (not isinstance(client_id, int) or client_id < 1):
            raise ValueError("client_id must be a positive integer")
        if registration_id is not None and (
            not isinstance(registration_id, int) or registration_id < 1
        ):
            raise ValueError("registration_id must be a positive integer")
        if status is not None and status not in TRANSACTION_STATUSES:
            raise ValueError(f"status must be one of {TRANSACTION_STATUSES}")

        params = {}
        if account_id is not None:
            params["accountId"] = account_id
        if client_id is not None:
            params["clientId"] = client_id
        if registration_id is not None:
            params["registrationId"] = registration_id
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        if status is not None:
            params["status"] = status
        if trans_type_ids is not None:
            params["transTypeIds"] = trans_type_ids
        if has_errors is not None:
            params["hasErrors"] = str(has_errors).lower()

        url = f"{self.base_url}/Portfolio/Transactions"
        if params:
            url += "?" + urlencode(params, doseq=True)
        res = self.api_request(url)
        return res.json()

    # -------------------------------------------------------------------------
    # Billing
    # -------------------------------------------------------------------------

    def get_fee_schedules(self):
        """Get all fee schedules.

        Returns:
            list: Fee schedules with billing rates and structures

        Note:
            Uses /v1/Billing/Schedules endpoint with schedule=Fee filter.
        """
        params = urlencode({"schedule": "Fee"})
        res = self.api_request(f"{self.base_url}/Billing/Schedules?{params}")
        return res.json()

    def get_account_billing(self, account_id):
        """Get billing information for a specific billing account.

        Args:
            account_id: Billing account ID (key)

        Returns:
            dict: Billing account details including fee schedule assignments

        Note:
            This is the billing account ID, which may be different from the
            portfolio account ID. Use /v1/Billing/Accounts endpoint.
        """
        if not isinstance(account_id, int) or account_id < 1:
            raise ValueError("account_id must be a positive integer")

        res = self.api_request(f"{self.base_url}/Billing/Accounts/{account_id}")
        return res.json()

    def get_billing_household_summary(self, household_id):
        """Get billing summary for a specific household.

        Args:
            household_id: Household ID (client ID)

        Returns:
            dict: Household billing summary with aggregated fee information

        Note:
            Uses /v1/Billing/HouseholdSummary/{key} endpoint.
            Requires a specific household/client ID.
        """
        if not isinstance(household_id, int) or household_id < 1:
            raise ValueError("household_id must be a positive integer")

        res = self.api_request(f"{self.base_url}/Billing/HouseholdSummary/{household_id}")
        return res.json()

    def get_billing_instances(self, start_date=None, end_date=None):
        """List billing instances, optionally filtered by date range.

        Args:
            start_date: Optional start date filter (YYYY-MM-DD format)
            end_date: Optional end date filter (YYYY-MM-DD format)

        Returns:
            list: Billing instances
        """
        params = {}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date

        url = f"{self.base_url}/Billing/Instances"
        if params:
            url += "?" + urlencode(params)
        res = self.api_request(url)
        return res.json()

    def get_billing_instance(self, instance_id):
        """Get details for a single billing instance.

        Args:
            instance_id: Billing instance ID

        Returns:
            dict: Billing instance details including status
        """
        if not isinstance(instance_id, int) or instance_id < 1:
            raise ValueError("instance_id must be a positive integer")

        res = self.api_request(f"{self.base_url}/Billing/Instances/{instance_id}")
        return res.json()

    def create_billing_instance(
        self,
        is_forecast=False,
        run_for="AllHouseholds",
        run_for_accounts="ActiveAccounts",
        bill_type="Renewal",
        nickname=None,
        keys=None,
        as_of_date=None,
        end_date_override=None,
        include_cash_flow=False,
    ):
        """Create a new billing instance (live or forecast).

        Args:
            is_forecast: If True, creates a forecast/mock bill (default False)
            run_for: Scope of the billing run. One of: AllHouseholds, FundFamily,
                Custodian, Representative, BusinessLine, SingleHHNewBill,
                SingleHHRerun, Accounts, ImportedHouseholds
            run_for_accounts: Account filter. One of: ActiveAccounts,
                InActiveAccounts, AllAccounts
            bill_type: Type of bill. One of: Unknown, Renewal, NewMoney,
                NewAccount, FinancialPlanningFee, Performance, AdvanceCreditDebit
            nickname: Optional nickname for this billing instance
            keys: Optional list of integer IDs for the selected run_for scope
            as_of_date: Optional as-of date (YYYY-MM-DD format)
            end_date_override: Optional end date override (YYYY-MM-DD format)
            include_cash_flow: Whether to include cash flow (default False)

        Returns:
            dict: Created billing instance details
        """
        if run_for not in BILLING_RUN_FOR_TYPES:
            raise ValueError(f"run_for must be one of {BILLING_RUN_FOR_TYPES}")

        if run_for_accounts not in BILLING_ACCOUNT_FILTERS:
            raise ValueError(f"run_for_accounts must be one of {BILLING_ACCOUNT_FILTERS}")

        if bill_type not in BILLING_BILL_TYPES:
            raise ValueError(f"bill_type must be one of {BILLING_BILL_TYPES}")

        if keys is not None and not isinstance(keys, list):
            raise ValueError("keys must be a list of integers")

        payload = {
            "isMockBill": is_forecast,
            "runFor": run_for,
            "runForAccounts": run_for_accounts,
            "billType": bill_type,
            "includeCashFlow": include_cash_flow,
        }
        if nickname is not None:
            payload["nickName"] = nickname
        if keys is not None:
            payload["keys"] = keys
        if as_of_date is not None:
            payload["asOfDate"] = as_of_date
        if end_date_override is not None:
            payload["endDateOverride"] = end_date_override

        res = self.api_request(
            f"{self.base_url}/Billing/BillGenerator/Action/Instance",
            requests.post,
            json=payload,
        )
        return res.json()

    def generate_billing(self, instance_id, lock_down=True):
        """Generate bills for a billing instance.

        Args:
            instance_id: Billing instance ID
            lock_down: Whether to lock down the instance during generation (default True)

        Returns:
            dict: Generation result
        """
        if not isinstance(instance_id, int) or instance_id < 1:
            raise ValueError("instance_id must be a positive integer")

        params = urlencode({"lockDown": str(lock_down).lower()})
        res = self.api_request(
            f"{self.base_url}/Billing/Instances/{instance_id}/Action/Generate?{params}",
            requests.put,
        )
        return res.json()

    def complete_billing_instance(self, instance_id):
        """Finalize/complete a billing instance.

        Args:
            instance_id: Billing instance ID

        Returns:
            dict: Updated billing instance
        """
        if not isinstance(instance_id, int) or instance_id < 1:
            raise ValueError("instance_id must be a positive integer")

        res = self.api_request(
            f"{self.base_url}/Billing/Instances/{instance_id}/Action/Complete",
            requests.post,
        )
        return res.json()

    def invalidate_billing_instance(self, instance_id):
        """Invalidate/cancel a billing instance.

        Args:
            instance_id: Billing instance ID

        Returns:
            dict: Updated billing instance
        """
        if not isinstance(instance_id, int) or instance_id < 1:
            raise ValueError("instance_id must be a positive integer")

        res = self.api_request(
            f"{self.base_url}/Billing/Instances/{instance_id}/Action/Invalidate",
            requests.post,
        )
        return res.json()

    def generate_fee_files(self, instance_id, custodian_id=None):
        """Generate fee files for a billing instance.

        Args:
            instance_id: Billing instance ID
            custodian_id: Optional custodian ID to filter fee files

        Returns:
            dict: Fee file generation result
        """
        if not isinstance(instance_id, int) or instance_id < 1:
            raise ValueError("instance_id must be a positive integer")

        url = f"{self.base_url}/Billing/Instances/Action/FeeFiles"
        if custodian_id is not None:
            if not isinstance(custodian_id, int) or custodian_id < 1:
                raise ValueError("custodian_id must be a positive integer")
            url += "?" + urlencode({"custodianId": custodian_id})

        res = self.api_request(url, requests.post, json={"ids": [instance_id]})
        return res.json()

    def get_fee_files(self, instance_id):
        """Get fee files for a billing instance.

        Args:
            instance_id: Billing instance ID

        Returns:
            list: Fee file details including fileName, status, etc.
        """
        if not isinstance(instance_id, int) or instance_id < 1:
            raise ValueError("instance_id must be a positive integer")

        res = self.api_request(f"{self.base_url}/Billing/FeeFile/instance/{instance_id}")
        return res.json()

    def get_bills(self, instance_id=None, is_valid=None, bill_type=None):
        """Get bills, optionally filtered.

        Args:
            instance_id: Optional billing instance ID to filter by
            is_valid: Optional boolean to filter by validity
            bill_type: Optional bill type string to filter by

        Returns:
            list: Bill records
        """
        params = {}
        if instance_id is not None:
            if not isinstance(instance_id, int) or instance_id < 1:
                raise ValueError("instance_id must be a positive integer")
            params["instanceId"] = instance_id
        if is_valid is not None:
            params["isValid"] = str(is_valid).lower()
        if bill_type is not None:
            params["billType"] = bill_type

        url = f"{self.base_url}/Billing/Bills"
        if params:
            url += "?" + urlencode(params)
        res = self.api_request(url)
        return res.json()

    def get_adjustment_types(self, is_payable=None, is_debit=None):
        """Get available billing adjustment types.

        Args:
            is_payable: Optional filter for payable adjustment types
            is_debit: Optional filter for debit adjustment types

        Returns:
            list: Adjustment type records with id, name, isDebit, isPayable, etc.
        """
        params = {}
        if is_payable is not None:
            params["isPayable"] = str(is_payable).lower()
        if is_debit is not None:
            params["isDebit"] = str(is_debit).lower()

        url = f"{self.base_url}/Billing/AdjustmentTypes"
        if params:
            url += "?" + urlencode(params)
        res = self.api_request(url)
        return res.json()

    def get_recurring_adjustments(self, account_id=None):
        """Get recurring billing adjustments, optionally filtered by account.

        Args:
            account_id: Optional account ID to filter by

        Returns:
            list: Recurring adjustment records with amounts, types, schedules, etc.
        """
        if account_id is not None:
            if not isinstance(account_id, int) or account_id < 1:
                raise ValueError("account_id must be a positive integer")

        url = f"{self.base_url}/Billing/Accounts/RecurringAdjustments"
        if account_id is not None:
            url += "?" + urlencode({"accountId": account_id})
        res = self.api_request(url)
        return res.json()

    def get_household_recurring_adjustments(self, household_id=None):
        """Get recurring billing adjustments at the household level.

        Args:
            household_id: Optional household/client ID to filter by

        Returns:
            list: Household recurring adjustment records
        """
        if household_id is not None:
            if not isinstance(household_id, int) or household_id < 1:
                raise ValueError("household_id must be a positive integer")

        url = f"{self.base_url}/Billing/Accounts/HouseholdRecurringAdjustments"
        if household_id is not None:
            url += "?" + urlencode({"householdId": household_id})
        res = self.api_request(url)
        return res.json()

    def get_bill_item_adjustments(self, bill_account_item_id):
        """Get adjustments for a specific bill account item.

        Args:
            bill_account_item_id: Bill account item ID

        Returns:
            list: Adjustment records with changeAmount, adjustmentType, status, etc.
        """
        if not isinstance(bill_account_item_id, int) or bill_account_item_id < 1:
            raise ValueError("bill_account_item_id must be a positive integer")

        res = self.api_request(
            f"{self.base_url}/Billing/BillGenerator/BillAccountItems/BillAccountAdj/{bill_account_item_id}"
        )
        return res.json()

    def update_bill_item_adjustments(
        self, bill_account_item_id, adjustments, create_payable_adj=None
    ):
        """Add, update, or delete adjustments on a bill account item.

        Each adjustment dict should include:
            - adjustmentTypeId (int): ID of the adjustment type
            - changeAmount (float): Dollar amount of the adjustment
            - dateOccured (str): Date of the adjustment (YYYY-MM-DD)
            - status (str): "Add", "Update", or "Delete"

        For updates/deletes, also include:
            - id (int): Existing adjustment ID

        Args:
            bill_account_item_id: Bill account item ID
            adjustments: List of adjustment dicts
            create_payable_adj: Optional bool to also create payable adjustments

        Returns:
            list: Updated adjustment records
        """
        if not isinstance(bill_account_item_id, int) or bill_account_item_id < 1:
            raise ValueError("bill_account_item_id must be a positive integer")
        if not isinstance(adjustments, list) or not adjustments:
            raise ValueError("adjustments must be a non-empty list")

        url = (
            f"{self.base_url}/Billing/BillGenerator/BillAccountItems"
            f"/BillAccountAdj/edit/{bill_account_item_id}"
        )
        if create_payable_adj is not None:
            url += "?" + urlencode({"createPayableAdj": str(create_payable_adj).lower()})

        res = self.api_request(url, requests.put, json=adjustments)
        return res.json()

    # -------------------------------------------------------------------------
    # Cash Funding
    # -------------------------------------------------------------------------

    def get_cash_funding(self, start_date, end_date, is_forecast=False, take=10000, skip=0):
        """Get cash funding data showing after-fee cash balances.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            is_forecast: If True, returns forecast data (default False)
            take: Number of records to return (default 10000)
            skip: Number of records to skip (default 0)

        Returns:
            list: CashFundingGridDto records with registrationName,
                moneyMarketBalance, balanceDue, difference, accountNumber, etc.
        """
        if not isinstance(start_date, str) or not start_date.strip():
            raise ValueError("start_date must be a non-empty string")
        if not isinstance(end_date, str) or not end_date.strip():
            raise ValueError("end_date must be a non-empty string")
        if not isinstance(take, int) or take < 1:
            raise ValueError("take must be a positive integer")

        params = {
            "startDate": start_date,
            "endDate": end_date,
            "forecast": 1 if is_forecast else 0,
            "take": take,
        }
        if skip > 0:
            params["skip"] = skip

        url = f"{self.base_url}/Billing/CashFunding?" + urlencode(params)
        res = self.api_request(url)
        return res.json()

    def generate_cash_funding(
        self, instance_ids, start_date=None, end_date=None, is_forecast=False
    ):
        """Generate cash funding data for billing instance(s).

        Args:
            instance_ids: List of billing instance IDs
            start_date: Optional start date (YYYY-MM-DD format)
            end_date: Optional end date (YYYY-MM-DD format)
            is_forecast: If True, generates forecast data (default False)

        Returns:
            dict: Generation result
        """
        if not isinstance(instance_ids, list) or not instance_ids:
            raise ValueError("instance_ids must be a non-empty list")

        params = {"billInstanceIds": instance_ids}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        if is_forecast:
            params["isForecast"] = "true"

        url = f"{self.base_url}/Billing/Instances/GenerateCashFunding?" + urlencode(
            params, doseq=True
        )
        res = self.api_request(url, requests.post)
        return res.json()

    # -------------------------------------------------------------------------
    # Bill Management
    # -------------------------------------------------------------------------

    def delete_bills(self, bill_ids, delete_related_households=False):
        """Delete bills by ID list.

        To recalculate a bill, delete it with this method then call
        generate_billing(instance_id) to regenerate.

        Args:
            bill_ids: List of bill IDs to delete
            delete_related_households: If True, also deletes related household
                bills (default False)

        Returns:
            list: Deleted bill IDs
        """
        if not isinstance(bill_ids, list) or not bill_ids:
            raise ValueError("bill_ids must be a non-empty list")

        url = f"{self.base_url}/Billing/Bills/Action/Delete"
        if delete_related_households:
            url += "?" + urlencode({"deleteRelatedHouseholds": "true"})

        res = self.api_request(url, requests.put, json={"ids": bill_ids})
        return res.json()

    # -------------------------------------------------------------------------
    # Receivables / Post Payment
    # -------------------------------------------------------------------------

    def get_receivables(self, instance_id):
        """Get outstanding fees (receivables) for a billing instance.

        Args:
            instance_id: Billing instance ID

        Returns:
            dict: Outstanding fee details for the instance
        """
        if not isinstance(instance_id, int) or instance_id < 1:
            raise ValueError("instance_id must be a positive integer")

        res = self.api_request(f"{self.base_url}/Billing/PostPayments/BillInstance/{instance_id}")
        return res.json()

    def post_payments(self, batch_number, payments):
        """Post payments to mark fees as collected.

        Args:
            batch_number: Batch number string for this payment run
            payments: List of PostPaymentsDto dicts with fields like
                accountId, billId, amountToPost, paymentDate, payMethod, etc.

        Returns:
            dict: Payment posting result
        """
        if not isinstance(batch_number, str) or not batch_number.strip():
            raise ValueError("batch_number must be a non-empty string")
        if not isinstance(payments, list) or not payments:
            raise ValueError("payments must be a non-empty list")

        url = f"{self.base_url}/Billing/PostPayments?" + urlencode({"batchNumber": batch_number})
        res = self.api_request(url, requests.post, json=payments)
        return res.json()

    def write_off_bills(self, payments, payment_from="Household", batch_number=None):
        """Write off remaining balances on bills.

        Args:
            payments: List of PostPaymentsDto dicts
            payment_from: Source of payment - "Household" or "Account"
                (default "Household")
            batch_number: Optional batch number string

        Returns:
            dict: Write-off result
        """
        valid_payment_from = ("Household", "Account")
        if payment_from not in valid_payment_from:
            raise ValueError(f"payment_from must be one of {valid_payment_from}")
        if not isinstance(payments, list) or not payments:
            raise ValueError("payments must be a non-empty list")

        params = {"paymentFrom": payment_from}
        if batch_number is not None:
            params["batchNumber"] = batch_number

        url = f"{self.base_url}/Billing/PostPayments/WriteOffBills?" + urlencode(params)
        res = self.api_request(url, requests.post, json=payments)
        return res.json()

    # -------------------------------------------------------------------------
    # Reporting
    # -------------------------------------------------------------------------

    def get_performance_data(self, entity_id, start_date, end_date, entity_type="account"):
        """Get performance metrics for an account, client, or registration over a date range.

        Args:
            entity_id: Account ID, Registration ID, or Client ID
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            entity_type: Type of entity - "account", "registration", or "client" (default "account")

        Returns:
            dict: Performance metrics including returns, benchmarks, and statistics

        Note:
            Uses the Orion Connect API entity-specific performance endpoints:
            - /v1/Portfolio/Accounts/{key}/Performance
            - /v1/Portfolio/Clients/{key}/Performance
            - /v1/Portfolio/Registrations/{key}/Performance
        """
        if not isinstance(entity_id, int) or entity_id < 1:
            raise ValueError("entity_id must be a positive integer")
        if not isinstance(start_date, str) or not start_date.strip():
            raise ValueError("start_date must be a non-empty string")
        if not isinstance(end_date, str) or not end_date.strip():
            raise ValueError("end_date must be a non-empty string")

        valid_types = ["account", "registration", "client"]
        if entity_type not in valid_types:
            raise ValueError(f"entity_type must be one of {valid_types}")

        # Map entity type to endpoint path
        endpoint_map = {
            "account": f"{self.base_url}/Portfolio/Accounts/{entity_id}/Performance",
            "registration": f"{self.base_url}/Portfolio/Registrations/{entity_id}/Performance",
            "client": f"{self.base_url}/Portfolio/Clients/{entity_id}/Performance",
        }

        params = urlencode({"startDate": start_date, "endDate": end_date})
        res = self.api_request(f"{endpoint_map[entity_type]}?{params}")
        return res.json()

    # -------------------------------------------------------------------------
    # Report Batches
    # -------------------------------------------------------------------------

    def get_report_batches(self, qpe_item_id=None):
        """List all report batches.

        Args:
            qpe_item_id: Optional QPE item ID to filter by

        Returns:
            list: ReportBatchDto records
        """
        params = {}
        if qpe_item_id is not None:
            params["qpeItemId"] = qpe_item_id

        url = f"{self.base_url}/Reporting/Batch"
        if params:
            url += "?" + urlencode(params)
        res = self.api_request(url)
        return res.json()

    def get_report_batch(self, batch_id):
        """Get a single report batch.

        Args:
            batch_id: Report batch ID

        Returns:
            dict: Report batch details including status, dates, entity type, lock status
        """
        if not isinstance(batch_id, int) or batch_id < 1:
            raise ValueError("batch_id must be a positive integer")

        res = self.api_request(f"{self.base_url}/Reporting/Batch/{batch_id}")
        return res.json()

    def get_report_batch_entities(self, batch_id, generation_status=None):
        """Get entities in a report batch.

        Args:
            batch_id: Report batch ID
            generation_status: Optional filter - "NotGenerated", "ErroredReport",
                "OnHold", "Generated", "PendingGeneration", or "WillNotBeGenerated"

        Returns:
            list: Batch entity records
        """
        if not isinstance(batch_id, int) or batch_id < 1:
            raise ValueError("batch_id must be a positive integer")
        if generation_status is not None and generation_status not in REPORT_GENERATION_STATUSES:
            raise ValueError(f"generation_status must be one of {REPORT_GENERATION_STATUSES}")

        params = {}
        if generation_status is not None:
            params["generationStatus"] = generation_status

        url = f"{self.base_url}/Reporting/Batch/{batch_id}/Entities"
        if params:
            url += "?" + urlencode(params)
        res = self.api_request(url)
        return res.json()

    def generate_statements(self, batch_id, entity_ids=None):
        """Generate PDF statements for a report batch.

        Args:
            batch_id: Report batch ID
            entity_ids: Optional list of entity IDs. If omitted, generates all.

        Returns:
            list: Updated entity IDs
        """
        if not isinstance(batch_id, int) or batch_id < 1:
            raise ValueError("batch_id must be a positive integer")

        url = f"{self.base_url}/Reporting/Batch/{batch_id}/Entities/Action/Generate"
        kwargs = {}
        if entity_ids is not None:
            kwargs["json"] = entity_ids

        res = self.api_request(url, requests.post, **kwargs)
        return res.json()

    def send_electronic_statements(self, batch_id, entity_ids=None):
        """Send electronic statements (email) for a report batch.

        Args:
            batch_id: Report batch ID
            entity_ids: Optional list of entity IDs. If omitted, sends all.

        Returns:
            list: Updated entity IDs
        """
        if not isinstance(batch_id, int) or batch_id < 1:
            raise ValueError("batch_id must be a positive integer")

        url = f"{self.base_url}/Reporting/Batch/{batch_id}/Entities/Action/SendElectronicStatement"
        kwargs = {}
        if entity_ids is not None:
            kwargs["json"] = entity_ids

        res = self.api_request(url, requests.post, **kwargs)
        return res.json()

    def get_report_batch_verbose(self, batch_id, expand="All"):
        """Get verbose details of a report batch.

        Args:
            batch_id: Report batch ID
            expand: Level of detail - "None", "Batch", "Inserts", or "All" (default)

        Returns:
            dict: Full batch configuration including report template, entity
                selection, email settings, and inserts
        """
        if not isinstance(batch_id, int) or batch_id < 1:
            raise ValueError("batch_id must be a positive integer")

        params = urlencode({"expand": expand})
        res = self.api_request(f"{self.base_url}/Reporting/Batch/Verbose/{batch_id}?{params}")
        return res.json()

    def create_report_batch(self, batch_data):
        """Create a new report batch.

        Args:
            batch_data: ReportBatchVerboseDto dict. At minimum, batch_data["batch"]
                must contain "name", "entity", and "reportId".

        Returns:
            dict: The created batch with server-assigned ID
        """
        res = self.api_request(
            f"{self.base_url}/Reporting/Batch/Verbose",
            requests.post,
            json=batch_data,
        )
        return res.json()

    def copy_report_batch(self, batch_id, name, start_date=None, end_date=None):
        """Copy an existing report batch with a new name and optional date range.

        Fetches the full configuration of the source batch, strips server-assigned
        fields (id, audit info, generation state), applies the new name and dates,
        and creates a new batch.

        Args:
            batch_id: Source batch ID to copy
            name: Name for the new batch
            start_date: Optional new start date (ISO format, e.g., "2026-04-01")
            end_date: Optional new end date (ISO format, e.g., "2026-06-30")

        Returns:
            dict: The newly created batch with server-assigned ID
        """
        if not isinstance(batch_id, int) or batch_id < 1:
            raise ValueError("batch_id must be a positive integer")
        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string")

        # 1. Fetch full source batch configuration
        source = self.get_report_batch_verbose(batch_id)

        # 2. Strip server-assigned / read-only fields
        source.pop("id", None)
        if "batch" in source and source["batch"]:
            source["batch"].pop("id", None)
            source["batch"].pop("auditedBy", None)
            source["batch"].pop("auditedDate", None)

            # 3. Apply new name and dates
            source["batch"]["name"] = name
            if start_date is not None:
                source["batch"]["startDate"] = start_date
            if end_date is not None:
                source["batch"]["endDate"] = end_date

        # Strip IDs from inserts so they're created fresh
        if "inserts" in source and source["inserts"]:
            for insert in source["inserts"]:
                insert.pop("id", None)

        # 4. Create the new batch
        return self.create_report_batch(source)

    def update_report_batch(self, batch_id, batch_data):
        """Update an existing report batch.

        Args:
            batch_id: Report batch ID to update
            batch_data: Full ReportBatchVerboseDto dict

        Returns:
            dict: The updated batch
        """
        if not isinstance(batch_id, int) or batch_id < 1:
            raise ValueError("batch_id must be a positive integer")

        res = self.api_request(
            f"{self.base_url}/Reporting/Batch/Verbose/{batch_id}",
            requests.put,
            json=batch_data,
        )
        return res.json()


class EclipseAPI(BaseAPI):
    """Client for the Eclipse Trading Platform API.

    Provides access to accounts, portfolios, models, orders, and trade tools.

    Args:
        usr: Username for authentication
        pwd: Password for authentication
        orion_token: Orion session token (alternative to usr/pwd)
        rate_limit: Maximum API calls per second (default 10, set to 0 to disable)
        verify_ssl: Verify SSL certificates (default True)
        ca_bundle: Path to custom CA bundle file (optional)

    Example:
        >>> api = EclipseAPI(usr="user@example.com", pwd="password")
        >>> api.check_username()
        'user@example.com'
    """

    def __init__(
        self, usr=None, pwd=None, orion_token=None, rate_limit=10, verify_ssl=True, ca_bundle=None
    ):
        super().__init__(rate_limit=rate_limit, verify_ssl=verify_ssl, ca_bundle=ca_bundle)
        self.eclipse_token = None
        self.base_url = "https://api.orioneclipse.com/v1"

        if usr is not None:
            self.login(usr, pwd)
            # Credentials are not stored to prevent memory exposure
        elif orion_token is not None:
            self.login(orion_token=orion_token)

    def login(self, usr=None, pwd=None, orion_token=None):
        """Authenticate with the Eclipse API.

        Args:
            usr: Username for authentication
            pwd: Password for authentication
            orion_token: Orion session token (alternative to usr/pwd)

        Raises:
            AuthenticationError: If credentials are invalid or missing
        """
        if orion_token is None and usr is None:
            raise AuthenticationError("Must provide either usr/pwd or orion_token")

        if usr is not None:
            res = requests.get(f"{self.base_url}/admin/token", auth=(usr, pwd))
            if not res.ok:
                raise AuthenticationError(f"Login failed: {res.status_code} {res.reason}")
            try:
                self.eclipse_token = res.json()["eclipse_access_token"]
            except (KeyError, ValueError) as e:
                raise AuthenticationError(f"Invalid response from auth endpoint: {e}") from e

        elif orion_token is not None:
            res = requests.get(
                f"{self.base_url}/admin/token",
                headers={"Authorization": "Session " + orion_token},
            )
            if not res.ok:
                raise AuthenticationError(f"Token exchange failed: {res.status_code} {res.reason}")
            try:
                self.eclipse_token = res.json()["eclipse_access_token"]
            except (KeyError, ValueError) as e:
                raise AuthenticationError(f"Invalid response from auth endpoint: {e}") from e

    def _get_auth_header(self):
        return {"Authorization": "Session " + self.eclipse_token}

    def check_username(self):
        """Get the authenticated user's login ID.

        Returns:
            str: The user's login ID
        """
        res = self.api_request(f"{self.base_url}/admin/authorization/user")
        return res.json()["userLoginId"]

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
        return res[0]["id"]

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
        num_match = [a for a in accounts if a["accountNumber"].endswith(from_acct)]

        if not num_match:
            raise NotFoundError(f"No accounts found for acct# {acct_num_portion}")

        # If multiple number matches, log but continue
        if len(num_match) > 1:
            logging.info(
                "Multiple accounts share trailing digits '%s': %s",
                from_acct,
                [
                    {k: a[k] for k in ["id", "name", "accountId", "accountNumber", "accountType"]}
                    for a in num_match
                ],
            )

        ### Pick the best fuzzy name match
        best_acct = max(
            num_match,
            key=lambda a: rapidfuzz.fuzz.partial_ratio(
                name_portion, self.normalize_name(a["name"])
            ),
        )
        return best_acct["id"], best_acct["accountNumber"]

    def create_set_aside(
        self,
        account_number,
        amount,
        min_amount=0.0,
        max_amount=0.0,
        description=None,
        cash_type="$",
        start_date=None,
        expire_type="None",
        expire_date=None,
        expire_trans_tol=0,
        expire_trans_type=1,
        percent_calc_type=0,
        sync=True,
    ):
        """Create a set-aside cash reservation for an account.

        Args:
            account_number: Full custodial account number
            amount: Cash amount to set aside
            min_amount: Minimum cash amount (default 0.0)
            max_amount: Maximum cash amount (default 0.0)
            description: Description of the set-aside
            cash_type: '$' for dollar amount, '%' for percentage (default '$')
            start_date: Start date for the set-aside
            expire_type: 'None', 'Date', or 'Transaction' (default 'None')
            expire_date: Expiration date (if expire_type='Date')
            expire_trans_tol: Transaction tolerance value (default 0)
            expire_trans_type: 1='Distribution / Merge Out', 3='Fee' (default 1)
            percent_calc_type: 0='Use Default/Managed Value', 1='Use Total Value',
                              2='Use Excluded Value' (default 0)
            sync: Wait for analytics to complete (default True)

        Returns:
            dict: Created set-aside details
        """
        account_id = self.get_internal_account_id(account_number)

        cash_type_map = {
            # end point account/accounts/asideCashAmountType
            "$": 1,
            "%": 2,
        }
        if isinstance(cash_type, str):
            cash_type = cash_type_map[cash_type]

        expire_type_map = {
            # end point account/accounts/asideCashExpirationType
            "Date": 1,
            "Transaction": 2,
            "None": 3,
        }
        if isinstance(expire_type, str):
            logging.debug("mapping expire type")
            expire_type = expire_type_map[expire_type]
        logging.debug("Expire type is %s (type: %s)", expire_type, type(expire_type))

        expire_trans_type_map = {
            # end point account/accounts/asideCashTransactionType
            "Distribution / Merge Out": 1,
            "Fee": 3,
        }
        if isinstance(expire_trans_type, str):
            expire_trans_type = expire_trans_type_map[expire_trans_type]

        if expire_type == 1:
            expire_value = expire_date
        elif expire_type == 2:
            # Transaction-based expiration uses toleranceValue, expirationValue should be 0
            expire_value = 0
        elif expire_type == 3:
            expire_value = 0

        percent_calc_type_map = {
            "Use Default/Managed Value": 0,
            "Use Total Value": 1,
            "Use Excluded Value": 2,
        }
        if isinstance(percent_calc_type, str):
            percent_calc_type = percent_calc_type_map[percent_calc_type]

        res = self.api_request(
            f"{self.base_url}/account/accounts/{account_id}/asidecash",
            requests.post,
            json={
                "cashAmountTypeId": cash_type,
                "cashAmount": float(amount),
                "minCashAmount": float(min_amount),
                "maxCashAmount": float(max_amount),
                "expirationTypeId": expire_type,
                "expirationValue": expire_value,
                "toleranceValue": expire_trans_tol,
                "transactionTypeId": expire_trans_type,
                "description": description,
                "percentCalculationTypeId": percent_calc_type,
            },
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result

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
        return res["summarySection"]["cashAvailable"]

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
            params={"accountType": account_type},
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

    def run_analytics(self):
        """Run analytics for portfolios that need it.

        Triggers the post-import analysis process for portfolios flagged
        as needing analytics. Status updates are sent via socket.io.

        Returns:
            dict: Response with analytics run status
        """
        res = self.api_request(f"{self.base_url}/postimport/run_need_analysis")
        return res.json()

    def get_analytics_status(self):
        """Check if analytics are currently running.

        Returns:
            dict: Status with 'isAnalysisRunning' and 'doRunAnalytics' flags
                  (0 = not running/no pending, 1 = running/pending)
        """
        res = self.api_request(f"{self.base_url}/dataimport/analysis/status")
        return res.json()

    def wait_for_analytics(self, poll_interval=1, timeout=300):
        """Wait for analytics to complete.

        Polls the analytics status until isAnalysisRunning is 0.

        Args:
            poll_interval: Seconds between status checks (default 1)
            timeout: Max seconds to wait (default 300)

        Returns:
            True when analytics complete

        Raises:
            TimeoutError: If analytics don't complete within timeout
        """
        start = time.time()
        while True:
            status = self.get_analytics_status()
            if not status.get("isAnalysisRunning"):
                return True
            if time.time() - start > timeout:
                raise TimeoutError(f"Analytics did not complete within {timeout} seconds")
            time.sleep(poll_interval)

    def _maybe_wait_for_analytics(self, sync):
        """Helper to conditionally wait for analytics."""
        if sync:
            self.wait_for_analytics()

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

    def cash_needs_trade(
        self,
        portfolio_ids,
        portfolio_trade_group_ids=None,
        is_view_only=True,
        reason="",
        is_excel_import=False,
        sync=True,
    ):
        """Rebalance CashNeeds Portfolios.

        Args:
            portfolio_ids: List of portfolio IDs to process
            portfolio_trade_group_ids: List of portfolio trade group IDs (optional)
            is_view_only: If True, preview trades without executing (default True)
            reason: Reason for the trade
            is_excel_import: Whether this is from an Excel import (default False)
            sync: Wait for analytics to complete (default True)

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
            "isExcelImport": is_excel_import,
        }

        res = self.api_request(
            f"{self.base_url}/tradetool/cashneeds/action/generatetrade", requests.post, json=payload
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result

    def spend_cash_trade(
        self,
        portfolio_ids,
        portfolio_trade_group_ids=None,
        is_view_only=True,
        reason="",
        is_excel_import=False,
        sync=True,
    ):
        """Generate Spend Cash trade for portfolios.

        Args:
            portfolio_ids: List of portfolio IDs to process
            portfolio_trade_group_ids: List of portfolio trade group IDs (optional)
            is_view_only: If True, preview trades without executing (default True)
            reason: Reason for the trade
            is_excel_import: Whether this is from an Excel import (default False)
            sync: Wait for analytics to complete (default True)

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
            "isExcelImport": is_excel_import,
        }

        res = self.api_request(
            f"{self.base_url}/tradetool/spendcash/action/generatetrade", requests.post, json=payload
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result

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
            list: List of trade instance dicts with id, orderCount, executeStatus,
                  tradeInstanceType (string), tradeInstanceSubType (string), etc.
        """
        instances = self.api_request(
            f"{self.base_url}/tradeorder/instances?startDate={start_date}&endDate={end_date}"
        ).json()

        # Convert type/subtype IDs to friendly names
        for inst in instances:
            type_id = inst.get("tradeInstanceType")
            subtype_id = inst.get("tradeInstanceSubType")
            inst["tradeInstanceType"] = TRADE_INSTANCE_TYPES.get(type_id) if type_id else None
            inst["tradeInstanceSubType"] = (
                TRADE_INSTANCE_SUBTYPES.get(subtype_id) if subtype_id else None
            )

        return instances

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
        res = self.api_request(
            f"{self.base_url}/modeling/models/{id}/allocations?aggregateAllocations=true"
        )
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

    def add_model(
        self,
        name,
        name_space="Default",
        description=None,
        tags=None,
        status_id=1,
        management_style_id=2,
        is_community_model=False,
        is_dynamic=False,
        exclude_rebalance_sleeve=False,
    ):
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
            "excludeRebalanceSleeve": exclude_rebalance_sleeve,
        }

        res = self.api_request(f"{self.base_url}/modeling/models", requests.post, json=payload)
        return res.json()

    def add_model_detail(self, model_id, model_detail, sync=True):
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
            sync: Wait for analytics to complete (default True)

        Returns:
            dict with updated model details
        """
        res = self.api_request(
            f"{self.base_url}/modeling/models/{model_id}/modelDetail",
            requests.post,
            json={"modelDetail": model_detail},
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result

    def delete_model(self, model_id):
        """Delete a model (soft delete).

        Args:
            model_id: ID of the model to delete

        Returns:
            dict with success message
        """
        res = self.api_request(f"{self.base_url}/modeling/models/{model_id}", requests.delete)
        return res.json()

    def create_security_set(
        self, name, securities, description=None, tolerance_type="ABSOLUTE", tolerance_type_value=0
    ):
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
            "securities": securities,
        }

        res = self.api_request(f"{self.base_url}/security/securityset", requests.post, json=payload)
        return res.json()

    def update_security_set(
        self,
        set_id,
        name,
        securities,
        description=None,
        tolerance_type="ABSOLUTE",
        tolerance_type_value=0,
        sync=True,
    ):
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
            sync: Wait for analytics to complete (default True)

        Returns:
            dict with updated security set details
        """
        payload = {
            "name": name,
            "description": description,
            "toleranceType": tolerance_type,
            "toleranceTypeValue": tolerance_type_value,
            "securities": securities,
        }

        res = self.api_request(
            f"{self.base_url}/security/securityset/{set_id}", requests.put, json=payload
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result

    def search_securities(self, search, top=20, exclude_cash=True):
        """Search for securities by ticker symbol, name, or ID.

        Args:
            search: Search string (ticker, name, or ID)
            top: Maximum number of results (default 20)
            exclude_cash: Exclude cash securities (default True)

        Returns:
            list: List of matching security dicts with id, name, symbol, price, etc.
        """
        params = {"search": search, "top": top, "excludeCashSecurity": str(exclude_cash).lower()}
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
            if sec.get("symbol", "").upper() == ticker.upper():
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
        # Validate file path
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        name = None
        description = None
        securities = []

        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse header comments
                if line.startswith("#"):
                    if line.lower().startswith("# security set:"):
                        name = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("# description:"):
                        description = line.split(":", 1)[1].strip()
                    continue

                # Parse equivalent security line (indented, starts with =)
                if line.startswith("="):
                    equiv_ticker = line[1:].strip()
                    if securities and equiv_ticker:
                        if "equivalents" not in securities[-1]:
                            securities[-1]["equivalents"] = []
                        securities[-1]["equivalents"].append(equiv_ticker)
                    continue

                # Parse security line: TICKER LOWER TARGET UPPER
                parts = line.split()
                if len(parts) >= 4:
                    ticker = parts[0]
                    lower = float(parts[1].rstrip("%"))
                    target = float(parts[2].rstrip("%"))
                    upper = float(parts[3].rstrip("%"))

                    securities.append(
                        {
                            "ticker": ticker,
                            "lower_bound": lower,
                            "target": target,
                            "upper_bound": upper,
                        }
                    )

        return {"name": name, "description": description, "securities": securities}

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
            security_info = self.get_security_by_ticker(sec["ticker"])

            # Convert absolute bounds to relative tolerances
            lower_tolerance = sec["target"] - sec["lower_bound"]
            upper_tolerance = sec["upper_bound"] - sec["target"]

            sec_data = {
                "id": security_info["id"],
                "targetPercent": sec["target"],
                "lowerModelTolerancePercent": lower_tolerance,
                "upperModelTolerancePercent": upper_tolerance,
                "rank": i,
            }

            # Add equivalences if present
            if sec.get("equivalents"):
                equivalences = []
                for equiv_ticker in sec["equivalents"]:
                    try:
                        equiv_info = self.get_security_by_ticker(equiv_ticker)
                        equivalences.append({"id": equiv_info["id"]})
                    except NotFoundError:
                        # Skip equivalents that can't be found
                        pass
                if equivalences:
                    sec_data["equivalences"] = equivalences

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

        if not parsed["name"]:
            raise ValueError("Security set file must have '# Security Set: Name' header")

        existing = self.find_security_set_by_name(parsed["name"])

        result = {
            "action": "update" if existing else "create",
            "name": parsed["name"],
            "existing_id": existing["id"] if existing else None,
            "changes": [],
            "new_securities": [],
            "old_securities": [],
        }

        # Build new securities list with bounds
        for sec in parsed["securities"]:
            sec_info = {
                "ticker": sec["ticker"],
                "lower": sec["lower_bound"],
                "target": sec["target"],
                "upper": sec["upper_bound"],
                "equivalents": sec.get("equivalents", []),
            }
            result["new_securities"].append(sec_info)

        if existing:
            # Get current Eclipse data
            eclipse_ss = self.get_security_set(existing["id"])

            # Build old securities lookup
            old_by_ticker = {}
            for sec in eclipse_ss.get("securities", []):
                ticker = sec.get("symbol", "")
                target = sec.get("targetPercent", 0)
                lower_tol = sec.get("lowerModelTolerancePercent", 0)
                upper_tol = sec.get("upperModelTolerancePercent", 0)
                equiv_tickers = [e.get("symbol", "") for e in sec.get("equivalences", [])]

                old_info = {
                    "ticker": ticker,
                    "lower": target - lower_tol,
                    "target": target,
                    "upper": target + upper_tol,
                    "equivalents": equiv_tickers,
                }
                result["old_securities"].append(old_info)
                old_by_ticker[ticker.upper()] = old_info

            # Compare and find changes
            new_tickers = set()
            for new_sec in result["new_securities"]:
                ticker = new_sec["ticker"].upper()
                new_tickers.add(ticker)
                old_sec = old_by_ticker.get(ticker)

                if not old_sec:
                    result["changes"].append(
                        f"+ ADD {new_sec['ticker']}: {new_sec['lower']}/{new_sec['target']}/{new_sec['upper']}"
                    )
                else:
                    changes = []
                    if old_sec["lower"] != new_sec["lower"]:
                        changes.append(f"lower {old_sec['lower']} -> {new_sec['lower']}")
                    if old_sec["target"] != new_sec["target"]:
                        changes.append(f"target {old_sec['target']} -> {new_sec['target']}")
                    if old_sec["upper"] != new_sec["upper"]:
                        changes.append(f"upper {old_sec['upper']} -> {new_sec['upper']}")

                    # Compare equivalents
                    old_equiv = set(old_sec.get("equivalents", []))
                    new_equiv = set(new_sec.get("equivalents", []))
                    added_equiv = new_equiv - old_equiv
                    removed_equiv = old_equiv - new_equiv
                    if added_equiv:
                        changes.append(f"+equiv: {', '.join(added_equiv)}")
                    if removed_equiv:
                        changes.append(f"-equiv: {', '.join(removed_equiv)}")

                    if changes:
                        result["changes"].append(f"~ {new_sec['ticker']}: {', '.join(changes)}")

            # Check for removed securities
            for old_sec in result["old_securities"]:
                if old_sec["ticker"].upper() not in new_tickers:
                    result["changes"].append(
                        f"- REMOVE {old_sec['ticker']}: {old_sec['lower']}/{old_sec['target']}/{old_sec['upper']}"
                    )

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

        if not parsed["name"]:
            raise ValueError("Security set file must have '# Security Set: Name' header")

        eclipse_securities = self.convert_to_eclipse_tolerances(parsed["securities"])

        if set_id:
            return self.update_security_set(
                set_id=set_id,
                name=parsed["name"],
                securities=eclipse_securities,
                description=parsed["description"],
            )
        else:
            return self.create_security_set(
                name=parsed["name"],
                securities=eclipse_securities,
                description=parsed["description"],
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
            if ss.get("name", "").lower() == name.lower():
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

        if not parsed["name"]:
            raise ValueError("Security set file must have '# Security Set: Name' header")

        existing = self.find_security_set_by_name(parsed["name"])

        if existing:
            result = self.sync_security_set_from_file(file_path, set_id=existing["id"])
            return result, "updated"
        else:
            result = self.sync_security_set_from_file(file_path)
            return result, "created"

    def export_security_set_to_file(self, set_id, file_path):
        """Export a security set to a definition file.

        Converts Eclipse tolerance format back to absolute bounds.
        Includes equivalent securities indented under primary security.

        Args:
            set_id: ID of the security set to export
            file_path: Path to write the definition file
        """
        # Validate file path
        file_path = Path(file_path).resolve()
        if not file_path.parent.exists():
            raise FileNotFoundError(f"Parent directory does not exist: {file_path.parent}")
        if file_path.exists() and not file_path.is_file():
            raise ValueError(f"Path exists but is not a file: {file_path}")

        ss = self.get_security_set(set_id)

        lines = [
            f"# Security Set: {ss.get('name', 'Unknown')}",
            f"# Description: {ss.get('description', '')}",
            "",
            "# Ticker  Lower%  Target%  Upper%",
        ]

        for sec in ss.get("securities", []):
            ticker = sec.get("symbol", sec.get("name", f"ID:{sec.get('id')}"))
            target = sec.get("targetPercent", 0)
            lower_tol = sec.get("lowerModelTolerancePercent", 0)
            upper_tol = sec.get("upperModelTolerancePercent", 0)

            # Convert back to absolute bounds
            lower_bound = target - lower_tol
            upper_bound = target + upper_tol

            lines.append(f"{ticker:<8} {lower_bound:<7.2f} {target:<7.2f} {upper_bound:<7.2f}")

            # Add equivalent securities
            for equiv in sec.get("equivalences", []):
                equiv_symbol = equiv.get("symbol", equiv.get("name", ""))
                if equiv_symbol:
                    lines.append(f"  = {equiv_symbol}")

        with open(file_path, "w") as f:
            f.write("\n".join(lines) + "\n")

    # Model Sync Helpers

    def update_model_detail(self, model_id, model_detail, sync=True):
        """Update model detail/structure for an existing model.

        Args:
            model_id: ID of the model to update
            model_detail: Dict with model structure (same format as add_model_detail)
            sync: Wait for analytics to complete (default True)

        Returns:
            dict with updated model details
        """
        res = self.api_request(
            f"{self.base_url}/modeling/models/{model_id}/modelDetail",
            requests.put,
            json={"modelDetail": model_detail},
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result

    def find_model_by_name(self, name):
        """Find a model by name.

        Args:
            name: Name of the model

        Returns:
            dict: Model if found, None otherwise
        """
        all_models = self.get_all_models()
        for m in all_models:
            if m.get("name", "").lower() == name.lower():
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
        # Validate file path
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        name = None
        description = None
        components = []

        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse header comments
                if line.startswith("#"):
                    if line.lower().startswith("# model:"):
                        name = line.split(":", 1)[1].strip()
                    elif line.lower().startswith("# description:"):
                        description = line.split(":", 1)[1].strip()
                    continue

                # Parse component line: NAME LOWER TARGET UPPER
                # Handle names with spaces by splitting from the right
                parts = line.rsplit(None, 3)
                if len(parts) >= 4:
                    # Last 3 parts are numbers, rest is the name
                    component_name = parts[0]
                    lower = float(parts[1].rstrip("%"))
                    target = float(parts[2].rstrip("%"))
                    upper = float(parts[3].rstrip("%"))

                    components.append(
                        {
                            "name": component_name,
                            "lower_bound": lower,
                            "target": target,
                            "upper_bound": upper,
                        }
                    )

        return {"name": name, "description": description, "components": components}

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
        model_detail = existing_model.get("modelDetail") if existing_model else None
        if model_detail:
            root_info = {
                "id": model_detail.get("id"),
                "modelDetailId": model_detail.get("modelDetailId"),
                "name": model_detail.get("name"),
                "nameSpace": model_detail.get("nameSpace"),
            }
            for child in model_detail.get("children", []):
                existing_children[child.get("name", "").lower()] = child

        children = []
        for i, comp in enumerate(components):
            # Look up security set by name
            ss = self.find_security_set_by_name(comp["name"])
            if not ss:
                raise NotFoundError(f"Security set not found: {comp['name']}")

            # Convert absolute bounds to relative tolerances
            lower_tolerance = comp["target"] - comp["lower_bound"]
            upper_tolerance = comp["upper_bound"] - comp["target"]

            child = {
                "name": comp["name"],
                "modelTypeId": 4,  # Security Set
                "securityAsset": {"id": ss["id"]},
                "targetPercent": comp["target"],
                "lowerModelTolerancePercent": lower_tolerance,
                "upperModelTolerancePercent": upper_tolerance,
                "rank": i,
                "children": [],
            }

            # Preserve existing IDs if updating
            existing = existing_children.get(comp["name"].lower())
            if existing:
                if "id" in existing:
                    child["id"] = existing["id"]
                if "modelDetailId" in existing:
                    child["modelDetailId"] = existing["modelDetailId"]

            children.append(child)

        # For updates with existing detail, include root node info
        if model_detail:
            return {
                "id": root_info.get("id"),
                "modelDetailId": root_info.get("modelDetailId"),
                "name": root_info.get("name"),
                "nameSpace": root_info.get("nameSpace"),
                "children": children,
            }
        else:
            # For new models or models with null detail, include name and nameSpace
            return {"name": model_name or "Model", "nameSpace": "Default", "children": children}

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

        if not parsed["name"]:
            raise ValueError("Model file must have '# Model: Name' header")

        existing = self.find_model_by_name(parsed["name"])

        result = {
            "action": "update" if existing else "create",
            "name": parsed["name"],
            "existing_id": existing["id"] if existing else None,
            "changes": [],
            "new_components": [],
            "old_components": [],
        }

        # Build new components list with bounds
        for comp in parsed["components"]:
            comp_info = {
                "name": comp["name"],
                "lower": comp["lower_bound"],
                "target": comp["target"],
                "upper": comp["upper_bound"],
            }
            result["new_components"].append(comp_info)

        if existing:
            # Get current Eclipse data
            eclipse_model = self.get_model(existing["id"])
            model_detail = eclipse_model.get("modelDetail", {})

            # Build old components lookup
            old_by_name = {}
            for child in model_detail.get("children", []):
                name = child.get("name", "")
                target = child.get("targetPercent", 0) or 0
                lower_tol = child.get("lowerModelTolerancePercent", 0) or 0
                upper_tol = child.get("upperModelTolerancePercent", 0) or 0

                old_info = {
                    "name": name,
                    "lower": target - lower_tol,
                    "target": target,
                    "upper": target + upper_tol,
                }
                result["old_components"].append(old_info)
                old_by_name[name.lower()] = old_info

            # Compare and find changes
            new_names = set()
            for new_comp in result["new_components"]:
                name_key = new_comp["name"].lower()
                new_names.add(name_key)
                old_comp = old_by_name.get(name_key)

                if not old_comp:
                    result["changes"].append(
                        f"+ ADD {new_comp['name']}: {new_comp['lower']}/{new_comp['target']}/{new_comp['upper']}"
                    )
                else:
                    changes = []
                    if old_comp["lower"] != new_comp["lower"]:
                        changes.append(f"lower {old_comp['lower']} -> {new_comp['lower']}")
                    if old_comp["target"] != new_comp["target"]:
                        changes.append(f"target {old_comp['target']} -> {new_comp['target']}")
                    if old_comp["upper"] != new_comp["upper"]:
                        changes.append(f"upper {old_comp['upper']} -> {new_comp['upper']}")

                    if changes:
                        result["changes"].append(f"~ {new_comp['name']}: {', '.join(changes)}")

            # Check for removed components
            for old_comp in result["old_components"]:
                if old_comp["name"].lower() not in new_names:
                    result["changes"].append(
                        f"- REMOVE {old_comp['name']}: {old_comp['lower']}/{old_comp['target']}/{old_comp['upper']}"
                    )

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

        if not parsed["name"]:
            raise ValueError("Model file must have '# Model: Name' header")

        if model_id:
            # Update existing model
            existing_model = self.get_model(model_id)
            model_detail = self.convert_model_to_eclipse_format(
                parsed["components"], existing_model
            )
            # Use PUT if model has detail, POST if not
            if existing_model.get("modelDetail"):
                return self.update_model_detail(model_id, model_detail)
            else:
                return self.add_model_detail(model_id, model_detail)
        else:
            # Create new model
            new_model = self.add_model(name=parsed["name"], description=parsed["description"])
            # For new models, use POST (add_model_detail)
            model_detail = self.convert_model_to_eclipse_format(parsed["components"])
            return self.add_model_detail(new_model["id"], model_detail)

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

        if not parsed["name"]:
            raise ValueError("Model file must have '# Model: Name' header")

        existing = self.find_model_by_name(parsed["name"])

        if existing:
            result = self.sync_model_from_file(file_path, model_id=existing["id"])
            return result, "updated"
        else:
            result = self.sync_model_from_file(file_path)
            return result, "created"

    def export_model_to_file(self, model_id, file_path):
        """Export a model to a definition file.

        Converts Eclipse tolerance format back to absolute bounds.

        Args:
            model_id: ID of the model to export
            file_path: Path to write the definition file
        """
        # Validate file path
        file_path = Path(file_path).resolve()
        if not file_path.parent.exists():
            raise FileNotFoundError(f"Parent directory does not exist: {file_path.parent}")
        if file_path.exists() and not file_path.is_file():
            raise ValueError(f"Path exists but is not a file: {file_path}")

        model = self.get_model(model_id)

        lines = [
            f"# Model: {model.get('name', 'Unknown')}",
            f"# Description: {model.get('description', '')}",
            "",
            "# Component                      Lower%  Target%  Upper%",
        ]

        model_detail = model.get("modelDetail", {})
        for child in model_detail.get("children", []):
            name = child.get("name", f"ID:{child.get('id')}")
            target = child.get("targetPercent", 0) or 0
            lower_tol = child.get("lowerModelTolerancePercent", 0) or 0
            upper_tol = child.get("upperModelTolerancePercent", 0) or 0

            # Convert back to absolute bounds
            lower_bound = target - lower_tol
            upper_bound = target + upper_tol

            lines.append(f"{name:<32} {lower_bound:<7.2f} {target:<7.2f} {upper_bound:<7.2f}")

        with open(file_path, "w") as f:
            f.write("\n".join(lines) + "\n")

    # -------------------------------------------------------------------------
    # Security Preferences
    # -------------------------------------------------------------------------

    def get_security_preferences(self, portfolio_id, security_id):
        """Get rebalance preferences/rules for a security in a portfolio.

        Args:
            portfolio_id: Portfolio ID
            security_id: Security ID

        Returns:
            dict: Security preferences including buy/sell restrictions
        """
        if not isinstance(portfolio_id, int) or portfolio_id < 1:
            raise ValueError("portfolio_id must be a positive integer")
        if not isinstance(security_id, int) or security_id < 1:
            raise ValueError("security_id must be a positive integer")

        res = self.api_request(
            f"{self.base_url}/preference/Portfolio/securityPreference/{portfolio_id}/{security_id}/0/0"
        )
        return res.json()

    # -------------------------------------------------------------------------
    # Trade Management
    # -------------------------------------------------------------------------

    def get_trade_status(self, trade_id):
        """Get status and details for a specific trade.

        Args:
            trade_id: Trade ID

        Returns:
            dict: Trade details including status, execution info
        """
        if not isinstance(trade_id, int) or trade_id < 1:
            raise ValueError("trade_id must be a positive integer")

        res = self.api_request(f"{self.base_url}/tradeorder/trades/{trade_id}")
        return res.json()

    def get_trade_instance(self, instance_id):
        """Get details for a specific trade instance.

        Args:
            instance_id: Trade instance ID

        Returns:
            dict: Instance details including status, order counts, creation info
        """
        if not isinstance(instance_id, int) or instance_id < 1:
            raise ValueError("instance_id must be a positive integer")

        res = self.api_request(f"{self.base_url}/tradeorder/instances/{instance_id}")
        return res.json()

    def get_trade_instance_logs(self, instance_id):
        """Get trade logs for a specific trade instance.

        Args:
            instance_id: Trade instance ID

        Returns:
            list: Trade log entries with portfolio, application, and error info
        """
        if not isinstance(instance_id, int) or instance_id < 1:
            raise ValueError("instance_id must be a positive integer")

        res = self.api_request(f"{self.base_url}/tradeorder/instances/{instance_id}/tradeLogs")
        return res.json()

    def get_trade_log_detail(self, log_id):
        """Get detailed HTML trade log showing trading engine decision-making.

        Args:
            log_id: Trade log ID (from get_trade_instance_logs)

        Returns:
            str: Decoded HTML content showing detailed trade log
        """
        if not isinstance(log_id, int) or log_id < 1:
            raise ValueError("log_id must be a positive integer")

        # Note: This endpoint uses v2 API (different path structure)
        # base_url is https://api.orioneclipse.com/v1
        # v2 endpoint is https://api.orioneclipse.com/api/v2/Trading/TradeLogById/{id}
        base_url_v2 = self.base_url.replace("/v1", "/api/v2")
        res = self.api_request(f"{base_url_v2}/Trading/TradeLogById/{log_id}")
        response_data = res.json()

        if not response_data.get("isSuccess"):
            raise OrionAPIError("Failed to retrieve trade log detail")

        # Decode base64 content
        import base64

        html_content = base64.b64decode(response_data["content"]).decode("utf-8")
        return html_content

    def get_portfolio_trade_instances(self, portfolio_id, start_date, end_date):
        """Get all trade instances for a specific portfolio within a date range.

        Args:
            portfolio_id: Portfolio ID
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            list: Trade instances for the portfolio
        """
        if not isinstance(portfolio_id, int) or portfolio_id < 1:
            raise ValueError("portfolio_id must be a positive integer")
        if not isinstance(start_date, str) or not start_date.strip():
            raise ValueError("start_date must be a non-empty string")
        if not isinstance(end_date, str) or not end_date.strip():
            raise ValueError("end_date must be a non-empty string")

        res = self.api_request(
            f"{self.base_url}/tradeorder/instances/portfolio/{portfolio_id}/search"
            f"?startDate={start_date}&endDate={end_date}"
        )
        return res.json()

    def set_portfolio_tradeable(self, portfolio_id, tradeable=True, sync=True):
        """Set whether trading is allowed for a portfolio.

        Args:
            portfolio_id: Portfolio ID
            tradeable: True to allow trading, False to block (default True)
            sync: Wait for analytics to complete (default True)

        Returns:
            dict: Updated portfolio details
        """
        if not isinstance(portfolio_id, int) or portfolio_id < 1:
            raise ValueError("portfolio_id must be a positive integer")
        if not isinstance(tradeable, bool):
            raise ValueError("tradeable must be a boolean")

        # Get current portfolio to preserve other fields
        portfolio = self.get_portfolio(portfolio_id)
        general = portfolio.get("general", {})

        # Build payload preserving existing fields
        payload = {
            "name": general.get("portfolioName"),
            "modelId": general.get("modelId"),
            "isSleevePortfolio": general.get("sleevePortfolio", False),
            "doNotTrade": 0 if tradeable else 1,
            "tags": general.get("tags", ""),
            "teamIds": general.get("teamIds", []),
            "primaryTeamId": general.get("primaryTeamId"),
        }

        res = self.api_request(
            f"{self.base_url}/portfolio/portfolios/{portfolio_id}",
            requests.put,
            json=payload,
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result

    def set_account_tradeable(self, account_id, trade_restriction="tradeable", sync=True):
        """Set trading restrictions for an account.

        Args:
            account_id: Internal Eclipse account ID
            trade_restriction: One of:
                - "tradeable": Allow both advisor and custodian trading (default)
                - "block_advisor": Block advisor trading only
                - "block_custodian": Block custodian trading only
            sync: Wait for analytics to complete (default True)

        Returns:
            dict: Updated account details

        Note:
            These are mutually exclusive options - only one can be active at a time.
        """
        if not isinstance(account_id, int) or account_id < 1:
            raise ValueError("account_id must be a positive integer")

        valid_restrictions = ["tradeable", "block_advisor", "block_custodian"]
        if trade_restriction not in valid_restrictions:
            raise ValueError(f"trade_restriction must be one of {valid_restrictions}")

        # Get current account details
        account = self.get_account_details(account_id)
        general = account.get("generalSection", {})

        # Build payload
        payload = {
            "accountName": general.get("accountName"),
            "portfolioId": general.get("portfolioId"),
        }

        # Set flags based on restriction type
        if trade_restriction == "tradeable":
            payload["doNotTrade"] = 0
            payload["doNotTradeCustodian"] = 0
        elif trade_restriction == "block_advisor":
            payload["doNotTrade"] = 1
            payload["doNotTradeCustodian"] = 0
        elif trade_restriction == "block_custodian":
            payload["doNotTrade"] = 0
            payload["doNotTradeCustodian"] = 1

        res = self.api_request(
            f"{self.base_url}/account/accounts/{account_id}", requests.put, json=payload
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result
