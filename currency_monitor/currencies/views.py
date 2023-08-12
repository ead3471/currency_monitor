from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .core import get_coin_rate, get_coin_info
from .models import CurrencyValue
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import (
    HistoricalRecordSerializer,
    GetCurrencyValueSerializer,
    CurrencyDiffSerializer,
    EnableRetrievingSerializer,
    ForceRetrievingSerializer,
    RetrieveForGivenCodesSerializer,
    RegisterCurrencySerializer,
    PatchCurrencySerializer,
)
from dataclasses import asdict
from datetime import datetime
from django.utils import timezone
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from django_celery_beat.models import PeriodicTask
from django.conf import settings
from tasks import retrieve_data, retrieve_coins_rates, register_coin

import logging

logger = logging.getLogger(__name__)


# ===============Ok PART===================
class GetCurrencyHistory(APIView):
    @swagger_auto_schema(
        responses={
            200: HistoricalRecordSerializer,
            404: "Coin is not found",
        },
        operation_description=(
            "This is the GET endpoint returning "
            "list of historical data for given currency"
        ),
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
        operation_description=(
            "This is the GET endpoint returning differense ",
            "between actual and historical data for given currency",
        ),
        responses={
            200: CurrencyDiffSerializer,
            404: "Object is not found",
        },
    )
    def get(self, request, code):
        currency = get_object_or_404(CurrencyValue, code=code)
        current_course = asdict(get_coin_rate(code))
        last_course = currency.history.latest()
        print(type(last_course.rate))
        serializer = CurrencyDiffSerializer(
            data={
                "current_course": current_course,
                "latest_course": HistoricalRecordSerializer(last_course).data,
            }
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ForceRetrieving(APIView):
    @swagger_auto_schema(
        request_body=ForceRetrievingSerializer,
        operation_description=(
            "This is the POST endpoint for force runnig once a celery task ",
            "what retrieves data from server.",
        ),
        responses={200: "Task is delayed"},
    )
    def post(self, request: Request):
        serializer = ForceRetrievingSerializer(data=request.data)
        logger.info("Forcing run retrieving request recieved")
        serializer.is_valid(raise_exception=True)
        main_task_name = settings.MAIN_SCAN_RATES_TASK_NAME
        scheduled_task: PeriodicTask = PeriodicTask.objects.get(
            name=main_task_name
        )
        if scheduled_task.enabled:
            logger.info("Forcing run retrieving task")
            retrieve_data.delay()
            return Response(status=status.HTTP_200_OK, data="Task is delayed")
        else:
            logger.info(
                "Forcing run retrieving task skipped: task is disabled"
            )
            return Response(
                status=status.HTTP_409_CONFLICT, data="Task is disabled"
            )


class EnableRetrieving(APIView):
    @swagger_auto_schema(
        request_body=EnableRetrievingSerializer,
        operation_description=(
            "This is the POST endpoint for enable or disable celery task ",
            "what retrieves data from server.",
        ),
        responses={200: "Main task is started/stopped"},
    )
    def post(self, request: Request):
        serializer = EnableRetrievingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        main_task_name = settings.MAIN_SCAN_RATES_TASK_NAME
        task = PeriodicTask.objects.get(name=main_task_name)

        enable_flag = serializer.validated_data["enable"]
        if task:
            logger.info(f"Set enabled for taks {main_task_name}={enable_flag}")
            task.enabled = enable_flag
            task.save()
            return Response(
                status=status.HTTP_200_OK,
                data=(
                    "Main task is "
                    f"{'started' if enable_flag else 'stopped'}"
                ),
            )
        else:
            logger.warning(f"Task {main_task_name} is not found")
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RetrieveForGivenCodes(APIView):
    @swagger_auto_schema(
        request_body=RetrieveForGivenCodesSerializer,
        operation_description=(
            (
                "This is the POST endpoint for starting task "
                "what retrieves rates for given currencies codes"
            ),
        ),
        responses={200: "Task started"},
    )
    def post(self, request: Request):
        codes = request.data["codes"]
        logger.info(
            (
                "Request for immidiatly data retrieving recieved. "
                f"Codes to retrieve:{codes}"
            )
        )
        retrieve_coins_rates.apply_async(kwargs={"coins_codes": codes})
        return Response("Task is delayed")


class CurrencyViewSet(ModelViewSet):
    queryset = CurrencyValue.objects.all()
    lookup_field = "code"

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RegisterCurrencySerializer
        if self.request.method == "PATCH":
            return PatchCurrencySerializer
        if self.request.method == "PUT":
            return PatchCurrencySerializer
        else:
            return GetCurrencyValueSerializer

    def create(self, request, *args, **kwargs):
        serializer: RegisterCurrencySerializer = self.get_serializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        coin_code = serializer.validated_data.get("code")
        is_scan_on = serializer.validated_data.get("is_scan_on")
        register_coin.apply_async(
            kwargs={"coin_code": coin_code, "is_scan_on": is_scan_on}
        )
        return Response(
            status=status.HTTP_200_OK, data="Register task created"
        )


# ===============IN Process===========


class UpdateCurrencyRate(APIView):
    def get(self, request, code: str):
        recieved_currency_rate = get_coin_rate(code)
        currency = CurrencyValue.objects.filter(code=code).first()

        if currency:
            currency.timestamp = datetime.fromtimestamp(
                recieved_currency_rate.timestamp,
                tz=timezone.utc,
            )
            currency.rate = recieved_currency_rate.rate
            currency.save()
        else:
            currency_info = get_coin_info(code)
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
