import unittest
from unittest.mock import patch, MagicMock

from src.main import main

class TestExitLoopException(Exception):
    pass

def exit_loop():
    raise TestExitLoopException("Exiting loop for test")

class TestMainFunction(unittest.TestCase):
    @patch('src.main.time.sleep', side_effect=exit_loop)
    @patch('src.main.fetch_current_price_data')
    @patch('src.main.get_available_products')
    @patch('src.main.fetch_last_checked_price')
    @patch('src.main.check_and_execute_buy')
    @patch('src.main.check_and_execute_sell_order')
    @patch('src.main.rate_limiter')
    def test_main(self, mock_rate_limiter, mock_sell, mock_buy, mock_last_price, mock_available_products, mock_current_price, mock_sleep):
        # Mock the available products to control the flow in the main function, remind self to pay attention just cause it runs doesn mean it will be right...
        mock_available_products.return_value = ['BTC-USD']#so we will use this jsut to test but remeber to maybe add a user input to test also so scraping will work when we add that..

        # Mock the last checked price
        mock_last_price.return_value = 45000.0

        # Mock the buy function to simulate a buy operation
        mock_buy.return_value = True

        # Mock the sell function to simulate a sell operation
        mock_sell.return_value = False

        # Set global variables to initial state
        global owned_crypto, held_crypto
        owned_crypto = False
        held_crypto = None

        # Run the main function and handle the custom exception to exit the loop
        try:
            main()
        except TestExitLoopException:
            pass  # Expected exception to exit the loop

        # Make sure that fetch_current_price_data was called
        mock_current_price.assert_called()

        # Make sure that the rate limiter was called,, IMPORTANT!!!!!!!!!!!!!! 
        mock_rate_limiter.assert_called()

        # Assert that check_and_execute_buy was called
        mock_buy.assert_called_with('BTC-USD', 45000.0)

        # Reset the global variables to their initial state if necessary
        owned_crypto = False
        held_crypto = None

if __name__ == '__main__':
    unittest.main()
