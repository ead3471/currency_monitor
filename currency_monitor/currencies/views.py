from rest_framework.views import APIView
from .core import get_current_currency_value, get_currency_info
from .models import CurrencyValue
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import (
    HistoricalRecordSerializer,
    GetCurrencyValueSerializer,
    CurrencyDiffSerializer,
    SetRetrievingParametersSerializer,
)
from dataclasses import asdict
from datetime import datetime
from django.utils import timezone
from rest_framework.request import Request
from django.http import HttpResponseBadRequest
from drf_yasg.utils import swagger_auto_schema
from django_celery_beat.models import PeriodicTask
from django.conf import settings

import logging

logger = logging.getLogger(__name__)


# ===============Ok PART===================
class GetCurrencyHistory(APIView):
    @swagger_auto_schema(
        responses={
            200: HistoricalRecordSerializer,
            404: "Coin is not found",
        },
        operation_description="This is the GET endpoint returning list of historical data for given currency",
    )
    def get(self, request, code):
        currency = get_object_or_404(
            CurrencyValue,
            code=code,
        )
        history_records = currency.history.all()
        serializer = HistoricalRecordSerializer(
            instance=history_records, many=True
        )
        return Response(serializer.data)


class GetCurrencyDif(APIView):
    @swagger_auto_schema(
        operation_description="This is the GET endpoint returning differense between actual and historical data for given currency",
        responses={
            200: CurrencyDiffSerializer,
            404: "Object is not found",
        },
    )
    def get(self, request, code):
        currency = get_object_or_404(CurrencyValue, code=code)
        current_course = asdict(get_current_currency_value(code))
        last_course = currency.history.latest()
        print(type(last_course.rate))
        serializer = CurrencyDiffSerializer(
            data={
                "current_course": current_course,
                "latest_course": HistoricalRecordSerializer(last_course).data,
            }
        )
        serializer.is_valid()
        return Response(serializer.data)


class StartRetrieving(APIView):
    @swagger_auto_schema(
        request_body=SetRetrievingParametersSerializer,
        operation_description="This is the POST endpoint for start or stop retrieving data from server celery task.",
        responses={200: "Success response description"},
    )
    def post(self, request: Request):
        serializer = SetRetrievingParametersSerializer(data=request.data)
        if serializer.is_valid():
            main_task_name = settings.MAIN_SCAN_RATES_TASK_NAME
            task = PeriodicTask.objects.get(name=main_task_name)

            enable_flag = serializer.validated_data["enable"]
            if task:
                logger.info(
                    f"Set enabled for taks {main_task_name}={enable_flag}"
                )
                task.enabled = enable_flag
                task.save()
                return Response(
                    status=status.HTTP_200_OK,
                    data=f"Main task is {'started' if enable_flag else 'stopped'}",
                )
            else:
                logger.warning(f"Task {main_task_name} is not found")
                return Response(
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=serializer.errors,
            )


# ===============IN Process===========


class UpdateCurrencyRate(APIView):
    def get(self, request, code: str):
        recieved_currency_rate = get_current_currency_value(code)
        currency = CurrencyValue.objects.filter(code=code).first()

        if currency:
            currency.timestamp = datetime.fromtimestamp(
                recieved_currency_rate.timestamp,
                tz=timezone.utc,
            )
            currency.rate = recieved_currency_rate.rate
            currency.save()
        else:
            currency_info = get_currency_info(code)
            currency = CurrencyValue(
                code=currency_info.code,
                name=currency_info.name,
                rate=recieved_currency_rate.rate,
                timestamp=datetime.fromtimestamp(
                    recieved_currency_rate.timestamp,
                    tz=timezone.utc,
                ),
            )
            currency.save()
        serializer = GetCurrencyValueSerializer(instance=currency)
        return Response(serializer.data)

    def delete(self, request, code: str):
        instance = get_object_or_404(CurrencyValue, code=code)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkCoinToScan(APIView):
    def post(self, request, codes):
        coins = CurrencyValue.objects.all()
        return Response(GetCurrencyValueSerializer(coins, many=True).data)
