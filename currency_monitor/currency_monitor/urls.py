from django.contrib import admin
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from currencies.views import (
    UpdateCurrencyRate,
    GetCurrencyHistory,
    GetCurrencyDif,
)
from rest_framework.permissions import AllowAny

schema_view = get_schema_view(
    openapi.Info(
        title="Currency monitor API description",
        default_version="v1",
    ),
    permission_classes=(AllowAny,),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "api/currency/<str:code>",
        UpdateCurrencyRate.as_view(),
        name="get-currency",
    ),
    path(
        "api/currency/<str:code>/history",
        GetCurrencyHistory.as_view(),
        name="get-currency-history",
    ),
    path(
        "api/currency/<str:code>/dif",
        GetCurrencyDif.as_view(),
        name="get-currency-dif",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger"),
        name="schema-swagger-ui",
    ),
]
