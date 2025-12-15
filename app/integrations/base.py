import logging
import time

import requests
from requests.adapters import HTTPAdapter, Retry

logger = logging.getLogger(__name__)


class BaseClient:
    headers = {}
    timeout = 0
    ClientName = None
    status_code = None

    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=0, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.response = {}

    def _make_request(self, method: str, url: str, data=None, params=None):
        self.start_time = time.time()
        response = None
        try:
            logger.info(f"Making {method} request to {url} with data: {data}")
            response = self.session.request(
                method,
                url,
                json=data,
                headers=self.headers,
                timeout=self.timeout,
                params=params
            )

            self.response = response.json()
            self.status_code = response.status_code
            return self.response, self.status_code

        except requests.exceptions.Timeout:
            self.status_code = 408
            self.response = {"message": "request timeout"}
            logger.warning(f"Request to {url} timed out")
            return None, self.status_code

        except requests.exceptions.HTTPError as http_err:
            self.status_code = response.status_code if response else 500
            try:
                self.response = response.json() if response else {}
            except ValueError:
                self.response = {"message": "non-json response"}
            logger.error(f"HTTP error {self.status_code}: {http_err}")
            return None, self.status_code

        except requests.exceptions.RequestException as req_err:
            self.status_code = 500
            self.response = {"message": str(req_err)}
            logger.error(f"Request exception: {req_err}")
            return None, self.status_code

        except Exception as err:
            self.status_code = 500
            self.response = {"message": str(err)}
            logger.error(f"Unexpected error: {err}")
            return None, self.status_code
