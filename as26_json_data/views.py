import json
import requests
import re
import datetime
import time
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def api_request_with_retry(method: str, url: str, retries: int = 3, delay: int = 2, **kwargs):
    attempt = 0
    while attempt < retries:
        try:
            # Log input data
            logger.info(f"API Request Input (Attempt {attempt + 1}/{retries}):")
            logger.info(f"Method: {method}")
            logger.info(f"URL: {url}")
            logger.info(f"Headers: {json.dumps(kwargs.get('headers', {}), indent=2)}")
            if 'data' in kwargs:
                logger.info(f"Payload: {kwargs['data']}")
            if 'cookies' in kwargs:
                logger.info(f"Cookies: {json.dumps(kwargs['cookies'], indent=2)}")
            
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Log output data
            logger.info(f"API Response Output (Attempt {attempt + 1}/{retries}):")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Headers: {json.dumps(dict(response.headers), indent=2)}")
            logger.info(f"Response Body: {response.text[:1000]}")  # Limit body to avoid huge output
            logger.info("-" * 50)
            
            return response
        except requests.HTTPError as e:
            attempt += 1
            logger.error(f"HTTP Error (Attempt {attempt}/{retries}): {str(e)}")
            logger.error(f"Response Content: {e.response.text if e.response else 'No response content'}")
            if attempt == retries:
                raise
            time.sleep(delay)
        except requests.RequestException as e:
            attempt += 1
            logger.error(f"Request Failed (Attempt {attempt}/{retries}): {str(e)}")
            if attempt == retries:
                raise
            time.sleep(delay)
    return None

