import yfinance as yf
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import pandas as pd

class StockPriceView(APIView):

    def get(self, request):
        financial_year = request.query_params.get('financial_year')
        tickers = request.query_params.get('tickerslist')

        # Validate input parameters
        if not financial_year or not tickers:
            return Response({"error": "Both financial_year and tickerslist are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            financial_year_start, financial_year_end = financial_year.split('-')
            financial_year_start = int(financial_year_start)
            financial_year_end = int(financial_year_end)
        except ValueError:
            return Response({"error": "Invalid financial_year format. Please use 'YYYY-YYYY'."}, status=status.HTTP_400_BAD_REQUEST)

        # Get current financial year based on today's date
        current_year = datetime.now().year
        current_month = datetime.now().month
        if current_month <= 3:
            current_financial_year = f"{current_year - 1}-{current_year}"
        else:
            current_financial_year = f"{current_year}-{current_year + 1}"

        # Validate ticker
        try:
            stock = yf.Ticker(tickers)
            stock_info = stock.info  # Check if ticker is valid
            if not stock_info or 'symbol' not in stock_info:
                return Response({"error": f"Ticker {tickers} is invalid or not found."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed to validate ticker {tickers}: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch stock data based on financial year
        if financial_year == current_financial_year:
            stock_data = self.get_stock_data(tickers)
            if stock_data is None:
                return Response({"error": f"No data available for {tickers} today."}, status=status.HTTP_404_NOT_FOUND)
            return Response({
                "financial_year": financial_year,
                "ticker": tickers,
                "price": stock_data
            })
        elif financial_year_end <= current_year:  # Ensure past financial year
            stock_data = self.get_stock_data_on_march_31(tickers, financial_year)
            if stock_data is None:
                return Response({"error": f"No data available for {tickers} on March 31, {financial_year_end}."}, status=status.HTTP_404_NOT_FOUND)
            return Response({
                "financial_year": financial_year,
                "ticker": tickers,
                "price": stock_data
            })
        else:
            return Response({"error": "Future financial years are not supported."}, status=status.HTTP_400_BAD_REQUEST)

    def get_stock_data(self, tickers):
        try:
            stock = yf.Ticker(tickers)
            todays_data = stock.history(period="1d")
            if todays_data.empty:
                return None
            todays_data = todays_data.iloc[0]
            stock_data = {
                "open": todays_data.get('Open', None),
                "high": todays_data.get('High', None),
                "low": todays_data.get('Low', None),
                "close": todays_data.get('Close', None),
                "adj_close": todays_data.get('Adj Close', None),
                "volume": todays_data.get('Volume', None)
            }
            return stock_data
        except Exception as e:
            print(f"Error fetching today's data for {tickers}: {e}")
            return None

    def get_stock_data_on_march_31(self, tickers, financial_year):
        try:
            financial_year_start = int(financial_year.split('-')[0])
            start_date = f"{financial_year_start}-04-01"
            end_date = f"{financial_year_start + 1}-03-31"
            stock = yf.Ticker(tickers)
            data = stock.history(start=start_date, end=end_date)
            if data.empty:
                return None
            # Filter for the last trading day in March
            march_data = data[data.index.month == 3]
            if march_data.empty:
                return None
            march_31_data = march_data.iloc[-1]
            stock_data = {
                "open": march_31_data.get('Open', None),
                "high": march_31_data.get('High', None),
                "low": march_31_data.get('Low', None),
                "close": march_31_data.get('Close', None),
                "adj_close": march_31_data.get('Adj Close', None),
                "volume": march_31_data.get('Volume', None)
            }
            return stock_data
        except Exception as e:
            print(f"Error fetching data for {tickers} on March 31, {financial_year}: {e}")
            return None