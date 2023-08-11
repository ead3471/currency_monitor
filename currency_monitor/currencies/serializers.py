from rest_framework import serializers
from simple_history.models import HistoricalRecords
from .models import CurrencyValue
from decimal import Decimal


class HistoricalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyValue.history.model
        exclude = ("history_user", "history_change_reason")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["rate"] = Decimal(representation["rate"])
        return representation


class GetCurrencyValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyValue
        fields = "__all__"


class CurrencyDiffSerializer(serializers.Serializer):
    latest_course = HistoricalRecordSerializer()
    current_course = serializers.DictField()

    difference = serializers.SerializerMethodField(
        method_name="get_difference"
    )

    def get_difference(self, obj):
        current_rate = obj["current_course"]["rate"]
        last_rate = obj["latest_course"]["rate"]
        print(type(current_rate), type(last_rate))
        return current_rate - last_rate

    def create(self, validated_data):
        combined_data = {
            "latest_course": validated_data.get("latest_course"),
            "current_course": validated_data.get("current_course"),
        }
        return combined_data


class SetRetrievingParametersSerializer(serializers.Serializer):
    enable = serializers.BooleanField()
