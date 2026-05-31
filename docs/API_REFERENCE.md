# orionapi API Reference (v2.20.0)

Auto-generated from docstrings by `scripts/gen_api_reference.py`. Eclipse methods note their underlying endpoint.

Classes: `OrionAPI` (Orion Advisor), `EclipseV1` / `EclipseV2` (explicit Eclipse surfaces), `Eclipse` (best-of-both unifier). Response TypedDicts live in `orionapi.models`.

## OrionAPI

Client for the Orion Advisor API.

**74 methods.**

| Method | Endpoint | Description |
|---|---|---|
| `cancel_client(client_id, cancel_type='Full', account_ids=None, as_of_date=None, zero_assets=False, exclude_download=False, create_final_bill=False)` | `PUT /Portfolio/Clients/Action/Cancel` | Cancel a client/household (full or partial). |
| `check_username()` | `GET /authorization/user` | Get the authenticated user's login ID. |
| `complete_billing_instance(instance_id)` | `POST /Billing/Instances/{instance_id}/Action/Complete` | Finalize/complete a billing instance. |
| `convert_account(from_account_id, convert_date, copy_assets=True, copy_billing=True, copy_transactions=True, old_active=False)` | `POST /Portfolio/Accounts/Action/ConvertAccount` | Convert an account (e.g., IRA to Roth conversion). |
| `copy_report_batch(batch_id, name, start_date=None, end_date=None)` |  | Copy an existing report batch with a new name and optional date range. |
| `create_billing_instance(is_forecast=False, run_for='AllHouseholds', run_for_accounts='ActiveAccounts', bill_type='Renewal', nickname=None, keys=None, as_of_date=None, end_date_override=None, include_cash_flow=False)` | `POST /Billing/BillGenerator/Action/Instance` | Create a new billing instance (live or forecast). |
| `create_client(data)` | `POST /Portfolio/Clients/Verbose` | Create a new client/household. |
| `create_orion_account(data, generate_account_number=False)` | `POST /Portfolio/Accounts/Verbose` | Create a new account. |
| `create_registration(data)` | `POST /Portfolio/Registrations/Verbose` | Create a new registration. |
| `create_report_batch(batch_data)` | `POST /Reporting/Batch/Verbose` | Create a new report batch. |
| `delete_accounts(account_ids)` | `PUT /Portfolio/Accounts/Action/Delete` | Delete accounts by ID. |
| `delete_bills(bill_ids, delete_related_households=False)` | `PUT /Billing/Bills/Action/Delete` | Delete bills by ID list. |
| `delete_clients(client_ids)` | `PUT /Portfolio/Clients/Action/Delete` | Delete clients/households by ID. |
| `delete_registrations(registration_ids)` | `PUT /Portfolio/Registrations/Action/Delete` | Delete registrations by ID. |
| `download_report_pdf(batch_id, entity_key)` | `GET /Reporting/Batch/{batch_id}/Entities/{entity_key}/Action/Download` | Download the rendered PDF for one entity in a generated report batch. |
| `find_query_by_name(name)` |  | Return the ID of the saved query whose name exactly matches ``name``. |
| `generate_billing(instance_id, lock_down=True)` | `PUT /Billing/Instances/{instance_id}/Action/Generate` | Generate bills for a billing instance. |
| `generate_cash_funding(instance_ids, start_date=None, end_date=None, is_forecast=False)` | `POST /Billing/Instances/GenerateCashFunding` | Generate cash funding data for billing instance(s). |
| `generate_fee_files(instance_id, custodian_id=None)` | `POST /Billing/Instances/Action/FeeFiles` | Generate fee files for a billing instance. |
| `generate_statements(batch_id, entity_ids=None)` | `POST /Reporting/Batch/{batch_id}/Entities/Action/Generate` | Generate PDF statements for a report batch. |
| `get_account_billing(account_id)` | `GET /Billing/Accounts/{account_id}` | Get billing information for a specific billing account. |
| `get_adjustment_types(is_payable=None, is_debit=None)` | `GET /Billing/AdjustmentTypes` | Get available billing adjustment types. |
| `get_all_queries(search_term='', top=100)` |  | Deprecated alias for :meth:`search_queries`. |
| `get_assets(account_id, has_value=True)` | `GET /Portfolio/Assets` | Get assets for a specific account. |
| `get_bill_item_adjustments(bill_account_item_id)` | `GET /Billing/BillGenerator/BillAccountItems/BillAccountAdj/{bill_account_item_id}` | Get adjustments for a specific bill account item. |
| `get_billing_household_summary(household_id)` | `GET /Billing/HouseholdSummary/{household_id}` | Get billing summary for a specific household. |
| `get_billing_instance(instance_id)` | `GET /Billing/Instances/{instance_id}` | Get details for a single billing instance. |
| `get_billing_instances(start_date=None, end_date=None)` | `GET /Billing/Instances` | List billing instances, optionally filtered by date range. |
| `get_bills(instance_id=None, is_valid=None, bill_type=None)` | `GET /Billing/Bills` | Get bills, optionally filtered. |
| `get_cash_funding(start_date, end_date, is_forecast=False, take=10000, skip=0)` | `GET /Billing/CashFunding` | Get cash funding data showing after-fee cash balances. |
| `get_client(client_id)` | `GET /Portfolio/Clients/{client_id}` | Get full details for a household/client. |
| `get_client_registrations(client_id, is_active=True)` | `GET /Portfolio/Clients/{client_id}/Registrations` | Get all registrations for a household/client. |
| `get_custom_field_definitions(entity)` | `GET /Settings/UserDefinedFields/Definitions/{entity}` | Get custom field definitions for an entity type. |
| `get_fee_files(instance_id)` | `GET /Billing/FeeFile/instance/{instance_id}` | Get fee files for a billing instance. |
| `get_fee_schedules()` | `GET /Billing/Schedules` | Get all fee schedules. |
| `get_household_recurring_adjustments(household_id=None)` | `GET /Billing/Accounts/HouseholdRecurringAdjustments` | Get recurring billing adjustments at the household level. |
| `get_orion_account(account_id)` | `GET /Portfolio/Accounts/{account_id}` | Get full details for an account. |
| `get_performance_data(entity_id, start_date, end_date, entity_type='account')` | `GET /Portfolio/Accounts/{entity_id}/Performance` | Get performance metrics for an account, client, or registration over a date range. |
| `get_portfolio_tree(client_id, include_additional=False, include_rep=False, filter_type=None)` | `GET /Portfolio/Clients/{client_id}/PortfolioTree` | Get hierarchical portfolio tree for a client. |
| `get_query_metadata(id)` |  | Return the full saved-query record plus its params list. |
| `get_query_params(id)` |  | Get the parameters for a custom query. |
| `get_query_params_description(id)` |  | Print a formatted table of query parameters. |
| `get_query_payload(id)` | `GET /Reporting/Custom/{id}` | Get the full payload for a custom query. |
| `get_receivables(instance_id)` | `GET /Billing/PostPayments/BillInstance/{instance_id}` | Get outstanding fees (receivables) for a billing instance. |
| `get_recurring_adjustments(account_id=None)` | `GET /Billing/Accounts/RecurringAdjustments` | Get recurring billing adjustments, optionally filtered by account. |
| `get_registration(registration_id)` | `GET /Portfolio/Registrations/{registration_id}` | Get full details for a registration. |
| `get_registration_types()` | `GET /Portfolio/Registrations/Types` | Get available registration types (IRA, 401k, etc.). |
| `get_report_batch(batch_id)` | `GET /Reporting/Batch/{batch_id}` | Get a single report batch. |
| `get_report_batch_entities(batch_id, generation_status=None)` | `GET /Reporting/Batch/{batch_id}/Entities` | Get entities in a report batch. |
| `get_report_batch_verbose(batch_id, expand='All')` | `GET /Reporting/Batch/Verbose/{batch_id}` | Get verbose details of a report batch. |
| `get_report_batches(qpe_item_id=None)` | `GET /Reporting/Batch` | List all report batches. |
| `get_transactions(account_id=None, client_id=None, registration_id=None, start_date=None, end_date=None, status=None, trans_type_ids=None, has_errors=None)` | `GET /Portfolio/Transactions` | Get transactions, optionally filtered. |
| `invalidate_billing_instance(instance_id)` | `POST /Billing/Instances/{instance_id}/Action/Invalidate` | Invalidate/cancel a billing instance. |
| `login(usr=None, pwd=None)` | `GET /security/token` | Authenticate with the Orion API. |
| `merge_accounts(merges)` | `PUT /Portfolio/Accounts/Action/Merge` | Merge accounts. |
| `move_account(account_id, target_registration_id)` | `PUT /Portfolio/Accounts/{account_id}/Action/MoveToRegistration/{target_registration_id}` | Move an account to a different registration. |
| `move_registration(registration_ids, target_client_id)` | `PUT /Portfolio/Registrations/Action/MoveToClient/{target_client_id}` | Move registrations to a different client/household. |
| `poll_until_generated(batch_id, timeout=600, poll_interval=5, progress_callback=None)` |  | Block until every entity in the batch reaches a terminal generation state. |
| `post_payments(batch_number, payments)` | `POST /Billing/PostPayments` | Post payments to mark fees as collected. |
| `query(id, params=None)` | `POST /Reporting/Custom/{id}/Generate/Table` | Execute a custom query. |
| `search_assets(search_term, top=20)` | `GET /Portfolio/Assets/Simple/Search` | Search for assets by ticker, CUSIP, or name. |
| `search_clients(search_term, top=20, is_active=True)` | `GET /Portfolio/Clients/Simple/Search` | Search for households/clients by name. |
| `search_orion_accounts(search_term, top=20, is_active=True)` | `GET /Portfolio/Accounts/Simple/Search` | Search for accounts by name or number. |
| `search_queries(search_term='', top=100, skip=0)` | `GET /Reporting/Custom/Simple/Search` | Search the firm's saved DataQueries by name substring. |
| `search_registrations(search_term, top=20, is_active=True)` | `GET /Portfolio/Registrations/Simple/Search` | Search for registrations by name. |
| `send_electronic_statements(batch_id, entity_ids=None)` | `POST /Reporting/Batch/{batch_id}/Entities/Action/SendElectronicStatement` | Send electronic statements (email) for a report batch. |
| `split_registration(registration_id)` | `PUT /Portfolio/Registrations/{registration_id}/Action/Split` | Split a registration so each active non-sleeved account gets its own registration. |
| `undo_account_conversion(account_id)` | `DELETE /Portfolio/Accounts/{account_id}/Action/UndoConversion` | Undo an account conversion. |
| `update_bill_item_adjustments(bill_account_item_id, adjustments, create_payable_adj=None)` | `PUT /Billing/BillGenerator/BillAccountItems/BillAccountAdj/edit/{bill_account_item_id}` | Add, update, or delete adjustments on a bill account item. |
| `update_client(client_id, data)` | `PUT /Portfolio/Clients/{client_id}` | Update a household/client. |
| `update_orion_account(account_id, data)` | `PUT /Portfolio/Accounts/{account_id}` | Update an account. |
| `update_registration(registration_id, data)` | `PUT /Portfolio/Registrations/{registration_id}` | Update a registration. |
| `update_report_batch(batch_id, batch_data)` | `PUT /Reporting/Batch/Verbose/{batch_id}` | Update an existing report batch. |
| `write_off_bills(payments, payment_from='Household', batch_number=None)` | `POST /Billing/PostPayments/WriteOffBills` | Write off remaining balances on bills. |

## EclipseV1

Eclipse client targeting the v1 API surface (``/v1/...``) only.

**220 methods.**

