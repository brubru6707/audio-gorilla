# Unit Tests

This directory contains comprehensive unit tests for each API class. Each test file focuses on testing every single function in each API independently, with individual test methods for each function and its various parameters.

## Test Files

- `test_slack_api.py` - Comprehensive tests for all Slack API functions
- `test_walmart_marketplace_api.py` - Comprehensive tests for all Walmart Marketplace API functions  
- `test_smart_home_api.py` - Comprehensive tests for all Smart Home API functions
- `test_netflix_api.py` - Comprehensive tests for all Netflix API functions

## Test Structure

Each test file is organized into sections that test every single function in the respective API:

### Slack API Tests (`test_slack_api.py`)
- **Chat Methods**: `chat_postMessage`, `chat_postEphemeral`, `chat_update`, `chat_delete`, `chat_scheduleMessage`, `chat_deleteScheduledMessage`
- **Conversations Methods**: `conversations_list`, `conversations_open`, `conversations_close`, `conversations_join`, `conversations_leave`, `conversations_info`, `conversations_history`, `conversations_replies`, `conversations_setTopic`, `conversations_setPurpose`, `conversations_rename`, `conversations_create`
- **Users Methods**: `users_list`, `users_info`, `users_lookupByEmail`, `users_conversations`, `users_getPresence`
- **Search Methods**: `search_messages`, `search_files`, `search_all`
- **Reminders Methods**: `reminders_add`, `reminders_list`, `reminders_complete`, `reminders_delete`, `reminders_info`
- **Files Methods**: `files_upload`, `files_list`, `files_info`, `files_delete`
- **Reactions Methods**: `reactions_add`, `reactions_remove`, `reactions_get`, `reactions_list`
- **Pins Methods**: `pins_add`, `pins_remove`, `pins_list`
- **DND Methods**: `dnd_setSnooze`, `dnd_endSnooze`, `dnd_endDnd`, `dnd_info`
- **Team Methods**: `team_info`

### Walmart Marketplace API Tests (`test_walmart_marketplace_api.py`)
- **Items Methods**: `get_items`, `get_item`, `update_item`, `retire_item`, `bulk_item_upload`, `get_bulk_item_status`
- **Inventory Methods**: `get_inventory`, `update_inventory`, `bulk_inventory_update`, `get_bulk_inventory_status`
- **Orders Methods**: `get_orders`, `get_order`, `acknowledge_order`, `ship_order`, `cancel_order`, `refund_order`, `get_order_shipment`, `get_order_advance_shipment_notice`
- **Price Methods**: `get_price`, `update_price`, `bulk_price_update`, `get_bulk_price_status`
- **Promotions Methods**: `get_promotions`, `create_promotion`, `update_promotion`, `get_promotion`
- **Reports Methods**: `get_reports`, `request_report`, `download_report`
- **Feeds Methods**: `get_feeds`, `get_feed_status`
- **Returns Methods**: `get_returns`, `get_return`, `approve_return`, `reject_return`

### Smart Home API Tests (`test_smart_home_api.py`)
- **Switch Methods**: `on`, `off`
- **Switch Level Methods**: `setLevel`
- **Color Control Methods**: `setColor`, `setHue`, `setSaturation`
- **Lock Methods**: `lock`, `unlock`
- **Lock Codes Methods**: `setCode`, `requestCode`, `deleteCode`, `reloadAllCodes`, `setCodeLength`, `updateCodes`
- **Thermostat Cooling Setpoint Methods**: `setCoolingSetpoint`
- **Thermostat Fan Mode Methods**: `fanAuto`, `fanOn`, `setThermostatFanMode`
- **Media Playback Methods**: `fastForward`, `pause`, `stop`
- **Controller API Methods**: `getClient`, `getDevice`, `readCapability`

### Netflix API Tests (`test_netflix_api.py`)
- **Profiles Methods**: `profiles_list`, `profiles_get`, `profiles_create`, `profiles_update`, `profiles_delete`
- **Watchlist Methods**: `watchlist_add`, `watchlist_remove`, `watchlist_list`
- **Ratings Methods**: `ratings_add`, `ratings_remove`, `ratings_list`
- **Recommendations Methods**: `recommendations_get`, `recommendations_because_you_watched`
- **Search Methods**: `search_content`, `search_suggestions`
- **Continue Watching Methods**: `continue_watching_list`, `continue_watching_update`
- **Trending Methods**: `trending_get`, `trending_movies`, `trending_shows`
- **Categories Methods**: `categories_list`, `categories_get`
- **Subscription Methods**: `get_subscription_info`, `subscription_plans`, `subscription_cancel`
- **Devices Methods**: `devices_list`, `devices_remove`, `devices_logout_all`
- **Notifications Methods**: `notifications_list`, `notifications_mark_read`, `notifications_mark_all_read`
- **Favorites Methods**: `favorites_add`, `favorites_remove`, `favorites_list`
- **Parental Controls Methods**: `parental_controls_get`, `parental_controls_update`
- **Viewing Activity Methods**: `viewing_activity_add`, `viewing_activity_list`, `viewing_activity_clear`

## Test Coverage

Each function is tested with:
- **Basic functionality** - Normal operation with standard parameters
- **Parameter variations** - Different parameter combinations and values
- **Edge cases** - Boundary values, empty/null values, extreme values
- **Error conditions** - Invalid inputs, nonexistent resources, error states
- **State transitions** - Multiple operations on the same resource
- **Concurrent operations** - Operations on different components simultaneously

## Running Tests

Each test file is completely self-contained and can be executed directly with Python’s built-in `unittest` runner. There is no longer a separate `run_tests.py` runner script.

### Run All Tests in the Suite

```bash
# Discover and run everything in the unit_tests directory
python -m unittest discover unit_tests
```

### Run a Specific API’s Test File

```bash
# Slack API tests
python -m unittest unit_tests.test_slack_api

# Netflix API tests
python -m unittest unit_tests.test_netflix_api

# Walmart Marketplace API tests
python -m unittest unit_tests.test_walmart_marketplace_api

# Smart Home API tests
python -m unittest unit_tests.test_smart_home_api
```

### Run a Single Test Method

```bash
python -m unittest unit_tests.test_slack_api.TestSlackAPI.test_chat_postMessage_basic
```

### Filtering Tests

Use unittest’s `-k` pattern matching or other CLI flags to filter and control output. For example:

```bash
# Run only tests whose names start with "test_chat_"
python -m unittest unit_tests.test_slack_api.TestSlackAPI -k test_chat_

# Verbose output
python -m unittest -v unit_tests.test_slack_api
```

## Test Organization

Each test file follows this structure:
1. **Setup** - Initialize API instances in `setUp()`