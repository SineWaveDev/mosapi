import datetime
import yfinance as yf
import datetime as dt
import pandas as pd
from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework import status
# from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import  APIView
import json
# @api_view(['POST'])
# def index(request):
class GetRate(APIView):
    def get(self,request):
        tickerslist = request.GET.getlist('tickerslist',None)
        financial_year = request.GET.get('financial_year',None)
        financial_year = financial_year.split(',')
        # print("tickerslist-->",tickerslist,type(tickerslist))
        # print("financial_year-->", financial_year,type(financial_year))

        start = financial_year[0].split('-')
        output = start
        start_1 = output[0]
        end_1 = output[1]
        # print("start_1-->",start_1,type(start_1))
        # print("end_1-->", end_1, type(end_1))

        current_year = dt.date.today().year
        # print('current_year-->',current_year, type(current_year))
        current_date = dt.date.today()
        # print('current_date-->',current_date, type(current_date))
        previous_year = current_year - 1
        # print('previous_year-->',previous_year, type(previous_year))
        next_year = current_year + 1
        # print('next_year-->',next_year, type(next_year))

        date = 0
        last_date = 0
        if end_1 == str(next_year):
            date = current_date
            # print('date-->',date, type(date))
        else:
            end_year = end_1
            end_year = int(end_1)
            end_date = dt.date(end_year, 3, 31)
            last_date = end_date
            # print('last_date',last_date,type(last_date))

        date_str = str(date) if date else str(last_date)
        # print(date_str)
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

        next_date = date_obj + datetime.timedelta(days=1)
        next_date_str = next_date.strftime("%Y-%m-%d")
        df = pd.DataFrame()

        for ticker in tickerslist:
            data = yf.download(tickers=ticker, start=date_str, end=next_date_str)
            df = pd.concat([df, data])
        df1 = df.to_json(orient='records')
        print(df1)

        return Response(df1)