| Method | Endpoint | Description |
|---|---|---|
| `add_model(name, name_space='Default', description=None, tags=None, status_id=1, management_style_id=2, is_community_model=False, is_dynamic=False, exclude_rebalance_sleeve=False)` | `POST /modeling/models` | Create a new model. |
| `add_model_detail(model_id, model_detail, sync=True)` | `POST /modeling/models/{model_id}/modelDetail` | Add model detail/structure to an existing model. |
| `add_model_portfolios(model_id, payload)` | `POST /modeling/models/{model_id}/portfolios` | Assign portfolios to a model (mutating). |
| `add_model_sleeves(model_id, payload)` | `POST /modeling/models/{model_id}/sleeves` | Add sleeves to a model (mutating). |
| `add_portfolio_accounts(portfolio_id, payload)` | `POST /portfolio/portfolios/{portfolio_id}/accounts` | Add accounts to a portfolio (mutating). |
| `add_security_corporate_action(security_id, payload)` | `POST /security/securities/{security_id}/corporateAction` | Add a corporate action to a security (mutating). |
| `add_submodel_detail(payload)` | `POST /modeling/models/submodels/submodeldetail` | Add a submodel detail (mutating). |
| `auto_rebalance(payload)` | `POST /tradetool/rebalancer/action/autoRebalance` | Generate an auto-rebalance trade. |
| `cash_needs_trade(portfolio_ids, portfolio_trade_group_ids=None, is_view_only=True, reason='', is_excel_import=False, sync=True)` | `POST /tradetool/cashneeds/action/generatetrade` | Rebalance CashNeeds Portfolios. |
| `check_tlh_gain_loss(portfolio_ids=None, account_ids=None)` | `POST /tradetool/taxLossHarvesting/action/checkGainLoss` | Check projected gain/loss for tax-loss harvesting (preview only). |
| `check_username()` | `GET /admin/authorization/user` | Get the authenticated user's login ID. |
| `convert_model_to_eclipse_format(components, existing_model=None, model_name=None)` |  | Convert parsed model components to Eclipse modelDetail format. |
| `convert_to_eclipse_tolerances(securities)` |  | Convert absolute bounds to Eclipse tolerance format. |
| `copy_model(model_id, payload)` | `POST /modeling/models/{model_id}/copy` | Copy a model (mutating). |
| `copy_submodel(submodel_id, payload)` | `POST /modeling/models/submodels/{submodel_id}/copy` | Copy a submodel (mutating). |
| `create_portfolio(payload)` | `POST /portfolio/portfolios/` | Create a portfolio (mutating). |
| `create_portfolio_aside_cash(portfolio_id, payload)` | `POST /portfolio/portfolios/{portfolio_id}/asideCash` | Create set-aside cash for a portfolio (mutating). |
| `create_security(payload)` | `POST /security/securities` | Create a security (mutating). |
| `create_security_set(name, securities, description=None, tolerance_type='ABSOLUTE', tolerance_type_value=0)` | `POST /security/securityset` | Create a new security set. |
| `create_set_aside(account_number, amount, min_amount=0.0, max_amount=0.0, description=None, cash_type='$', start_date=None, expire_type='None', expire_date=None, expire_trans_tol=0, expire_trans_type=1, percent_calc_type=0, sync=True)` | `POST /account/accounts/{account_id}/asidecash` | Create a set-aside cash reservation for an account. |
| `create_submodel(payload)` | `POST /modeling/models/submodels` | Create a submodel (mutating). |
| `create_tlh_trade(payload)` | `POST /tradetool/taxLossHarvesting/action/createTLHTrade` | Create a tax-loss-harvesting trade. |
| `create_tlh_trade_batch(payload)` | `POST /tradetool/taxLossHarvesting/action/createTLHTradeBatchId` | Create a tax-loss-harvesting trade by batch ID. |
| `create_tlh_trade_generic(payload)` | `POST /tradetool/taxLossHarvesting/action/createTrade` | Create a tax-loss-harvesting trade (generic createTrade). |
| `delete_account_aside_cash(account_id, aside_cash_id)` | `DELETE /account/accounts/{account_id}/asidecash/{aside_cash_id}` | Delete an account set-aside cash entry (mutating). |
| `delete_model(model_id)` | `DELETE /modeling/models/{model_id}` | Delete a model (soft delete). |
| `delete_model_portfolio(model_id, portfolio_id)` | `DELETE /modeling/models/{model_id}/portfolios/{portfolio_id}` | Unassign a portfolio from a model (mutating). |
| `delete_model_sleeve(model_id, sleeve_id)` | `DELETE /modeling/models/{model_id}/sleeves/{sleeve_id}` | Delete a sleeve from a model (mutating). |
| `delete_portfolio(portfolio_id)` | `DELETE /portfolio/portfolios/{portfolio_id}` | Delete a portfolio (mutating). |
| `delete_portfolio_aside_cash(portfolio_id, aside_cash_id)` | `DELETE /portfolio/portfolios/{portfolio_id}/asideCash/{aside_cash_id}` | Delete a portfolio set-aside cash entry (mutating). |
| `delete_security(security_id)` | `DELETE /security/securities/{security_id}` | Delete a security (mutating). |
| `delete_security_set(set_id)` | `DELETE /security/securityset/{set_id}` | Delete a security set (mutating). |
| `delete_submodel(submodel_id, model_id=None, model_detail_id=None)` | `DELETE /modeling/models/submodels/{submodel_id}` | Delete a submodel (mutating). |
| `deserialize_global_trade(payload)` | `POST /tradetool/globaltrades/action/deserialize` | Deserialize a global-trade upload (POST-body). |
| `deserialize_ticker_swap(payload)` | `POST /tradetool/tickerswap/action/deserialize` | Deserialize a ticker-swap upload (POST-body). |
| `deserialize_trade_to_target(payload)` | `POST /tradetool/tradetotarget/action/deserialize` | Deserialize a trade-to-target upload (POST-body). |
| `export_model_to_file(model_id, file_path)` |  | Export a model to a definition file. |
| `export_models(payload)` | `POST /modeling/models/export` | Export models (POST-body). |
| `export_security_set_to_file(set_id, file_path)` |  | Export a security set to a definition file. |
| `find_model_by_name(name)` |  | Find a model by name. |
| `find_security_set_by_name(name)` |  | Find a security set by name. |
| `generate_global_trade(payload)` | `POST /tradetool/globaltrades/action/generateTrade` | Generate a global trade. |
| `generate_liquidate_trade(payload)` | `POST /tradetool/liquidate/generateTrade` | Generate a liquidation trade. |
| `generate_prorated_cash_trade(payload)` | `POST /tradetool/proratedcash/action/generatetrade` | Generate a prorated-cash trade. |
| `generate_raise_cash_trade(payload)` | `POST /tradetool/raisecash/action/generatetrade` | Generate a raise-cash trade. |
| `generate_trade_instance(payload)` | `POST /tradetool/tradeInstance/action/generateinstance` | Generate a trade instance. |
| `generate_trade_to_target(payload)` | `POST /tradetool/tradetotarget/action/generateTrade` | Generate a trade-to-target trade. |
| `get_account_cash_available(internal_id)` |  | Get available cash for an account. |
| `get_account_custodial_information(account_id)` | `GET /account/accounts/{account_id}/custodialInformation` | Get custodial information for an account. |
| `get_account_details(internal_id)` | `GET /account/accounts/{internal_id}` | Get detailed information for a specific account. |
| `get_account_filters()` | `GET /account/accounts/accountfilters` | Get the available account filters. |
| `get_account_holdings(account_id, search=None)` | `GET /holding/holdings/simple` | Get holdings for a specific account. |
| `get_account_holdings_detail(account_id)` | `GET /account/accounts/{account_id}/holdings` | Get holdings for an account via the account-path holdings endpoint. |
| `get_account_model_types(account_id)` | `GET /account/accounts/{account_id}/model/modelTypes` | Get the model types for an account. |
| `get_account_portfolio_id(account_id)` | `GET /account/accounts/{account_id}/portfolioId` | Get the portfolio ID for an account. |
| `get_account_portfolio_id_by_firm(account_id, firm_id)` | `GET /account/accounts/{account_id}/{firm_id}/portfolioId` | Get the portfolio ID for an account scoped by firm. |
| `get_account_portfolio_ids(body)` | `POST /account/accounts/portfolioIds` | Get portfolio IDs for a set of accounts (POST-body read). |
| `get_account_set_aside(account_id, aside_cash_id)` | `GET /account/accounts/{account_id}/asidecash/{aside_cash_id}` | Get a single account set-aside cash entry. |
| `get_account_simple(account_id)` | `GET /account/accounts/simple/{account_id}` | Get a lightweight account record by internal ID. |
| `get_account_sma(account_id)` | `GET /account/accounts/{account_id}/sma` | Get SMA info for an account. |
| `get_account_submodels(account_id, model_type_id=None)` | `GET /account/accounts/{account_id}/model/submodels` | Get the submodels for an account. |
| `get_accounts_portfolio_ids_detail(body)` | `POST /account/accounts/list/portfolioIdsDetail` | Get portfolio-id detail for a set of accounts (POST-body read). |
| `get_accounts_simple_by_type(account_type)` | `GET /account/accounts/simpleList/type/{account_type}` | Get a simple account list filtered by account type. |
| `get_accounts_without_portfolio()` | `GET /account/accounts/noPortfolio` | Get accounts not assigned to a portfolio. |
| `get_all_account_details()` | `GET /account/accounts/` | Get detailed information for all accounts. |
| `get_all_models(name=None, top=None)` | `GET /modeling/models` | Get all investment models. |
| `get_all_portfolios(include_value=True, search=None, top=None)` | `GET /portfolio/portfolios/simple` | Get list of all portfolios. |
| `get_all_security_sets()` | `GET /security/securityset` | Get all security sets. |
| `get_all_submodels(model_type=None)` | `GET /modeling/models/allSubModel` | Get all submodels, optionally filtered by model type. |
| `get_allow_short_term_gains_options()` | `GET /tradetool/allowshorttermgains` | Get the allow-short-term-gains options. |
| `get_allow_wash_sales_options()` | `GET /tradetool/allowwashsales` | Get the allow-wash-sales options. |
| `get_analytics_status()` | `GET /dataimport/analysis/status` | Check if analytics are currently running. |
| `get_aside_cash_account_types()` | `GET /portfolio/portfolios/asideCashAccountType` | Get the set-aside-cash account types. |
| `get_aside_cash_amount_types()` | `GET /account/accounts/asideCashAmountType` | Get set-aside-cash amount types. |
| `get_aside_cash_expiration_types()` | `GET /account/accounts/asideCashExpirationType` | Get set-aside-cash expiration types. |
| `get_aside_cash_percent_calc_types()` | `GET /account/accounts/accountSetAsidePercentCalculationType` | Get set-aside-cash percent calculation types. |
| `get_aside_cash_transaction_types()` | `GET /account/accounts/asideCashTransactionType` | Get set-aside-cash transaction types. |
| `get_closed_trades()` | `GET /tradeorder/closedtrades` | Get all closed/executed trade orders. |
| `get_corporate_action_types()` | `GET /security/securities/corporateActionTypes` | Get the corporate-action types. |
| `get_firm_token(payload)` | `POST /admin/token/firm` | Get a firm token (mutating; token issuance). |
| `get_firm_token_by_id(firm_id)` | `GET /admin/token/firm/{firm_id}` | Get a firm token by firm ID. |
| `get_holding(holding_id)` | `GET /holding/holdings/{holding_id}` | Get a holding by ID. |
| `get_holding_filters()` | `GET /holding/holdings/holdingfilters` | Get the available holding filters. |
| `get_holding_transactions(holding_id)` | `GET /holding/holdings/{holding_id}/transactions` | Get transactions for a holding. |
| `get_house_account(custodian_id)` | `GET /account/accounts/action/houseAccount/{custodian_id}` | Get the house account for a custodian. |
| `get_model(id)` | `GET /modeling/models/{id}` | Get details for a specific model. |
| `get_model_allocations(id, aggregate=True)` | `GET /modeling/models/{id}/allocations` | Get allocations for a model. |
| `get_model_analysis(model_id, asset_type='securityset')` | `GET /modeling/models/{model_id}/modelAnalysis` | Get model analysis for a model. |
| `get_model_can_delete(model_id)` | `GET /modeling/models/{model_id}/canDelete` | Check whether a model can be deleted. |
| `get_model_can_rebalance(model_id)` | `GET /modeling/models/{model_id}/canRebalance` | Check whether a model can be rebalanced. |
| `get_model_detail_portfolio_ids()` | `GET /modeling/models/modelDetails/portfolioId` | Get model-detail portfolio IDs. |
| `get_model_filter_types()` | `GET /modeling/models/filterTypes` | Get model filter types. |
| `get_model_import_error_logs()` | `GET /modeling/models/upload/modelImportErrorLogs` | Get model-import error logs. |
| `get_model_management_styles()` | `GET /modeling/models/managementStyles` | Get model management styles. |
| `get_model_nodes(model_id)` | `GET /modeling/models/{model_id}/Model/nodes` | Get the node tree for a model. |
| `get_model_pending(model_id)` | `GET /modeling/models/{model_id}/pending` | Get pending changes for a model. |
| `get_model_pending_portfolios(model_id)` | `GET /modeling/models/{model_id}/portfolios/pending` | Get pending portfolios for a model. |
| `get_model_pending_sleeve_accounts(model_id)` | `GET /modeling/models/{model_id}/sleeveaccount/pending` | Get pending sleeve accounts for a model. |
| `get_model_portfolios(model_id)` | `GET /modeling/models/{model_id}/portfolios` | Get portfolios assigned to a model. |
| `get_model_security_types(model_id)` | `GET /modeling/models/{model_id}/securitytypes` | Get the security types for a model. |
| `get_model_sleeves(model_id)` | `GET /modeling/models/{model_id}/sleeves` | Get sleeves for a model. |
| `get_model_sma_weightings(model_id, model_element_id)` | `GET /modeling/models/{model_id}/smaweightings/{model_element_id}` | Get the SMA weightings for a model element. |
| `get_model_status()` | `GET /modeling/models/modelStatus` | Get the list of model statuses. |
| `get_model_teams(model_id, is_edit_model=None)` | `GET /modeling/models/{model_id}/teams` | Get the teams for a model. |
| `get_model_tolerance(portfolio_id, account_id, account_type='Normal')` | `GET /portfolio/portfolios/{portfolio_id}/ModelMACTolerance/{account_id}` | Get model tolerance values for a portfolio/account. |
| `get_model_tolerance_detail(portfolio_id, account_id, asset_type=None, is_sleeved_portfolio=None)` | `GET /portfolio/portfolios/{portfolio_id}/modelTolerance/{account_id}` | Get model tolerance detail for a portfolio/account by asset type. |
| `get_model_types()` | `GET /modeling/models/modelTypes` | Get the list of model types. |
| `get_model_upload_templates()` | `GET /modeling/models/upload/templates` | Get the model-upload templates. |
| `get_models_by_model_details(body)` | `POST /modeling/models/modelsByModelDetails` | Get models by model-detail criteria (POST-body read). |
| `get_new_account_template()` | `GET /account/accounts/new` | Get a blank/new account template. |
| `get_new_portfolio_template()` | `GET /portfolio/portfolios/new` | Get a blank/new portfolio template. |
| `get_orders()` | `GET /tradeorder/trades` | Get all completed (non-pending) trade orders. |
| `get_orders_pending()` | `GET /tradeorder/trades` | Get all pending trade orders. |
| `get_out_of_tolerance_accounts(model_id, asset_id, asset_type='class')` | `GET /account/accounts/{model_id}/outOfTolerance/{asset_id}` | Get accounts out of tolerance for a model asset. |
| `get_portfolio(portfolio_id)` | `GET /portfolio/portfolios/{portfolio_id}` | Get portfolio details by ID. |
| `get_portfolio_account_count()` | `GET /account/accounts/portfolioAccountCount` | Get the portfolio/account count. |
| `get_portfolio_accounts(portfolio_id, simple=False)` | `GET {path}` | Get list of accounts for a portfolio. |
| `get_portfolio_accounts_detailed(portfolio_id)` | `GET /portfolio/portfolios/{portfolio_id}/accounts/detailed` | Get detailed accounts for a portfolio. |
| `get_portfolio_accounts_summary(portfolio_id)` | `GET /portfolio/portfolios/{portfolio_id}/accounts/summary` | Get an account summary for a portfolio. |
| `get_portfolio_contribution_amount(portfolio_id)` | `GET /portfolio/portfolios/{portfolio_id}/contributionamount` | Get the contribution amount for a portfolio. |
| `get_portfolio_filters()` | `GET /portfolio/portfolios/portfolioFilters` | Get the available portfolio filters. |
| `get_portfolio_holdings(portfolio_id, search=None)` | `GET /holding/holdings/simple` | Get all holdings across a portfolio. |
| `get_portfolio_holdings_detail(portfolio_id)` | `GET /portfolio/portfolios/{portfolio_id}/holdings` | Get holdings for a portfolio via the portfolio-path holdings endpoint. |
| `get_portfolio_levels(body)` | `POST /portfolio/portfolios/levels` | Get portfolio levels (POST-body read). |
| `get_portfolio_pending_models(portfolio_id)` | `GET /portfolio/portfolios/{portfolio_id}/pending/models` | Get pending models for a portfolio. |
| `get_portfolio_set_aside(portfolio_id, aside_cash_id)` | `GET /portfolio/portfolios/{portfolio_id}/asideCash/{aside_cash_id}` | Get a single portfolio set-aside cash entry. |
| `get_portfolio_set_asides(portfolio_id)` | `GET /portfolio/portfolios/{portfolio_id}/asidecash` | Get set-aside cash for a portfolio. |
| `get_portfolio_simple(portfolio_id)` | `GET /portfolio/portfolios/simple/{portfolio_id}` | Get a lightweight portfolio record by ID. |
| `get_portfolio_trade_instances(portfolio_id, start_date, end_date)` | `GET /tradeorder/instances/portfolio/{portfolio_id}/search` | Get all trade instances for a specific portfolio within a date range. |
| `get_portfolios_by_household(household_ids)` | `GET /portfolio/portfolios` | Get portfolios for the given household IDs. |
| `get_raise_cash_methods()` | `GET /tradetool/raisecash/calculation_methods` | Get the available raise-cash calculation methods. |
| `get_restricted_plans()` | `GET /account/accounts/restrictedPlans` | Get the restricted plans. |
| `get_security(security_id)` | `GET /security/securities/{security_id}` | Get a security by ID. |
| `get_security_alternate_prefs(security_id)` | `GET /security/securities/{security_id}/securityAlternatePreferences` | Get the alternate-security preferences for a security. |
| `get_security_by_ticker(ticker)` |  | Get a security by its ticker symbol. |
| `get_security_corporate_action(security_id)` | `GET /security/securities/{security_id}/corporateAction` | Get corporate actions for a security. |
| `get_security_count(security_id, body=None)` | `POST /security/securities/{security_id}/count` | Get a usage count for a security (POST-body). |
| `get_security_maintain(location)` | `GET /security/securities/maintain/{location}` | Get security maintenance data for a location. |
| `get_security_min_initial_buy_prefs(security_id)` | `GET /security/securities/{security_id}/securityMinimumInitialBuyAmountPreferences` | Get the minimum-initial-buy-amount preferences for a security. |
| `get_security_preferences(portfolio_id, security_id)` | `GET /preference/Portfolio/securityPreference/{portfolio_id}/{security_id}/0/0` | Get rebalance preferences/rules for a security in a portfolio. |
| `get_security_price(security_id)` | `GET /security/securities/price/{security_id}` | Get the price for a security. |
| `get_security_priority_prefs(security_id, priority=None)` | `GET /security/securities/{security_id}/securityPriorityPreferences` | Get the buy/sell priority preferences for a security. |
| `get_security_set(id)` | `GET /security/securityset/details/{id}` | Get details for a specific security set. |
| `get_security_set_buy_priority()` | `GET /security/securityset/buypriority` | Get the security-set buy priorities. |
| `get_security_set_can_delete(set_id, ignore_model_id=None)` | `GET /security/securityset/{set_id}/canDelete` | Check whether a security set can be deleted. |
| `get_security_set_details()` | `GET /security/securityset/detail` | Get the full security-set detail list. |
| `get_security_set_equivalent_types()` | `GET /security/securityset/equivalentType` | Get the security-set equivalent types. |
| `get_security_set_sell_priority()` | `GET /security/securityset/sellpriority` | Get the security-set sell priorities. |
| `get_security_set_summary(id)` | `GET /security/securityset/{id}` | Get a security set by ID via the summary endpoint. |
| `get_security_statuses()` | `GET /security/securities/securitystatus` | Get the security statuses. |
| `get_security_types()` | `GET /security/securities/securitytype` | Get the security types. |
| `get_set_asides(account_id, active_only=False)` | `GET /account/accounts/{internal_id}/asidecash` | Get set-aside cash settings for a specific account (v1 surface). |
| `get_sleeve_allocations_v1(account_id)` | `GET /portfolio/sleeves/{account_id}/allocations` | Get sleeve allocation details for an account (v1). |
| `get_sleeves()` | `GET /portfolio/sleeves` | Get all sleeves (v1). |
| `get_spend_cash_methods()` | `GET /tradetool/spendcash/calculation_methods` | Get the available spend-cash calculation methods. |
| `get_submodel(submodel_id)` | `GET /modeling/models/submodels/{submodel_id}` | Get a submodel by ID. |
| `get_submodel_can_delete(submodel_id, model_id=None, model_detail_id=None)` | `GET /modeling/models/submodels/{submodel_id}/canDelete` | Check whether a submodel can be deleted. |
| `get_submodel_securities(body)` | `POST /modeling/models/submodels/securities` | Get securities for submodels (POST-body read). |
| `get_submodel_teams(submodel_id)` | `GET /modeling/models/submodel/{submodel_id}/teams` | Get the teams for a submodel. |
| `get_submodels(model_type=None, search=None)` | `GET /modeling/models/submodels` | Get submodels, optionally filtered by type and name. |
| `get_submodels_usage()` | `GET /modeling/models/submodels/usage` | Get submodel usage. |
| `get_tactical_rebalance_cash_protection()` | `GET /tradetool/tacticalRebalanceCashProtection` | Get the tactical-rebalance cash-protection options. |
| `get_taxlots(holding_id)` | `GET /holding/holdings/{holding_id}/taxlots` | Get tax lots for a holding. |
| `get_tlh_gainloss_options()` | `GET /tradetool/taxLossHarvesting/gainloss/options` | Get the tax-loss-harvesting gain/loss options. |
| `get_tlh_securities(portfolio_ids=None, account_ids=None)` | `POST /tradetool/taxLossHarvesting/securities` | Get tax-loss-harvesting candidate securities (preview only). |
| `get_tlh_sign_options()` | `GET /tradetool/taxLossHarvesting/sign/options` | Get the tax-loss-harvesting sign options. |
| `get_tlh_term_options()` | `GET /tradetool/taxLossHarvesting/term/options` | Get the tax-loss-harvesting term options. |
| `get_trade_instance(instance_id)` | `GET /tradeorder/instances/{instance_id}` | Get details for a specific trade instance. |
| `get_trade_instance_logs(instance_id)` | `GET /tradeorder/instances/{instance_id}/tradeLogs` | Get trade logs for a specific trade instance. |
| `get_trade_instances(start_date, end_date, normalize=True)` | `GET /tradeorder/instances` | Get trade instances (batches of trades) within a date range. |
| `get_trade_log_detail(log_id)` | `GET /api/v2/Trading/TradeLogById/{log_id}` | Get detailed HTML trade log showing trading engine decision-making. |
| `get_trade_priority_rankings()` | `GET /tradetool/priorityrankings` | Get the available trade priority rankings. |
| `get_trade_side_options()` | `GET /tradetool/tradeside` | Get the trade-side options. |
| `get_trade_status(trade_id)` | `GET /tradeorder/trades/{trade_id}` | Get status and details for a specific trade. |
| `get_trades(portfolio_id=None, top=None, is_pending=None)` | `GET /tradeorder/trades` | Get trade orders with optional portfolio / paging / pending filters. |
| `list_accounts_simple_v1(body=None)` | `POST /account/accounts/simple/list` | List accounts (simple) via the v1 POST-body endpoint. |
| `list_models_simple_v1(body=None)` | `POST /modeling/models/simple/list` | List models (simple) via the v1 POST-body endpoint. |
| `list_portfolio_accounts_simple(body)` | `POST /portfolio/portfolios/accounts/simple/list` | List portfolio accounts (simple) via the v1 POST-body endpoint. |
| `list_portfolios_simple_v1(body=None)` | `POST /portfolio/portfolios/simple/list` | List portfolios (simple) via the v1 POST-body endpoint. |
| `login_as(payload)` | `POST /admin/token/loginas` | Impersonate (login as) another user (mutating). |
| `logout()` | `GET /admin/logout` | Log out the current session. |
| `parse_model_file(file_path)` |  | Parse a model definition file. |
| `parse_security_set_file(file_path)` |  | Parse a security set definition file. |
| `preview_model_changes(file_path)` |  | Preview changes between a model file and Eclipse. |
| `preview_security_set_changes(file_path)` |  | Preview changes between a security set file and Eclipse. |
| `rebalance_trade(portfolio_ids=None, account_ids=None, filter_type=None, is_view_only=True, max_gain_amount=0, minimum_trade_amount=0, minimum_trade_amount_type='$', allow_wash_sale=False, rounding=0, sync=False)` | `POST /tradetool/rebalancer/action/generatetrade` | Generate a rebalance trade (preview/staging by default). |
| `retry_update_other_model(payload)` | `POST /modeling/models/updateOtherModel/retryProcess` | Retry the update-other-model process (mutating). |
| `revert_login_as()` | `GET /admin/token/loginas/revert` | Revert a login-as impersonation. |
| `run_analytics()` | `GET /postimport/run_need_analysis` | Run analytics for portfolios that need it. |
| `search_holdings(search)` | `GET /holding/holdings` | Search holdings by id or name. |
| `search_orion_securities(search, top=20)` | `GET /security/securities/orion` | Search the Orion security master. |
| `search_securities(search, top=20, exclude_cash=True)` | `GET /security/securities` | Search for securities by ticker symbol, name, or ID. |
| `search_tlh_securities(payload)` | `POST /tradetool/taxLossHarvesting/action/searchTLHsecurity` | Search tax-loss-harvesting securities (POST-body). |
| `set_account_tradeable(account_id, trade_restriction='tradeable', sync=True)` | `PUT /account/accounts/{account_id}` | Set trading restrictions for an account. |
| `set_portfolio_flag(payload)` | `POST /portfolio/portfolioFlag` | Set a portfolio flag (mutating). |
| `set_portfolio_tradeable(portfolio_id, tradeable=True, sync=True)` | `PUT /portfolio/portfolios/{portfolio_id}` | Set whether trading is allowed for a portfolio. |
| `set_security_set_favorite(set_id, payload)` | `PUT /security/securityset/favorites/{set_id}` | Set a security set as favorite (mutating). |
| `set_submodel_favorite(submodel_id, payload)` | `PUT /modeling/models/submodels/favorites/{submodel_id}` | Set a submodel as favorite (mutating). |
| `spend_cash_trade(portfolio_ids, portfolio_trade_group_ids=None, is_view_only=True, reason='', is_excel_import=False, sync=True, selected_method_id=None, spend_full_amount=None, filter_type=None)` | `POST /tradetool/spendcash/action/generatetrade` | Generate Spend Cash trade for portfolios. |
| `sync_model_from_file(file_path, model_id=None)` |  | Sync a model from a definition file to Eclipse. |
| `sync_model_from_file_by_name(file_path)` |  | Sync a model from file, auto-detecting create vs update. |
| `sync_security_set_from_file(file_path, set_id=None)` |  | Sync a security set from a definition file to Eclipse. |
| `sync_security_set_from_file_by_name(file_path)` |  | Sync a security set from file, auto-detecting create vs update. |
| `tlh_trade(portfolio_ids=None, account_ids=None, is_view_only=True, sync=False)` | `POST /tradetool/taxLossHarvesting/action/generateTrade` | Generate a tax-loss-harvesting trade (preview/staging by default). |
| `update_account_aside_cash(account_id, aside_cash_id, payload)` | `PUT /account/accounts/{account_id}/asidecash/{aside_cash_id}` | Update an account set-aside cash entry (mutating). |
| `update_account_sma(account_id, payload)` | `PUT /account/accounts/{account_id}/sma/` | Update SMA settings for an account (mutating). |
| `update_model(model_id, payload)` | `PUT /modeling/models/{model_id}` | Update a model (mutating). |
| `update_model_detail(model_id, model_detail, sync=True)` | `PUT /modeling/models/{model_id}/modelDetail` | Update model detail/structure for an existing model. |
| `update_model_detail_element(model_id, model_detail_id, payload)` | `PUT /modeling/models/{model_id}/modelDetail/{model_detail_id}` | Update a single model-detail element (mutating). |
| `update_portfolio_accounts(portfolio_id, payload)` | `PUT /portfolio/portfolios/{portfolio_id}/accounts` | Update accounts on a portfolio (mutating). |
| `update_security(security_id, payload)` | `PUT /security/securities/{security_id}` | Update a security (mutating). |
| `update_security_set(set_id, name, securities, description=None, tolerance_type='ABSOLUTE', tolerance_type_value=0, sync=True)` | `PUT /security/securityset/{set_id}` | Update an existing security set. |
| `update_submodel(submodel_id, payload)` | `PUT /modeling/models/submodels/{submodel_id}` | Update a submodel (mutating). |
| `update_submodel_by_model(payload, model_id=None)` | `PUT /modeling/models/submodels` | Update a submodel in the context of a model (mutating). |
| `upload_model(payload)` | `POST /modeling/models/upload` | Upload a model file (mutating). |
| `upload_trade_file(payload, is_sleeve=None)` | `POST /tradetool/uploadfile` | Upload a trade file. |
| `validate_buy_preferred_tlh_securities(payload)` | `POST /tradetool/taxLossHarvesting/action/validateBuyPreferredTHSecurities` | Validate buy-preferred tax-loss-harvesting securities (POST-body). |
| `validate_model_upload(payload)` | `POST /modeling/models/upload/validate` | Validate a model upload (POST-body). |
| `validate_tlh_securities(payload)` | `POST /tradetool/taxLossHarvesting/action/validateTLHSecurities` | Validate tax-loss-harvesting securities (POST-body). |
| `wait_for_analytics(poll_interval=1, timeout=300)` |  | Wait for analytics to complete. |

