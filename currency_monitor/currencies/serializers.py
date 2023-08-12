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


class EnableRetrievingSerializer(serializers.Serializer):
    enable = serializers.BooleanField()


class ForceRetrievingSerializer(serializers.Serializer):
    force = serializers.BooleanField()


class RetrieveForGivenCodesSerializer(serializers.Serializer):
    codes = serializers.ListField(child=serializers.CharField())


class RegisterCurrencySerializer(serializers.ModelSerializer):
    code = serializers.CharField(max_length=10)
    is_scan_on = serializers.BooleanField(default=False)

    class Meta:
        model = CurrencyValue
        fields = ["code", "is_scan_on"]
        extra_kwargs = {
            "is_scan_on": {"required": False},
        }


class PatchCurrencySerializer(serializers.ModelSerializer):
    is_scan_on = serializers.BooleanField()

    class Meta:
        model = CurrencyValue
        fields = ["is_scan_on"]


class EmptySerializer(serializers.Serializer):
    pass
