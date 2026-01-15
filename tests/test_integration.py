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
        portfolio_id = accounts[0].get('portfolioId')
        if not portfolio_id:
            pytest.skip("No portfolio ID found in accounts")

        portfolio = eclipse_client.get_portfolio(portfolio_id)
        assert 'general' in portfolio
        assert 'portfolioName' in portfolio['general']

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
            assert 'id' in portfolios[0]

    def test_get_portfolio_accounts(self, eclipse_client):
        """Test that we can fetch accounts for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]['id']
        accounts = eclipse_client.get_portfolio_accounts(portfolio_id)
        assert isinstance(accounts, list)

    def test_get_portfolio_holdings(self, eclipse_client):
        """Test that we can fetch holdings for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]['id']
        holdings = eclipse_client.get_portfolio_holdings(portfolio_id)
        assert isinstance(holdings, list)

    def test_get_account_holdings(self, eclipse_client):
        """Test that we can fetch holdings for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]['id']
        holdings = eclipse_client.get_account_holdings(account_id)
        assert isinstance(holdings, list)

    # High priority tests

    def test_get_account_details(self, eclipse_client):
        """Test that we can fetch details for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]['id']
        details = eclipse_client.get_account_details(account_id)
        assert isinstance(details, dict)
        assert 'id' in details or 'accountNumber' in details

    def test_get_model(self, eclipse_client):
        """Test that we can fetch a model by ID."""
        models = eclipse_client.get_all_models()
        if not models:
            pytest.skip("No models available")

        model_id = models[0]['id']
        model = eclipse_client.get_model(model_id)
        assert isinstance(model, dict)
        assert 'id' in model

    def test_get_model_tolerance(self, eclipse_client):
        """Test that we can fetch model tolerance for a portfolio/account."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]['id']
        accounts = eclipse_client.get_portfolio_accounts(portfolio_id)
        if not accounts:
            pytest.skip("No accounts in portfolio")

        account_id = accounts[0]['id']
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
        acct_num = acct.get('accountNumber', '')
        acct_name = acct.get('name', '')

        if not acct_num or not acct_name:
            pytest.skip("Account missing number or name")

        # Search using trailing digits and name portion
        acct_id, found_num = eclipse_client.search_accounts_number_and_name(
            acct_num[-4:],
            acct_name[:5]
        )
        assert isinstance(acct_id, int)
        assert isinstance(found_num, str)

    # Medium priority tests

    def test_get_model_allocations(self, eclipse_client):
        """Test that we can fetch model allocations."""
        models = eclipse_client.get_all_models()
        if not models:
            pytest.skip("No models available")

        model_id = models[0]['id']
        allocations = eclipse_client.get_model_allocations(model_id)
        assert isinstance(allocations, (dict, list))

    def test_get_set_asides(self, eclipse_client):
        """Test that we can fetch set asides for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]['id']
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

        acct_num = accounts[0].get('accountNumber', '')
        if not acct_num:
            pytest.skip("Account missing number")

        internal_id = eclipse_client.get_internal_account_id(acct_num)
        assert isinstance(internal_id, int)

    def test_get_account_cash_available(self, eclipse_client):
        """Test that we can get available cash for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]['id']
        cash = eclipse_client.get_account_cash_available(account_id)
        assert isinstance(cash, (int, float))

    def test_get_security_set(self, eclipse_client):
        """Test that we can fetch a security set by ID."""
        security_sets = eclipse_client.get_all_security_sets()
        if not security_sets:
            pytest.skip("No security sets available")

        set_id = security_sets[0]['id']
        security_set = eclipse_client.get_security_set(set_id)
        assert isinstance(security_set, dict)

    def test_get_set_asides_v2(self, eclipse_client):
        """Test that we can fetch all set asides via v2 API."""
        import requests
        try:
            set_asides = eclipse_client.get_set_asides_v2()
            assert isinstance(set_asides, (dict, list))
        except requests.exceptions.HTTPError as e:
            if "403" in str(e):
                pytest.skip("Insufficient privileges for v2 set asides endpoint")
            raise
