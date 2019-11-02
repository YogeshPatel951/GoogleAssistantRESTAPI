from django.shortcuts import render
from .bin.AssistantTextInputRefactored  import GetAssistantObject, GetResponseForQuery
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.core import serializers
from django.conf import settings
import json
from django.views import View
# Create your views here.
@api_view(["POST"])
def GetResponseFromAssistant(query):
	try:
		query_text=json.loads(query.body)
		assobj=GetAssistantObject()
		print(type(assobj))
		res=GetResponseForQuery(assobj,query_text)
		return JsonResponse(res,safe=False)
	except ValueError as e:
		return Response(e.args[0],status.HTTP_400_BAD_REQUEST)	