## EclipseV2

Eclipse client targeting the v2 API surface (``/api/v2/...``) only.

**307 methods.**

| Method | Endpoint | Description |
|---|---|---|
| `abandon_custom_import(instance_id)` | `PUT /api/v2/CustomImports/Instances/Abandon/{instance_id}` | Abandon a custom-import instance (mutating). |
| `account_search(search, limit=None, offset=None)` | `GET /api/v2/AccountSearch/AccountSearchList` | Search accounts (v2 UI search). |
| `add_fixed_income_trade_block_detail(related_type, payload)` | `POST /api/v2/TradeBlockDetails/FixedIncome/{related_type}` | Add a fixed-income trade-block detail (mutating). |
| `add_manual_trade_block_detail(related_type, related_type_id, payload)` | `POST /api/v2/TradeBlockDetails/Manual/{related_type}/{related_type_id}` | Add a manual trade-block detail for an entity (mutating). |
| `add_notes(notes)` | `POST /api/v2/Notes/AddList` | Create notes. |
| `add_saved_view_to_dashboard(view_id, is_firm_action_items=None)` | `POST /api/v2/SavedView/{view_id}/dashboard` | Add a saved view to the user-level dashboard. |
| `add_trade_block_details(payload)` | `POST /api/v2/TradeBlockDetails/AddList` | Add trade-block details (mutating). |
| `add_trade_block_reason_by_name(payload)` | `POST /api/v2/TradeBlockReasons/AddByName` | Add a trade-block reason by name (mutating). |
| `apply_custom_import(instance_id)` | `PUT /api/v2/CustomImports/Instances/Apply/{instance_id}` | Apply a custom-import instance (mutating). |
| `assign_model_to_portfolios(payload)` | `PUT /api/v2/Portfolio/Portfolios/action/assignModel` | Assign a model to portfolios (mutating). |
| `billing_set_aside_cash(payload)` | `POST /api/v2/SetAsideCash/BillingSetAsideCash` | Create billing set-aside cash (mutating). |
| `cancel_analytics()` | `POST /api/v2/Analytics/Cancel` | Cancel the running analytics (mutating). |
| `classify_securities(classifications)` | `POST /api/v2/AssetClassification/Security/Classifications` | Assign classifications to securities. |
| `compare_trades(payload)` | `POST /api/v2/CompareTool/Trades` | Run a trade comparison (POST-body). |
| `create_asset_classification_group(group)` | `POST /api/v2/AssetClassification/ClassificationGroup` | Create an asset-classification group. |
| `create_custodian(payload)` | `POST /api/v2/Admin/Custodian` | Create a custodian (mutating). |
| `create_custodian_algo_instructions(custodian_id, payload)` | `POST /api/v2/Admin/Custodian/{custodian_id}/CustodianAlgoInstructions` | Create custodian algo instructions (mutating). |
| `create_esg_assignments(assignments)` | `POST /api/v2/ESG/Assignments` | Create ESG assignments. |
| `create_esg_theme(theme)` | `POST /api/v2/ESG/Themes` | Create an ESG theme. |
| `create_extract(extract_type, when=None)` | `POST /api/v2/Extracts/{extract_type}` | Create/schedule an extract job (mutating). |
| `create_model_from_aggs(payload)` | `POST /api/v2/Model/CreateFromModelAggs` | Create a model from model aggregates (mutating). |
| `create_notification(notification)` | `POST /api/v2/Notifications/Notification/CreateNotification` | Create a notification. |
| `create_sma_model(payload)` | `POST /api/v2/Model/SMA` | Create an SMA model (mutating). |
| `create_ticker_based_model(payload)` | `POST /api/v2/Model/TickerBasedModel` | Create a ticker-based model (mutating). |
| `create_workflow_context(context)` | `POST /api/v2/Workflow/contexts` | Create a workflow context (mutating). |
| `custom_import_add_row(instance_id, row)` | `POST /api/v2/CustomImports/Instances/AddRow/{instance_id}` | Add a row to a custom-import instance (mutating). |
| `custom_import_generate_override(instance_id)` | `POST /api/v2/CustomImports/Instances/GenerateOverride/{instance_id}` | Generate an override for a custom-import instance (mutating). |
| `custom_import_reupload_file(payload)` | `POST /api/v2/CustomImports/Instances/ReuploadFile` | Re-upload a custom-import file (mutating). |
| `custom_import_update_row(instance_id, row)` | `POST /api/v2/CustomImports/Instances/UpdateRow/{instance_id}` | Update a row in a custom-import instance (mutating). |
| `custom_import_upload_file(payload)` | `POST /api/v2/CustomImports/Instances/UploadFile` | Upload a custom-import file (mutating). |
| `custom_import_validate_rows(instance_id, rows)` | `POST /api/v2/CustomImports/Instances/ValidateRows/{instance_id}` | Validate rows in a custom-import instance. |
| `delete_account_set_aside_cash(payload)` | `POST /api/v2/SetAsideCash/DeleteAccountSetAsideCash` | Delete account set-aside cash (mutating). |
| `delete_asset_classification_group(group_id)` | `DELETE /api/v2/AssetClassification/ClassificationGroup/{group_id}` | Delete an asset-classification group. |
| `delete_astro_securities_restrictions(account_id, payload)` | `POST /api/v2/Account/AstroAccounts/{account_id}/DeleteSecuritiesRestrictions` | Delete Astro security restrictions for an account (mutating). |
| `delete_configuration(config_id)` | `DELETE /api/v2/Configuration/{config_id}` | Delete a configuration by ID (mutating). |
| `delete_custodian_algo_instructions(custodian_id, instruction_id)` | `DELETE /api/v2/Admin/Custodian/{custodian_id}/CustodianAlgoInstructions/{instruction_id}` | Delete custodian algo instructions (mutating). |
| `delete_deletable_trade_block_details(entity_id, entity_type_id)` | `DELETE /api/v2/TradeBlockDetails/DeletableDetails/{entity_id}/{entity_type_id}` | Delete the deletable trade-block details for an entity (mutating). |
| `delete_esg_themes(themes)` | `DELETE /api/v2/ESG/Themes` | Delete ESG themes. |
| `delete_extract(extract_type, reason=None)` | `DELETE /api/v2/Extracts/{extract_type}` | Delete extracts of a given type (mutating). |
| `delete_extract_job(job_id, reason=None)` | `DELETE /api/v2/Extracts/job/{job_id}` | Delete an extract job (mutating). |
| `delete_note(note_id)` | `DELETE /api/v2/Notes/{note_id}` | Delete a single note. |
| `delete_notes(notes)` | `POST /api/v2/Notes/DeleteList` | Delete notes (batch). |
| `delete_portfolio_set_aside_cash(payload)` | `POST /api/v2/SetAsideCash/DeletePortfolioSetAsideCash` | Delete portfolio set-aside cash (mutating). |
| `delete_saved_view(view_id)` | `DELETE /api/v2/SavedView/{view_id}` | Delete a saved view. |
| `delete_saved_views(view_ids)` | `POST /api/v2/SavedView/Delete` | Delete an array of saved views. |
| `delete_tag(tag)` | `POST /api/v2/Tags/delete` | Delete a tag. |
| `delete_trade_block_detail(detail_id)` | `DELETE /api/v2/TradeBlockDetails/{detail_id}` | Delete a single trade-block detail (mutating). |
| `delete_trade_block_details(payload)` | `POST /api/v2/TradeBlockDetails/DeleteList` | Delete trade-block details (batch, mutating). |
| `delete_trade_block_reason(reason_id)` | `DELETE /api/v2/TradeBlockReasons/{reason_id}` | Delete a trade-block reason (mutating). |
| `delete_workflow_context(context_id)` | `DELETE /api/v2/Workflow/contexts/{context_id}` | Delete a workflow context (mutating). |
| `download_custom_import_template(template_id)` | `POST /api/v2/CustomImports/Templates/Download/{template_id}` | Download a custom-import template. |
| `execute_saved_view(view_id)` | `GET /api/v2/SavedView/Execute/{view_id}` | Execute a saved view and return the number of records. |
| `expire_account_set_asides(payload)` | `PUT /api/v2/Account/Accounts/expireAccountSetAsides` | Expire account set-asides (mutating). |
| `export_import_history(payload)` | `POST /api/v2/DataImport/Export/ImportHistory` | Export import history (POST-body export). |
| `export_portfolios_grid()` | `POST /api/v2/Portfolio/Portfolios/list/export/excel/griddata` | Export the portfolios list as Excel grid data (mutating/export). |
| `export_reverse_sync_history(payload)` | `POST /api/v2/DataImport/Export/ReverseSyncHistory` | Export reverse-sync history (POST-body export). |
| `get_accessible_account_count()` | `GET /api/v2/Account/Accounts/AccessibleCount` | Get the count of accounts accessible to the authenticated user. |
| `get_accessible_portfolio_count()` | `GET /api/v2/Portfolio/Portfolios/AccessibleCount` | Get the count of portfolios accessible to the authenticated user. |
| `get_account(account_id) -> orionapi.models.AccountDetailResponseDto` | `GET /api/v2/Account/Accounts/{account_id}` | Get an account's detail (v2). |
| `get_account_by_external(external_firm_id, external_account_id)` | `GET /api/v2/Account/Accounts/byexternal/{external_firm_id}/{external_account_id}` | Get an account by external firm + account ID. |
| `get_account_cash_details(account_id) -> orionapi.models.AccountCashDetailsDto` | `GET /api/v2/Account/Accounts/{account_id}/CashDetails` | Get cash details for an account. |
| `get_account_dashboard()` | `GET /api/v2/Dashboard/AccountDashboard` | Get the data populating the account dashboard. |
| `get_account_excluded_cash_details(account_portfolio_id, id_type)` | `GET /api/v2/Account/Accounts/{account_portfolio_id}/{id_type}/modelTolerance/AccountExcludedCashDetails` | Get model-tolerance excluded-cash details for an account. |
| `get_account_gain_loss_summary(account_id) -> orionapi.models.AccountGainLossSummaryDto` | `GET /api/v2/Account/Accounts/{account_id}/GainLossSummary` | Get the gain/loss summary for an account. |
| `get_account_history(account_id, from_date=None, to_date=None)` | `GET /api/v2/Account/Accounts/{account_id}/History` | Get account history. |
| `get_account_model_history(account_id, from_date=None, to_date=None)` | `GET /api/v2/Account/Accounts/{account_id}/ModelHistory` | Get an account's model history. |
| `get_account_transactions(account_id, start_date=None, end_date=None)` | `GET /api/v2/Account/Accounts/{account_id}/Transactions` | Get account transactions over a date range. |
| `get_accounts(filter_id=None) -> orionapi.models.AccountListDto` | `GET /api/v2/Account/Accounts` | Get accounts (v2 list). |
| `get_advisor_number()` | `GET /api/v2/ServiceTeams/GetAdvisorNumber` | Get the advisor number. |
| `get_all_executing_destinations()` | `GET /api/v2/Admin/Custodian/GetAllExecutingDestinations` | Get all executing destinations. |
| `get_all_portfolio_account_errors()` | `GET /api/v2/DataErrors/GetAllPortfolioAccounts` | Get all portfolio/account data errors. |
| `get_all_portfolio_account_errors_count()` | `GET /api/v2/DataErrors/GetAllPortfolioAccountsCount` | Get the count of portfolio/account data errors. |
| `get_all_price_updates()` | `GET /api/v2/SecurityPriceChanges/GetAllUpdates` | Get all security price updates. |
| `get_allocation_instructions()` | `GET /api/v2/Admin/Custodian/GetAllocationInstructions` | Get allocation instructions. |
| `get_analytics_banner_status()` | `GET /api/v2/Analytics/BannerSpinner/Status` | Get the analytics banner-spinner status. |
| `get_analytics_run_config()` | `GET /api/v2/Analytics/RunAnalyticsConfig` | Get the run-analytics configurations. |
| `get_analytics_run_history()` | `GET /api/v2/Dashboard/AnalyticsRunHistory` | Get analytics run history (for the dashboard). |
| `get_asset_classification_groups()` | `GET /api/v2/AssetClassification/ClassificationGroups` | Get all asset-classification groups. |
| `get_asset_classification_methods()` | `GET /api/v2/AssetClassification/ClassificationMethods` | Get all asset-classification methods. |
| `get_assigned_models(payload)` | `POST /api/v2/Modeling/Models/GetAssignedModels` | Get assigned models (POST-body read). |
| `get_astro_account_filters()` | `GET /api/v2/Account/AstroAccounts/Filters` | Get the filters usable in the Astro-accounts endpoint. |
| `get_astro_account_investor_preferences(account_id, strategy_name=None, al_client_id=None)` | `GET /api/v2/Account/AstroAccounts/{account_id}/InvestorPreferences` | Get Astro investor preferences for an account. |
| `get_astro_account_log(account_id=None, batch_name=None, connect_firm_id=None)` | `GET /api/v2/Account/AstroAccounts/Log` | Get the Astro account optimization log. |
| `get_astro_account_message(account_id, batch_name, connect_firm_id=None)` | `GET /api/v2/Account/AstroAccounts/Message/Account/{account_id}/Batch/{batch_name}` | Get the Astro optimization message for an account/batch. |
| `get_astro_account_saved_investor_preferences(account_id)` | `GET /api/v2/Account/AstroAccounts/preference/{account_id}/InvestorPreferences` | Get the saved Astro investor preferences for an account. |
| `get_astro_account_securities_restrictions(account_id)` | `GET /api/v2/Account/AstroAccounts/{account_id}/SecuritiesRestrictions` | Get Astro security restrictions for an account. |
| `get_astro_accounts(filter=None)` | `GET /api/v2/Account/AstroAccounts` | Get Astro account values (including alert-determination data). |
| `get_astro_accounts_status_count(payload, unique_batch_identifier=None)` | `POST /api/v2/Account/AstroAccounts/Status/Count` | Get the Astro account status count for a batch (POST-body read). |
| `get_astro_accounts_status_detail(payload, unique_batch_identifier=None)` | `POST /api/v2/Account/AstroAccounts/Status/Detail` | Get the Astro account status detail for a batch (POST-body read). |
| `get_astro_all_templates()` | `GET /api/v2/Astro/AllTemplates` | Get Astro templates (Eclipse-UI route). |
| `get_astro_models()` | `GET /api/v2/Modeling/Models/Astro` | Get Astro models. |
| `get_astro_templates(al_client_id=None)` | `GET /api/v2/Astro/Templates` | Get the list of Astro templates. |
| `get_avg_import_duration(import_type=None, record_count_to_average=None)` | `GET /api/v2/DataImport/Action/AvgImportDuration` | Get the average import duration. |
| `get_calculate_contributions_for_sleeves()` | `GET /api/v2/TradeTool/CalculateContributionsForSleeves` | Calculate contributions for sleeves. |
| `get_community_models_by_list(payload)` | `POST /api/v2/Model/GetCommunityModelsByList` | Get community models for a list of identifiers (POST-body read). |
| `get_community_trade_queue_details(trade_queue_id)` | `GET /api/v2/Communities/tradeQueueDetails/{trade_queue_id}` | Get community trade-queue details. |
| `get_compare_tool_status(correlation_id)` | `GET /api/v2/CompareTool/Status/{correlation_id}` | Get the status of a compare-tool run. |
| `get_configuration(config_id)` | `GET /api/v2/Configuration/{config_id}` | Get a configuration by ID. |
| `get_custodian_algo_instruction(custodian_id, tag_info_id)` | `GET /api/v2/Admin/Custodian/{custodian_id}/CustodianAlgoInstructions/{tag_info_id}` | Get a custodian algo instruction by tag-info ID. |
| `get_custodian_algo_instructions(custodian_id)` | `GET /api/v2/Admin/Custodian/{custodian_id}/CustodianAlgoInstructions` | Get custodian algo instructions. |
| `get_custodian_algo_tag_info(tag_info_id)` | `GET /api/v2/Admin/Custodian/CustodianAlgoTagInfo/{tag_info_id}` | Get custodian algo tag info by ID. |
| `get_custodian_algo_tag_info_by_custodian(custodian_id)` | `GET /api/v2/Admin/Custodian/CustodianAlgoTagInfoByCustodian/{custodian_id}` | Get custodian algo tag info for a custodian. |
| `get_custodian_algo_tag_info_by_ids(payload)` | `POST /api/v2/Admin/Custodian/GetCustodianAlgoTagInfoByIds` | Get custodian algo tag info for a list of IDs (POST-body read). |
| `get_custodian_execution_settings(custodian_id)` | `GET /api/v2/Admin/Custodian/CustodianExecutionSettings` | Get execution settings for a custodian. |
| `get_custom_import_history()` | `GET /api/v2/CustomImports/Instances/History` | Get the custom-import instance history. |
| `get_custom_import_staged_data(instance_id)` | `GET /api/v2/CustomImports/Instances/StagedData/{instance_id}` | Get staged data for a custom-import instance. |
| `get_custom_import_template_definition(template_id)` | `GET /api/v2/CustomImports/Templates/Definition/{template_id}` | Get a custom-import template definition. |
| `get_custom_import_template_definition_by_instance(instance_id)` | `GET /api/v2/CustomImports/Templates/DefinitionByInstanceId/{instance_id}` | Get a custom-import template definition by instance ID. |
| `get_custom_import_templates()` | `GET /api/v2/CustomImports/Templates` | Get the custom-import templates. |
| `get_dashboard(dashboard_id)` | `GET /api/v2/Dashboard/{dashboard_id}` | Get a single dashboard layout by ID. |
| `get_dashboard_fields() -> list[orionapi.models.DashboardFieldDto]` | `GET /api/v2/Dashboard/Fields` | Get the available fields and categories usable on a dashboard. |
| `get_dashboards(user_id=None, team_id=None)` | `GET /api/v2/Dashboard` | Get user/team/firm-level dashboard layouts. |
| `get_data_imports_by_requested_by(requested_by_id)` | `GET /api/v2/DataImport/ByRequestedById/{requested_by_id}` | Get data imports requested by a given user. |
| `get_date_account_set_asides(condition=None, number_of_days=None)` | `GET /api/v2/Account/Accounts/dateaccountsetasides` | Get date-based account set-asides over a range. |
| `get_eclipse_firms_by_al_client_id(al_client_id)` | `GET /api/v2/Firm/GetEclipseFirmsByAlClientId/{al_client_id}` | Get Eclipse firms by AL client ID. |
| `get_editable_trade_block_reasons()` | `GET /api/v2/TradeBlockReasons/Editable` | Get the editable trade-block reasons. |
| `get_esg_assignments()` | `GET /api/v2/ESG/Assignments` | Get the firm-preference ESG assignments. |
| `get_esg_restrictions_for_portfolio(portfolio_id)` | `GET /api/v2/ESG/ESGRestrictionsForPortfolio` | Get ESG restrictions associated with a portfolio. |
| `get_esg_themes() -> list[orionapi.models.EsgThemeDto]` | `GET /api/v2/ESG/Themes` | Get the firm-preference ESG themes. |
| `get_executing_destinations_for_security_type(security_type_id)` | `GET /api/v2/Admin/Custodian/GetExecutingDestinationsWithTypeForSecurityType` | Get executing destinations (with type) for a security type. |
| `get_execution_destination_types()` | `GET /api/v2/Admin/Custodian/GetExecutionDestinationTypes` | Get execution-destination types. |
| `get_expired_set_asides_and_transactions(transactions_types=None, number_of_days=None)` | `GET /api/v2/Account/Accounts/expiredaccountsetasidesandtransactions` | Get expired account set-asides and the transactions that expired them. |
| `get_extracts(extract_type)` | `GET /api/v2/Extracts/{extract_type}` | Get extracts of a given type. |
| `get_feature_flag(feature_flag_name)` | `GET /api/v2/FeatureFlags/{feature_flag_name}` | Get the value of a feature flag. |
| `get_firm_entity_option_by_code(code)` | `GET /api/v2/OrionConnect/GetFirmEntityOptionByCode` | Get a firm entity option by code. |
| `get_firm_logo()` | `GET /api/v2/Firm/Logo` | Get the firm logo. |
| `get_firm_logo_base64()` | `GET /api/v2/Firm/Logo/Base64` | Get the firm logo as base64. |
| `get_firm_types()` | `GET /api/v2/Firm/FirmTypes` | Get the firm types. |
| `get_hidden_levers_durations()` | `GET /api/v2/Lookup/HiddenLeversDurations` | Get the available HiddenLevers risk-profile durations. |
| `get_hidden_levers_user_status(email)` | `GET /api/v2/Modeling/Models/UserStatus` | Get the HiddenLevers status (paid or free) of a user. |
| `get_import_log_history(from_date=None, to_date=None)` | `GET /api/v2/DataImport/ImportLogHistory` | Get the import-log history. |
| `get_last_import_status_info()` | `GET /api/v2/DataImport/Action/LastImportStatusInfo` | Get the last import status info. |
| `get_model_aggregate_analysis(model_id, is_include_cost_basis=None, is_include_trade_block_account=None, is_exclude_asset=None)` | `GET /api/v2/Modeling/Models/{model_id}/ModelAnalysis/ModelAggregate` | Get the model-aggregate detail for model analysis. |
| `get_model_analysis_v2(model_id, asset_type='securityset', is_include_cost_basis=None, is_include_trade_block_account=None, is_exclude_asset=None)` | `GET /api/v2/Modeling/Models/{model_id}/ModelAnalysis` | Get model analysis (v2) for a security set / category / class / subclass. |
| `get_model_levels(model_id)` | `GET /api/v2/Modeling/Models/{model_id}/Levels` | Get all the levels for a model. |
| `get_model_risk_profile(model_id, duration)` | `GET /api/v2/Model/{model_id}/RiskProfile/{duration}` | Get the HiddenLevers risk-profile information for a model. |
| `get_model_sync_oc_firms(model_id)` | `GET /api/v2/Model/GetModelSyncToOCFirms` | Get the Orion Connect firms available to sync a model to. |
| `get_model_types_v2()` | `GET /api/v2/Model/GetModelTypes` | Get all model types (v2). |
| `get_models_v2(filter=None, model_id=None, search=None, name=None)` | `GET /api/v2/Model/GetAllModels` | Get models via the v2 GetAllModels endpoint (rich filters). |
| `get_money_market_allocation_preference(related_type, related_type_id)` | `GET /api/v2/Preference/Preference/MoneyMarketPreference/Allocation/{related_type}/{related_type_id}` | Get money-market allocation preference values. |
| `get_money_market_allocation_preference_master(related_type)` | `GET /api/v2/Preference/Preference/MoneyMarketPreference/Allocation/{related_type}/Master` | Get the money-market allocation preference master (JSON structure). |
| `get_money_market_fund_preference(related_type, related_type_id)` | `GET /api/v2/Preference/Preference/MoneyMarketPreference/Fund/{related_type}/{related_type_id}` | Get money-market fund preference values. |
| `get_money_market_fund_preference_by_security(security_id)` | `GET /api/v2/Preference/Preference/MoneyMarketPreference/Fund/Security/{security_id}` | Get money-market fund preferences by security ID. |
| `get_money_market_fund_preference_master(related_type)` | `GET /api/v2/Preference/Preference/MoneyMarketPreference/Fund/{related_type}/Master` | Get the money-market fund preference master (JSON structure). |
| `get_money_market_preference_audit_history(start_date=None, end_date=None)` | `GET /api/v2/PreferenceAuditHistory/MoneyMarket` | Get money-market preference audit history. |
| `get_note_related_entities(entity_id, entity_type)` | `GET /api/v2/Notes/RelatedEntities` | Get entities related to a primary entity (for notes). |
| `get_notes(related_type, related_id)` | `GET /api/v2/Notes` | Get the notes for a related entity. |
| `get_notes_history(related_type, related_id, from_date=None, to_date=None)` | `GET /api/v2/Notes/History` | Get notes history for a related entity. |
| `get_optimization_account_messages(batch_id, account_id=None)` | `GET /api/v2/Optimization/summaries/{batch_id}/messages` | Get optimizer-emitted messages for an account in a batch. |
| `get_optimization_account_summary(batch_id, account_id=None)` | `GET /api/v2/Optimization/summaries/{batch_id}` | Get the optimization summary (and holdings) for an account in a batch. |
| `get_optimization_accounts(batch_id)` | `GET /api/v2/Optimization/accounts/{batch_id}` | Get the current state of accounts in an optimization batch. |
| `get_optimization_batch_account_summaries(batch_id)` | `GET /api/v2/Optimization/summaries/batch/{batch_id}` | Get every optimization summary belonging to a batch (one row per account). |
| `get_optimization_batch_status(batch_name)` | `GET /api/v2/Optimization/Status/Batch/{batch_name}` | Get the current status of a batch optimization. |
| `get_optimization_batch_summary(start_date=None, end_date=None)` | `GET /api/v2/Optimization/Summary/Batch` | Get batch optimization summary by date range (defaults to ~1 week). |
| `get_optimization_holdings_target(account_id, batch_name=None, al_client_id=None)` | `GET /api/v2/Optimization/HoldingsTarget/{account_id}` | Get the holdings and target strategies for an account in a batch. |
| `get_optimization_log(connect_account_id=None, batch_name=None, connect_firm_id=None)` | `GET /api/v2/Optimization/Log` | Get the optimization log. |
| `get_optimization_summaries(start_date=None, end_date=None)` | `GET /api/v2/Optimization/summaries` | Get optimization summaries, optionally filtered by a date range. |
| `get_outsource_trade_execution_firm(custodian_id)` | `GET /api/v2/Admin/Custodian/GetOutsourceTradeExecutionFirm` | Get the outsource trade-execution firm for a custodian. |
| `get_portfolio_accounts_v2(portfolio_id)` | `GET /api/v2/Portfolio/Portfolios/{portfolio_id}/Accounts` | Get a portfolio's accounts (v2). |
| `get_portfolio_allocations(portfolio_id)` | `GET /api/v2/Portfolio/Portfolios/{portfolio_id}/Allocations` | Get portfolio allocations. |
| `get_portfolio_allocations_security(portfolio_id, assign_by_security=None)` | `GET /api/v2/Portfolio/Portfolios/{portfolio_id}/PortfolioAllocationsSecurity` | Get portfolio allocations by security. |
| `get_portfolio_auto_rebalance_history(portfolio_id, start_date=None, end_date=None)` | `GET /api/v2/Portfolio/Portfolios/{portfolio_id}/AutoRebalanceHistory` | Get auto-rebalance history for a portfolio. |
| `get_portfolio_cash_details(portfolio_id)` | `GET /api/v2/Portfolio/Portfolios/CashDetails/{portfolio_id}` | Get cash details for a portfolio. |
| `get_portfolio_gain_loss_summary(portfolio_id)` | `GET /api/v2/Portfolio/Portfolios/{portfolio_id}/GainLossSummary` | Get the gain/loss summary for a portfolio. |
| `get_portfolio_list(filter=None, limit=None, offset=None)` | `GET /api/v2/Portfolio/Portfolios/GetPortfolioList` | Get the firm portfolio list (v2). |
| `get_portfolio_mac_history(portfolio_id, from_date=None, to_date=None)` | `GET /api/v2/Portfolio/Portfolios/{portfolio_id}/MacHistory` | Get portfolio MAC (model-assignment-change) history. |
| `get_portfolio_out_of_tolerance(model_id, asset_id, asset_type=None, model_element_id=None)` | `GET /api/v2/Portfolio/Portfolios/{model_id}/OutOfTolerance/{asset_id}` | Get out-of-tolerance portfolios for a model asset. |
| `get_portfolio_search(search=None, include_value=None, limit=None, offset=None)` | `GET /api/v2/Portfolio/Portfolios/GetPortfolioSearch` | Search firm portfolios (v2 paged search). |
| `get_portfolio_substitutions_history(portfolio_id, from_date=None, to_date=None)` | `GET /api/v2/Portfolio/Portfolios/{portfolio_id}/PortfolioSubstitutionsHistory` | Get a portfolio's substitutions history. |
| `get_portfolio_summary(portfolio_id)` | `GET /api/v2/Portfolio/Portfolios/summary/{portfolio_id}` | Get the portfolio summary (v2 beta). |
| `get_portfolio_team_history(portfolio_id, start_date=None, end_date=None)` | `GET /api/v2/Portfolio/Portfolios/{portfolio_id}/TeamHistory` | Get a portfolio's team history. |
| `get_portfolio_tree(portfolio_id=None, account_id=None)` | `GET /api/v2/Portfolio/Portfolios/PortfolioTree` | Get the portfolio/account hierarchy for a portfolio or account. |
| `get_portfolio_v2(portfolio_id) -> orionapi.models.PortfolioDetails` | `GET /api/v2/Portfolio/Portfolios/{portfolio_id}` | Get portfolio details (v2). |
| `get_portfolios_analytics_status(payload)` | `POST /api/v2/Analytics/GetPortfoliosAnalyticsStatus` | Get analytics status for a set of portfolios (POST-body read). |
| `get_portfolios_by_external_account_ids(payload)` | `POST /api/v2/Portfolio/Portfolios/PortfolioInfoByExternalAccountIdList` | Get portfolio info by a list of external account IDs (POST-body read). |
| `get_portfolios_by_group(portfolio_group_id)` | `GET /api/v2/Portfolio/Portfolios/ByPortfolioGroup/{portfolio_group_id}` | Get portfolios by portfolio-group ID. |
| `get_preference(preference_name)` | `GET /api/v2/Preference/Preference/GetPreference` | Get the value of a named preference. |
| `get_preference_securities(level_name, record_id)` | `GET /api/v2/Preference/Preference/{level_name}/Securities/{record_id}` | Get portfolio- or account-level preference securities. |
| `get_previous_business_day(reference_date)` | `GET /api/v2/BusinessDayRules/PreviousDay` | Get the previous business day relative to a reference date. |
| `get_price_updates_for_day(payload)` | `POST /api/v2/SecurityPriceChanges/GetSpecificDayUpdates` | Get security price updates for a specific day (POST-body read). |
| `get_product_classes()` | `GET /api/v2/OrionConnect/GetProductClasses` | Get OrionConnect product classes. |
| `get_restricted_plan_accounts(restricted_plan_id=None, external_plan_id=None)` | `GET /api/v2/Account/Accounts/RestrictedPlan` | Get the accounts linked to a restricted plan. |
| `get_reverse_sync_log_errors(import_id)` | `GET /api/v2/DataImport/ReverseSyncLogErrors/{import_id}` | Get reverse-sync log errors for an import. |
| `get_risk_categories()` | `GET /api/v2/OrionConnect/GetRiskCategories` | Get OrionConnect risk categories. |
| `get_saved_views(view_type_id, name=None)` | `GET /api/v2/SavedView/ViewType/{view_type_id}` | Get the current user's saved views for a view type. |
| `get_saved_views_for_types(view_type_ids)` | `POST /api/v2/SavedView/ViewType` | Get the current user's saved views for an array of view types (POST query). |
| `get_saved_views_ranked(view_type_id, simple_views=None, filter_required=None)` | `GET /api/v2/SavedView/ViewType/{view_type_id}/Rank` | Get the user's saved views for a view type, including rank/order. |
| `get_securities(security_id=None, is_cached=None)` | `GET /api/v2/Security/GetSecurities` | Get securities (v2). |
| `get_securities_by_name(payload)` | `POST /api/v2/Security/GetSecuritiesByNameAsync` | Get securities by name (async POST-body read). |
| `get_securities_by_oc_external_ids(payload)` | `POST /api/v2/Security/GetSecuritiesByOrionConnectExternalIds` | Get securities by Orion Connect external IDs (POST-body read). |
| `get_securities_by_ticker(payload)` | `POST /api/v2/Security/GetSecuritiesByTickerAsync` | Get securities by ticker (async POST-body read). |
| `get_securities_prices(payload)` | `POST /api/v2/Security/SecuritiesPrices` | Get prices for securities (POST-body read). |
| `get_security_models(payload)` | `POST /api/v2/Security/GetSecurityModels` | Get the models that use given securities (POST-body read). |
| `get_security_set_detail_history(security_set_id, from_date=None, to_date=None)` | `GET /api/v2/SecuritySet/{security_set_id}/DetailHistory` | Get the detailed change history for a security set. |
| `get_security_set_history(security_set_id, from_date=None, to_date=None)` | `GET /api/v2/SecuritySet/{security_set_id}/History` | Get the change history for a security set. |
| `get_security_sets_v2(security_set_id=None)` | `GET /api/v2/SecuritySet/GetSecuritySets` | Get security sets via the v2 GetSecuritySets endpoint. |
| `get_service_team()` | `GET /api/v2/ServiceTeams/GetServiceTeam` | Get the service team. |
| `get_service_teams(service_type=None)` | `GET /api/v2/ServiceTeams/GetServiceTeams` | Get service teams. |
| `get_set_aside_expiring_transactions(set_aside_id, set_aside_type=None)` | `GET /api/v2/SetAsideCash/SetAsideExpiringTransactions/{set_aside_id}` | Get the expiring transactions for a set-aside. |
| `get_set_asides(account_id=None, active_only=False)` | `POST /api/v2/Account/Accounts/SetAsideCashSettings` | Get set-aside cash reservations, including the Eclipse set-aside id. |
| `get_sleeve_allocations(account_id)` | `GET /api/v2/Portfolio/Sleeves/{account_id}/Allocations` | Get sleeve allocation details for an account. |
| `get_sleeve_contribution_methods()` | `GET /api/v2/Portfolio/Sleeves/SleeveContributionMethods` | Get all sleeve contribution methods. |
| `get_sleeve_distribution_methods()` | `GET /api/v2/Portfolio/Sleeves/SleeveDistributionMethods` | Get all sleeve distribution methods. |
| `get_sleeve_strategies()` | `GET /api/v2/Portfolio/Sleeves/SleeveStrategies` | Get all sleeve strategies. |
| `get_sleeve_strategies_by_firm_ids(payload)` | `POST /api/v2/Portfolio/Sleeves/SleeveStrategiesByFirmIds` | Get sleeve strategies for a list of firm IDs (POST-body read). |
| `get_sleeve_strategy_aggregates()` | `GET /api/v2/Portfolio/Sleeves/SleeveStrategyAggregates` | Get all sleeve strategy aggregates. |
| `get_sleeve_strategy_aggregates_by_firm_ids(payload)` | `POST /api/v2/Portfolio/Sleeves/SleeveStrategyAggregatesByFirmIds` | Get sleeve strategy aggregates for a list of firm IDs (POST-body read). |
| `get_sma_account_type_restrictions(category=None)` | `GET /api/v2{path}` | Get SMA account-type restriction values. |
| `get_strategist_models()` | `GET /api/v2/Modeling/Models/GetStrategistModels` | Get community models with their associated strategist (for the user). |
| `get_stress_test_results(payload)` | `POST /api/v2/Modeling/Models/StressTestResults` | Get HiddenLevers stress-test results (POST-body read). |
| `get_stress_test_scenarios()` | `GET /api/v2/Modeling/Models/StressTestScenarios` | Get HiddenLevers stress-test scenarios. |
| `get_tactical_account_cash_detail(portfolio_id)` | `GET /api/v2/Tactical/AccountAndCashDetail/{portfolio_id}` | Get account and cash detail for a portfolio (tactical view). |
| `get_tactical_model_analyzer(portfolio_id, account_id=None, aggregate_alternates=None)` | `GET /api/v2/Tactical/ModelAnalyzer/{portfolio_id}` | Get model-analyzer data for a portfolio (tactical view). |
| `get_tactical_portfolio_summary(portfolio_id) -> orionapi.models.TacticalPortfolioSummary` | `GET /api/v2/Tactical/PortfolioSummary/{portfolio_id}` | Get the tactical portfolio summary for a portfolio. |
| `get_tactical_restricted_securities(portfolio_id)` | `GET /api/v2/Tactical/RestrictedSecurities/{portfolio_id}` | Get restricted securities for a portfolio (tactical view). |
| `get_tactical_tax_lots(portfolio_id, account_id=None) -> list[orionapi.models.RankedTaxLots]` | `GET /api/v2/Tactical/TaxLots/{portfolio_id}` | Get tax-lot data for a portfolio (tactical view). |
| `get_tactical_trades(portfolio_id, account_id=None)` | `GET /api/v2/Tactical/Trades/{portfolio_id}` | Get trades for a portfolio (tactical view). |
| `get_tax_lot_depletion_preference(related_type, record_id, preference_value_id=None, inherited_preference_value_id=None)` | `GET /api/v2/Preference/Preference/{related_type}/taxLotDepletionMethodPreference/{record_id}` | Get tax-lot depletion-method preference values for a record. |
| `get_tax_lot_depletion_preference_master(related_type, preference_value_id=None, inherited_preference_value_id=None)` | `GET /api/v2/Preference/Preference/{related_type}/taxLotDepletionMethodPreference/Master` | Get the tax-lot depletion-method preference master (JSON structure). |
| `get_teams(external_id=None)` | `GET /api/v2/Team/Team/GetTeams` | Get teams. |
| `get_tlh_opportunity_flag(payload)` | `POST /api/v2/TradeTool/TlhOpportunityFlag` | Get the tax-loss-harvesting opportunity flag (POST-body read). |
| `get_todays_price_updates()` | `GET /api/v2/SecurityPriceChanges/GetTodaysUpdates` | Get today's security price updates. |
| `get_token_environment()` | `GET /api/v2/Admin/Token/Environment` | Get the token environment. |
| `get_token_info()` | `GET /api/v2/Admin/Token/Info` | Get token info for the authenticated session. |
| `get_trade_block_details_history(related_type, related_type_id, start_date=None, end_date=None)` | `GET /api/v2/TradeBlockDetails/History/{related_type}/{related_type_id}` | Get trade-block-detail history for an entity. |
| `get_trade_block_details_related_entities(entity_id, entity_type)` | `GET /api/v2/TradeBlockDetails/RelatedEntities` | Get entities related to a trade-block-detail entity. |
| `get_trade_block_fix_messages(trade_block_id)` | `GET /api/v2/Trading/Blocks/{trade_block_id}/FixMessages` | Get all FIX messages for a trade block. |
| `get_trade_block_reason_permissions_by_global_ids(global_ids)` | `POST /api/v2/TradeBlockReasons/TradeBlockReasonsPermissionByGlobalIds` | Get trade-block-reason permissions for a list of global IDs (POST-body read). |
| `get_trade_block_reason_permissions_by_role(role_id)` | `GET /api/v2/TradeBlockReasons/TradeBlockReasonPermissionsByRole/{role_id}` | Get trade-block-reason permissions for a role. |
| `get_trade_block_reason_role_permissions(reason_id)` | `GET /api/v2/TradeBlockReasons/{reason_id}/RolePermissions` | Get role permissions for a trade-block reason. |
| `get_trade_blocks(has_quodd=None, registration_status=None, get_adv=None)` | `GET /api/v2/Trading/Blocks` | Get trade blocks. |
| `get_trade_blocks_grid(block_ids, has_quodd=None, registration_status=None, get_adv=None)` | `GET /api/v2/Trading/Blocks/BlocksGrid` | Get trade-block data in the blocks-grid format for given block IDs. |
| `get_trade_execution_allocation_types()` | `GET /api/v2/Admin/tradeExecutionTypes/allocation` | Get trade-execution allocation types. |
| `get_trade_execution_sftp_config(trade_execution_type_id)` | `GET /api/v2/Admin/tradeExecutionTypes/{trade_execution_type_id}/sftpConfig` | Get the SFTP config for a trade-execution type. |
| `get_trade_execution_types()` | `GET /api/v2/Admin/tradeExecutionTypes/execution` | Get trade-execution types. |
| `get_trading_active_batch_jobs(start_date=None, end_date=None)` | `GET /api/v2/Trading/ActiveBatchJobs` | Get active batch-job entries for the user. |
| `get_trading_instance_trades(trade_instance_id)` | `GET /api/v2/Trading/TradeInstance/{trade_instance_id}/Trades` | Get the trades for a v2 trade instance. |
| `get_trading_instances(trade_instance_id=None, advisor_external_id=None, is_enabled=None, is_deleted=None)` | `GET /api/v2/Trading/TradeInstance` | Get trade instance(s) from the v2 Trading surface. |
| `get_trading_instances_by_date_range(start_date, end_date)` | `GET /api/v2/Trading/TradeInstance/GetByDateRange` | Get the trade-instance grid for a date range. |
| `get_trading_instances_for_user(start_date, end_date, offset=None, limit=None)` | `GET /api/v2/Trading/TradeInstance/ForUser` | Get trade instances for portfolios accessible to the user, by date range. |
| `get_trading_instances_paginated(start_date=None, end_date=None, portfolio_id=None, external_firm_id=None, external_account_id=None, skip=None, take=None)` | `GET /api/v2/Trading/TradeInstance/Paginated` | Get a paginated list of trade instances (without trades) plus a total count. |
| `get_trading_instances_with_trades(portfolio_id=None, start_date=None, end_date=None, order_status=None, skip=None, take=None)` | `GET /api/v2/Trading/TradeInstance/WithTrades` | Get a paginated list of trade instances including their trades. |
| `get_unexpired_set_asides_and_transactions(transactions_types=None, number_of_days=None)` | `GET /api/v2/Account/Accounts/unexpiredaccountsetasidesandtransactions` | Get unexpired account set-asides that had transactions. |
| `get_user(user_id)` | `GET /api/v2/User/{user_id}` | Get a user by ID. |
| `get_user_portfolio_ids()` | `GET /api/v2/Portfolio/Portfolios/GetUserPortfolioIds` | Get the portfolio IDs accessible to the authenticated user. |
| `get_workflow_context(context_id)` | `GET /api/v2/Workflow/contexts/{context_id}` | Get a workflow context by ID. |
| `get_workflow_contexts()` | `GET /api/v2/Workflow/contexts` | Get workflow contexts. |
| `get_workflow_mcp_server(server_id)` | `GET /api/v2/Workflow/mcp-servers/{server_id}` | Get a workflow MCP server by ID. |
| `get_workflow_mcp_servers()` | `GET /api/v2/Workflow/mcp-servers` | Get workflow MCP servers. |
| `get_workflow_tools()` | `GET /api/v2/Workflow/tools` | Get workflow tools. |
| `global_search(search=None, name=None, status=None, include_value=None, limit=None)` | `GET /api/v2/GlobalSearch/GlobalSearchList` | Global search across Eclipse entities (v2). |
| `list_accounts(body=None, filter_id=None, portfolio_id=None, limit=None, offset=None)` | `POST /api/v2/Account/Accounts/list` | List accounts via the v2 POST-body filtered endpoint. |
| `list_portfolios(body=None, filter_id=None, limit=None, offset=None)` | `POST /api/v2/Portfolio/Portfolios/list` | List portfolios via the v2 POST-body filtered endpoint. |
| `patch_portfolio(portfolio_id, payload)` | `PATCH /api/v2/Portfolio/Portfolios/{portfolio_id}` | Patch a portfolio (partial update, mutating). |
| `raise_cash_by_fund(payload)` | `POST /api/v2/TradeTool/RaiseCashByFund` | Generate a raise-cash-by-fund trade (pass isViewOnly in body for preview). |
| `raise_cash_distribution_full_rebalance(payload)` | `POST /api/v2/TradeTool/RaiseCashDistributionFullRebalance` | Generate a raise-cash-distribution full-rebalance trade. |
| `request_import(payload)` | `POST /api/v2/DataImport/Action/RequestImport` | Request a data import (mutating). |
| `reset_analytics_run_history()` | `GET /api/v2/Analytics/ResetAnalyticsRunHistory` | Reset the analytics run history (mutating). |
| `resync_import_errored_accounts()` | `POST /api/v2/DataImport/Action/ResyncImportErroredAccounts` | Resync accounts that errored during import (mutating). |
| `reverse_sync_portfolio_assignments(payload)` | `POST /api/v2/Portfolio/Portfolios/Action/ReverseSyncPortfolioAssignments` | Reverse-sync portfolio model assignments (mutating). |
| `run_analytics_v2(payload)` | `POST /api/v2/Analytics/RunAnalytics` | Run analytics (v2, mutating). |
| `save_astro_investor_preferences(account_id, payload)` | `PUT /api/v2/Account/AstroAccounts/preference/SaveInvestorPreferences/{account_id}` | Save Astro investor preferences for an account (mutating). |
| `save_saved_view(view)` | `POST /api/v2/SavedView/SavedViewByIdSave` | Save (create/update) a saved view for a specific view id. |
| `save_saved_views_ranking(view_type_id, views)` | `POST /api/v2/SavedView/ViewType/{view_type_id}/Rank` | Save the ranking/order of saved views for a view type. |
| `security_search(search, skip=None, take=None, external_firm_id=None, external_account_id=None)` | `GET /api/v2/SecuritySearch/SecuritySearchList` | Search securities (v2 UI search). |
| `send_notification(notification)` | `POST /api/v2/Notifications/Notification/SendNotification` | Send a notification. |
| `send_trading_notification(notification)` | `POST /api/v2/Notifications/Notification/SendTradingNotification` | Send a trading notification. |
| `set_account_preferences(preferences)` | `POST /api/v2/Preference/Preference/AccountPreferences` | Set account preferences. |
| `set_account_tags(payload)` | `PUT /api/v2/Account/Accounts/Tags` | Set tags on accounts (mutating). |
| `set_account_trade_block(payload)` | `PUT /api/v2/Account/Accounts/action/setAccountTradeBlock` | Set the trade-block state on accounts (mutating). |
| `set_accounts_do_not_trade_all_reverse_sync(payload)` | `POST /api/v2/Account/Accounts/donottradeallaccountsreversesync` | Reverse-sync the do-not-trade flag for all accounts (mutating). |
| `set_accounts_do_not_trade_reverse_sync(payload)` | `POST /api/v2/Account/Accounts/donottradereversesync` | Reverse-sync the do-not-trade flag for accounts (mutating). |
| `set_custom_import_template_favorite(payload)` | `POST /api/v2/CustomImports/Templates/SetUserFavorite` | Set a custom-import template as the user's favorite (mutating). |
| `set_default_saved_view(view_type_id, view_id)` | `POST /api/v2/SavedView/ViewType/{view_type_id}/DefaultView/{view_id}` | Set a view as the default view for a view type. |
| `set_portfolio_trade_block(payload)` | `PUT /api/v2/Portfolio/Portfolios/action/setPortfolioTradeBlock` | Set the trade-block state on portfolios (mutating). |
| `set_security_setting_equivalents(related_type, payload)` | `POST /api/v2/SecuritySettingPreference/Equivalents/{related_type}` | Set security-setting equivalents for a related type (mutating). |
| `set_trade_block_reason_permissions_by_role(role_id, payload)` | `PUT /api/v2/TradeBlockReasons/TradeBlockReasonPermissionsByRole/{role_id}` | Set trade-block-reason permissions for a role (mutating). |
| `set_trade_block_reason_role_permissions(reason_id, payload)` | `PUT /api/v2/TradeBlockReasons/{reason_id}/RolePermissions` | Set role permissions for a trade-block reason (mutating). |
| `start_astro_accounts(payload)` | `POST /api/v2/Account/AstroAccounts/Start` | Start an Astro batch for accounts (mutating). |
| `sync_accounts(payload)` | `POST /api/v2/DataImport/Action/SyncAccounts` | Sync accounts (mutating). |
| `sync_accounts_by_portfolio(payload)` | `POST /api/v2/DataImport/Action/SyncAccountsByPortfolio` | Sync accounts by portfolio (mutating). |
| `sync_community_model(payload)` | `POST /api/v2/Communities/SyncCommunityModel` | Sync a community model (mutating). |
| `sync_trade_analysis_report(payload)` | `POST /api/v2/TradeAnalysisReport/SyncTradeAnalysisReport` | Sync the trade-analysis report (mutating). |
| `trigger_security_set_reverse_sync(payload)` | `POST /api/v2/Model/Action/TriggerSecuritySetReverseSync` | Trigger a security-set reverse sync (mutating). |
| `update_account_details(account_id, details, with_reverse_sync=None)` | `PUT /api/v2/Account/Accounts/{account_id}/Details` | Update an account's details (mutating). |
| `update_analytics_status(payload)` | `POST /api/v2/Analytics/StatusUpdate` | Update the analytics status (mutating). |
| `update_asset_classification_group(group)` | `PUT /api/v2/AssetClassification/ClassificationGroup` | Update an asset-classification group. |
| `update_astro_account_investor_preferences(account_id, payload, al_client_id=None)` | `PUT /api/v2/Account/AstroAccounts/InvestorPreferences/{account_id}` | Update Astro investor preferences for an account (mutating). |
| `update_astro_fields()` | `POST /api/v2/Account/AstroAccounts/UpdateAstroFields` | Trigger an Astro-fields update (mutating). |
| `update_custodian_algo_instructions(custodian_id, instruction_id, payload)` | `PUT /api/v2/Admin/Custodian/{custodian_id}/CustodianAlgoInstructions/{instruction_id}` | Update custodian algo instructions (mutating). |
| `update_esg_restrictions_for_portfolio(restrictions)` | `PUT /api/v2/ESG/ESGRestrictionsForPortfolio` | Update the ESG restrictions for a portfolio. |
| `update_esg_theme(theme)` | `PUT /api/v2/ESG/Themes` | Update an ESG theme. |
| `update_money_market_allocation_preference(payload)` | `PUT /api/v2/Preference/Preference/UpdateMoneyMarketAllocationPreference` | Update money-market allocation preference. |
| `update_money_market_fund_preference(payload)` | `PUT /api/v2/Preference/Preference/UpdateMoneyMarketFundPreference` | Update money-market fund preference. |
| `update_note(note_id, note)` | `PUT /api/v2/Notes/{note_id}` | Update a single note. |
| `update_notes(notes)` | `POST /api/v2/Notes/UpdateList` | Update notes. |
| `update_notification(notification)` | `PUT /api/v2/Notifications/Notification/UpdateNotification` | Update a notification. |
| `update_restricted_plan(restricted_plan_id, payload)` | `PUT /api/v2/Account/Accounts/RestrictedPlan/{restricted_plan_id}` | Update a restricted plan (mutating). |
| `update_run_analytics_config(config_id, payload)` | `PUT /api/v2/Analytics/RunAnalyticsConfig/{config_id}` | Update a run-analytics configuration (mutating). |
| `update_security_preference_batch_job(payload)` | `PUT /api/v2/Preference/Preference/UpdateBatchJobForSecurityPreferenceChange` | Update the batch job for a security-preference change. |
| `update_trade_block_detail(detail_id, payload)` | `PUT /api/v2/TradeBlockDetails/{detail_id}` | Update a single trade-block detail (mutating). |
| `update_trade_block_details(payload)` | `POST /api/v2/TradeBlockDetails/UpdateList` | Update trade-block details (mutating). |
| `update_trade_execution_sftp_config(trade_execution_type_id, payload)` | `PUT /api/v2/Admin/tradeExecutionTypes/{trade_execution_type_id}/sftpConfig` | Update the SFTP config for a trade-execution type (mutating). |
| `update_workflow_context(context_id, context)` | `PUT /api/v2/Workflow/contexts/{context_id}` | Update a workflow context (mutating). |
| `upload_security_setting_equivalents(payload)` | `POST /api/v2/SecuritySettingPreference/Equivalents/Upload` | Upload security-setting equivalents (mutating). |
| `validate_community_model_unassign(payload, apply_delete=None)` | `POST /api/v2/Communities/ModelUnAssignValidation` | Validate (and optionally apply) a community-model unassign (mutating when applied). |
| `withdraw_astro_cash(payload)` | `POST /api/v2/Account/AstroAccounts/WithdrawCash` | Withdraw cash via Astro (mutating). |

## Eclipse

Best-of-both Eclipse client composing :class:`EclipseV1` and :class:`EclipseV2`.

**1 methods.**

| Method | Endpoint | Description |
|---|---|---|
| `get_set_asides(account_id=None, active_only=False)` |  | Set-asides via the v2 batch endpoint (best: firm-wide + set-aside id). |
