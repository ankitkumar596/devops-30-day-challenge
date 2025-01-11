import unittest
from unittest.mock import patch, MagicMock
import json
from weather_dashboard import WeatherDashboard

class TestWeatherDashboard(unittest.TestCase):

    @patch('boto3.client')
    def test_create_bucket_if_not_exists(self, mock_boto_client):
        # Mocking the S3 client and its methods
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        # Mock head_bucket to simulate that the bucket exists
        mock_s3_client.head_bucket.return_value = None
        
        dashboard = WeatherDashboard()
        dashboard.create_bucket_if_not_exists()
        mock_s3_client.head_bucket.assert_called_with(Bucket=dashboard.bucket_name)

        # Simulate a bucket creation failure
        mock_s3_client.head_bucket.side_effect = Exception("Bucket doesn't exist")
        dashboard.create_bucket_if_not_exists()
        mock_s3_client.create_bucket.assert_called_with(Bucket=dashboard.bucket_name)

    @patch('requests.get')
    def test_fetch_weather(self, mock_requests_get):
        # Mocking the requests.get to return a fake weather response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'main': {'temp': 72, 'feels_like': 70, 'humidity': 50},
            'weather': [{'description': 'clear sky'}]
        }
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response
        
        dashboard = WeatherDashboard()
        weather_data = dashboard.fetch_weather('Philadelphia')
        
        self.assertEqual(weather_data['main']['temp'], 72)
        self.assertEqual(weather_data['weather'][0]['description'], 'clear sky')

    @patch('boto3.client')
    def test_save_to_s3(self, mock_boto_client):
        # Mocking the S3 client and its methods
        mock_s3_client = MagicMock()
        mock_boto_client.return_value = mock_s3_client

        weather_data = {
            'main': {'temp': 72, 'feels_like': 70, 'humidity': 50},
            'weather': [{'description': 'clear sky'}]
        }

        dashboard = WeatherDashboard()
        success = dashboard.save_to_s3(weather_data, 'Philadelphia')
        self.assertTrue(success)
        mock_s3_client.put_object.assert_called_once()

if __name__ == '__main__':
    unittest.main()
