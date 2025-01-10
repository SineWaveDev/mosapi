import yfinance as yf
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

class StockPriceView(APIView):

    def get(self, request):
        financial_year = request.query_params.get('financial_year')
        tickers = request.query_params.get('tickerslist')

        # Validate financial_year format (e.g., '2024-2025')
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

        # Check if current month is before or after March to determine the fiscal year
        if current_month <= 3:
            current_financial_year = f"{current_year - 1}-{current_year}"
        else:
            current_financial_year = f"{current_year}-{current_year + 1}"

        # Fetch stock data based on comparison of financial years
        stock_data = self.get_stock_data(tickers)

        if financial_year == current_financial_year:
            return Response({
                "financial_year": financial_year,
                "ticker": tickers,
                "price": stock_data
            })

        elif financial_year < current_financial_year:
            # Fetch stock data for the last day of March for the passed financial year
            return Response({
                "financial_year": financial_year,
                "ticker": tickers,
                "price": self.get_stock_data_on_march_31(tickers, financial_year)
            })

        return Response({"error": "Invalid financial year."}, status=status.HTTP_400_BAD_REQUEST)

    def get_stock_data(self, tickers):
        # Fetch today's stock price
        stock = yf.Ticker(tickers)
        todays_data = stock.history(period="1d").iloc[0]

        # Safely access stock data columns
        stock_data = {
            "open": todays_data.get('Open', None),
            "high": todays_data.get('High', None),
            "low": todays_data.get('Low', None),
            "close": todays_data.get('Close', None),
            "adj_close": todays_data.get('Adj Close', None),  # Using get() to avoid KeyError
            "volume": todays_data.get('Volume', None)
        }
        return stock_data

    def get_stock_data_on_march_31(self, tickers, financial_year):
        # Convert financial_year to an integer if it is a string
        financial_year = int(financial_year.split('-')[0])
        
        # Calculate the end date for the given financial year (March 31st of the next year)
        start_date = f"{financial_year}-04-01"
        end_date = f"{financial_year + 1}-03-31"
        
        # Fetch stock data from yfinance
        stock = yf.Ticker(tickers)
        data = stock.history(start=start_date, end=end_date)
        
        # Get the last date in March (March 31st)
        march_31_data = data.loc[data.index.month == 3].iloc[-1]

        # Safely access stock data columns
        stock_data = {
            "open": march_31_data.get('Open', None),
            "high": march_31_data.get('High', None),
            "low": march_31_data.get('Low', None),
            "close": march_31_data.get('Close', None),
            "adj_close": march_31_data.get('Adj Close', None),  # Using get() to avoid KeyError
            "volume": march_31_data.get('Volume', None)
        }
        return stock_data
