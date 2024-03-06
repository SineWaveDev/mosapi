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

        # Extract the last year from the financial year range
        last_year = financial_year[-1]

        current_year = dt.date.today().year
        print("current_year", current_year)

        date_str = ""
        next_date_str = ""

        if current_year < int(last_year):
            date_str = str(dt.date(current_year, 3, 31))
            next_date_str = str(dt.date(current_year, 4, 1))
        elif current_year == int(last_year):
            if dt.date.today() < dt.date(current_year, 3, 31):
                date_str = str(dt.date.today())
                next_date_str = str(
                    dt.date.today() + datetime.timedelta(days=1))
            else:
                date_str = str(dt.date(current_year, 3, 31))
                next_date_str = str(dt.date(current_year, 4, 1))
        else:
            date_str = str(dt.date(int(last_year), 3, 31))
            next_date_str = str(dt.date(int(last_year), 4, 1))

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
