import unittest

from datetime import datetime, timedelta
import pandas as pd
from src.main import (
    fetch_historical_data,
    fetch_current_price_data,
    fetch_last_checked_price,
    get_available_products,
    check_and_execute_buy,
    check_and_execute_sell_order,
    main

)

from unittest.mock import patch, MagicMock, ANY

class TestExitLoopException(Exception):
    pass

def exit_loop():
    raise TestExitLoopException("Exiting loop for test")


class TestCryptoBot(unittest.TestCase):

    @patch('src.main.requests.get')  # Updated patch path
    def test_fetch_historical_data_success(self, mock_get):
        # Mock the response from the API call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            [1609459200, 29000, 29500, 29300, 29400, 100.0],  # Sample data
            # ... more sample data
        ]
        mock_get.return_value = mock_response

        start_time = datetime.now() - timedelta(days=1)
        end_time = datetime.now()
        granularity = 300
        product_id = 'BTC-USD'

        # Call the function with the mocked API response
        data = fetch_historical_data(product_id, start_time, end_time, granularity)

        # Assertions to verify function behavior
        self.assertIsNotNone(data)
        self.assertIsInstance(data, pd.DataFrame)
        self.assertFalse(data.empty)
        # ... more assertions as needed

    # add more test methods here to test different scenarios


@patch('src.main.requests.get')  # Patch the 'requests.get' call within 'fetch_current_price_data' function
def test_fetch_current_price_data_success(self, mock_get):
    # Mock the response from the API call
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'price': '50000.0'  # Sample price data
    }
    mock_get.return_value = mock_response

    product_id = 'BTC-USD'

    # Call the function with the mocked API response
    price = fetch_current_price_data(product_id)

    # Assertions to verify function behavior
    self.assertIsNotNone(price)
    self.assertEqual(price, 50000.0)  # Assert that the returned price is as expected

@patch('src.main.pd.read_csv')
def test_fetch_last_checked_price_success(self, mock_read_csv):
    # Mock reading from a CSV file
    mock_read_csv.return_value = pd.DataFrame({
        'product_id': ['BTC-USD', 'ETH-USD'],
        'close': [45000.0, 3000.0]
    })

    product_id = 'BTC-USD'
    # Call the function
    last_checked_price = fetch_last_checked_price(product_id)

    # Assertions to verify function behavior
    self.assertEqual(last_checked_price, 45000.0)

@patch('src.main.requests.get')
def test_get_available_products_success(self, mock_get):
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {'id': 'BTC-USD', 'trading_disabled': False},
        {'id': 'ETH-USD', 'trading_disabled': True},  # This product should be filtered out
    ]
    mock_get.return_value = mock_response

    # Call the function
    available_products = get_available_products()

    # Assertions to verify function behavior
    self.assertIn('BTC-USD', available_products)
    self.assertNotIn('ETH-USD', available_products)  # ETH-USD should not be in the list because trading is disabled

@patch('src.main.requests.post')
@patch('src.main.fetch_current_price_data')
@patch('src.main.fetch_historical_data')

def test_check_and_execute_buy(self, mock_fetch_historical, mock_fetch_current, mock_post):
        # Setup mock responses
        mock_fetch_historical.return_value = pd.DataFrame({'open': [44000], 'close': [50000]})
        mock_fetch_current.return_value = 51000.0

        # Mock response for the POST request to execute buy order
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {'filled_size': 1.0, 'executed_value': 51000.0}
        mock_post.return_value = mock_post_response

        # Run the function with test data
        product_id = 'BTC-USD'
        last_checked_price = 45000.0
        result = check_and_execute_buy(product_id, last_checked_price)

        # Assertions
        mock_fetch_historical.assert_called_with(product_id, ANY, ANY, ANY)  # Replace ANY  arguments
        mock_fetch_current.assert_called_with(product_id)
        mock_post.assert_called()

        # Assert based on your function's logic and return value
        # Update this assertion based on what your function returns or should return
        self.assertFalse(result)

@patch('src.main.requests.post')
@patch('src.main.fetch_current_price_data')
def test_check_and_execute_sell_order(self, mock_fetch_current, mock_post):
        # Initialize global variables
        global held_crypto, owned_crypto
        held_crypto = {
            'product_id': 'BTC-USD',
            'purchase_price': 45000.0,
            'amount': 1.0,
            'time': datetime.now()
        }
        owned_crypto = True

        # Setup mock responses
        mock_fetch_current.return_value = {'price': 47000.0}  # Current price is higher than purchase price
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {}  # Response data structure after a successful sell
        mock_post.return_value = mock_post_response

        # Call the function with test data
        product_id = 'BTC-USD'
        purchase_price = 45000.0
        highest_price = 48000.0
        previous_price = 47000.0
        purchase_time = datetime.now() - timedelta(hours=2)
        result = check_and_execute_sell_order(product_id, purchase_price, highest_price, previous_price, purchase_time)

        # Assertions
        mock_fetch_current.assert_called_with(product_id)
        mock_post.assert_called()

        # Assert based on  function's logic and return value
        self.assertTrue(result)# If the sell was successful, the result should be True



class TestMainFunction(unittest.TestCase):
    @patch('src.main.time.sleep', side_effect=exit_loop)
    @patch('src.main.fetch_current_price_data')
    @patch('src.main.get_available_products')
    @patch('src.main.fetch_last_checked_price')
    @patch('src.main.check_and_execute_buy')
    @patch('src.main.check_and_execute_sell_order')
    @patch('src.main.rate_limiter')
    def test_main(self, mock_rate_limiter, mock_sell, mock_buy, mock_last_price, mock_available_products,
                  mock_current_price, mock_sleep):
        # Mock the available products to control the flow in the main function
        mock_available_products.return_value = ['BTC-USD']

        # Mock the last checked price
        mock_last_price.return_value = 45000.0

        # Mock the buy function to simulate a buy operation
        mock_buy.return_value = True

        # Mock the sell function to simulate a sell operation
        mock_sell.return_value = False

        # Set global variables
        global owned_crypto, held_crypto
        owned_crypto = False
        held_crypto = None

        # Run the main function and handle the custom exception to exit the loop
        try:
            main()
        except TestExitLoopException:
            pass  # Expected exception to exit the loop

        # Assert that fetch_current_price_data was called
        mock_current_price.assert_called()

        # Assert that the rate limiter was called
        mock_rate_limiter.assert_called()

        # Assert that check_and_execute_buy was called
        mock_buy.assert_called_with('BTC-USD', 45000.0)

        # Reset the global variables to their initial state if necessary
        owned_crypto = False
        held_crypto = None


if __name__ == '__main__':
    unittest.main()
