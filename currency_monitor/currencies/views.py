from rest_framework.views import APIView
from .core import get_current_currency_values, get_currency_info
from .models import CurrencyValue
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import (
    HistoricalRecordSerializer,
    CurrencyValueSerializer,
    CurrencyDiffSerializer,
)
from dataclasses import asdict
from datetime import datetime
from django.utils import timezone


class UpdateCurrencyRate(APIView):
    def get(self, request, code: str):
        recieved_currency_rate = get_current_currency_values(
            [
                code,
            ]
        )[0]
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
        serializer = CurrencyValueSerializer(instance=currency)
        return Response(serializer.data)

    def delete(self, request, code: str):
        instance = get_object_or_404(CurrencyValue, code=code)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetCurrencyHistory(APIView):
    def get(self, request, code):
        currency = get_object_or_404(CurrencyValue, code=code)
        history_records = currency.history.all()
        serializer = HistoricalRecordSerializer(
            instance=history_records, many=True
        )
        return Response(serializer.data)


class GetCurrencyDif(APIView):
    def get(self, request, code):
        currency = get_object_or_404(CurrencyValue, code=code)
        current_course = asdict(
            get_current_currency_values(
                [
                    code,
                ]
            )[0]
        )
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
