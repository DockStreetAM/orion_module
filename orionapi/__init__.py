__version__ = "2.13.0"

import logging
import re
import threading
import time
import warnings
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

TERMINAL_GENERATION_STATUSES = {"Generated", "ErroredReport"}

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
    """Thread-safe rate limiter to prevent API abuse.

    Limits requests per second across all threads sharing this instance.
    Concurrent ``wait()`` callers serialize on an internal lock so that
    each one observes the previous caller's reservation.

    Args:
        calls_per_second: Maximum number of API calls per second (default 10)
    """

    def __init__(self, calls_per_second=10):
        self.calls_per_second = calls_per_second
        self.min_interval = 1.0 / calls_per_second if calls_per_second > 0 else 0
        self.last_call = 0.0
        self._lock = threading.Lock()

    def wait(self):
        """Wait if necessary to respect rate limit."""
        if self.calls_per_second <= 0:
            return  # Rate limiting disabled

        with self._lock:
            now = time.time()
            sleep_for = max(0.0, self.min_interval - (now - self.last_call))
            # Reserve the next allowed slot under the lock so concurrent
            # callers see the updated timestamp and block correctly.
            self.last_call = now + sleep_for

        if sleep_for > 0:
            time.sleep(sleep_for)


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
        # RLock so subclasses can hold the lock across an internal call
        # path that re-enters auth-header construction.
        self._token_lock = threading.RLock()

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

    def api_request(self, url, req_func=None, timeout=30, **kwargs):
        """Make an authenticated API request with error handling.

        Args:
            url: The API endpoint URL
            req_func: The requests function to use (get, post, put, delete).
                Defaults to ``requests.get``. Resolved at call time (not bound as a
                default argument) so that patching ``requests.get`` in tests takes
                effect for GET methods.
            timeout: Request timeout in seconds (default 30)
            **kwargs: Additional arguments passed to the request

        Returns:
            requests.Response object

        Raises:
            AuthenticationError: On 401/403 responses
            NotFoundError: On 404 responses
            OrionAPIError: On other 4xx/5xx responses
        """
        if req_func is None:
            req_func = requests.get

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
            # Try to get error message from response body. The body may be a JSON
            # object ({"message": ...}), a bare JSON string, a list, or non-JSON —
            # so guard the .get() to avoid masking the real HTTP error with an
            # AttributeError when the body isn't a dict.
            try:
                error_body = res.json()
                if isinstance(error_body, dict):
                    message = error_body.get("message", str(error_body))
                else:
                    message = str(error_body)
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

    Instances are safe to share across threads after ``login()``. Token
    reads/writes, the rate limiter, and the custom-field cache are
    serialized internally; callers may run methods concurrently from
    multiple threads on a single client.

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
        self._custom_field_cache = {}
        self._custom_field_lock = threading.Lock()

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
        with self._token_lock:
            res = requests.get(f"{self.base_url}/security/token", auth=(usr, pwd))
            if not res.ok:
                raise AuthenticationError(f"Login failed: {res.status_code} {res.reason}")
            try:
                self.token = res.json()["access_token"]
            except (KeyError, ValueError) as e:
                raise AuthenticationError(f"Invalid response from auth endpoint: {e}") from e

    def _get_auth_header(self):
        with self._token_lock:
            if self.token is None:
                raise AuthenticationError("Not logged in")
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

    def search_queries(self, search_term="", top=100, skip=0):
        """Search the firm's saved DataQueries by name substring.

        Args:
            search_term: Name substring filter. **The Orion endpoint
                requires a non-empty term**; passing ``""`` returns an
                empty list rather than "all queries". Pass a single
                character (e.g., ``"a"``) for a broad result set.
            top: Max results to return. Default 100.
            skip: Pagination offset (OData ``$skip``). Default 0.

        Returns:
            list: dicts, each with ``id`` and ``name``. For richer fields
            (description, owner, etc.), call :meth:`get_query_metadata`
            with the id.

        Raises:
            OrionAPIError: on non-200 responses.
        """
        if not isinstance(search_term, str):
            raise ValueError("search_term must be a string")
        if not isinstance(top, int) or top < 1:
            raise ValueError("top must be a positive integer")
        if not isinstance(skip, int) or skip < 0:
            raise ValueError("skip must be a non-negative integer")

        params = urlencode({"Search": search_term, "$top": top, "$skip": skip})
        res = self.api_request(f"{self.base_url}/Reporting/Custom/Simple/Search?{params}")
        data = res.json()
        # Tolerate OData envelope ({"value": [...]}) even though the
        # endpoint has returned a bare list in practice.
        return data if isinstance(data, list) else data.get("value", [])

    def find_query_by_name(self, name):
        """Return the ID of the saved query whose name exactly matches ``name``.

        Args:
            name: Exact query name to match (case-sensitive).

        Returns:
            int: The query ID, or None if no exact match is found.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("name must be a non-empty string")
        for row in self.search_queries(search_term=name, top=100):
            if row.get("name") == name:
                return row.get("id")
        return None

    def get_query_metadata(self, id):
        """Return the full saved-query record plus its params list.

        Args:
            id: The custom query ID.

        Returns:
            dict: The saved-query record (id, name, description, owner,
            isPrivate, ...) passed through from the endpoint, plus a
            ``params`` key mirroring ``prompts``.

        Raises:
            NotFoundError: if the query doesn't exist.
        """
        payload = self.get_query_payload(id)
        return {**payload, "params": payload.get("prompts", [])}

    def get_all_queries(self, search_term="", top=100):
        """Deprecated alias for :meth:`search_queries`.

        Kept for backwards compatibility with pre-1.9 callers.
        """
        return self.search_queries(search_term=search_term, top=top)

    # -------------------------------------------------------------------------
    # Custom Field Definitions
    # -------------------------------------------------------------------------

    def get_custom_field_definitions(self, entity):
        """Get custom field definitions for an entity type.

        Args:
            entity: 'client', 'registration', or 'account'

        Returns:
            list: Field definitions with code, description, type, options, etc.
        """
        res = self.api_request(f"{self.base_url}/Settings/UserDefinedFields/Definitions/{entity}")
        fields = res.json()

        mapping = {f["description"]: f["code"] for f in fields if f.get("description")}
        with self._custom_field_lock:
            self._custom_field_cache[entity] = mapping
        return fields

    def _translate_custom_fields(self, entity, data):
        """Translate custom field display names to codes.

        Args:
            entity: 'client', 'registration', or 'account'
            data: Dict that may contain display names as keys

        Returns:
            dict: Data with display names replaced by udf-prefixed codes
        """
        with self._custom_field_lock:
            name_to_code = self._custom_field_cache.get(entity)
        # Refresh outside the lock — the HTTP call shouldn't block other
        # entities' translations, and get_custom_field_definitions
        # re-acquires the lock to install the result.
        if name_to_code is None:
            self.get_custom_field_definitions(entity)
            with self._custom_field_lock:
                name_to_code = self._custom_field_cache.get(entity, {})

        translated = {}
        for key, value in data.items():
            if key in name_to_code:
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

    def download_report_pdf(self, batch_id, entity_key):
        """Download the rendered PDF for one entity in a generated report batch.

        Args:
            batch_id: Report batch ID (positive int).
            entity_key: Entity key within the batch — the `id` field from each
                entry returned by `get_report_batch_entities`. (The endpoint
                path names this parameter `{key}`.)

        Returns:
            bytes: Raw PDF bytes; will start with b"%PDF-".

        Raises:
            ValueError: if batch_id/entity_key are not positive ints.
            OrionAPIError: if the response body is not a PDF.
        """
        if not isinstance(batch_id, int) or batch_id < 1:
            raise ValueError("batch_id must be a positive integer")
        if not isinstance(entity_key, int) or entity_key < 1:
            raise ValueError("entity_key must be a positive integer")

        url = f"{self.base_url}/Reporting/Batch/{batch_id}/Entities/{entity_key}/Action/Download"
        res = self.api_request(url, headers={"Accept": "application/pdf"})

        content_type = (res.headers.get("Content-Type") or "").lower()
        body = res.content
        is_pdf = ("pdf" in content_type or "octet-stream" in content_type) and body.startswith(
            b"%PDF-"
        )
        if not is_pdf:
            raise OrionAPIError(
                f"Expected PDF response from {url}; "
                f"got Content-Type={content_type!r}, "
                f"first 16 bytes={body[:16]!r}"
            )
        return body

    def poll_until_generated(
        self,
        batch_id,
        timeout=600,
        poll_interval=5,
        progress_callback=None,
    ):
        """Block until every entity in the batch reaches a terminal generation state.

        Terminal states are "Generated" and "ErroredReport". Useful after
        `generate_statements()` to wait for PDFs to be ready before
        downloading them.

        Args:
            batch_id: Report batch ID (positive int).
            timeout: Wall-clock timeout in seconds (default 600).
            poll_interval: Seconds between polls (default 5).
            progress_callback: Optional callable invoked after each poll
                with (terminal_count, total_count) for logging.

        Returns:
            list[dict]: Final entities from `get_report_batch_entities`.

        Raises:
            ValueError: on invalid args.
            TimeoutError: if not all entities are terminal within `timeout`.
        """
        if not isinstance(batch_id, int) or batch_id < 1:
            raise ValueError("batch_id must be a positive integer")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("timeout must be a positive number")
        if not isinstance(poll_interval, (int, float)) or poll_interval <= 0:
            raise ValueError("poll_interval must be a positive number")

        deadline = time.monotonic() + timeout
        last_reported = None
        while True:
            entities = self.get_report_batch_entities(batch_id)
            total = len(entities)
            terminal_count = sum(
                1 for e in entities if e.get("generationStatus") in TERMINAL_GENERATION_STATUSES
            )
            if progress_callback is not None and (terminal_count, total) != last_reported:
                progress_callback(terminal_count, total)
                last_reported = (terminal_count, total)
            if total > 0 and terminal_count == total:
                return entities
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"Batch {batch_id} did not finish generating within "
                    f"{timeout}s ({terminal_count}/{total} terminal)"
                )
            time.sleep(poll_interval)

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


class EclipseBase(BaseAPI):
    """Shared base for the Eclipse Trading Platform API clients.

    Holds authentication, the v1/v2 base URLs, account-id resolution helpers
    (which some v2 operations rely on), and the generic ``eclipse_request``
    escape hatch. Concrete surfaces are provided by :class:`EclipseV1` and
    :class:`EclipseV2`; :class:`Eclipse` composes both. Not normally constructed
    directly.

    Instances are safe to share across threads after ``login()``. Token
    reads/writes and the rate limiter are serialized internally.

    Args:
        usr: Username for authentication
        pwd: Password for authentication
        orion_token: Orion session token (alternative to usr/pwd)
        eclipse_token: An already-minted Eclipse session token to use directly,
            skipping the login round-trip (used by :class:`Eclipse` to share one
            token across its v1/v2 sub-clients). Takes precedence over usr/pwd.
        rate_limit: Maximum API calls per second (default 10, set to 0 to disable)
        verify_ssl: Verify SSL certificates (default True)
        ca_bundle: Path to custom CA bundle file (optional)
    """

    def __init__(
        self,
        usr=None,
        pwd=None,
        orion_token=None,
        eclipse_token=None,
        rate_limit=10,
        verify_ssl=True,
        ca_bundle=None,
    ):
        super().__init__(rate_limit=rate_limit, verify_ssl=verify_ssl, ca_bundle=ca_bundle)
        self.eclipse_token = None
        self.base_url = "https://api.orioneclipse.com/v1"
        # The v2 surface lives at the host root (/api/v2/...), NOT under /v1.
        # Building it off base_url yields an unroutable /v1/api/v2/... path that
        # Eclipse answers with a misleading 403 "missing privileges" error.
        self.base_url_v2 = "https://api.orioneclipse.com/api/v2"

        if eclipse_token is not None:
            # Use a pre-minted token directly (no network round-trip).
            self.eclipse_token = eclipse_token
        elif usr is not None:
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

        with self._token_lock:
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
                    raise AuthenticationError(
                        f"Token exchange failed: {res.status_code} {res.reason}"
                    )
                try:
                    self.eclipse_token = res.json()["eclipse_access_token"]
                except (KeyError, ValueError) as e:
                    raise AuthenticationError(f"Invalid response from auth endpoint: {e}") from e

    def _get_auth_header(self):
        with self._token_lock:
            if self.eclipse_token is None:
                raise AuthenticationError("Not logged in")
            return {"Authorization": "Session " + self.eclipse_token}

    def eclipse_request(self, path, version="v1", method="get", **kwargs):
        """Call any Eclipse endpoint on either API surface and return parsed JSON.

        An explicit escape hatch for endpoints this wrapper does not yet provide a
        typed method for — especially the large ``/api/v2`` surface. This is NOT a
        hidden fallback: the caller chooses the version explicitly.

        Note:
            The v1 and v2 surfaces live at different roots on the same host
            (``/v1/...`` vs ``/api/v2/...``); ``version`` selects which.

        Args:
            path: Endpoint path, with or without a leading slash (e.g.
                ``"account/accounts/simple"`` or ``"/Account/Accounts"``).
            version: ``"v1"`` (default) or ``"v2"``.
            method: HTTP method: ``"get"`` (default), ``"post"``, ``"put"``,
                or ``"delete"``.
            **kwargs: Passed through to the request (e.g. ``json=``, ``params=``).

        Returns:
            The parsed JSON response.

        Raises:
            ValueError: If ``version`` or ``method`` is not recognized.
        """
        if version not in ("v1", "v2"):
            raise ValueError("version must be 'v1' or 'v2'")
        method_map = {
            "get": requests.get,
            "post": requests.post,
            "put": requests.put,
            "delete": requests.delete,
        }
        req_func = method_map.get(method.lower())
        if req_func is None:
            raise ValueError(f"method must be one of {sorted(method_map)}")

        base = self.base_url_v2 if version == "v2" else self.base_url
        path = path if path.startswith("/") else f"/{path}"
        res = self.api_request(f"{base}{path}", req_func, **kwargs)
        return res.json()

    def get_all_accounts(self):
        """Get a simplified list of all accounts.

        Returns:
            list: List of account dicts with basic info (id, name, accountNumber, etc.)
        """
        res = self.api_request(f"{self.base_url}/account/accounts/simple")
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


class EclipseV1(EclipseBase):
    """Eclipse client targeting the v1 API surface (``/v1/...``) only.

    Every method here calls a ``/v1`` endpoint, so callers always know which
    surface they are hitting. For the newer ``/api/v2`` surface use
    :class:`EclipseV2`, or :class:`Eclipse` for a best-of-both client.

    Args:
        usr: Username for authentication
        pwd: Password for authentication
        orion_token: Orion session token (alternative to usr/pwd)
        rate_limit: Maximum API calls per second (default 10, set to 0 to disable)
        verify_ssl: Verify SSL certificates (default True)
        ca_bundle: Path to custom CA bundle file (optional)

    Example:
        >>> api = EclipseV1(usr="user@example.com", pwd="password")
        >>> api.check_username()
        'user@example.com'
    """

    def check_username(self):
        """Get the authenticated user's login ID.

        Returns:
            str: The user's login ID
        """
        res = self.api_request(f"{self.base_url}/admin/authorization/user")
        return res.json()["userLoginId"]

    def get_set_asides(self, account_id, active_only=False):
        """Get set-aside cash settings for a specific account (v1 surface).

        Returns the raw v1 records from ``GET /account/accounts/{id}/asidecash``.
        For firm-wide set-asides or normalized fields (including the authoritative
        Eclipse set-aside id), use :meth:`EclipseV2.get_set_asides` or the
        :class:`Eclipse` unifier.

        Args:
            account_id: Account ID, number, or name (resolved via search).
            active_only: When True, keep only records where ``isActive`` is truthy.
                Defaults to False (includes expired/inactive).

        Returns:
            list: Raw v1 set-aside records for the account.
        """
        internal_id = self.get_internal_account_id(account_id)
        res = self.api_request(f"{self.base_url}/account/accounts/{internal_id}/asidecash")
        records = res.json()
        if active_only:
            records = [r for r in records if r.get("isActive")]
        return records

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

    def get_account_simple(self, account_id):
        """Get a lightweight account record by internal ID.

        Hits ``/account/accounts/simple/{id}`` — a lighter payload than the full
        record returned by :meth:`get_account_details`.

        Args:
            account_id: Internal Eclipse account ID

        Returns:
            dict: Lightweight account record
        """
        res = self.api_request(f"{self.base_url}/account/accounts/simple/{account_id}")
        return res.json()

    def get_account_holdings_detail(self, account_id):
        """Get holdings for an account via the account-path holdings endpoint.

        Hits ``/account/accounts/{id}/holdings`` — a different path and shape than
        :meth:`get_account_holdings` (which uses ``/holding/holdings/simple``).

        Args:
            account_id: Internal Eclipse account ID

        Returns:
            list: Holding dicts as returned by the account-path endpoint
        """
        res = self.api_request(f"{self.base_url}/account/accounts/{account_id}/holdings")
        return res.json()

    def get_out_of_tolerance_accounts(self, model_id, asset_id, asset_type="class"):
        """Get accounts out of tolerance for a model asset.

        Args:
            model_id: Model ID (note: the API uses this value in the account path
                segment — kept as-is per the documented endpoint quirk)
            asset_id: Asset ID
            asset_type: Asset type (default "class")

        Returns:
            list: Out-of-tolerance account dicts
        """
        res = self.api_request(
            f"{self.base_url}/account/accounts/{model_id}/outOfTolerance/{asset_id}",
            params={"assetType": asset_type},
        )
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

    def get_portfolio_accounts(self, portfolio_id, simple=False):
        """Get list of accounts for a portfolio.

        Args:
            portfolio_id: Portfolio ID
            simple: When True, hit the lightweight ``/accounts/simple`` path
                (default False returns the full account records)

        Returns list of accounts with cash targets, sleeve settings, and values.
        """
        path = f"/portfolio/portfolios/{portfolio_id}/accounts"
        if simple:
            path += "/simple"
        res = self.api_request(f"{self.base_url}{path}")
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

    def get_all_portfolios(self, include_value=True, search=None, top=None):
        """Get list of all portfolios.

        Args:
            include_value: Include holding values (default True)
            search: Optional search string
            top: Optional max number of results (maps to ``$top``)

        Returns list of portfolios with basic info and optionally values.
        """
        params = {"includevalue": str(include_value).lower()}
        if search:
            params["search"] = search
        if top is not None:
            params["$top"] = top
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

    def get_portfolio_holdings_detail(self, portfolio_id):
        """Get holdings for a portfolio via the portfolio-path holdings endpoint.

        Hits ``/portfolio/portfolios/{id}/holdings`` — a different path and shape
        than :meth:`get_portfolio_holdings` (which uses ``/holding/holdings/simple``).

        Args:
            portfolio_id: Portfolio ID

        Returns:
            list: Holding dicts as returned by the portfolio-path endpoint
        """
        res = self.api_request(f"{self.base_url}/portfolio/portfolios/{portfolio_id}/holdings")
        return res.json()

    def get_taxlots(self, holding_id):
        """Get tax lots for a holding.

        Args:
            holding_id: Holding ID

        Returns:
            list: Tax-lot dicts (acquisition date, cost basis, quantity, etc.)
        """
        res = self.api_request(f"{self.base_url}/holding/holdings/{holding_id}/taxlots")
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

    def get_trades(self, portfolio_id=None, top=None, is_pending=None):
        """Get trade orders with optional portfolio / paging / pending filters.

        Hits the same ``/tradeorder/trades`` endpoint as :meth:`get_orders` /
        :meth:`get_orders_pending`, but lets the caller filter by portfolio and cap
        the result count.

        Args:
            portfolio_id: Optional portfolio ID filter (maps to ``portfolioId``)
            top: Optional max number of results (maps to ``$top``)
            is_pending: Optional bool; when set, filter by pending status
                (maps to ``isPending``)

        Returns:
            list: Trade order dicts
        """
        params = {}
        if portfolio_id is not None:
            params["portfolioId"] = portfolio_id
        if top is not None:
            params["$top"] = top
        if is_pending is not None:
            params["isPending"] = str(is_pending).lower()
        res = self.api_request(f"{self.base_url}/tradeorder/trades", params=params)
        return res.json()

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
        selected_method_id=None,
        spend_full_amount=None,
        filter_type=None,
    ):
        """Generate Spend Cash trade for portfolios.

        Args:
            portfolio_ids: List of portfolio IDs to process
            portfolio_trade_group_ids: List of portfolio trade group IDs (optional)
            is_view_only: If True, preview trades without executing (default True)
            reason: Reason for the trade
            is_excel_import: Whether this is from an Excel import (default False)
            sync: Wait for analytics to complete (default True)

        Args (additional):
            selected_method_id: Optional spend-cash calculation method id
                (see ``get_spend_cash_methods``); added to the body only when provided
            spend_full_amount: Optional bool; added to the body only when provided
            filter_type: Optional filter type; added to the body only when provided

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
        if selected_method_id is not None:
            payload["selectedMethodId"] = selected_method_id
        if spend_full_amount is not None:
            payload["spendFullAmount"] = spend_full_amount
        if filter_type is not None:
            payload["filterType"] = filter_type

        res = self.api_request(
            f"{self.base_url}/tradetool/spendcash/action/generatetrade", requests.post, json=payload
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result

    def get_raise_cash_methods(self):
        """Get the available raise-cash calculation methods.

        Returns:
            list: Calculation-method dicts (id, name, etc.)
        """
        res = self.api_request(f"{self.base_url}/tradetool/raisecash/calculation_methods")
        return res.json()

    def get_spend_cash_methods(self):
        """Get the available spend-cash calculation methods.

        Returns:
            list: Calculation-method dicts (id, name, etc.)
        """
        res = self.api_request(f"{self.base_url}/tradetool/spendcash/calculation_methods")
        return res.json()

    @staticmethod
    def _tlh_id_body(portfolio_ids, account_ids):
        """Build a tax-loss-harvesting request body, omitting empty id lists."""
        body = {}
        if portfolio_ids is not None:
            body["portfolioIds"] = portfolio_ids
        if account_ids is not None:
            body["accountIds"] = account_ids
        return body

    def get_tlh_securities(self, portfolio_ids=None, account_ids=None):
        """Get tax-loss-harvesting candidate securities (preview only).

        Args:
            portfolio_ids: Optional list of portfolio IDs
            account_ids: Optional list of account IDs

        Returns:
            list: Candidate security dicts
        """
        res = self.api_request(
            f"{self.base_url}/tradetool/taxLossHarvesting/securities",
            requests.post,
            json=self._tlh_id_body(portfolio_ids, account_ids),
        )
        return res.json()

    def check_tlh_gain_loss(self, portfolio_ids=None, account_ids=None):
        """Check projected gain/loss for tax-loss harvesting (preview only).

        Args:
            portfolio_ids: Optional list of portfolio IDs
            account_ids: Optional list of account IDs

        Returns:
            dict: Projected gain/loss summary
        """
        res = self.api_request(
            f"{self.base_url}/tradetool/taxLossHarvesting/action/checkGainLoss",
            requests.post,
            json=self._tlh_id_body(portfolio_ids, account_ids),
        )
        return res.json()

    def tlh_trade(self, portfolio_ids=None, account_ids=None, is_view_only=True, sync=False):
        """Generate a tax-loss-harvesting trade (preview/staging by default).

        Args:
            portfolio_ids: Optional list of portfolio IDs
            account_ids: Optional list of account IDs
            is_view_only: If True (default), preview trades without executing
            sync: Wait for analytics to complete (default False)

        Returns:
            dict: Generated trade preview (instanceId, trades, etc.)
        """
        payload = self._tlh_id_body(portfolio_ids, account_ids)
        payload["isViewOnly"] = is_view_only
        res = self.api_request(
            f"{self.base_url}/tradetool/taxLossHarvesting/action/generateTrade",
            requests.post,
            json=payload,
        )
        result = res.json()
        self._maybe_wait_for_analytics(sync)
        return result

    def rebalance_trade(
        self,
        portfolio_ids=None,
        account_ids=None,
        filter_type=None,
        is_view_only=True,
        max_gain_amount=0,
        minimum_trade_amount=0,
        minimum_trade_amount_type="$",
        allow_wash_sale=False,
        rounding=0,
        sync=False,
    ):
        """Generate a rebalance trade (preview/staging by default).

        Args:
            portfolio_ids: Optional list of portfolio IDs
            account_ids: Optional list of account IDs
            filter_type: Optional filter type (maps to ``filterType``)
            is_view_only: If True (default), preview trades without executing
            max_gain_amount: Max gain amount (default 0)
            minimum_trade_amount: Minimum trade amount (default 0)
            minimum_trade_amount_type: Minimum trade amount type, "$" or "%" (default "$")
            allow_wash_sale: Whether to allow wash sales (default False)
            rounding: Rounding setting (default 0)
            sync: Wait for analytics to complete (default False)

        Returns:
            dict: Generated trade preview (instanceId, trades, etc.)
        """
        payload = {
            "filterType": filter_type,
            "isViewOnly": is_view_only,
            "isExcelImport": False,
            "maxGainAmount": max_gain_amount,
            "minimumTradeAmount": {
                "amount": minimum_trade_amount,
                "type": minimum_trade_amount_type,
            },
            "allowWashSale": allow_wash_sale,
            "allowShortTermGain": None,
            "priorityRanking": [],
            "rounding": rounding,
        }
        if portfolio_ids is not None:
            payload["portfolioIds"] = portfolio_ids
        if account_ids is not None:
            payload["accountIds"] = account_ids
        res = self.api_request(
            f"{self.base_url}/tradetool/rebalancer/action/generatetrade",
            requests.post,
            json=payload,
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

    def get_trade_instances(self, start_date, end_date, normalize=True):
        """Get trade instances (batches of trades) within a date range.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            normalize: When True (default), map the numeric tradeInstanceType /
                tradeInstanceSubType IDs to friendly names. When False, return the
                raw response unchanged (matching the API output).

        Returns:
            list: List of trade instance dicts with id, orderCount, executeStatus,
                  tradeInstanceType, tradeInstanceSubType, etc.
        """
        instances = self.api_request(
            f"{self.base_url}/tradeorder/instances?startDate={start_date}&endDate={end_date}"
        ).json()

        if not normalize:
            return instances

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

    def get_all_models(self, name=None, top=None):
        """Get all investment models.

        Args:
            name: Optional name filter
            top: Optional max number of results (maps to ``$top``)

        Returns:
            list: List of model dicts with id, name, status, etc.
        """
        params = {}
        if name is not None:
            params["name"] = name
        if top is not None:
            params["$top"] = top
        res = self.api_request(f"{self.base_url}/modeling/models", params=params)
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

    def get_model_allocations(self, id, aggregate=True):
        """Get allocations for a model.

        Args:
            id: Model ID
            aggregate: When True (default), aggregate allocations across the model
                tree (``aggregateAllocations=true``); when False, return per-node
                allocations.

        Returns:
            list: List of allocation dicts with target percentages
        """
        res = self.api_request(
            f"{self.base_url}/modeling/models/{id}/allocations",
            params={"aggregateAllocations": str(aggregate).lower()},
        )
        return res.json()

    def get_model_nodes(self, model_id):
        """Get the node tree for a model.

        Args:
            model_id: Model ID

        Returns:
            dict: Node tree with ``levels``, ``modelId`` and ``preSelectedNodeId``
        """
        res = self.api_request(f"{self.base_url}/modeling/models/{model_id}/Model/nodes")
        return res.json()

    def get_model_portfolios(self, model_id):
        """Get portfolios assigned to a model.

        Args:
            model_id: Model ID

        Returns:
            list: Portfolio dicts assigned to the model
        """
        res = self.api_request(f"{self.base_url}/modeling/models/{model_id}/portfolios")
        return res.json()

    def get_model_pending(self, model_id):
        """Get pending changes for a model.

        Args:
            model_id: Model ID

        Returns:
            dict: Pending-change details
        """
        res = self.api_request(f"{self.base_url}/modeling/models/{model_id}/pending")
        return res.json()

    def get_model_analysis(self, model_id, asset_type="securityset"):
        """Get model analysis for a model.

        Args:
            model_id: Model ID
            asset_type: Asset type to analyze (default "securityset")

        Returns:
            dict: Model analysis results
        """
        res = self.api_request(
            f"{self.base_url}/modeling/models/{model_id}/modelAnalysis",
            params={
                "assetType": asset_type,
                "isIncludeTradeBlockAccount": 0,
                "isExcludeAsset": 0,
            },
        )
        return res.json()

    def get_model_status(self):
        """Get the list of model statuses.

        Returns:
            list: Model-status dicts
        """
        res = self.api_request(f"{self.base_url}/modeling/models/modelStatus")
        return res.json()

    def get_model_types(self):
        """Get the list of model types.

        Returns:
            list: Model-type dicts
        """
        res = self.api_request(f"{self.base_url}/modeling/models/modelTypes")
        return res.json()

    def get_submodels(self, model_type=None, search=None):
        """Get submodels, optionally filtered by type and name.

        Args:
            model_type: Optional model-type filter (maps to ``modelType``)
            search: Optional name filter (maps to ``name``)

        Returns:
            list: Submodel dicts
        """
        params = {}
        if model_type is not None:
            params["modelType"] = model_type
        if search is not None:
            params["name"] = search
        res = self.api_request(f"{self.base_url}/modeling/models/submodels", params=params)
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

    def get_security_set_summary(self, id):
        """Get a security set by ID via the summary endpoint.

        Hits ``/security/securityset/{id}`` — a different path than
        :meth:`get_security_set` (which uses ``/security/securityset/details/{id}``).

        Args:
            id: Security set ID

        Returns:
            dict: Security set summary
        """
        res = self.api_request(f"{self.base_url}/security/securityset/{id}")
        return res.json()

    def get_security_set_details(self):
        """Get the full security-set detail list.

        Hits ``/security/securityset/detail`` (documented as a large list across all
        sets).

        .. note::
            As of 2026-05 this endpoint returns ``400 'id is not numeric string'`` on
            live Eclipse — the server routes the ``detail`` segment into the
            ``/security/securityset/{id}`` param route instead. Kept faithful to the
            documented endpoint (and the Eclipse MCP, which calls the same path), but
            the upstream route appears broken. Use :meth:`get_all_security_sets` plus
            :meth:`get_security_set` per id as a working alternative.

        Returns:
            list: Security-set detail dicts
        """
        res = self.api_request(f"{self.base_url}/security/securityset/detail")
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

    # =========================================================================
    # v1 read coverage (account / holding / portfolio). Reference/lookup reads
    # plus account & portfolio sub-resource reads. No trade execution/approval.
    # =========================================================================

    # --- Account reference + sub-resource reads ---

    def get_account_filters(self):
        """Get the available account filters.

        Returns:
            list: Account-filter dicts
        """
        return self.api_request(f"{self.base_url}/account/accounts/accountfilters").json()

    def get_accounts_without_portfolio(self):
        """Get accounts not assigned to a portfolio.

        Returns:
            list: Account dicts
        """
        return self.api_request(f"{self.base_url}/account/accounts/noPortfolio").json()

    def get_account_model_types(self, account_id):
        """Get the model types for an account.

        Args:
            account_id: Internal account ID

        Returns:
            list: Model-type dicts
        """
        return self.api_request(
            f"{self.base_url}/account/accounts/{account_id}/model/modelTypes"
        ).json()

    def get_account_submodels(self, account_id, model_type_id=None):
        """Get the submodels for an account.

        Args:
            account_id: Internal account ID
            model_type_id: Optional model-type filter (maps to ``modelTypeId``)

        Returns:
            list: Submodel dicts
        """
        params = {}
        if model_type_id is not None:
            params["modelTypeId"] = model_type_id
        return self.api_request(
            f"{self.base_url}/account/accounts/{account_id}/model/submodels", params=params
        ).json()

    def get_aside_cash_percent_calc_types(self):
        """Get set-aside-cash percent calculation types.

        Returns:
            list: Calculation-type dicts
        """
        return self.api_request(
            f"{self.base_url}/account/accounts/accountSetAsidePercentCalculationType"
        ).json()

    def get_aside_cash_amount_types(self):
        """Get set-aside-cash amount types.

        Returns:
            list: Amount-type dicts
        """
        return self.api_request(f"{self.base_url}/account/accounts/asideCashAmountType").json()

    def get_aside_cash_expiration_types(self):
        """Get set-aside-cash expiration types.

        Returns:
            list: Expiration-type dicts
        """
        return self.api_request(f"{self.base_url}/account/accounts/asideCashExpirationType").json()

    def get_aside_cash_transaction_types(self):
        """Get set-aside-cash transaction types.

        Returns:
            list: Transaction-type dicts
        """
        return self.api_request(f"{self.base_url}/account/accounts/asideCashTransactionType").json()

    def get_accounts_simple_by_type(self, account_type):
        """Get a simple account list filtered by account type.

        Args:
            account_type: Account type

        Returns:
            list: Account dicts
        """
        return self.api_request(
            f"{self.base_url}/account/accounts/simpleList/type/{account_type}"
        ).json()

    def get_account_custodial_information(self, account_id):
        """Get custodial information for an account.

        Args:
            account_id: Internal account ID

        Returns:
            dict: Custodial information
        """
        return self.api_request(
            f"{self.base_url}/account/accounts/{account_id}/custodialInformation"
        ).json()

    def get_account_sma(self, account_id):
        """Get SMA info for an account.

        Args:
            account_id: Internal account ID

        Returns:
            dict: SMA info
        """
        return self.api_request(f"{self.base_url}/account/accounts/{account_id}/sma").json()

    def get_restricted_plans(self):
        """Get the restricted plans.

        Returns:
            list: Restricted-plan dicts
        """
        return self.api_request(f"{self.base_url}/account/accounts/restrictedPlans").json()

    def get_portfolio_account_count(self):
        """Get the portfolio/account count.

        .. note::
            As of 2026-05 this documented endpoint returns
            ``400 'id is not numeric string'`` on live Eclipse — the server routes
            the ``portfolioAccountCount`` segment into ``/account/accounts/{id}``.
            Kept faithful to the documented path, but the upstream route appears
            broken (same class of issue as :meth:`get_security_set_details`).

        Returns:
            dict | int: Count
        """
        return self.api_request(f"{self.base_url}/account/accounts/portfolioAccountCount").json()

    def get_account_portfolio_id(self, account_id):
        """Get the portfolio ID for an account.

        Args:
            account_id: Internal account ID

        Returns:
            dict | int: Portfolio ID
        """
        return self.api_request(f"{self.base_url}/account/accounts/{account_id}/portfolioId").json()

    # --- Holding reads ---

    def get_holding(self, holding_id):
        """Get a holding by ID.

        Args:
            holding_id: Holding ID

        Returns:
            dict: Holding
        """
        return self.api_request(f"{self.base_url}/holding/holdings/{holding_id}").json()

    def get_holding_filters(self):
        """Get the available holding filters.

        Returns:
            list: Holding-filter dicts
        """
        return self.api_request(f"{self.base_url}/holding/holdings/holdingfilters").json()

    def get_holding_transactions(self, holding_id):
        """Get transactions for a holding.

        Args:
            holding_id: Holding ID

        Returns:
            list: Transaction dicts
        """
        return self.api_request(
            f"{self.base_url}/holding/holdings/{holding_id}/transactions"
        ).json()

    def search_holdings(self, search):
        """Search holdings by id or name.

        Args:
            search: Search string (id or name)

        Returns:
            list: Holding dicts
        """
        return self.api_request(
            f"{self.base_url}/holding/holdings", params={"search": search}
        ).json()

    # --- Portfolio reference + sub-resource reads ---

    def get_portfolio_filters(self):
        """Get the available portfolio filters.

        Returns:
            list: Portfolio-filter dicts
        """
        return self.api_request(f"{self.base_url}/portfolio/portfolios/portfolioFilters").json()

    def get_portfolio_accounts_detailed(self, portfolio_id):
        """Get detailed accounts for a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            list: Detailed account dicts
        """
        return self.api_request(
            f"{self.base_url}/portfolio/portfolios/{portfolio_id}/accounts/detailed"
        ).json()

    def get_portfolio_accounts_summary(self, portfolio_id):
        """Get an account summary for a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            list | dict: Account summary
        """
        return self.api_request(
            f"{self.base_url}/portfolio/portfolios/{portfolio_id}/accounts/summary"
        ).json()

    def get_portfolio_simple(self, portfolio_id):
        """Get a lightweight portfolio record by ID.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            dict: Lightweight portfolio
        """
        return self.api_request(
            f"{self.base_url}/portfolio/portfolios/simple/{portfolio_id}"
        ).json()

    def get_portfolio_set_asides(self, portfolio_id):
        """Get set-aside cash for a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            list: Set-aside dicts
        """
        return self.api_request(
            f"{self.base_url}/portfolio/portfolios/{portfolio_id}/asidecash"
        ).json()

    def get_portfolio_pending_models(self, portfolio_id):
        """Get pending models for a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            list | dict: Pending models
        """
        return self.api_request(
            f"{self.base_url}/portfolio/portfolios/{portfolio_id}/pending/models"
        ).json()

    def get_portfolio_contribution_amount(self, portfolio_id):
        """Get the contribution amount for a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            dict: Contribution amount
        """
        return self.api_request(
            f"{self.base_url}/portfolio/portfolios/{portfolio_id}/contributionamount"
        ).json()

    def get_sleeves(self):
        """Get all sleeves (v1).

        Returns:
            list: Sleeve dicts
        """
        return self.api_request(f"{self.base_url}/portfolio/sleeves").json()


class EclipseV2(EclipseBase):
    """Eclipse client targeting the v2 API surface (``/api/v2/...``) only.

    The v2 surface is newer and broader but does not cover everything v1 does
    (e.g. holdings and authorization/user have no v2 equivalent). Methods here
    call ``/api/v2`` endpoints explicitly. For the full v1 surface use
    :class:`EclipseV1`, or :class:`Eclipse` for a best-of-both client. The
    generic :meth:`eclipse_request` (inherited) reaches any un-wrapped v2 path.

    Account-id resolution helpers are inherited from :class:`EclipseBase`
    because some v2 calls (e.g. the set-aside batch) need internal account ids,
    which are sourced from the v1 account search.
    """

    def _normalize_set_aside(self, record):
        """Augment a raw v2 set-aside record with normalized snake_case fields.

        The original Eclipse keys are preserved; the normalized keys provide a
        stable contract (e.g. ``set_aside_id``, ``amount``) regardless of the
        upstream field spellings.

        Args:
            record: A raw AccountSetAsideCashResponseDto dict

        Returns:
            dict: The record with normalized keys added
        """
        expiration_type_id = record.get("expirationTypeId")
        end_date = record.get("expirationValue") if expiration_type_id == EXPIRE_TYPE_DATE else None
        return {
            **record,
            "set_aside_id": record.get("id"),
            "account_id": record.get("accountId"),
            "account_number": record.get("accountNumber"),
            "amount": record.get("setAsideCashAmount"),
            "active": record.get("isActive"),
            "description": record.get("description"),
            "start_date": record.get("startDate"),
            "end_date": end_date,
        }

    def get_set_asides(self, account_id=None, active_only=False):
        """Get set-aside cash reservations, including the Eclipse set-aside id.

        Uses the v2 batch endpoint, which accepts a list of internal account IDs
        and returns one record per set-aside (each carrying its own ``id``,
        ``accountId``, and ``accountNumber``). Records are augmented with
        normalized snake_case fields (``set_aside_id``, ``amount``, ``active``,
        ``account_number``, ``description``, ``start_date``, ``end_date``); the
        original Eclipse keys are preserved.

        Args:
            account_id: Account ID, number, or name to restrict to a single
                account. When None (default), returns set-asides firm-wide by
                issuing one batch POST over all accounts.
            active_only: When True, return only currently-active set-asides.
                Defaults to False (includes expired/inactive).

        Returns:
            list: Augmented set-aside records
        """
        if account_id is not None:
            account_ids = [self.get_internal_account_id(account_id)]
        else:
            account_ids = [a["id"] for a in self.get_all_accounts()]

        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/SetAsideCashSettings",
            requests.post,
            json=account_ids,
        )
        records = [self._normalize_set_aside(r) for r in res.json()]
        if active_only:
            records = [r for r in records if r.get("active")]
        return records

    # --- Tactical (v2-only): per-portfolio tactical analysis reads ---------------

    def get_tactical_portfolio_summary(self, portfolio_id):
        """Get the tactical portfolio summary for a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            dict: Tactical portfolio summary
        """
        res = self.api_request(f"{self.base_url_v2}/Tactical/PortfolioSummary/{portfolio_id}")
        return res.json()

    def get_tactical_account_cash_detail(self, portfolio_id):
        """Get account and cash detail for a portfolio (tactical view).

        Args:
            portfolio_id: Portfolio ID

        Returns:
            list: Per-account cash detail dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Tactical/AccountAndCashDetail/{portfolio_id}")
        return res.json()

    def get_tactical_model_analyzer(self, portfolio_id, account_id=None, aggregate_alternates=None):
        """Get model-analyzer data for a portfolio (tactical view).

        Args:
            portfolio_id: Portfolio ID
            account_id: Optional account ID filter (maps to ``accountId``)
            aggregate_alternates: Optional bool (maps to ``aggregateAlternates``)

        Returns:
            dict: Model-analyzer data
        """
        params = {}
        if account_id is not None:
            params["accountId"] = account_id
        if aggregate_alternates is not None:
            params["aggregateAlternates"] = str(aggregate_alternates).lower()
        res = self.api_request(
            f"{self.base_url_v2}/Tactical/ModelAnalyzer/{portfolio_id}", params=params
        )
        return res.json()

    def get_tactical_tax_lots(self, portfolio_id, account_id=None):
        """Get tax-lot data for a portfolio (tactical view).

        Args:
            portfolio_id: Portfolio ID
            account_id: Optional account ID filter (maps to ``accountId``)

        Returns:
            list: Tax-lot dicts
        """
        params = {}
        if account_id is not None:
            params["accountId"] = account_id
        res = self.api_request(f"{self.base_url_v2}/Tactical/TaxLots/{portfolio_id}", params=params)
        return res.json()

    def get_tactical_trades(self, portfolio_id, account_id=None):
        """Get trades for a portfolio (tactical view).

        Args:
            portfolio_id: Portfolio ID
            account_id: Optional account ID filter (maps to ``accountId``)

        Returns:
            list: Trade dicts
        """
        params = {}
        if account_id is not None:
            params["accountId"] = account_id
        res = self.api_request(f"{self.base_url_v2}/Tactical/Trades/{portfolio_id}", params=params)
        return res.json()

    def get_tactical_restricted_securities(self, portfolio_id):
        """Get restricted securities for a portfolio (tactical view).

        Args:
            portfolio_id: Portfolio ID

        Returns:
            list: Restricted-security dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Tactical/RestrictedSecurities/{portfolio_id}")
        return res.json()

    # --- ESG (v2-only) -----------------------------------------------------------

    def get_esg_themes(self):
        """Get the firm-preference ESG themes.

        Returns:
            list: ESG theme dicts
        """
        res = self.api_request(f"{self.base_url_v2}/ESG/Themes")
        return res.json()

    def get_esg_assignments(self):
        """Get the firm-preference ESG assignments.

        Returns:
            list: ESG assignment dicts
        """
        res = self.api_request(f"{self.base_url_v2}/ESG/Assignments")
        return res.json()

    def get_esg_restrictions_for_portfolio(self, portfolio_id):
        """Get ESG restrictions associated with a portfolio.

        Args:
            portfolio_id: Portfolio ID (maps to ``portfolioId``)

        Returns:
            list: ESG restriction dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/ESG/ESGRestrictionsForPortfolio",
            params={"portfolioId": portfolio_id},
        )
        return res.json()

    # --- Trading blocks (v2-only): read-only block views -------------------------

    def get_trade_blocks(self, has_quodd=None, registration_status=None, get_adv=None):
        """Get trade blocks.

        Args:
            has_quodd: Optional bool filter (maps to ``hasQuodd``)
            registration_status: Optional registration-status filter
                (maps to ``registrationStatus``)
            get_adv: Optional bool (maps to ``getAdv``)

        Returns:
            list: Trade-block dicts
        """
        params = {}
        if has_quodd is not None:
            params["hasQuodd"] = str(has_quodd).lower()
        if registration_status is not None:
            params["registrationStatus"] = registration_status
        if get_adv is not None:
            params["getAdv"] = str(get_adv).lower()
        res = self.api_request(f"{self.base_url_v2}/Trading/Blocks", params=params)
        return res.json()

    def get_trade_blocks_grid(
        self, block_ids, has_quodd=None, registration_status=None, get_adv=None
    ):
        """Get trade-block data in the blocks-grid format for given block IDs.

        Args:
            block_ids: List of trade-block IDs (maps to ``blockIds``)
            has_quodd: Optional bool filter (maps to ``hasQuodd``)
            registration_status: Optional registration-status filter
            get_adv: Optional bool (maps to ``getAdv``)

        Returns:
            list: Trade-block grid dicts
        """
        params = {"blockIds": block_ids}
        if has_quodd is not None:
            params["hasQuodd"] = str(has_quodd).lower()
        if registration_status is not None:
            params["registrationStatus"] = registration_status
        if get_adv is not None:
            params["getAdv"] = str(get_adv).lower()
        res = self.api_request(f"{self.base_url_v2}/Trading/Blocks/BlocksGrid", params=params)
        return res.json()

    def get_trade_block_fix_messages(self, trade_block_id):
        """Get all FIX messages for a trade block.

        Args:
            trade_block_id: Trade-block ID

        Returns:
            list: FIX message dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Trading/Blocks/{trade_block_id}/FixMessages")
        return res.json()

    # --- Dashboard (v2-only) -----------------------------------------------------

    def get_dashboards(self, user_id=None, team_id=None):
        """Get user/team/firm-level dashboard layouts.

        Args:
            user_id: Optional user ID (maps to ``userId``)
            team_id: Optional team ID (maps to ``teamId``)

        Returns:
            list: Dashboard layout dicts
        """
        params = {}
        if user_id is not None:
            params["userId"] = user_id
        if team_id is not None:
            params["teamId"] = team_id
        res = self.api_request(f"{self.base_url_v2}/Dashboard", params=params)
        return res.json()

    def get_dashboard(self, dashboard_id):
        """Get a single dashboard layout by ID.

        Args:
            dashboard_id: Dashboard ID

        Returns:
            dict: Dashboard layout
        """
        res = self.api_request(f"{self.base_url_v2}/Dashboard/{dashboard_id}")
        return res.json()

    def get_account_dashboard(self):
        """Get the data populating the account dashboard.

        Returns:
            dict: Account-dashboard data
        """
        res = self.api_request(f"{self.base_url_v2}/Dashboard/AccountDashboard")
        return res.json()

    def get_dashboard_fields(self):
        """Get the available fields and categories usable on a dashboard.

        Returns:
            list: Field/category dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Dashboard/Fields")
        return res.json()

    def get_analytics_run_history(self):
        """Get analytics run history (for the dashboard).

        Returns:
            list: Analytics run-history dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Dashboard/AnalyticsRunHistory")
        return res.json()

    # --- Astro (v2-only): proposal/optimization templates & status ---------------

    def get_astro_templates(self, al_client_id=None):
        """Get the list of Astro templates.

        Args:
            al_client_id: Optional AL client ID (maps to ``alClientId``)

        Returns:
            list: Astro template dicts
        """
        params = {}
        if al_client_id is not None:
            params["alClientId"] = al_client_id
        res = self.api_request(f"{self.base_url_v2}/Astro/Templates", params=params)
        return res.json()

    def get_astro_all_templates(self):
        """Get Astro templates (Eclipse-UI route).

        Returns:
            dict: Response with an ``astroTemplates`` list plus ``success``/``message``
        """
        res = self.api_request(f"{self.base_url_v2}/Astro/AllTemplates")
        return res.json()

    # --- Optimization (v2-only): batch optimization summaries --------------------

    def get_optimization_summaries(self, start_date=None, end_date=None):
        """Get optimization summaries, optionally filtered by a date range.

        Args:
            start_date: Optional start date (``OptimizationStartTime``, ISO YYYY-MM-DD)
            end_date: Optional end date (ISO YYYY-MM-DD)

        Returns:
            list: Optimization summary dicts
        """
        params = {}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        res = self.api_request(f"{self.base_url_v2}/Optimization/summaries", params=params)
        return res.json()

    def get_optimization_batch_summary(self, start_date=None, end_date=None):
        """Get batch optimization summary by date range (defaults to ~1 week).

        Args:
            start_date: Optional start date (ISO YYYY-MM-DD)
            end_date: Optional end date (ISO YYYY-MM-DD)

        Returns:
            list: Batch optimization summary dicts
        """
        params = {}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        res = self.api_request(f"{self.base_url_v2}/Optimization/Summary/Batch", params=params)
        return res.json()

    def get_optimization_batch_status(self, batch_name):
        """Get the current status of a batch optimization.

        Args:
            batch_name: Optimization batch name

        Returns:
            dict: Batch status
        """
        res = self.api_request(f"{self.base_url_v2}/Optimization/Status/Batch/{batch_name}")
        return res.json()

    # --- Asset classification (v2-only) ------------------------------------------

    def get_asset_classification_groups(self):
        """Get all asset-classification groups.

        Returns:
            list: Classification-group dicts
        """
        res = self.api_request(f"{self.base_url_v2}/AssetClassification/ClassificationGroups")
        return res.json()

    def get_asset_classification_methods(self):
        """Get all asset-classification methods.

        Returns:
            list: Classification-method dicts
        """
        res = self.api_request(f"{self.base_url_v2}/AssetClassification/ClassificationMethods")
        return res.json()

    # --- Analytics config (v2-only) ----------------------------------------------

    def get_analytics_run_config(self):
        """Get the run-analytics configurations.

        Returns:
            list: Run-analytics configuration dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Analytics/RunAnalyticsConfig")
        return res.json()

    def get_analytics_banner_status(self):
        """Get the analytics banner-spinner status.

        Returns:
            dict: Banner-spinner status
        """
        res = self.api_request(f"{self.base_url_v2}/Analytics/BannerSpinner/Status")
        return res.json()

    # --- Trading / TradeInstance (v2-only): the richer v2 instance surface -------
    # Named with a ``trading_`` prefix to stay distinct from the v1
    # ``get_trade_instance(s)`` methods, which hit the separate /tradeorder surface.

    def get_trading_instances(
        self,
        trade_instance_id=None,
        advisor_external_id=None,
        is_enabled=None,
        is_deleted=None,
    ):
        """Get trade instance(s) from the v2 Trading surface.

        Args:
            trade_instance_id: Optional trade-instance ID (maps to ``tradeInstanceId``)
            advisor_external_id: Optional advisor external ID (``advisorExternalId``)
            is_enabled: Optional bool (maps to ``isEnabled``)
            is_deleted: Optional bool (maps to ``isDeleted``)

        Returns:
            list | dict: Trade instance(s)
        """
        params = {}
        if trade_instance_id is not None:
            params["tradeInstanceId"] = trade_instance_id
        if advisor_external_id is not None:
            params["advisorExternalId"] = advisor_external_id
        if is_enabled is not None:
            params["isEnabled"] = str(is_enabled).lower()
        if is_deleted is not None:
            params["isDeleted"] = str(is_deleted).lower()
        res = self.api_request(f"{self.base_url_v2}/Trading/TradeInstance", params=params)
        return res.json()

    def get_trading_instance_trades(self, trade_instance_id):
        """Get the trades for a v2 trade instance.

        Args:
            trade_instance_id: Trade-instance ID

        Returns:
            list: Trade dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Trading/TradeInstance/{trade_instance_id}/Trades"
        )
        return res.json()

    def get_trading_instances_for_user(self, start_date, end_date, offset=None, limit=None):
        """Get trade instances for portfolios accessible to the user, by date range.

        Args:
            start_date: Start date (ISO YYYY-MM-DD; maps to ``startDate``)
            end_date: End date (ISO YYYY-MM-DD; maps to ``endDate``)
            offset: Optional paging offset
            limit: Optional paging limit

        Returns:
            list: Trade instance dicts
        """
        params = {"startDate": start_date, "endDate": end_date}
        if offset is not None:
            params["offset"] = offset
        if limit is not None:
            params["limit"] = limit
        res = self.api_request(f"{self.base_url_v2}/Trading/TradeInstance/ForUser", params=params)
        return res.json()

    def get_trading_instances_by_date_range(self, start_date, end_date):
        """Get the trade-instance grid for a date range.

        Args:
            start_date: Start date (ISO YYYY-MM-DD)
            end_date: End date (ISO YYYY-MM-DD)

        Returns:
            list: Trade instance dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Trading/TradeInstance/GetByDateRange",
            params={"startDate": start_date, "endDate": end_date},
        )
        return res.json()

    def get_trading_instances_paginated(
        self,
        start_date=None,
        end_date=None,
        portfolio_id=None,
        external_firm_id=None,
        external_account_id=None,
        skip=None,
        take=None,
    ):
        """Get a paginated list of trade instances (without trades) plus a total count.

        Note:
            Eclipse requires a scoping filter — pass ``portfolio_id`` (or the
            external firm/account IDs). A date window alone returns
            ``400 'Unable to retrieve trade instances'``.

        Args:
            start_date / end_date: Optional ISO date window
            portfolio_id: Portfolio filter (maps to ``portfolioId``)
            external_firm_id: Optional external firm ID (``externalFirmId``)
            external_account_id: Optional external account ID (``externalAccountId``)
            skip / take: Optional paging window

        Returns:
            dict: Paginated result with ``data`` (instances) and ``total`` count
        """
        params = {}
        for key, val in (
            ("startDate", start_date),
            ("endDate", end_date),
            ("portfolioId", portfolio_id),
            ("externalFirmId", external_firm_id),
            ("externalAccountId", external_account_id),
            ("skip", skip),
            ("take", take),
        ):
            if val is not None:
                params[key] = val
        res = self.api_request(f"{self.base_url_v2}/Trading/TradeInstance/Paginated", params=params)
        return res.json()

    def get_trading_instances_with_trades(
        self,
        portfolio_id=None,
        start_date=None,
        end_date=None,
        order_status=None,
        skip=None,
        take=None,
    ):
        """Get a paginated list of trade instances including their trades.

        Args:
            portfolio_id: Optional portfolio filter (maps to ``portfolioId``)
            start_date / end_date: Optional ISO date window
            order_status: Optional order-status filter (``orderStatus``)
            skip / take: Optional paging window

        Returns:
            dict: Paginated result with instances + trades
        """
        params = {}
        for key, val in (
            ("portfolioId", portfolio_id),
            ("startDate", start_date),
            ("endDate", end_date),
            ("orderStatus", order_status),
            ("skip", skip),
            ("take", take),
        ):
            if val is not None:
                params[key] = val
        res = self.api_request(
            f"{self.base_url_v2}/Trading/TradeInstance/WithTrades", params=params
        )
        return res.json()

    def get_trading_active_batch_jobs(self, start_date=None, end_date=None):
        """Get active batch-job entries for the user.

        Args:
            start_date / end_date: Optional ISO date window

        Returns:
            list: Active batch-job dicts
        """
        params = {}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        res = self.api_request(f"{self.base_url_v2}/Trading/ActiveBatchJobs", params=params)
        return res.json()

    # --- Optimization (v2-only): per-batch / per-account detail reads ------------

    def get_optimization_accounts(self, batch_id):
        """Get the current state of accounts in an optimization batch.

        Args:
            batch_id: Optimization batch ID

        Returns:
            list: Account-state dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Optimization/accounts/{batch_id}")
        return res.json()

    def get_optimization_account_summary(self, batch_id, account_id=None):
        """Get the optimization summary (and holdings) for an account in a batch.

        Args:
            batch_id: Optimization batch ID
            account_id: Optional account ID (maps to ``accountId``)

        Returns:
            dict: Optimization summary
        """
        params = {}
        if account_id is not None:
            params["accountId"] = account_id
        res = self.api_request(
            f"{self.base_url_v2}/Optimization/summaries/{batch_id}", params=params
        )
        return res.json()

    def get_optimization_batch_account_summaries(self, batch_id):
        """Get every optimization summary belonging to a batch (one row per account).

        Args:
            batch_id: Optimization batch ID

        Returns:
            list: Optimization summary dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Optimization/summaries/batch/{batch_id}")
        return res.json()

    def get_optimization_account_messages(self, batch_id, account_id=None):
        """Get optimizer-emitted messages for an account in a batch.

        Args:
            batch_id: Optimization batch ID
            account_id: Optional account ID (maps to ``accountId``)

        Returns:
            list: Optimizer message dicts
        """
        params = {}
        if account_id is not None:
            params["accountId"] = account_id
        res = self.api_request(
            f"{self.base_url_v2}/Optimization/summaries/{batch_id}/messages", params=params
        )
        return res.json()

    def get_optimization_log(self, connect_account_id=None, batch_name=None, connect_firm_id=None):
        """Get the optimization log.

        Args:
            connect_account_id: Optional Orion Connect account ID (``connectAccountId``)
            batch_name: Optional batch name (``batchName``)
            connect_firm_id: Optional Orion Connect firm ID (``connectFirmId``)

        Returns:
            dict | list: Optimization log
        """
        params = {}
        if connect_account_id is not None:
            params["connectAccountId"] = connect_account_id
        if batch_name is not None:
            params["batchName"] = batch_name
        if connect_firm_id is not None:
            params["connectFirmId"] = connect_firm_id
        res = self.api_request(f"{self.base_url_v2}/Optimization/Log", params=params)
        return res.json()

    def get_optimization_holdings_target(self, account_id, batch_name=None, al_client_id=None):
        """Get the holdings and target strategies for an account in a batch.

        Args:
            account_id: Account ID
            batch_name: Optional batch name (``batchName``)
            al_client_id: Optional AL client ID (``alClientId``)

        Returns:
            dict: Holdings + target strategies
        """
        params = {}
        if batch_name is not None:
            params["batchName"] = batch_name
        if al_client_id is not None:
            params["alClientId"] = al_client_id
        res = self.api_request(
            f"{self.base_url_v2}/Optimization/HoldingsTarget/{account_id}", params=params
        )
        return res.json()

    # --- SavedView (v2-only) -----------------------------------------------------

    def get_saved_views(self, view_type_id, name=None):
        """Get the current user's saved views for a view type.

        Args:
            view_type_id: View-type ID
            name: Optional name filter (maps to ``name``)

        Returns:
            list: Saved-view dicts
        """
        params = {}
        if name is not None:
            params["name"] = name
        res = self.api_request(
            f"{self.base_url_v2}/SavedView/ViewType/{view_type_id}", params=params
        )
        return res.json()

    def get_saved_views_ranked(self, view_type_id, simple_views=None, filter_required=None):
        """Get the user's saved views for a view type, including rank/order.

        Args:
            view_type_id: View-type ID
            simple_views: Optional bool (maps to ``simpleViews``)
            filter_required: Optional bool (maps to ``filterRequired``)

        Returns:
            list: Ranked saved-view dicts
        """
        params = {}
        if simple_views is not None:
            params["simpleViews"] = str(simple_views).lower()
        if filter_required is not None:
            params["filterRequired"] = str(filter_required).lower()
        res = self.api_request(
            f"{self.base_url_v2}/SavedView/ViewType/{view_type_id}/Rank", params=params
        )
        return res.json()

    def execute_saved_view(self, view_id):
        """Execute a saved view and return the number of records.

        Args:
            view_id: Saved-view ID

        Returns:
            dict: Execution result (record count)
        """
        res = self.api_request(f"{self.base_url_v2}/SavedView/Execute/{view_id}")
        return res.json()

    # --- Notes (v2-only) ---------------------------------------------------------

    def get_notes(self, related_type, related_id):
        """Get the notes for a related entity.

        Args:
            related_type: Related entity type (maps to ``relatedType``)
            related_id: Related entity ID (maps to ``relatedId``)

        Returns:
            list: Note dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Notes",
            params={"relatedType": related_type, "relatedId": related_id},
        )
        return res.json()

    def get_notes_history(self, related_type, related_id, from_date=None, to_date=None):
        """Get notes history for a related entity.

        Args:
            related_type: Related entity type (maps to ``relatedType``)
            related_id: Related entity ID (maps to ``relatedId``)
            from_date: Optional start date (``fromDate``)
            to_date: Optional end date (``toDate``)

        Returns:
            list: Note-history dicts
        """
        params = {"relatedType": related_type, "relatedId": related_id}
        if from_date is not None:
            params["fromDate"] = from_date
        if to_date is not None:
            params["toDate"] = to_date
        res = self.api_request(f"{self.base_url_v2}/Notes/History", params=params)
        return res.json()

    def get_note_related_entities(self, entity_id, entity_type):
        """Get entities related to a primary entity (for notes).

        Args:
            entity_id: Primary entity ID (maps to ``entityId``)
            entity_type: Primary entity type (maps to ``entityType``)

        Returns:
            list: Related-entity dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Notes/RelatedEntities",
            params={"entityId": entity_id, "entityType": entity_type},
        )
        return res.json()

    # --- Account detail (v2-only reads with no v1 equivalent) --------------------

    def get_account_cash_details(self, account_id):
        """Get cash details for an account.

        Args:
            account_id: Account ID

        Returns:
            dict: Cash details
        """
        res = self.api_request(f"{self.base_url_v2}/Account/Accounts/{account_id}/CashDetails")
        return res.json()

    def get_account_gain_loss_summary(self, account_id):
        """Get the gain/loss summary for an account.

        Args:
            account_id: Account ID

        Returns:
            dict: Gain/loss summary
        """
        res = self.api_request(f"{self.base_url_v2}/Account/Accounts/{account_id}/GainLossSummary")
        return res.json()

    def get_account_history(self, account_id, from_date=None, to_date=None):
        """Get account history.

        Args:
            account_id: Account ID
            from_date / to_date: Optional ISO date window (``fromDate`` / ``toDate``)

        Returns:
            list: Account-history dicts
        """
        params = {}
        if from_date is not None:
            params["fromDate"] = from_date
        if to_date is not None:
            params["toDate"] = to_date
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/{account_id}/History", params=params
        )
        return res.json()

    def get_account_model_history(self, account_id, from_date=None, to_date=None):
        """Get an account's model history.

        Args:
            account_id: Account ID
            from_date / to_date: Optional ISO date window (``fromDate`` / ``toDate``)

        Returns:
            list: Model-history dicts
        """
        params = {}
        if from_date is not None:
            params["fromDate"] = from_date
        if to_date is not None:
            params["toDate"] = to_date
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/{account_id}/ModelHistory", params=params
        )
        return res.json()

    def get_account_transactions(self, account_id, start_date=None, end_date=None):
        """Get account transactions over a date range.

        Args:
            account_id: Account ID
            start_date / end_date: Optional ISO date window (``startDate`` / ``endDate``)

        Returns:
            list: Transaction dicts
        """
        params = {}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/{account_id}/Transactions", params=params
        )
        return res.json()

    def get_accessible_account_count(self):
        """Get the count of accounts accessible to the authenticated user.

        Returns:
            int | dict: Accessible-account count
        """
        res = self.api_request(f"{self.base_url_v2}/Account/Accounts/AccessibleCount")
        return res.json()

    def get_account_by_external(self, external_firm_id, external_account_id):
        """Get an account by external firm + account ID.

        Args:
            external_firm_id: External firm ID
            external_account_id: External account ID

        Returns:
            dict: Account detail
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/byexternal/"
            f"{external_firm_id}/{external_account_id}"
        )
        return res.json()

    # --- Astro accounts (v2-only) ------------------------------------------------

    def get_astro_accounts(self, filter=None):
        """Get Astro account values (including alert-determination data).

        Args:
            filter: Optional filter (maps to ``filter``; see
                :meth:`get_astro_account_filters`)

        Returns:
            list: Astro-account dicts
        """
        params = {}
        if filter is not None:
            params["filter"] = filter
        res = self.api_request(f"{self.base_url_v2}/Account/AstroAccounts", params=params)
        return res.json()

    def get_astro_account_filters(self):
        """Get the filters usable in the Astro-accounts endpoint.

        Returns:
            list: Filter dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Account/AstroAccounts/Filters")
        return res.json()

    def get_astro_account_securities_restrictions(self, account_id):
        """Get Astro security restrictions for an account.

        Args:
            account_id: Account ID

        Returns:
            list: Security-restriction dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/AstroAccounts/{account_id}/SecuritiesRestrictions"
        )
        return res.json()

    def get_astro_account_investor_preferences(
        self, account_id, strategy_name=None, al_client_id=None
    ):
        """Get Astro investor preferences for an account.

        Args:
            account_id: Account ID
            strategy_name: Optional strategy name (``strategyName``)
            al_client_id: Optional AL client ID (``alClientId``)

        Returns:
            dict: Investor preferences
        """
        params = {}
        if strategy_name is not None:
            params["strategyName"] = strategy_name
        if al_client_id is not None:
            params["alClientId"] = al_client_id
        res = self.api_request(
            f"{self.base_url_v2}/Account/AstroAccounts/{account_id}/InvestorPreferences",
            params=params,
        )
        return res.json()

    # --- Portfolio detail (v2-only reads) ----------------------------------------

    def get_portfolio_allocations(self, portfolio_id):
        """Get portfolio allocations.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            dict: Allocations with ``categories`` / ``classes`` and reserve cash
        """
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/{portfolio_id}/Allocations"
        )
        return res.json()

    def get_portfolio_cash_details(self, portfolio_id):
        """Get cash details for a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            dict: Cash details
        """
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/CashDetails/{portfolio_id}"
        )
        return res.json()

    def get_portfolio_gain_loss_summary(self, portfolio_id):
        """Get the gain/loss summary for a portfolio.

        Args:
            portfolio_id: Portfolio ID

        Returns:
            dict: Gain/loss summary
        """
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/{portfolio_id}/GainLossSummary"
        )
        return res.json()

    def get_portfolio_mac_history(self, portfolio_id, from_date=None, to_date=None):
        """Get portfolio MAC (model-assignment-change) history.

        Args:
            portfolio_id: Portfolio ID
            from_date / to_date: Optional ISO date window (``fromDate`` / ``toDate``)

        Returns:
            dict: MAC history with ``details`` and ``statuses``
        """
        params = {}
        if from_date is not None:
            params["fromDate"] = from_date
        if to_date is not None:
            params["toDate"] = to_date
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/{portfolio_id}/MacHistory", params=params
        )
        return res.json()

    def get_portfolio_auto_rebalance_history(self, portfolio_id, start_date=None, end_date=None):
        """Get auto-rebalance history for a portfolio.

        Args:
            portfolio_id: Portfolio ID
            start_date / end_date: Optional ISO date window (``startDate`` / ``endDate``)

        Returns:
            list: Auto-rebalance-history dicts
        """
        params = {}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/{portfolio_id}/AutoRebalanceHistory",
            params=params,
        )
        return res.json()

    def get_portfolio_tree(self, portfolio_id=None, account_id=None):
        """Get the portfolio/account hierarchy for a portfolio or account.

        Args:
            portfolio_id: Optional portfolio ID (maps to ``portfolioId``)
            account_id: Optional account ID (maps to ``accountId``)

        Returns:
            dict: Portfolio/account tree
        """
        params = {}
        if portfolio_id is not None:
            params["portfolioId"] = portfolio_id
        if account_id is not None:
            params["accountId"] = account_id
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/PortfolioTree", params=params
        )
        return res.json()

    def get_portfolio_search(self, search=None, include_value=None, limit=None, offset=None):
        """Search firm portfolios (v2 paged search).

        Args:
            search: Optional search string
            include_value: Optional bool (maps to ``includeValue``)
            limit / offset: Optional paging window

        Returns:
            list: Portfolio dicts
        """
        params = {}
        if search is not None:
            params["search"] = search
        if include_value is not None:
            params["includeValue"] = str(include_value).lower()
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/GetPortfolioSearch", params=params
        )
        return res.json()

    def get_accessible_portfolio_count(self):
        """Get the count of portfolios accessible to the authenticated user.

        Returns:
            int | dict: Accessible-portfolio count
        """
        res = self.api_request(f"{self.base_url_v2}/Portfolio/Portfolios/AccessibleCount")
        return res.json()

    def get_user_portfolio_ids(self):
        """Get the portfolio IDs accessible to the authenticated user.

        Returns:
            list: Portfolio IDs
        """
        res = self.api_request(f"{self.base_url_v2}/Portfolio/Portfolios/GetUserPortfolioIds")
        return res.json()

    # --- Sleeves (v2-only) -------------------------------------------------------

    def get_sleeve_allocations(self, account_id):
        """Get sleeve allocation details for an account.

        Args:
            account_id: Account ID

        Returns:
            dict: Sleeve allocations with ``categories`` / ``classes`` and reserve cash
        """
        res = self.api_request(f"{self.base_url_v2}/Portfolio/Sleeves/{account_id}/Allocations")
        return res.json()

    def get_sleeve_strategies(self):
        """Get all sleeve strategies.

        Returns:
            list: Sleeve-strategy dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Portfolio/Sleeves/SleeveStrategies")
        return res.json()

    def get_sleeve_contribution_methods(self):
        """Get all sleeve contribution methods.

        Returns:
            list: Contribution-method dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Portfolio/Sleeves/SleeveContributionMethods")
        return res.json()

    def get_sleeve_distribution_methods(self):
        """Get all sleeve distribution methods.

        Returns:
            list: Distribution-method dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Portfolio/Sleeves/SleeveDistributionMethods")
        return res.json()

    # --- Preference (v2-only) ----------------------------------------------------

    def get_preference(self, preference_name):
        """Get the value of a named preference.

        Args:
            preference_name: Preference name (maps to ``preferenceName``)

        Returns:
            dict: Preference value
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/GetPreference",
            params={"preferenceName": preference_name},
        )
        return res.json()

    # --- Model / Modeling (v2 reads) ---------------------------------------------
    # ``_v2`` suffix where a v1 method of the same base name already exists, so the
    # method stays reachable on the Eclipse unifier (v1 wins bare-name collisions).

    def get_models_v2(self, filter=None, model_id=None, search=None, name=None):
        """Get models via the v2 GetAllModels endpoint (rich filters).

        Args:
            filter: Optional filter (maps to ``filter``)
            model_id: Optional model ID (maps to ``modelId``)
            search: Optional search string (maps to ``search``)
            name: Optional name filter (maps to ``name``)

        Returns:
            list: Model dicts
        """
        params = {}
        if filter is not None:
            params["filter"] = filter
        if model_id is not None:
            params["modelId"] = model_id
        if search is not None:
            params["search"] = search
        if name is not None:
            params["name"] = name
        res = self.api_request(f"{self.base_url_v2}/Model/GetAllModels", params=params)
        return res.json()

    def get_model_types_v2(self):
        """Get all model types (v2).

        Returns:
            list: Model-type dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Model/GetModelTypes")
        return res.json()

    def get_model_risk_profile(self, model_id, duration):
        """Get the HiddenLevers risk-profile information for a model.

        Args:
            model_id: Model ID
            duration: Risk-profile duration (see :meth:`get_hidden_levers_durations`)

        Returns:
            dict: Risk-profile information
        """
        res = self.api_request(f"{self.base_url_v2}/Model/{model_id}/RiskProfile/{duration}")
        return res.json()

    def get_model_sync_oc_firms(self, model_id):
        """Get the Orion Connect firms available to sync a model to.

        Args:
            model_id: Model ID (maps to ``modelId``)

        Returns:
            list: OC-firm dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Model/GetModelSyncToOCFirms", params={"modelId": model_id}
        )
        return res.json()

    def get_model_levels(self, model_id):
        """Get all the levels for a model.

        Args:
            model_id: Model ID

        Returns:
            list: Model-level dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Modeling/Models/{model_id}/Levels")
        return res.json()

    def get_model_analysis_v2(
        self,
        model_id,
        asset_type="securityset",
        is_include_cost_basis=None,
        is_include_trade_block_account=None,
        is_exclude_asset=None,
    ):
        """Get model analysis (v2) for a security set / category / class / subclass.

        Args:
            model_id: Model ID
            asset_type: Aggregation level (default "securityset"; maps to ``assetType``)
            is_include_cost_basis: Optional bool (``isIncludeCostBasis``)
            is_include_trade_block_account: Optional bool (``isIncludeTradeBlockAccount``)
            is_exclude_asset: Optional bool (``isExcludeAsset``)

        Returns:
            dict: Model analysis
        """
        params = {"assetType": asset_type}
        if is_include_cost_basis is not None:
            params["isIncludeCostBasis"] = str(is_include_cost_basis).lower()
        if is_include_trade_block_account is not None:
            params["isIncludeTradeBlockAccount"] = str(is_include_trade_block_account).lower()
        if is_exclude_asset is not None:
            params["isExcludeAsset"] = str(is_exclude_asset).lower()
        res = self.api_request(
            f"{self.base_url_v2}/Modeling/Models/{model_id}/ModelAnalysis", params=params
        )
        return res.json()

    def get_model_aggregate_analysis(
        self,
        model_id,
        is_include_cost_basis=None,
        is_include_trade_block_account=None,
        is_exclude_asset=None,
    ):
        """Get the model-aggregate detail for model analysis.

        Args:
            model_id: Model ID
            is_include_cost_basis: Optional bool (``isIncludeCostBasis``)
            is_include_trade_block_account: Optional bool (``isIncludeTradeBlockAccount``)
            is_exclude_asset: Optional bool (``isExcludeAsset``)

        Returns:
            dict: Model-aggregate analysis
        """
        params = {}
        if is_include_cost_basis is not None:
            params["isIncludeCostBasis"] = str(is_include_cost_basis).lower()
        if is_include_trade_block_account is not None:
            params["isIncludeTradeBlockAccount"] = str(is_include_trade_block_account).lower()
        if is_exclude_asset is not None:
            params["isExcludeAsset"] = str(is_exclude_asset).lower()
        res = self.api_request(
            f"{self.base_url_v2}/Modeling/Models/{model_id}/ModelAnalysis/ModelAggregate",
            params=params,
        )
        return res.json()

    def get_astro_models(self):
        """Get Astro models.

        Returns:
            list: Astro-model dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Modeling/Models/Astro")
        return res.json()

    def get_strategist_models(self):
        """Get community models with their associated strategist (for the user).

        Returns:
            list: Community/strategist model dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Modeling/Models/GetStrategistModels")
        return res.json()

    def get_stress_test_scenarios(self):
        """Get HiddenLevers stress-test scenarios.

        Returns:
            list: Stress-test scenario dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Modeling/Models/StressTestScenarios")
        return res.json()

    def get_hidden_levers_user_status(self, email):
        """Get the HiddenLevers status (paid or free) of a user.

        Args:
            email: User email (maps to ``email``)

        Returns:
            dict: User status
        """
        res = self.api_request(
            f"{self.base_url_v2}/Modeling/Models/UserStatus", params={"email": email}
        )
        return res.json()

    # --- Security / SecuritySet (v2 reads) ---------------------------------------

    def get_securities(self, security_id=None, is_cached=None):
        """Get securities (v2).

        Args:
            security_id: Optional security ID (maps to ``securityId``)
            is_cached: Optional bool (maps to ``isCached``)

        Returns:
            list: Security dicts
        """
        params = {}
        if security_id is not None:
            params["securityId"] = security_id
        if is_cached is not None:
            params["isCached"] = str(is_cached).lower()
        res = self.api_request(f"{self.base_url_v2}/Security/GetSecurities", params=params)
        return res.json()

    def get_security_sets_v2(self, security_set_id=None):
        """Get security sets via the v2 GetSecuritySets endpoint.

        Args:
            security_set_id: Optional security-set ID (maps to ``securitySetId``)

        Returns:
            list: Security-set dicts
        """
        params = {}
        if security_set_id is not None:
            params["securitySetId"] = security_set_id
        res = self.api_request(f"{self.base_url_v2}/SecuritySet/GetSecuritySets", params=params)
        return res.json()

    def get_security_set_history(self, security_set_id, from_date=None, to_date=None):
        """Get the change history for a security set.

        Args:
            security_set_id: Security-set ID
            from_date / to_date: Optional ISO date window (``fromDate`` / ``toDate``)

        Returns:
            list: History dicts
        """
        params = {}
        if from_date is not None:
            params["fromDate"] = from_date
        if to_date is not None:
            params["toDate"] = to_date
        res = self.api_request(
            f"{self.base_url_v2}/SecuritySet/{security_set_id}/History", params=params
        )
        return res.json()

    def get_security_set_detail_history(self, security_set_id, from_date=None, to_date=None):
        """Get the detailed change history for a security set.

        Args:
            security_set_id: Security-set ID
            from_date / to_date: Optional ISO date window (``fromDate`` / ``toDate``)

        Returns:
            dict: Detailed history (``details``, ``alternatives``, ``equivalences``, etc.)
        """
        params = {}
        if from_date is not None:
            params["fromDate"] = from_date
        if to_date is not None:
            params["toDate"] = to_date
        res = self.api_request(
            f"{self.base_url_v2}/SecuritySet/{security_set_id}/DetailHistory", params=params
        )
        return res.json()

    # --- Lookup (v2 reference data) ----------------------------------------------

    def get_hidden_levers_durations(self):
        """Get the available HiddenLevers risk-profile durations.

        Returns:
            list: Duration values
        """
        res = self.api_request(f"{self.base_url_v2}/Lookup/HiddenLeversDurations")
        return res.json()

    def get_sma_account_type_restrictions(self, category=None):
        """Get SMA account-type restriction values.

        Args:
            category: Optional category; when provided, hits the per-category route.

        Returns:
            list: Account-type restriction values
        """
        path = "/Lookup/SmaAccountTypeRestrictions"
        if category is not None:
            path += f"/Category/{category}"
        res = self.api_request(f"{self.base_url_v2}{path}")
        return res.json()

    # =========================================================================
    # WRITE methods (mutating). Low-blast-radius user/UI state: SavedView, Notes,
    # Tags. Bodies are passed through as documented DTOs so callers stay faithful
    # to the Swagger. These are NOT executed in the integration suite.
    # =========================================================================

    # --- SavedView writes ---

    def save_saved_view(self, view):
        """Save (create/update) a saved view for a specific view id.

        Args:
            view: Saved-view DTO (request body)

        Returns:
            dict: Saved view
        """
        res = self.api_request(
            f"{self.base_url_v2}/SavedView/SavedViewByIdSave", requests.post, json=view
        )
        return res.json()

    def delete_saved_view(self, view_id):
        """Delete a saved view.

        Args:
            view_id: Saved-view ID
        """
        res = self.api_request(f"{self.base_url_v2}/SavedView/{view_id}", requests.delete)
        return res.json()

    def delete_saved_views(self, view_ids):
        """Delete an array of saved views.

        Args:
            view_ids: List of saved-view IDs (request body)
        """
        res = self.api_request(f"{self.base_url_v2}/SavedView/Delete", requests.post, json=view_ids)
        return res.json()

    def add_saved_view_to_dashboard(self, view_id, is_firm_action_items=None):
        """Add a saved view to the user-level dashboard.

        Args:
            view_id: Saved-view ID
            is_firm_action_items: Optional bool (maps to ``isFirmActionItems``)

        Returns:
            dict: Result
        """
        params = {}
        if is_firm_action_items is not None:
            params["isFirmActionItems"] = str(is_firm_action_items).lower()
        res = self.api_request(
            f"{self.base_url_v2}/SavedView/{view_id}/dashboard", requests.post, params=params
        )
        return res.json()

    def set_default_saved_view(self, view_type_id, view_id):
        """Set a view as the default view for a view type.

        Args:
            view_type_id: View-type ID
            view_id: Saved-view ID
        """
        res = self.api_request(
            f"{self.base_url_v2}/SavedView/ViewType/{view_type_id}/DefaultView/{view_id}",
            requests.post,
        )
        return res.json()

    def save_saved_views_ranking(self, view_type_id, views):
        """Save the ranking/order of saved views for a view type.

        Args:
            view_type_id: View-type ID
            views: Ranked saved-view DTOs (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/SavedView/ViewType/{view_type_id}/Rank",
            requests.post,
            json=views,
        )
        return res.json()

    def get_saved_views_for_types(self, view_type_ids):
        """Get the current user's saved views for an array of view types (POST query).

        Args:
            view_type_ids: List of view-type IDs (request body)

        Returns:
            list: Saved-view dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/SavedView/ViewType", requests.post, json=view_type_ids
        )
        return res.json()

    # --- Notes writes ---

    def add_notes(self, notes):
        """Create notes.

        Args:
            notes: List of note DTOs (request body)

        Returns:
            list | dict: Created notes
        """
        res = self.api_request(f"{self.base_url_v2}/Notes/AddList", requests.post, json=notes)
        return res.json()

    def update_notes(self, notes):
        """Update notes.

        Args:
            notes: List of note DTOs (request body)

        Returns:
            list | dict: Updated notes
        """
        res = self.api_request(f"{self.base_url_v2}/Notes/UpdateList", requests.post, json=notes)
        return res.json()

    def delete_notes(self, notes):
        """Delete notes (batch).

        Args:
            notes: List of note DTOs / IDs (request body)
        """
        res = self.api_request(f"{self.base_url_v2}/Notes/DeleteList", requests.post, json=notes)
        return res.json()

    def update_note(self, note_id, note):
        """Update a single note.

        Args:
            note_id: Note ID
            note: Note DTO (request body)

        Returns:
            dict: Updated note
        """
        res = self.api_request(f"{self.base_url_v2}/Notes/{note_id}", requests.put, json=note)
        return res.json()

    def delete_note(self, note_id):
        """Delete a single note.

        Args:
            note_id: Note ID
        """
        res = self.api_request(f"{self.base_url_v2}/Notes/{note_id}", requests.delete)
        return res.json()

    # --- Tags writes ---

    def delete_tag(self, tag):
        """Delete a tag.

        Args:
            tag: Tag DTO / identifier (request body)
        """
        res = self.api_request(f"{self.base_url_v2}/Tags/delete", requests.post, json=tag)
        return res.json()

    # --- ESG writes (mutating) ---

    def create_esg_theme(self, theme):
        """Create an ESG theme.

        Args:
            theme: ESG-theme DTO (request body)

        Returns:
            dict: Created theme
        """
        res = self.api_request(f"{self.base_url_v2}/ESG/Themes", requests.post, json=theme)
        return res.json()

    def update_esg_theme(self, theme):
        """Update an ESG theme.

        Args:
            theme: ESG-theme DTO (request body)

        Returns:
            dict: Updated theme
        """
        res = self.api_request(f"{self.base_url_v2}/ESG/Themes", requests.put, json=theme)
        return res.json()

    def delete_esg_themes(self, themes):
        """Delete ESG themes.

        Args:
            themes: List of ESG-theme DTOs / IDs (request body)
        """
        res = self.api_request(f"{self.base_url_v2}/ESG/Themes", requests.delete, json=themes)
        return res.json()

    def create_esg_assignments(self, assignments):
        """Create ESG assignments.

        Args:
            assignments: List of ESG-assignment DTOs (request body)

        Returns:
            list | dict: Created assignments
        """
        res = self.api_request(
            f"{self.base_url_v2}/ESG/Assignments", requests.post, json=assignments
        )
        return res.json()

    def update_esg_restrictions_for_portfolio(self, restrictions):
        """Update the ESG restrictions for a portfolio.

        Args:
            restrictions: ESG-restrictions DTO (request body)

        Returns:
            dict: Updated restrictions
        """
        res = self.api_request(
            f"{self.base_url_v2}/ESG/ESGRestrictionsForPortfolio", requests.put, json=restrictions
        )
        return res.json()

    # --- Asset classification writes (mutating) ---

    def create_asset_classification_group(self, group):
        """Create an asset-classification group.

        Args:
            group: Classification-group DTO (request body)

        Returns:
            dict: Created group
        """
        res = self.api_request(
            f"{self.base_url_v2}/AssetClassification/ClassificationGroup",
            requests.post,
            json=group,
        )
        return res.json()

    def update_asset_classification_group(self, group):
        """Update an asset-classification group.

        Args:
            group: Classification-group DTO (request body)

        Returns:
            dict: Updated group
        """
        res = self.api_request(
            f"{self.base_url_v2}/AssetClassification/ClassificationGroup",
            requests.put,
            json=group,
        )
        return res.json()

    def delete_asset_classification_group(self, group_id):
        """Delete an asset-classification group.

        Args:
            group_id: Classification-group ID
        """
        res = self.api_request(
            f"{self.base_url_v2}/AssetClassification/ClassificationGroup/{group_id}",
            requests.delete,
        )
        return res.json()

    def classify_securities(self, classifications):
        """Assign classifications to securities.

        Args:
            classifications: Security-classification DTO(s) (request body)

        Returns:
            dict: Result
        """
        res = self.api_request(
            f"{self.base_url_v2}/AssetClassification/Security/Classifications",
            requests.post,
            json=classifications,
        )
        return res.json()

    # --- Notification writes (mutating) ---

    def create_notification(self, notification):
        """Create a notification.

        Args:
            notification: Notification DTO (request body)

        Returns:
            dict: Created notification
        """
        res = self.api_request(
            f"{self.base_url_v2}/Notifications/Notification/CreateNotification",
            requests.post,
            json=notification,
        )
        return res.json()

    def update_notification(self, notification):
        """Update a notification.

        Args:
            notification: Notification DTO (request body)

        Returns:
            dict: Updated notification
        """
        res = self.api_request(
            f"{self.base_url_v2}/Notifications/Notification/UpdateNotification",
            requests.put,
            json=notification,
        )
        return res.json()

    def send_notification(self, notification):
        """Send a notification.

        Args:
            notification: Notification DTO (request body)

        Returns:
            dict: Result
        """
        res = self.api_request(
            f"{self.base_url_v2}/Notifications/Notification/SendNotification",
            requests.post,
            json=notification,
        )
        return res.json()

    def send_trading_notification(self, notification):
        """Send a trading notification.

        Args:
            notification: Trading-notification DTO (request body)

        Returns:
            dict: Result
        """
        res = self.api_request(
            f"{self.base_url_v2}/Notifications/Notification/SendTradingNotification",
            requests.post,
            json=notification,
        )
        return res.json()

    # --- Preference reads (v2; complements get_preference) -----------------------

    def get_preference_securities(self, level_name, record_id):
        """Get portfolio- or account-level preference securities.

        Args:
            level_name: Preference level (e.g. "Portfolio", "Account")
            record_id: Portfolio or account ID

        Returns:
            list: Preference-security dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/{level_name}/Securities/{record_id}"
        )
        return res.json()

    def get_tax_lot_depletion_preference(
        self, related_type, record_id, preference_value_id=None, inherited_preference_value_id=None
    ):
        """Get tax-lot depletion-method preference values for a record.

        Args:
            related_type: Related entity type (e.g. "Portfolio", "Account")
            record_id: Record ID
            preference_value_id: Optional preference value ID (``preferenceValueId``)
            inherited_preference_value_id: Optional inherited value ID
                (``inheritedPreferenceValueId``)

        Returns:
            dict: Tax-lot depletion preference values
        """
        params = {}
        if preference_value_id is not None:
            params["preferenceValueId"] = preference_value_id
        if inherited_preference_value_id is not None:
            params["inheritedPreferenceValueId"] = inherited_preference_value_id
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/{related_type}"
            f"/taxLotDepletionMethodPreference/{record_id}",
            params=params,
        )
        return res.json()

    def get_tax_lot_depletion_preference_master(
        self, related_type, preference_value_id=None, inherited_preference_value_id=None
    ):
        """Get the tax-lot depletion-method preference master (JSON structure).

        Args:
            related_type: Related entity type (e.g. "Portfolio", "Account")
            preference_value_id: Optional preference value ID (``preferenceValueId``)
            inherited_preference_value_id: Optional inherited value ID

        Returns:
            dict: Master preference structure
        """
        params = {}
        if preference_value_id is not None:
            params["preferenceValueId"] = preference_value_id
        if inherited_preference_value_id is not None:
            params["inheritedPreferenceValueId"] = inherited_preference_value_id
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/{related_type}"
            f"/taxLotDepletionMethodPreference/Master",
            params=params,
        )
        return res.json()

    def get_money_market_allocation_preference(self, related_type, related_type_id):
        """Get money-market allocation preference values.

        Args:
            related_type: Related entity type (e.g. "Portfolio", "Account")
            related_type_id: Related entity ID

        Returns:
            dict: Allocation preference values
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/MoneyMarketPreference/Allocation"
            f"/{related_type}/{related_type_id}"
        )
        return res.json()

    def get_money_market_allocation_preference_master(self, related_type):
        """Get the money-market allocation preference master (JSON structure).

        Args:
            related_type: Related entity type (e.g. "Portfolio", "Account")

        Returns:
            dict: Master allocation preference structure
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/MoneyMarketPreference/Allocation"
            f"/{related_type}/Master"
        )
        return res.json()

    def get_money_market_fund_preference(self, related_type, related_type_id):
        """Get money-market fund preference values.

        Args:
            related_type: Related entity type (e.g. "Portfolio", "Account")
            related_type_id: Related entity ID

        Returns:
            dict: Fund preference values
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/MoneyMarketPreference/Fund"
            f"/{related_type}/{related_type_id}"
        )
        return res.json()

    def get_money_market_fund_preference_master(self, related_type):
        """Get the money-market fund preference master (JSON structure).

        Args:
            related_type: Related entity type (e.g. "Portfolio", "Account")

        Returns:
            dict: Master fund preference structure
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/MoneyMarketPreference/Fund"
            f"/{related_type}/Master"
        )
        return res.json()

    def get_money_market_fund_preference_by_security(self, security_id):
        """Get money-market fund preferences by security ID.

        Args:
            security_id: Security ID

        Returns:
            dict: Fund preferences for the security
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/MoneyMarketPreference/Fund"
            f"/Security/{security_id}"
        )
        return res.json()

    # --- Preference writes (mutating) --------------------------------------------

    def set_account_preferences(self, preferences):
        """Set account preferences.

        Args:
            preferences: Account-preferences DTO (request body)

        Returns:
            dict: Result
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/AccountPreferences",
            requests.post,
            json=preferences,
        )
        return res.json()

    def update_security_preference_batch_job(self, payload):
        """Update the batch job for a security-preference change.

        Args:
            payload: Batch-job DTO (request body)

        Returns:
            dict: Result
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/UpdateBatchJobForSecurityPreferenceChange",
            requests.put,
            json=payload,
        )
        return res.json()

    def update_money_market_allocation_preference(self, payload):
        """Update money-market allocation preference.

        Args:
            payload: Allocation-preference DTO (request body)

        Returns:
            dict: Result
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/UpdateMoneyMarketAllocationPreference",
            requests.put,
            json=payload,
        )
        return res.json()

    def update_money_market_fund_preference(self, payload):
        """Update money-market fund preference.

        Args:
            payload: Fund-preference DTO (request body)

        Returns:
            dict: Result
        """
        res = self.api_request(
            f"{self.base_url_v2}/Preference/Preference/UpdateMoneyMarketFundPreference",
            requests.put,
            json=payload,
        )
        return res.json()

    # --- Configuration / FeatureFlags / BusinessDayRules -------------------------

    def get_configuration(self, config_id):
        """Get a configuration by ID.

        Args:
            config_id: Configuration ID

        Returns:
            dict: Configuration
        """
        res = self.api_request(f"{self.base_url_v2}/Configuration/{config_id}")
        return res.json()

    def delete_configuration(self, config_id):
        """Delete a configuration by ID (mutating).

        Args:
            config_id: Configuration ID
        """
        res = self.api_request(f"{self.base_url_v2}/Configuration/{config_id}", requests.delete)
        return res.json()

    def get_feature_flag(self, feature_flag_name):
        """Get the value of a feature flag.

        Args:
            feature_flag_name: Feature-flag name

        Returns:
            dict: Feature-flag value
        """
        res = self.api_request(f"{self.base_url_v2}/FeatureFlags/{feature_flag_name}")
        return res.json()

    def get_previous_business_day(self, reference_date):
        """Get the previous business day relative to a reference date.

        Args:
            reference_date: Reference date (ISO YYYY-MM-DD; maps to ``referenceDate``)

        Returns:
            dict | str: Previous business day
        """
        res = self.api_request(
            f"{self.base_url_v2}/BusinessDayRules/PreviousDay",
            params={"referenceDate": reference_date},
        )
        return res.json()

    # --- Set-aside cash (reads + mutating deletes) -------------------------------

    def get_set_aside_expiring_transactions(self, set_aside_id, set_aside_type=None):
        """Get the expiring transactions for a set-aside.

        Args:
            set_aside_id: Set-aside ID
            set_aside_type: Optional set-aside type (maps to ``setAsideType``)

        Returns:
            list: Expiring-transaction dicts
        """
        params = {}
        if set_aside_type is not None:
            params["setAsideType"] = set_aside_type
        res = self.api_request(
            f"{self.base_url_v2}/SetAsideCash/SetAsideExpiringTransactions/{set_aside_id}",
            params=params,
        )
        return res.json()

    def billing_set_aside_cash(self, payload):
        """Create billing set-aside cash (mutating).

        Args:
            payload: Billing set-aside DTO (request body)

        Returns:
            dict: Result
        """
        res = self.api_request(
            f"{self.base_url_v2}/SetAsideCash/BillingSetAsideCash", requests.post, json=payload
        )
        return res.json()

    def delete_account_set_aside_cash(self, payload):
        """Delete account set-aside cash (mutating).

        Args:
            payload: DTO identifying the account set-asides to delete (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/SetAsideCash/DeleteAccountSetAsideCash",
            requests.post,
            json=payload,
        )
        return res.json()

    def delete_portfolio_set_aside_cash(self, payload):
        """Delete portfolio set-aside cash (mutating).

        Args:
            payload: DTO identifying the portfolio set-asides to delete (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/SetAsideCash/DeletePortfolioSetAsideCash",
            requests.post,
            json=payload,
        )
        return res.json()

    # =========================================================================
    # Data-management CRUD / actions (v2). Account, portfolio, and model data
    # operations (no trade execution/approval). POST-with-body "list"/"status"
    # endpoints are filtered reads; the rest are mutating and are covered by
    # mocked unit tests only.
    # =========================================================================

    # --- Account filtered list + actions ---

    def list_accounts(self, body=None, filter_id=None, portfolio_id=None, limit=None, offset=None):
        """List accounts via the v2 POST-body filtered endpoint.

        Args:
            body: Optional filter DTO (request body)
            filter_id: Optional filter ID (``filterId``)
            portfolio_id: Optional portfolio filter (``portfolioId``)
            limit / offset: Optional paging window

        Returns:
            list | dict: Accounts
        """
        params = {}
        for key, val in (
            ("filterId", filter_id),
            ("portfolioId", portfolio_id),
            ("limit", limit),
            ("offset", offset),
        ):
            if val is not None:
                params[key] = val
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/list", requests.post, json=body, params=params
        )
        return res.json()

    def update_account_details(self, account_id, details, with_reverse_sync=None):
        """Update an account's details (mutating).

        Args:
            account_id: Account ID
            details: Account-details DTO (request body)
            with_reverse_sync: Optional bool (maps to ``withReverseSync``)

        Returns:
            dict: Updated account
        """
        params = {}
        if with_reverse_sync is not None:
            params["withReverseSync"] = str(with_reverse_sync).lower()
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/{account_id}/Details",
            requests.put,
            json=details,
            params=params,
        )
        return res.json()

    def set_account_trade_block(self, payload):
        """Set the trade-block state on accounts (mutating).

        Args:
            payload: Trade-block DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/action/setAccountTradeBlock",
            requests.put,
            json=payload,
        )
        return res.json()

    def expire_account_set_asides(self, payload):
        """Expire account set-asides (mutating).

        Args:
            payload: DTO identifying the set-asides to expire (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/expireAccountSetAsides",
            requests.put,
            json=payload,
        )
        return res.json()

    def set_account_tags(self, payload):
        """Set tags on accounts (mutating).

        Args:
            payload: Account-tags DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/Tags", requests.put, json=payload
        )
        return res.json()

    def update_restricted_plan(self, restricted_plan_id, payload):
        """Update a restricted plan (mutating).

        Args:
            restricted_plan_id: Restricted-plan ID
            payload: Restricted-plan DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/RestrictedPlan/{restricted_plan_id}",
            requests.put,
            json=payload,
        )
        return res.json()

    def set_accounts_do_not_trade_reverse_sync(self, payload):
        """Reverse-sync the do-not-trade flag for accounts (mutating).

        Args:
            payload: DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/Accounts/donottradereversesync",
            requests.post,
            json=payload,
        )
        return res.json()

    # --- Astro account actions ---

    def start_astro_accounts(self, payload):
        """Start an Astro batch for accounts (mutating).

        Args:
            payload: Astro-start DTO (request body)

        Returns:
            dict: Batch start result
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/AstroAccounts/Start", requests.post, json=payload
        )
        return res.json()

    def get_astro_accounts_status_count(self, payload, unique_batch_identifier=None):
        """Get the Astro account status count for a batch (POST-body read).

        Args:
            payload: Status-request DTO (request body)
            unique_batch_identifier: Optional batch identifier (``uniqueBatchIdentifier``)

        Returns:
            dict: Status count
        """
        params = {}
        if unique_batch_identifier is not None:
            params["uniqueBatchIdentifier"] = unique_batch_identifier
        res = self.api_request(
            f"{self.base_url_v2}/Account/AstroAccounts/Status/Count",
            requests.post,
            json=payload,
            params=params,
        )
        return res.json()

    def get_astro_accounts_status_detail(self, payload, unique_batch_identifier=None):
        """Get the Astro account status detail for a batch (POST-body read).

        Args:
            payload: Status-request DTO (request body)
            unique_batch_identifier: Optional batch identifier (``uniqueBatchIdentifier``)

        Returns:
            list | dict: Status detail
        """
        params = {}
        if unique_batch_identifier is not None:
            params["uniqueBatchIdentifier"] = unique_batch_identifier
        res = self.api_request(
            f"{self.base_url_v2}/Account/AstroAccounts/Status/Detail",
            requests.post,
            json=payload,
            params=params,
        )
        return res.json()

    def withdraw_astro_cash(self, payload):
        """Withdraw cash via Astro (mutating).

        Args:
            payload: Withdraw-cash DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/AstroAccounts/WithdrawCash", requests.post, json=payload
        )
        return res.json()

    def delete_astro_securities_restrictions(self, account_id, payload):
        """Delete Astro security restrictions for an account (mutating).

        Args:
            account_id: Account ID
            payload: DTO identifying restrictions to delete (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/AstroAccounts/{account_id}/DeleteSecuritiesRestrictions",
            requests.post,
            json=payload,
        )
        return res.json()

    def save_astro_investor_preferences(self, account_id, payload):
        """Save Astro investor preferences for an account (mutating).

        Args:
            account_id: Account ID
            payload: Investor-preferences DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Account/AstroAccounts/preference"
            f"/SaveInvestorPreferences/{account_id}",
            requests.put,
            json=payload,
        )
        return res.json()

    # --- Portfolio actions + filtered list ---

    def list_portfolios(self, body=None, filter_id=None, limit=None, offset=None):
        """List portfolios via the v2 POST-body filtered endpoint.

        Args:
            body: Optional filter DTO (request body)
            filter_id: Optional filter ID (``filterId``)
            limit / offset: Optional paging window

        Returns:
            list | dict: Portfolios
        """
        params = {}
        for key, val in (("filterId", filter_id), ("limit", limit), ("offset", offset)):
            if val is not None:
                params[key] = val
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/list", requests.post, json=body, params=params
        )
        return res.json()

    def get_portfolios_by_external_account_ids(self, payload):
        """Get portfolio info by a list of external account IDs (POST-body read).

        Args:
            payload: List of external account ID DTOs (request body)

        Returns:
            list: Portfolio-info dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/PortfolioInfoByExternalAccountIdList",
            requests.post,
            json=payload,
        )
        return res.json()

    def assign_model_to_portfolios(self, payload):
        """Assign a model to portfolios (mutating).

        Args:
            payload: Model-assignment DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/action/assignModel",
            requests.put,
            json=payload,
        )
        return res.json()

    def set_portfolio_trade_block(self, payload):
        """Set the trade-block state on portfolios (mutating).

        Args:
            payload: Trade-block DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/action/setPortfolioTradeBlock",
            requests.put,
            json=payload,
        )
        return res.json()

    def reverse_sync_portfolio_assignments(self, payload):
        """Reverse-sync portfolio model assignments (mutating).

        Args:
            payload: DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Portfolios/Action/ReverseSyncPortfolioAssignments",
            requests.post,
            json=payload,
        )
        return res.json()

    def get_sleeve_strategies_by_firm_ids(self, payload):
        """Get sleeve strategies for a list of firm IDs (POST-body read).

        Args:
            payload: List of firm IDs (request body)

        Returns:
            list: Sleeve-strategy dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Portfolio/Sleeves/SleeveStrategiesByFirmIds",
            requests.post,
            json=payload,
        )
        return res.json()

    # --- Model creates / actions ---

    def create_model_from_aggs(self, payload):
        """Create a model from model aggregates (mutating).

        Args:
            payload: Model-aggregates DTO (request body)

        Returns:
            dict: Created model
        """
        res = self.api_request(
            f"{self.base_url_v2}/Model/CreateFromModelAggs", requests.post, json=payload
        )
        return res.json()

    def create_sma_model(self, payload):
        """Create an SMA model (mutating).

        Args:
            payload: SMA-model DTO (request body)

        Returns:
            dict: Created model
        """
        res = self.api_request(f"{self.base_url_v2}/Model/SMA", requests.post, json=payload)
        return res.json()

    def create_ticker_based_model(self, payload):
        """Create a ticker-based model (mutating).

        Args:
            payload: Ticker-based-model DTO (request body)

        Returns:
            dict: Created model
        """
        res = self.api_request(
            f"{self.base_url_v2}/Model/TickerBasedModel", requests.post, json=payload
        )
        return res.json()

    def get_community_models_by_list(self, payload):
        """Get community models for a list of identifiers (POST-body read).

        Args:
            payload: List of identifiers (request body)

        Returns:
            list: Community-model dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Model/GetCommunityModelsByList", requests.post, json=payload
        )
        return res.json()

    def trigger_security_set_reverse_sync(self, payload):
        """Trigger a security-set reverse sync (mutating).

        Args:
            payload: DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Model/Action/TriggerSecuritySetReverseSync",
            requests.post,
            json=payload,
        )
        return res.json()

    # =========================================================================
    # Import / export / extracts (v2). Reads + import-pipeline actions. Mutating
    # endpoints are covered by mocked unit tests only.
    # =========================================================================

    # --- CustomImports reads ---

    def get_custom_import_history(self):
        """Get the custom-import instance history.

        Returns:
            list: Import-instance dicts
        """
        res = self.api_request(f"{self.base_url_v2}/CustomImports/Instances/History")
        return res.json()

    def get_custom_import_staged_data(self, instance_id):
        """Get staged data for a custom-import instance.

        Args:
            instance_id: Import-instance ID

        Returns:
            list | dict: Staged data
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Instances/StagedData/{instance_id}"
        )
        return res.json()

    def get_custom_import_templates(self):
        """Get the custom-import templates.

        Returns:
            list: Template dicts
        """
        res = self.api_request(f"{self.base_url_v2}/CustomImports/Templates")
        return res.json()

    def get_custom_import_template_definition(self, template_id):
        """Get a custom-import template definition.

        Args:
            template_id: Template ID

        Returns:
            dict: Template definition
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Templates/Definition/{template_id}"
        )
        return res.json()

    def get_custom_import_template_definition_by_instance(self, instance_id):
        """Get a custom-import template definition by instance ID.

        Args:
            instance_id: Import-instance ID

        Returns:
            dict: Template definition
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Templates/DefinitionByInstanceId/{instance_id}"
        )
        return res.json()

    # --- CustomImports writes (mutating) ---

    def custom_import_add_row(self, instance_id, row):
        """Add a row to a custom-import instance (mutating).

        Args:
            instance_id: Import-instance ID
            row: Row DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Instances/AddRow/{instance_id}",
            requests.post,
            json=row,
        )
        return res.json()

    def custom_import_update_row(self, instance_id, row):
        """Update a row in a custom-import instance (mutating).

        Args:
            instance_id: Import-instance ID
            row: Row DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Instances/UpdateRow/{instance_id}",
            requests.post,
            json=row,
        )
        return res.json()

    def custom_import_validate_rows(self, instance_id, rows):
        """Validate rows in a custom-import instance.

        Args:
            instance_id: Import-instance ID
            rows: Rows DTO (request body)

        Returns:
            dict: Validation result
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Instances/ValidateRows/{instance_id}",
            requests.post,
            json=rows,
        )
        return res.json()

    def custom_import_generate_override(self, instance_id):
        """Generate an override for a custom-import instance (mutating).

        Args:
            instance_id: Import-instance ID
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Instances/GenerateOverride/{instance_id}",
            requests.post,
        )
        return res.json()

    def custom_import_upload_file(self, payload):
        """Upload a custom-import file (mutating).

        Args:
            payload: Upload DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Instances/UploadFile", requests.post, json=payload
        )
        return res.json()

    def custom_import_reupload_file(self, payload):
        """Re-upload a custom-import file (mutating).

        Args:
            payload: Upload DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Instances/ReuploadFile", requests.post, json=payload
        )
        return res.json()

    def download_custom_import_template(self, template_id):
        """Download a custom-import template.

        Args:
            template_id: Template ID

        Returns:
            dict | list: Template download payload
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Templates/Download/{template_id}", requests.post
        )
        return res.json()

    def set_custom_import_template_favorite(self, payload):
        """Set a custom-import template as the user's favorite (mutating).

        Args:
            payload: Favorite DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Templates/SetUserFavorite",
            requests.post,
            json=payload,
        )
        return res.json()

    def abandon_custom_import(self, instance_id):
        """Abandon a custom-import instance (mutating).

        Args:
            instance_id: Import-instance ID
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Instances/Abandon/{instance_id}", requests.put
        )
        return res.json()

    def apply_custom_import(self, instance_id):
        """Apply a custom-import instance (mutating).

        Args:
            instance_id: Import-instance ID
        """
        res = self.api_request(
            f"{self.base_url_v2}/CustomImports/Instances/Apply/{instance_id}", requests.put
        )
        return res.json()

    # --- DataImport reads ---

    def get_avg_import_duration(self, import_type=None, record_count_to_average=None):
        """Get the average import duration.

        Args:
            import_type: Optional import type (``importType``)
            record_count_to_average: Optional record count (``recordCountToAverage``)

        Returns:
            dict: Average-duration info
        """
        params = {}
        if import_type is not None:
            params["importType"] = import_type
        if record_count_to_average is not None:
            params["recordCountToAverage"] = record_count_to_average
        res = self.api_request(
            f"{self.base_url_v2}/DataImport/Action/AvgImportDuration", params=params
        )
        return res.json()

    def get_last_import_status_info(self):
        """Get the last import status info.

        Returns:
            dict: Last-import status info
        """
        res = self.api_request(f"{self.base_url_v2}/DataImport/Action/LastImportStatusInfo")
        return res.json()

    def get_data_imports_by_requested_by(self, requested_by_id):
        """Get data imports requested by a given user.

        Args:
            requested_by_id: User ID

        Returns:
            list: Import dicts
        """
        res = self.api_request(f"{self.base_url_v2}/DataImport/ByRequestedById/{requested_by_id}")
        return res.json()

    def get_import_log_history(self, from_date=None, to_date=None):
        """Get the import-log history.

        Args:
            from_date / to_date: Optional ISO date window (``fromDate`` / ``toDate``)

        Returns:
            list: Import-log dicts
        """
        params = {}
        if from_date is not None:
            params["fromDate"] = from_date
        if to_date is not None:
            params["toDate"] = to_date
        res = self.api_request(f"{self.base_url_v2}/DataImport/ImportLogHistory", params=params)
        return res.json()

    def get_reverse_sync_log_errors(self, import_id):
        """Get reverse-sync log errors for an import.

        Args:
            import_id: Import ID

        Returns:
            list: Error dicts
        """
        res = self.api_request(f"{self.base_url_v2}/DataImport/ReverseSyncLogErrors/{import_id}")
        return res.json()

    # --- DataImport actions / export (mutating) ---

    def request_import(self, payload):
        """Request a data import (mutating).

        Args:
            payload: Import-request DTO (request body)

        Returns:
            dict: Request result
        """
        res = self.api_request(
            f"{self.base_url_v2}/DataImport/Action/RequestImport", requests.post, json=payload
        )
        return res.json()

    def sync_accounts(self, payload):
        """Sync accounts (mutating).

        Args:
            payload: Sync DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/DataImport/Action/SyncAccounts", requests.post, json=payload
        )
        return res.json()

    def sync_accounts_by_portfolio(self, payload):
        """Sync accounts by portfolio (mutating).

        Args:
            payload: Sync DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/DataImport/Action/SyncAccountsByPortfolio",
            requests.post,
            json=payload,
        )
        return res.json()

    def resync_import_errored_accounts(self):
        """Resync accounts that errored during import (mutating)."""
        res = self.api_request(
            f"{self.base_url_v2}/DataImport/Action/ResyncImportErroredAccounts", requests.post
        )
        return res.json()

    def export_import_history(self, payload):
        """Export import history (POST-body export).

        Args:
            payload: Export-request DTO (request body)

        Returns:
            dict | list: Export result
        """
        res = self.api_request(
            f"{self.base_url_v2}/DataImport/Export/ImportHistory", requests.post, json=payload
        )
        return res.json()

    def export_reverse_sync_history(self, payload):
        """Export reverse-sync history (POST-body export).

        Args:
            payload: Export-request DTO (request body)

        Returns:
            dict | list: Export result
        """
        res = self.api_request(
            f"{self.base_url_v2}/DataImport/Export/ReverseSyncHistory", requests.post, json=payload
        )
        return res.json()

    # --- Extracts ---

    def get_extracts(self, extract_type):
        """Get extracts of a given type.

        Args:
            extract_type: Extract type

        Returns:
            list | dict: Extract data
        """
        res = self.api_request(f"{self.base_url_v2}/Extracts/{extract_type}")
        return res.json()

    def create_extract(self, extract_type, when=None):
        """Create/schedule an extract job (mutating).

        Args:
            extract_type: Extract type
            when: Optional schedule value (sent as the ``X-ExtractJob-When`` header)

        Returns:
            dict: Extract-job result
        """
        headers = {}
        if when is not None:
            headers["X-ExtractJob-When"] = when
        res = self.api_request(
            f"{self.base_url_v2}/Extracts/{extract_type}", requests.post, headers=headers
        )
        return res.json()

    def delete_extract(self, extract_type, reason=None):
        """Delete extracts of a given type (mutating).

        Args:
            extract_type: Extract type
            reason: Optional reason (sent as the ``X-ExtractJob-Reason`` header)
        """
        headers = {}
        if reason is not None:
            headers["X-ExtractJob-Reason"] = reason
        res = self.api_request(
            f"{self.base_url_v2}/Extracts/{extract_type}", requests.delete, headers=headers
        )
        return res.json()

    def delete_extract_job(self, job_id, reason=None):
        """Delete an extract job (mutating).

        Args:
            job_id: Extract-job ID
            reason: Optional reason (maps to ``reason``)
        """
        params = {}
        if reason is not None:
            params["reason"] = reason
        res = self.api_request(
            f"{self.base_url_v2}/Extracts/job/{job_id}", requests.delete, params=params
        )
        return res.json()

    # =========================================================================
    # Org / workflow / reference (v2). Search, firm/team/user, admin custodian &
    # token, OrionConnect lookups, and the v2 Workflow surface. Reads plus a few
    # CRUD writes (covered by mocked unit tests only).
    # =========================================================================

    # --- Search ---

    def account_search(self, search, limit=None, offset=None):
        """Search accounts (v2 UI search).

        Args:
            search: Search string
            limit / offset: Optional paging window

        Returns:
            list: Account search results
        """
        params = {"search": search}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        res = self.api_request(f"{self.base_url_v2}/AccountSearch/AccountSearchList", params=params)
        return res.json()

    def security_search(
        self, search, skip=None, take=None, external_firm_id=None, external_account_id=None
    ):
        """Search securities (v2 UI search).

        Note:
            Eclipse requires an external firm/account context — pass
            ``external_firm_id`` and ``external_account_id``. A bare ``search``
            returns ``400 PortfolioNotFound``. For a context-free security lookup
            use :meth:`EclipseV1.search_securities` instead.

        Args:
            search: Search string
            skip / take: Optional paging window
            external_firm_id: External firm ID (``externalFirmId``)
            external_account_id: External account ID (``externalAccountId``)

        Returns:
            list: Security search results
        """
        params = {"search": search}
        for key, val in (
            ("skip", skip),
            ("take", take),
            ("externalFirmId", external_firm_id),
            ("externalAccountId", external_account_id),
        ):
            if val is not None:
                params[key] = val
        res = self.api_request(
            f"{self.base_url_v2}/SecuritySearch/SecuritySearchList", params=params
        )
        return res.json()

    def global_search(self, search=None, name=None, status=None, include_value=None, limit=None):
        """Global search across Eclipse entities (v2).

        Args:
            search: Optional search string
            name: Optional name filter
            status: Optional status filter
            include_value: Optional bool (maps to ``includeValue``)
            limit: Optional max results

        Returns:
            list | dict: Global search results
        """
        params = {}
        if search is not None:
            params["search"] = search
        if name is not None:
            params["name"] = name
        if status is not None:
            params["status"] = status
        if include_value is not None:
            params["includeValue"] = str(include_value).lower()
        if limit is not None:
            params["limit"] = limit
        res = self.api_request(f"{self.base_url_v2}/GlobalSearch/GlobalSearchList", params=params)
        return res.json()

    # --- Firm ---

    def get_firm_types(self):
        """Get the firm types.

        Returns:
            list: Firm-type dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Firm/FirmTypes")
        return res.json()

    def get_eclipse_firms_by_al_client_id(self, al_client_id):
        """Get Eclipse firms by AL client ID.

        Args:
            al_client_id: AL client ID

        Returns:
            list: Firm dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Firm/GetEclipseFirmsByAlClientId/{al_client_id}"
        )
        return res.json()

    def get_firm_logo(self):
        """Get the firm logo.

        Returns:
            dict: Firm logo
        """
        res = self.api_request(f"{self.base_url_v2}/Firm/Logo")
        return res.json()

    def get_firm_logo_base64(self):
        """Get the firm logo as base64.

        Returns:
            dict | str: Base64 logo
        """
        res = self.api_request(f"{self.base_url_v2}/Firm/Logo/Base64")
        return res.json()

    # --- Team / ServiceTeams / User ---

    def get_teams(self, external_id=None):
        """Get teams.

        Args:
            external_id: Optional external ID filter (maps to ``externalId``)

        Returns:
            list: Team dicts
        """
        params = {}
        if external_id is not None:
            params["externalId"] = external_id
        res = self.api_request(f"{self.base_url_v2}/Team/Team/GetTeams", params=params)
        return res.json()

    def get_service_team(self):
        """Get the service team.

        Returns:
            dict: Service-team info
        """
        res = self.api_request(f"{self.base_url_v2}/ServiceTeams/GetServiceTeam")
        return res.json()

    def get_service_teams(self, service_type=None):
        """Get service teams.

        Args:
            service_type: Optional service-type filter (maps to ``serviceType``)

        Returns:
            list: Service-team dicts
        """
        params = {}
        if service_type is not None:
            params["serviceType"] = service_type
        res = self.api_request(f"{self.base_url_v2}/ServiceTeams/GetServiceTeams", params=params)
        return res.json()

    def get_advisor_number(self):
        """Get the advisor number.

        Returns:
            dict | str: Advisor number
        """
        res = self.api_request(f"{self.base_url_v2}/ServiceTeams/GetAdvisorNumber")
        return res.json()

    def get_user(self, user_id):
        """Get a user by ID.

        Args:
            user_id: User ID

        Returns:
            dict: User
        """
        res = self.api_request(f"{self.base_url_v2}/User/{user_id}")
        return res.json()

    # --- Admin: token + custodian/execution reference ---

    def get_token_environment(self):
        """Get the token environment.

        Returns:
            dict | str: Environment
        """
        res = self.api_request(f"{self.base_url_v2}/Admin/Token/Environment")
        return res.json()

    def get_token_info(self):
        """Get token info for the authenticated session.

        Returns:
            dict: Token info
        """
        res = self.api_request(f"{self.base_url_v2}/Admin/Token/Info")
        return res.json()

    def get_execution_destination_types(self):
        """Get execution-destination types.

        Returns:
            list: Destination-type dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Admin/Custodian/GetExecutionDestinationTypes")
        return res.json()

    def get_all_executing_destinations(self):
        """Get all executing destinations.

        Returns:
            list: Destination dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Admin/Custodian/GetAllExecutingDestinations")
        return res.json()

    def get_allocation_instructions(self):
        """Get allocation instructions.

        Returns:
            list: Allocation-instruction dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Admin/Custodian/GetAllocationInstructions")
        return res.json()

    def get_custodian_execution_settings(self, custodian_id):
        """Get execution settings for a custodian.

        Args:
            custodian_id: Custodian ID (maps to ``custodianId``)

        Returns:
            dict: Execution settings
        """
        res = self.api_request(
            f"{self.base_url_v2}/Admin/Custodian/CustodianExecutionSettings",
            params={"custodianId": custodian_id},
        )
        return res.json()

    def get_executing_destinations_for_security_type(self, security_type_id):
        """Get executing destinations (with type) for a security type.

        Args:
            security_type_id: Security-type ID (maps to ``securityTypeId``)

        Returns:
            list: Destination dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Admin/Custodian/GetExecutingDestinationsWithTypeForSecurityType",
            params={"securityTypeId": security_type_id},
        )
        return res.json()

    def get_outsource_trade_execution_firm(self, custodian_id):
        """Get the outsource trade-execution firm for a custodian.

        Args:
            custodian_id: Custodian ID (maps to ``custodianId``)

        Returns:
            dict: Outsource-firm info
        """
        res = self.api_request(
            f"{self.base_url_v2}/Admin/Custodian/GetOutsourceTradeExecutionFirm",
            params={"custodianId": custodian_id},
        )
        return res.json()

    def get_custodian_algo_instructions(self, custodian_id):
        """Get custodian algo instructions.

        Args:
            custodian_id: Custodian ID

        Returns:
            list: Algo-instruction dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/Admin/Custodian/{custodian_id}/CustodianAlgoInstructions"
        )
        return res.json()

    def get_trade_execution_allocation_types(self):
        """Get trade-execution allocation types.

        Returns:
            list: Allocation-type dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Admin/tradeExecutionTypes/allocation")
        return res.json()

    def get_trade_execution_types(self):
        """Get trade-execution types.

        Returns:
            list: Execution-type dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Admin/tradeExecutionTypes/execution")
        return res.json()

    # --- OrionConnect lookups ---

    def get_firm_entity_option_by_code(self, code):
        """Get a firm entity option by code.

        Args:
            code: Option code (maps to ``code``)

        Returns:
            dict: Firm-entity option
        """
        res = self.api_request(
            f"{self.base_url_v2}/OrionConnect/GetFirmEntityOptionByCode", params={"code": code}
        )
        return res.json()

    def get_product_classes(self):
        """Get OrionConnect product classes.

        Returns:
            list: Product-class dicts
        """
        res = self.api_request(f"{self.base_url_v2}/OrionConnect/GetProductClasses")
        return res.json()

    def get_risk_categories(self):
        """Get OrionConnect risk categories.

        Returns:
            list: Risk-category dicts
        """
        res = self.api_request(f"{self.base_url_v2}/OrionConnect/GetRiskCategories")
        return res.json()

    # --- Workflow (reads + CRUD) ---

    def get_workflow_contexts(self):
        """Get workflow contexts.

        Returns:
            list: Workflow-context dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Workflow/contexts")
        return res.json()

    def get_workflow_context(self, context_id):
        """Get a workflow context by ID.

        Args:
            context_id: Workflow-context ID

        Returns:
            dict: Workflow context
        """
        res = self.api_request(f"{self.base_url_v2}/Workflow/contexts/{context_id}")
        return res.json()

    def create_workflow_context(self, context):
        """Create a workflow context (mutating).

        Args:
            context: Workflow-context DTO (request body)

        Returns:
            dict: Created context
        """
        res = self.api_request(f"{self.base_url_v2}/Workflow/contexts", requests.post, json=context)
        return res.json()

    def update_workflow_context(self, context_id, context):
        """Update a workflow context (mutating).

        Args:
            context_id: Workflow-context ID
            context: Workflow-context DTO (request body)

        Returns:
            dict: Updated context
        """
        res = self.api_request(
            f"{self.base_url_v2}/Workflow/contexts/{context_id}", requests.put, json=context
        )
        return res.json()

    def delete_workflow_context(self, context_id):
        """Delete a workflow context (mutating).

        Args:
            context_id: Workflow-context ID
        """
        res = self.api_request(
            f"{self.base_url_v2}/Workflow/contexts/{context_id}", requests.delete
        )
        return res.json()

    def get_workflow_tools(self):
        """Get workflow tools.

        Returns:
            list: Workflow-tool dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Workflow/tools")
        return res.json()

    def get_workflow_mcp_servers(self):
        """Get workflow MCP servers.

        Returns:
            list: MCP-server dicts
        """
        res = self.api_request(f"{self.base_url_v2}/Workflow/mcp-servers")
        return res.json()

    def get_workflow_mcp_server(self, server_id):
        """Get a workflow MCP server by ID.

        Args:
            server_id: MCP-server ID

        Returns:
            dict: MCP server
        """
        res = self.api_request(f"{self.base_url_v2}/Workflow/mcp-servers/{server_id}")
        return res.json()

    # =========================================================================
    # Trade-block restriction metadata + reference misc (v2). Trade BLOCKS here
    # are do-not-trade restrictions / reasons (config), NOT trade approval or
    # execution. Plus security price changes, compare tool, data errors,
    # communities, preference audit. Writes covered by mocked unit tests only.
    # =========================================================================

    # --- TradeBlockReasons (restriction reason config) ---

    def get_editable_trade_block_reasons(self):
        """Get the editable trade-block reasons.

        Returns:
            list: Trade-block-reason dicts
        """
        res = self.api_request(f"{self.base_url_v2}/TradeBlockReasons/Editable")
        return res.json()

    def get_trade_block_reason_role_permissions(self, reason_id):
        """Get role permissions for a trade-block reason.

        Args:
            reason_id: Trade-block-reason ID

        Returns:
            list: Role-permission dicts
        """
        res = self.api_request(f"{self.base_url_v2}/TradeBlockReasons/{reason_id}/RolePermissions")
        return res.json()

    def get_trade_block_reason_permissions_by_role(self, role_id):
        """Get trade-block-reason permissions for a role.

        Args:
            role_id: Role ID

        Returns:
            list: Permission dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockReasons/TradeBlockReasonPermissionsByRole/{role_id}"
        )
        return res.json()

    def get_trade_block_reason_permissions_by_global_ids(self, global_ids):
        """Get trade-block-reason permissions for a list of global IDs (POST-body read).

        Args:
            global_ids: List of global IDs (request body)

        Returns:
            list: Permission dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockReasons/TradeBlockReasonsPermissionByGlobalIds",
            requests.post,
            json=global_ids,
        )
        return res.json()

    def add_trade_block_reason_by_name(self, payload):
        """Add a trade-block reason by name (mutating).

        Args:
            payload: Trade-block-reason DTO (request body)

        Returns:
            dict: Created reason
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockReasons/AddByName", requests.post, json=payload
        )
        return res.json()

    def delete_trade_block_reason(self, reason_id):
        """Delete a trade-block reason (mutating).

        Args:
            reason_id: Trade-block-reason ID
        """
        res = self.api_request(f"{self.base_url_v2}/TradeBlockReasons/{reason_id}", requests.delete)
        return res.json()

    def set_trade_block_reason_role_permissions(self, reason_id, payload):
        """Set role permissions for a trade-block reason (mutating).

        Args:
            reason_id: Trade-block-reason ID
            payload: Role-permissions DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockReasons/{reason_id}/RolePermissions",
            requests.put,
            json=payload,
        )
        return res.json()

    def set_trade_block_reason_permissions_by_role(self, role_id, payload):
        """Set trade-block-reason permissions for a role (mutating).

        Args:
            role_id: Role ID
            payload: Permissions DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockReasons/TradeBlockReasonPermissionsByRole/{role_id}",
            requests.put,
            json=payload,
        )
        return res.json()

    # --- TradeBlockDetails (restriction records) ---

    def get_trade_block_details_history(
        self, related_type, related_type_id, start_date=None, end_date=None
    ):
        """Get trade-block-detail history for an entity.

        Args:
            related_type: Related entity type
            related_type_id: Related entity ID
            start_date / end_date: Optional ISO date window

        Returns:
            list: History dicts
        """
        params = {}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockDetails/History/{related_type}/{related_type_id}",
            params=params,
        )
        return res.json()

    def get_trade_block_details_related_entities(self, entity_id, entity_type):
        """Get entities related to a trade-block-detail entity.

        Args:
            entity_id: Entity ID (maps to ``entityId``)
            entity_type: Entity type (maps to ``entityType``)

        Returns:
            list: Related-entity dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockDetails/RelatedEntities",
            params={"entityId": entity_id, "entityType": entity_type},
        )
        return res.json()

    def add_trade_block_details(self, payload):
        """Add trade-block details (mutating).

        Args:
            payload: List of trade-block-detail DTOs (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockDetails/AddList", requests.post, json=payload
        )
        return res.json()

    def update_trade_block_details(self, payload):
        """Update trade-block details (mutating).

        Args:
            payload: List of trade-block-detail DTOs (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockDetails/UpdateList", requests.post, json=payload
        )
        return res.json()

    def delete_trade_block_details(self, payload):
        """Delete trade-block details (batch, mutating).

        Args:
            payload: List of trade-block-detail DTOs / IDs (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockDetails/DeleteList", requests.post, json=payload
        )
        return res.json()

    def add_manual_trade_block_detail(self, related_type, related_type_id, payload):
        """Add a manual trade-block detail for an entity (mutating).

        Args:
            related_type: Related entity type
            related_type_id: Related entity ID
            payload: Trade-block-detail DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockDetails/Manual/{related_type}/{related_type_id}",
            requests.post,
            json=payload,
        )
        return res.json()

    def add_fixed_income_trade_block_detail(self, related_type, payload):
        """Add a fixed-income trade-block detail (mutating).

        Args:
            related_type: Related entity type
            payload: Trade-block-detail DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockDetails/FixedIncome/{related_type}",
            requests.post,
            json=payload,
        )
        return res.json()

    def update_trade_block_detail(self, detail_id, payload):
        """Update a single trade-block detail (mutating).

        Args:
            detail_id: Trade-block-detail ID
            payload: Trade-block-detail DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockDetails/{detail_id}", requests.put, json=payload
        )
        return res.json()

    def delete_trade_block_detail(self, detail_id):
        """Delete a single trade-block detail (mutating).

        Args:
            detail_id: Trade-block-detail ID
        """
        res = self.api_request(f"{self.base_url_v2}/TradeBlockDetails/{detail_id}", requests.delete)
        return res.json()

    def delete_deletable_trade_block_details(self, entity_id, entity_type_id):
        """Delete the deletable trade-block details for an entity (mutating).

        Args:
            entity_id: Entity ID
            entity_type_id: Entity-type ID
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeBlockDetails/DeletableDetails/{entity_id}/{entity_type_id}",
            requests.delete,
        )
        return res.json()

    # --- SecurityPriceChanges ---

    def get_all_price_updates(self):
        """Get all security price updates.

        Returns:
            list: Price-update dicts
        """
        res = self.api_request(f"{self.base_url_v2}/SecurityPriceChanges/GetAllUpdates")
        return res.json()

    def get_todays_price_updates(self):
        """Get today's security price updates.

        Returns:
            list: Price-update dicts
        """
        res = self.api_request(f"{self.base_url_v2}/SecurityPriceChanges/GetTodaysUpdates")
        return res.json()

    def get_price_updates_for_day(self, payload):
        """Get security price updates for a specific day (POST-body read).

        Args:
            payload: Day-request DTO (request body)

        Returns:
            list: Price-update dicts
        """
        res = self.api_request(
            f"{self.base_url_v2}/SecurityPriceChanges/GetSpecificDayUpdates",
            requests.post,
            json=payload,
        )
        return res.json()

    # --- CompareTool ---

    def get_compare_tool_status(self, correlation_id):
        """Get the status of a compare-tool run.

        Args:
            correlation_id: Compare-tool correlation ID

        Returns:
            dict: Status
        """
        res = self.api_request(f"{self.base_url_v2}/CompareTool/Status/{correlation_id}")
        return res.json()

    def compare_trades(self, payload):
        """Run a trade comparison (POST-body).

        Args:
            payload: Compare-request DTO (request body)

        Returns:
            dict: Comparison result
        """
        res = self.api_request(
            f"{self.base_url_v2}/CompareTool/Trades", requests.post, json=payload
        )
        return res.json()

    # --- DataErrors ---

    def get_all_portfolio_account_errors(self):
        """Get all portfolio/account data errors.

        Returns:
            list: Error dicts
        """
        res = self.api_request(f"{self.base_url_v2}/DataErrors/GetAllPortfolioAccounts")
        return res.json()

    def get_all_portfolio_account_errors_count(self):
        """Get the count of portfolio/account data errors.

        Returns:
            int | dict: Error count
        """
        res = self.api_request(f"{self.base_url_v2}/DataErrors/GetAllPortfolioAccountsCount")
        return res.json()

    # --- Communities ---

    def get_community_trade_queue_details(self, trade_queue_id):
        """Get community trade-queue details.

        Args:
            trade_queue_id: Trade-queue ID

        Returns:
            dict: Trade-queue details
        """
        res = self.api_request(f"{self.base_url_v2}/Communities/tradeQueueDetails/{trade_queue_id}")
        return res.json()

    def validate_community_model_unassign(self, payload, apply_delete=None):
        """Validate (and optionally apply) a community-model unassign (mutating when applied).

        Args:
            payload: Validation DTO (request body)
            apply_delete: Optional bool (maps to ``applyDelete``)

        Returns:
            dict: Validation result
        """
        params = {}
        if apply_delete is not None:
            params["applyDelete"] = str(apply_delete).lower()
        res = self.api_request(
            f"{self.base_url_v2}/Communities/ModelUnAssignValidation",
            requests.post,
            json=payload,
            params=params,
        )
        return res.json()

    def sync_community_model(self, payload):
        """Sync a community model (mutating).

        Args:
            payload: Sync DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/Communities/SyncCommunityModel", requests.post, json=payload
        )
        return res.json()

    # --- PreferenceAuditHistory ---

    def get_money_market_preference_audit_history(self, start_date=None, end_date=None):
        """Get money-market preference audit history.

        Args:
            start_date / end_date: Optional ISO date window (``startDate`` / ``endDate``)

        Returns:
            list: Audit-history dicts
        """
        params = {}
        if start_date is not None:
            params["startDate"] = start_date
        if end_date is not None:
            params["endDate"] = end_date
        res = self.api_request(
            f"{self.base_url_v2}/PreferenceAuditHistory/MoneyMarket", params=params
        )
        return res.json()

    # --- SecuritySettingPreference + TradeAnalysisReport ---

    def set_security_setting_equivalents(self, related_type, payload):
        """Set security-setting equivalents for a related type (mutating).

        Args:
            related_type: Related entity type
            payload: Equivalents DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/SecuritySettingPreference/Equivalents/{related_type}",
            requests.post,
            json=payload,
        )
        return res.json()

    def upload_security_setting_equivalents(self, payload):
        """Upload security-setting equivalents (mutating).

        Args:
            payload: Upload DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/SecuritySettingPreference/Equivalents/Upload",
            requests.post,
            json=payload,
        )
        return res.json()

    def sync_trade_analysis_report(self, payload):
        """Sync the trade-analysis report (mutating).

        Args:
            payload: Sync DTO (request body)
        """
        res = self.api_request(
            f"{self.base_url_v2}/TradeAnalysisReport/SyncTradeAnalysisReport",
            requests.post,
            json=payload,
        )
        return res.json()


