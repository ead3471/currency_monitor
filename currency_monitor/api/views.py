import logging
from dataclasses import asdict

from currencies.models import CurrencyValue
from django.conf import settings
from django.contrib.auth.views import LoginView as DefaultLoginView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django_celery_beat.models import PeriodicTask
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from tasks import register_coin, retrieve_coins_rates, retrieve_data

from .core import get_coin_rate
from .serializers import (CurrencyDiffSerializer, EnableRetrievingSerializer,
                          ForceRetrievingSerializer,
                          GetCurrencyValueSerializer,
                          HistoricalRecordSerializer, PatchCurrencySerializer,
                          RegisterCurrencySerializer,
                          RetrieveForGivenCodesSerializer)

logger = logging.getLogger(__name__)


class ForceRetrieving(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=ForceRetrievingSerializer,
        operation_description=(
            "This is the POST endpoint to force run the "
            "main celery task that fetches data from the server."
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
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=EnableRetrievingSerializer,
        operation_description=(
            "This is the POST endpoint to enable or disable the celery "
            "task that retrieves data from the server."
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
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=RetrieveForGivenCodesSerializer,
        operation_description=(
            "This is the POST endpoint to run a task that "
            "fetches the rates for given in request currency codes"
        ),
        responses={200: "Task started"},
    )
    def post(self, request: Request):
        codes = request.data["codes"]
        logger.info(
            (
                "A request has been received for immediate data retrieval. "
                f"Codes to retrieve:{codes}"
            )
        )
        retrieve_coins_rates.apply_async(kwargs={"coins_codes": codes})
        return Response("Task is delayed")


class CurrencyViewSet(ModelViewSet):
    queryset = CurrencyValue.objects.all()
    lookup_field = "code"
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

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
            status=status.HTTP_200_OK,
            data=f"Register {coin_code} task created by {self.request.user}",
        )

    @swagger_auto_schema(
        # request_body=EmptySerializer,
        operation_description=(
            "This is a GET endpoint that returns the difference "
            "between actual and historical data for a given currency"
        ),
        responses={
            200: CurrencyDiffSerializer,
            404: "Object is not found",
        },
    )
    @action(detail=True, methods=["GET"])
    def difference(self, request, code):
        currency = get_object_or_404(CurrencyValue, code=code)
        try:
            current_course = asdict(get_coin_rate(code))
        except ValueError as ex:
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=str(ex)
            )
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

    @swagger_auto_schema(
        responses={
            200: HistoricalRecordSerializer,
            404: "Coin is not found",
        },
        operation_description=(
            "This is the GET endpoint returning "
            "list of historical data for the given currency"
        ),
    )
    @action(detail=True, methods=["GET"])
    def history(self, request, code):
        currency = get_object_or_404(
            CurrencyValue,
            code=code,
        )
        history_records = currency.history.all()
        serializer = HistoricalRecordSerializer(
            instance=history_records, many=True
        )
        return Response(serializer.data)


class LoginView(DefaultLoginView):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("schema-swagger-ui")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("schema-swagger-ui")
