"""Integration tests that require real API credentials.

These tests are skipped if ECLIPSE_USER/ECLIPSE_PWD are not set.
To run: copy .env.example to .env, fill in credentials, then run pytest.
"""

import pytest


class TestEclipseAPI:
    def test_check_username(self, eclipse_client):
        """Test that we can authenticate and get username."""
        username = eclipse_client.check_username()
        assert username is not None
        assert len(username) > 0

    def test_get_all_accounts(self, eclipse_client):
        """Test that we can fetch accounts."""
        accounts = eclipse_client.get_all_accounts()
        assert isinstance(accounts, list)

    def test_get_portfolio(self, eclipse_client):
        """Test that we can fetch a portfolio by ID."""
        # Get list of accounts first to find a valid portfolio
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        # Try to get a portfolio - accounts have portfolioId
        portfolio_id = accounts[0].get("portfolioId")
        if not portfolio_id:
            pytest.skip("No portfolio ID found in accounts")

        portfolio = eclipse_client.get_portfolio(portfolio_id)
        assert "general" in portfolio
        assert "portfolioName" in portfolio["general"]

    def test_get_all_models(self, eclipse_client):
        """Test that we can fetch models."""
        models = eclipse_client.get_all_models()
        assert isinstance(models, list)

    def test_get_orders(self, eclipse_client):
        """Test that we can fetch orders."""
        orders = eclipse_client.get_orders()
        assert isinstance(orders, list)

    def test_get_all_portfolios(self, eclipse_client):
        """Test that we can fetch all portfolios with values."""
        portfolios = eclipse_client.get_all_portfolios(include_value=True)
        assert isinstance(portfolios, list)
        if portfolios:
            assert "id" in portfolios[0]

    def test_get_portfolio_accounts(self, eclipse_client):
        """Test that we can fetch accounts for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]
        accounts = eclipse_client.get_portfolio_accounts(portfolio_id)
        assert isinstance(accounts, list)

    def test_get_portfolio_holdings(self, eclipse_client):
        """Test that we can fetch holdings for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]
        holdings = eclipse_client.get_portfolio_holdings(portfolio_id)
        assert isinstance(holdings, list)

    def test_get_account_holdings(self, eclipse_client):
        """Test that we can fetch holdings for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]["id"]
        holdings = eclipse_client.get_account_holdings(account_id)
        assert isinstance(holdings, list)

    # High priority tests

    def test_get_account_details(self, eclipse_client):
        """Test that we can fetch details for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]["id"]
        details = eclipse_client.get_account_details(account_id)
        assert isinstance(details, dict)
        assert "id" in details or "accountNumber" in details

    def test_get_model(self, eclipse_client):
        """Test that we can fetch a model by ID."""
        models = eclipse_client.get_all_models()
        if not models:
            pytest.skip("No models available")

        model_id = models[0]["id"]
        model = eclipse_client.get_model(model_id)
        assert isinstance(model, dict)
        assert "id" in model

    def test_get_model_tolerance(self, eclipse_client):
        """Test that we can fetch model tolerance for a portfolio/account."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]
        accounts = eclipse_client.get_portfolio_accounts(portfolio_id)
        if not accounts:
            pytest.skip("No accounts in portfolio")

        account_id = accounts[0]["id"]
        tolerance = eclipse_client.get_model_tolerance(portfolio_id, account_id)
        assert isinstance(tolerance, (dict, list))

    def test_search_accounts_number_and_name(self, eclipse_client):
        """Test that we can search accounts by number and name."""
        # Get an existing account to use for search
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        # Use last 4 digits of account number and part of name
        acct = accounts[0]
        acct_num = acct.get("accountNumber", "")
        acct_name = acct.get("name", "")

        if not acct_num or not acct_name:
            pytest.skip("Account missing number or name")

        # Search using trailing digits and name portion
        acct_id, found_num = eclipse_client.search_accounts_number_and_name(
            acct_num[-4:], acct_name[:5]
        )
        assert isinstance(acct_id, int)
        assert isinstance(found_num, str)

    # Medium priority tests

    def test_get_model_allocations(self, eclipse_client):
        """Test that we can fetch model allocations."""
        models = eclipse_client.get_all_models()
        if not models:
            pytest.skip("No models available")

        model_id = models[0]["id"]
        allocations = eclipse_client.get_model_allocations(model_id)
        assert isinstance(allocations, (dict, list))

    def test_get_set_asides(self, eclipse_client):
        """Test that we can fetch set asides for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]["id"]
        set_asides = eclipse_client.get_set_asides(account_id)
        assert isinstance(set_asides, (dict, list))

    def test_get_all_security_sets(self, eclipse_client):
        """Test that we can fetch all security sets."""
        security_sets = eclipse_client.get_all_security_sets()
        assert isinstance(security_sets, list)

    # Additional read method tests

    def test_get_orders_pending(self, eclipse_client):
        """Test that we can fetch pending orders."""
        orders = eclipse_client.get_orders_pending()
        assert isinstance(orders, list)

    def test_get_all_account_details(self, eclipse_client):
        """Test that we can fetch details for all accounts."""
        details = eclipse_client.get_all_account_details()
        assert isinstance(details, list)

    def test_get_internal_account_id(self, eclipse_client):
        """Test that we can get internal account ID from account number."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        acct_num = accounts[0].get("accountNumber", "")
        if not acct_num:
            pytest.skip("Account missing number")

        internal_id = eclipse_client.get_internal_account_id(acct_num)
        assert isinstance(internal_id, int)

    def test_get_account_cash_available(self, eclipse_client):
        """Test that we can get available cash for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]["id"]
        cash = eclipse_client.get_account_cash_available(account_id)
        assert isinstance(cash, (int, float))

    def test_get_security_set(self, eclipse_client):
        """Test that we can fetch a security set by ID."""
        security_sets = eclipse_client.get_all_security_sets()
        if not security_sets:
            pytest.skip("No security sets available")

        set_id = security_sets[0]["id"]
        security_set = eclipse_client.get_security_set(set_id)
        assert isinstance(security_set, dict)

    def test_get_set_asides_v2(self, eclipse_client):
        """Test that we can fetch all set asides via v2 API."""
        from orionapi import AuthenticationError

        try:
            set_asides = eclipse_client.get_set_asides_v2()
            assert isinstance(set_asides, (dict, list))
        except AuthenticationError:
            pytest.skip("Insufficient privileges for v2 set asides endpoint")

    def test_search_securities(self, eclipse_client):
        """Test that we can search for securities."""
        results = eclipse_client.search_securities("AAPL", top=5)
        assert isinstance(results, list)
        # Should find at least one result
        assert len(results) > 0
        # Check structure
        assert "id" in results[0]
        assert "symbol" in results[0] or "name" in results[0]

    def test_get_security_by_ticker(self, eclipse_client):
        """Test that we can get a security by ticker."""
        sec = eclipse_client.get_security_by_ticker("AAPL")
        assert isinstance(sec, dict)
        assert "id" in sec
        assert sec.get("symbol", "").upper() == "AAPL"

    def test_parse_security_set_file(self, eclipse_client, tmp_path):
        """Test parsing a security set definition file."""
        # Create a test file
        test_file = tmp_path / "test_set.txt"
        test_file.write_text("""# Security Set: Test Set
# Description: A test security set

# Ticker  Lower%  Target%  Upper%
AAPL      5       10       20
MSFT      3       8        15
""")

        parsed = eclipse_client.parse_security_set_file(str(test_file))
        assert parsed["name"] == "Test Set"
        assert parsed["description"] == "A test security set"
        assert len(parsed["securities"]) == 2
        assert parsed["securities"][0]["ticker"] == "AAPL"
        assert parsed["securities"][0]["lower_bound"] == 5.0
        assert parsed["securities"][0]["target"] == 10.0
        assert parsed["securities"][0]["upper_bound"] == 20.0

    def test_convert_to_eclipse_tolerances(self, eclipse_client):
        """Test converting absolute bounds to Eclipse tolerance format."""
        securities = [{"ticker": "AAPL", "lower_bound": 5, "target": 10, "upper_bound": 20}]
        result = eclipse_client.convert_to_eclipse_tolerances(securities)
        assert len(result) == 1
        assert "id" in result[0]
        assert result[0]["targetPercent"] == 10
        # lower_tolerance = target - lower_bound = 10 - 5 = 5
        assert result[0]["lowerModelTolerancePercent"] == 5
        # upper_tolerance = upper_bound - target = 20 - 10 = 10
        assert result[0]["upperModelTolerancePercent"] == 10


