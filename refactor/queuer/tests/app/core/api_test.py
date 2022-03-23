import os
import mock
import requests
from app.core.api import DataService, APIService

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, './_test_assets/result.pkl')


class TestAPIService:

    mocked_json = {
        "test": "dict"
    }

    mocked_params = {
        "test": "params"
    }

    mocked_data = {
        "test": "data"
    }

    mocked_files = {
        "filename": b"" 
    }

    mocked_base_url = "http://example.com"
    mocked_route = "/route"
    mocked_endpoint = "http://example.com/route"

    def test_base_uri_set(self):
        # test that / suffix appended
        api_service = APIService(self.mocked_base_url)
        assert api_service.BASE_URI == "http://example.com/"
        # test that base uri is not altered when trailing "/"
        api_service = APIService(f"{self.mocked_base_url}/")
        assert api_service.BASE_URI == "http://example.com/"
        

    @mock.patch.object(APIService, '_format', autospec=True)
    @mock.patch.object(requests, 'post', autospec=True)
    def test_post(self, request_post_mock, api_service_format_mock):
        api_service = APIService(self.mocked_base_url)
        api_service.post(
            self.mocked_route, 
            json=self.mocked_json, 
            params=self.mocked_params, 
            data=self.mocked_data, 
            files=self.mocked_files
        )
        api_service_format_mock.assert_called()
        request_post_mock.assert_called_once_with(
            self.mocked_endpoint, 
            json=self.mocked_json, 
            params=self.mocked_params, 
            data=self.mocked_data, 
            files=self.mocked_files
        )

    @mock.patch.object(APIService, '_format', autospec=True)
    @mock.patch.object(requests, 'get', autospec=True)
    def test_get(self, request_get_mock, api_service_format_mock):
        api_service = APIService(self.mocked_base_url)
        api_service.get(self.mocked_route, params=self.mocked_params)
        api_service_format_mock.assert_called()
        request_get_mock.assert_called_once_with(self.mocked_endpoint, params=self.mocked_params)

    @mock.patch.object(APIService, '_format', autospec=True)
    @mock.patch.object(requests, 'delete', autospec=True)
    def test_delete(self, request_delete_mock, api_service_format_mock):
        api_service = APIService(self.mocked_base_url)
        api_service.delete(self.mocked_route, params=self.mocked_params)
        api_service_format_mock.assert_called()
        request_delete_mock.assert_called_once_with(self.mocked_endpoint, params=self.mocked_params)

    @mock.patch.object(APIService, '_format', autospec=True)
    @mock.patch.object(requests, 'patch', autospec=True)
    def test_patch(self, request_patch_mock, api_service_format_mock):
        api_service = APIService(self.mocked_base_url)
        api_service.patch(self.mocked_route, json=self.mocked_json, params=self.mocked_params, data=self.mocked_data)
        api_service_format_mock.assert_called()
        request_patch_mock.assert_called_once_with(self.mocked_endpoint, json=self.mocked_json, params=self.mocked_params, data=self.mocked_data)
        
    @mock.patch.object(APIService, '_format', autospec=True)
    @mock.patch.object(requests, 'put', autospec=True)
    def test_put(self, request_put_mock, api_service_format_mock):
        api_service = APIService(self.mocked_base_url)
        api_service.put(self.mocked_route, json=self.mocked_json, params=self.mocked_params, data=self.mocked_data)
        api_service_format_mock.assert_called()
        request_put_mock.assert_called_once_with(self.mocked_endpoint, json=self.mocked_json, params=self.mocked_params, data=self.mocked_data)
