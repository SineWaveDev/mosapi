import datetime
import yfinance as yf
import datetime as dt
import pandas as pd
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import json


class GetRate(APIView):
    def get(self, request):
        tickerslist = request.GET.getlist('tickerslist', None)
        financial_year = request.GET.get('financial_year', None)
        print("financial_year", financial_year)

        # Split financial_year only if it contains '-'
        if '-' in financial_year:
            financial_year = financial_year.split('-')
        else:
            # Handle the case where financial_year doesn't contain '-'
            return Response("Invalid financial year format", status=status.HTTP_400_BAD_REQUEST)

        # Extract the start year and end year from the financial year range
        start_year, end_year = map(int, financial_year)

        current_year = dt.date.today().year
        print("current_year", current_year)

        date_str = ""
        next_date_str = ""

        if start_year == current_year - 5 and end_year == current_year - 4:
            # If the financial year is 2019-2020
            date_str = "2020-03-31"
            next_date_str = "2020-04-01"
        elif start_year == current_year - 4 and end_year == current_year - 3:
            # If the financial year is 2020-2021
            date_str = "2021-03-31"
            next_date_str = "2021-04-01"
        elif start_year == current_year - 3 and end_year == current_year - 2:
            # If the financial year is 2021-2022
            date_str = "2022-03-31"
            next_date_str = "2022-04-01"
        elif start_year == current_year - 2 and end_year == current_year - 1:
            # If the financial year is 2022-2023
            date_str = "2023-03-31"
            next_date_str = "2023-04-01"
        elif start_year == current_year - 1 and end_year == current_year:
            # If the financial year is 2023-2024
            date_str = "2023-03-28"
            next_date_str = "2023-03-29"
        elif start_year == current_year and end_year == current_year + 1:
            # If the financial year is 2024-2025
            date_str = str(dt.date.today())
            next_date_str = str(dt.date.today() + datetime.timedelta(days=1))
        else:
            # Handle invalid financial year ranges
            return Response("Invalid financial year range", status=status.HTTP_400_BAD_REQUEST)

        print("Start_Date", date_str)
        print("end_date", next_date_str)

        df = pd.DataFrame()

        for ticker in tickerslist:
            data = yf.download(
                tickers=ticker, start=date_str, end=next_date_str)
            print("data", data)
            df = pd.concat([df, data])

        df1 = df.to_json(orient='records')
        print(df1)

        return Response(df1)