class TestOrionAPI:
    def test_check_username(self, orion_client):
        """Test that we can authenticate and get username."""
        username = orion_client.check_username()
        assert username is not None
        assert len(username) > 0

    def test_get_query_payload(self, orion_client, orion_query_id):
        """Test that we can get a query payload."""
        payload = orion_client.get_query_payload(orion_query_id)
        assert isinstance(payload, dict)
        assert "prompts" in payload

    def test_get_query_params(self, orion_client, orion_query_id):
        """Test that we can get query parameters."""
        params = orion_client.get_query_params(orion_query_id)
        assert isinstance(params, list)

    def test_query(self, orion_client, orion_query_id):
        """Test that we can run a query."""
        result = orion_client.query(orion_query_id, {})
        assert isinstance(result, (dict, list))

    # Custom Field Definitions

    def test_get_custom_field_definitions_client(self, orion_client):
        """Test fetching custom field definitions for clients."""
        from orionapi import AuthenticationError, NotFoundError

        try:
            fields = orion_client.get_custom_field_definitions("client")
            assert isinstance(fields, list)
        except (AuthenticationError, NotFoundError):
            pytest.skip("Custom field definitions endpoint not accessible")

    def test_get_custom_field_definitions_account(self, orion_client):
        """Test fetching custom field definitions for accounts."""
        from orionapi import AuthenticationError, NotFoundError

        try:
            fields = orion_client.get_custom_field_definitions("account")
            assert isinstance(fields, list)
        except (AuthenticationError, NotFoundError):
            pytest.skip("Custom field definitions endpoint not accessible")

    # Households (Clients)

    def test_search_clients(self, orion_client):
        """Test searching for clients by name."""
        results = orion_client.search_clients("a", top=5)
        assert isinstance(results, list)

    def test_get_client(self, orion_client):
        """Test fetching a client by ID."""
        results = orion_client.search_clients("a", top=1)
        if not results:
            pytest.skip("No clients found")
        client = orion_client.get_client(results[0]["id"])
        assert isinstance(client, dict)
        assert "id" in client

    def test_get_client_registrations(self, orion_client):
        """Test fetching registrations for a client."""
        results = orion_client.search_clients("a", top=1)
        if not results:
            pytest.skip("No clients found")
        registrations = orion_client.get_client_registrations(results[0]["id"])
        assert isinstance(registrations, list)

    # Registrations

    def test_search_registrations(self, orion_client):
        """Test searching for registrations by name."""
        results = orion_client.search_registrations("a", top=5)
        assert isinstance(results, list)

    def test_get_registration(self, orion_client):
        """Test fetching a registration by ID."""
        results = orion_client.search_registrations("a", top=1)
        if not results:
            pytest.skip("No registrations found")
        registration = orion_client.get_registration(results[0]["id"])
        assert isinstance(registration, dict)
        assert "id" in registration

    def test_get_registration_types(self, orion_client):
        """Test fetching registration types."""
        types = orion_client.get_registration_types()
        assert isinstance(types, list)
        if types:
            assert "id" in types[0]
            assert "name" in types[0]

    # Accounts

    def test_search_orion_accounts(self, orion_client):
        """Test searching for accounts by name."""
        results = orion_client.search_orion_accounts("a", top=5)
        assert isinstance(results, list)

    def test_get_orion_account(self, orion_client):
        """Test fetching an account by ID."""
        results = orion_client.search_orion_accounts("a", top=1)
        if not results:
            pytest.skip("No accounts found")
        account = orion_client.get_orion_account(results[0]["id"])
        assert isinstance(account, dict)
        assert "id" in account