class Eclipse(EclipseBase):
    """Best-of-both Eclipse client composing :class:`EclipseV1` and :class:`EclipseV2`.

    Authenticates once and shares the single Eclipse token with both sub-clients,
    exposed as ``.v1`` and ``.v2`` so the version you are hitting is always
    explicit. Unknown attributes delegate to the complete v1 surface; methods
    that v2 serves better are overridden here to use ``.v2``. Each overridden
    method's docstring names the surface it uses.

    Example:
        >>> api = Eclipse(usr="user@example.com", pwd="password")
        >>> api.get_set_asides()        # firm-wide, via v2 (best)
        >>> api.get_account_holdings(1)  # via v1 (no v2 equivalent)
        >>> api.v2.get_set_asides(1114)  # explicit v2
        >>> api.v1.get_set_asides(1114)  # explicit v1 (raw per-account)
    """

    def __init__(
        self,
        usr=None,
        pwd=None,
        orion_token=None,
        eclipse_token=None,
        rate_limit=10,
        verify_ssl=True,
        ca_bundle=None,
    ):
        super().__init__(
            usr=usr,
            pwd=pwd,
            orion_token=orion_token,
            eclipse_token=eclipse_token,
            rate_limit=rate_limit,
            verify_ssl=verify_ssl,
            ca_bundle=ca_bundle,
        )
        # Share the single authenticated token with both sub-clients (no re-login).
        sub_kwargs = {
            "eclipse_token": self.eclipse_token,
            "rate_limit": rate_limit,
            "verify_ssl": verify_ssl,
            "ca_bundle": ca_bundle,
        }
        self.v1 = EclipseV1(**sub_kwargs)
        self.v2 = EclipseV2(**sub_kwargs)

    def __getattr__(self, name):
        """Delegate unknown attributes to the v1 surface, then the v2 surface.

        Only invoked for attributes not found normally (i.e. not defined on
        Eclipse/EclipseBase). v1 is tried first so existing behavior is unchanged
        on any name both surfaces define; v2-only methods (e.g. the Tactical /
        ESG / Trading-block reads) fall through to ``self.v2``. Guarded so
        attribute access during __init__ — before ``self.v1`` / ``self.v2`` exist —
        raises AttributeError instead of recursing.
        """
        try:
            v1 = self.__dict__["v1"]
            v2 = self.__dict__["v2"]
        except KeyError as e:
            raise AttributeError(name) from e
        try:
            return getattr(v1, name)
        except AttributeError:
            return getattr(v2, name)

    # --- v2-preferred overrides (documented best-of-both choices) ---------------

    def get_set_asides(self, account_id=None, active_only=False):
        """Set-asides via the v2 batch endpoint (best: firm-wide + set-aside id).

        Delegates to :meth:`EclipseV2.get_set_asides`. Use ``self.v1.get_set_asides``
        for the raw per-account v1 form.
        """
        return self.v2.get_set_asides(account_id=account_id, active_only=active_only)


class EclipseAPI(Eclipse):
    """Deprecated alias of :class:`Eclipse` (best-of-both client).

    Retained for backwards compatibility with pre-2.0 callers. Prefer
    :class:`Eclipse`, or :class:`EclipseV1` / :class:`EclipseV2` to target a
    specific API surface explicitly. Emits a ``DeprecationWarning`` on
    construction and will be removed in a future major release.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "EclipseAPI is deprecated; use Eclipse (best of v1+v2), or "
            "EclipseV1 / EclipseV2 to target a surface explicitly.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
