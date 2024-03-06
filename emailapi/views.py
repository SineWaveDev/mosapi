from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from mailchimp3 import MailChimp


class ClientAPI(APIView):
    """
    This API is for stock buying and selling
    """

    def get(self, request, format=None):
        Email = request.GET.get("Email")

        print('Email:', Email)

        file_path = '/home/ubuntu/mosapi/final_email.html'
        # file_path = r'/Users/LT38/Documents/mosapi--MOS-main/final_email.html'
        # file_path = r'C:/Users/LT38/Desktop/Sinewave_API_Projects/MOS/final_email.html'
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Read the contents of the file
            html_content = file.read()

        # Set up SMTP connection
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'Sales@sinewave.co.in'
        smtp_password = 'cozijzxygatekuym'
        sender_email = 'Sales@sinewave.co.in'

        # Compose and send email
        message = MIMEText(html_content, 'html')
        message['Subject'] = 'Thank You For Downloading Our Software'
        message['From'] = sender_email
        message['To'] = Email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

        data = {
            'message': 'Success',
        }

        return Response(data)
