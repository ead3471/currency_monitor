from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from currencies.views import (
    GetCurrencyHistory,
    GetCurrencyDif,
    EnableRetrieving,
    ForceRetrieving,
    RetrieveForGivenCodes,
    CurrencyViewSet,
)
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"coins", CurrencyViewSet)

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
    path("users/", include("django.contrib.auth.urls")),
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
        "api/retrieve",
        EnableRetrieving.as_view(),
        name="retrieve-enable",
    ),
    path(
        "api/retrieve_once",
        RetrieveForGivenCodes.as_view(),
        name="retrieve-once",
    ),
    path(
        "api/retrieve/force",
        ForceRetrieving.as_view(),
        name="retrieve-force",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger"),
        name="schema-swagger-ui",
    ),
    path("", include(router.urls)),
]
