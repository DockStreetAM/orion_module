# Plan: Expand OrionAPI for Households, Registrations, Accounts & Custom Fields

## Goal
Add methods to OrionAPI class for reading and updating households, registrations, and accounts - including their custom fields.

## Phase 1: Custom Field Definitions
First, we need to retrieve custom field definitions to know field codes.

**Methods to add:**
- `get_custom_field_definitions(entity)` - entity is 'client', 'registration', or 'account'

**Endpoint (needs testing):**
- `GET /Settings/UserDefinedFields/Definitions/{entity}`

**Returns:** List of field definitions with code, description, type, options, etc.

---

## Phase 2: Households (Clients)

**Methods to add:**
- `search_clients(search_term, top=20, is_active=True)` - search by name
- `get_client(id)` - get full details including custom fields
- `update_client(id, data)` - update client fields including custom fields

**Endpoints:**
- `GET /Portfolio/Clients/Simple/Search?search={term}&top={n}&isActive={active}`
- `GET /Portfolio/Clients/{id}`
- `PUT /Portfolio/Clients/{id}`

---

## Phase 3: Registrations

**Methods to add:**
- `search_registrations(search_term, top=20, is_active=True)` - search by name
- `get_registration(id)` - get full details including custom fields
- `get_client_registrations(client_id, is_active=True)` - get registrations for a household
- `update_registration(id, data)` - update registration fields including custom fields
- `get_registration_types()` - list available registration types (IRA, 401k, etc.)

**Endpoints:**
- `GET /Portfolio/Registrations/Simple/Search?search={term}&top={n}&isActive={active}`
- `GET /Portfolio/Registrations/{id}`
- `GET /Portfolio/Clients/{id}/Registrations?isActive={active}`
- `PUT /Portfolio/Registrations/{id}`
- `GET /Portfolio/Registrations/Types`

---

## Phase 4: Accounts

**Methods to add:**
- `search_orion_accounts(search_term, top=20, is_active=True)` - search by name/number
- `get_orion_account(id)` - get full details including custom fields
- `update_orion_account(id, data)` - update account fields including custom fields

**Endpoints:**
- `GET /Portfolio/Accounts/Simple/Search?search={term}&top={n}&isActive={active}`
- `GET /Portfolio/Accounts/{id}`
- `PUT /Portfolio/Accounts/{id}`

**Note:** Named `_orion_account` to distinguish from EclipseAPI account methods.

---

## Phase 5: Convenience Methods for Custom Fields

**Methods to add:**
- `set_client_custom_field(client_id, field_code, value)` - update single custom field
- `set_registration_custom_field(reg_id, field_code, value)` - update single custom field
- `set_account_custom_field(account_id, field_code, value)` - update single custom field

These would:
1. GET current entity
2. Update just the custom field value
3. PUT back

---

## Implementation Order
1. Custom field definitions (Phase 1) - needed to understand field codes
2. Households (Phase 2) - most commonly needed
3. Accounts (Phase 4) - second most common
4. Registrations (Phase 3) - less frequently needed
5. Convenience methods (Phase 5) - nice to have

## Testing Approach
- Test each GET endpoint first to verify response structure
- Test search endpoints with known data
- Test updates on non-production data or with reversible changes

## Open Questions
- Confirm GET endpoint for custom field definitions works
- Determine exact payload structure for PUT updates (may need to fetch update template first)
- Check if there are batch update endpoints for efficiency