class TDSFileDownloadView(APIView):
    def post(self, request):
        # Validate input data
        data = request.data
        if not isinstance(data, dict):
            logger.error("Invalid input: JSON object required")
            return Response({"message": "Invalid input: JSON object required"}, status=status.HTTP_400_BAD_REQUEST)
        
        cookie = data.get('cookie')
        pan_no = data.get('pan_no')
        ay = data.get('ay')

        # Basic validation
        if not cookie or not isinstance(cookie, str):
            logger.error("Invalid or missing 'cookie'")
            return Response({"message": "Invalid or missing 'cookie'"}, status=status.HTTP_400_BAD_REQUEST)
        if not pan_no or not isinstance(pan_no, str) or len(pan_no) != 10 or not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan_no):
            logger.error("Invalid or missing 'pan_no' (must be 10 characters, 5 letters, 4 digits, 1 letter)")
            return Response({"message": "Invalid or missing 'pan_no' (must be 10 characters, 5 letters, 4 digits, 1 letter)"}, status=status.HTTP_400_BAD_REQUEST)
        if not ay or not isinstance(ay, str) or not re.match(r'^\d{4}-\d{2}$', ay):
            logger.error("Invalid or missing 'ay' (format: YYYY-YY)")
            return Response({"message": "Invalid or missing 'ay' (format: YYYY-YY)"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Initial POST request to redirectionView26AS
        url = "https://eportal.incometax.gov.in/iec/utilityservicesapi/auth/v0.1/redirectionView26AS"
        payload = json.dumps({"pan": pan_no, "ay": ay})
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://eportal.incometax.gov.in',
            'Referer': 'https://eportal.incometax.gov.in/iec/foservices/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sn': 'NA',
            'Cookie': cookie
        }

        try:
            response = api_request_with_retry("POST", url, retries=3, delay=2, headers=headers, data=payload)
            if not response:
                logger.error("No response from redirectionView26AS request")
                return Response({"message": "No response from redirectionView26AS request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.HTTPError as e:
            logger.error(f"HTTP Error in redirectionView26AS: {str(e)}")
            return Response({"message": f"HTTP Error in redirectionView26AS: {str(e)}", "details": e.response.text if e.response else "No response content"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            logger.error(f"Request Error in redirectionView26AS: {str(e)}")
            return Response({"message": f"Request Error in redirectionView26AS: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 2: POST request to view26AS.xhtml
        url = "https://services.tdscpc.gov.in/serv/view26AS.xhtml"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://eportal.incometax.gov.in",
            "Referer": "https://eportal.incometax.gov.in/",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        }

        try:
            response = api_request_with_retry("POST", url, retries=3, delay=2, allow_redirects=False, headers=headers, data=response.json())
            if not response:
                logger.error("No response from view26AS.xhtml request")
                return Response({"message": "No response from view26AS.xhtml request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            logger.error(f"Request Error in view26AS.xhtml: {str(e)}")
            return Response({"message": f"Request Error in view26AS.xhtml: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 3: GET request to welcome26AS.xhtml
        url = "https://services.tdscpc.gov.in/serv/tapn/welcome26AS.xhtml"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        }

        cookies = {
            "JSESSIONID": response.headers.get("set-cookie", "").split(";")[0].split("=")[-1] if "set-cookie" in response.headers else ""
        }

        try:
            response = api_request_with_retry("GET", url, retries=3, allow_redirects=True, delay=2, cookies=cookies, headers=headers)
            if not response:
                logger.error("No response from welcome26AS.xhtml request")
                return Response({"message": "No response from welcome26AS.xhtml request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            logger.error(f"Request Error in welcome26AS.xhtml: {str(e)}")
            return Response({"message": f"Request Error in welcome26AS.xhtml: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Extract oam.Flash.RENDERMAP.TOKEN from cookies
        def cookie_find_by_regex(cookie_value):
            pattern = r'oam\.Flash\.RENDERMAP\.TOKEN=([-a-zA-Z0-9]+)'
            match = re.search(pattern, cookie_value)
            return match.group(1) if match else None

        cookies["oam.Flash.RENDERMAP.TOKEN"] = cookie_find_by_regex(response.headers.get("set-cookie", ""))
        if not cookies["oam.Flash.RENDERMAP.TOKEN"]:
            logger.error("Could not extract oam.Flash.RENDERMAP.TOKEN")
            return Response({"message": "Error: Could not extract oam.Flash.RENDERMAP.TOKEN"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 4: GET request to view26AS.xhtml
        url = "https://services.tdscpc.gov.in/serv/tapn/view26AS.xhtml"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://services.tdscpc.gov.in/serv/tapn/welcome26AS.xhtml",
            "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        }

        try:
            response = api_request_with_retry("GET", url, retries=3, delay=2, cookies=cookies, headers=headers)
            if not response:
                logger.error("No response from view26AS.xhtml GET request")
                return Response({"message": "No response from view26AS.xhtml GET request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            logger.error(f"Request Error in view26AS.xhtml GET: {str(e)}")
            return Response({"message": f"Request Error in view26AS.xhtml GET: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Update oam.Flash.RENDERMAP.TOKEN
        cookies["oam.Flash.RENDERMAP.TOKEN"] = cookie_find_by_regex(response.headers.get("set-cookie", ""))
        if not cookies["oam.Flash.RENDERMAP.TOKEN"]:
            logger.error("Could not extract updated oam.Flash.RENDERMAP.TOKEN")
            return Response({"message": "Error: Could not extract updated oam.Flash.RENDERMAP.TOKEN"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 5: POST request to TDS26ASServlet
        year = datetime.datetime.now().year - 1
        url = "https://services.tdscpc.gov.in/serv/tapn/srv/TDS26ASServlet"
        payload = f"reqtype=GetTaxPayer&assessYear={year}&viewType=HTML"
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://services.tdscpc.gov.in',
            'Referer': 'https://services.tdscpc.gov.in/serv/tapn/view26AS.xhtml',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        try:
            response = api_request_with_retry("POST", url, retries=3, delay=2, cookies=cookies, headers=headers, data=payload)
            if not response:
                logger.error("No response from TDS26ASServlet request")
                return Response({"message": "No response from TDS26ASServlet request"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.RequestException as e:
            logger.error(f"Request Error in TDS26ASServlet: {str(e)}")
            return Response({"message": f"Request Error in TDS26ASServlet: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Process final response
        try:
            final_data = response.json()
            logger.info("Successfully retrieved 26AS data")
            return Response({"data": final_data}, status=status.HTTP_200_OK)
        except ValueError:
            logger.error("Response is not valid JSON")
            return Response({"message": "Error: Response is not valid JSON", "data": response.text}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)