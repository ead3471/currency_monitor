from django.contrib import admin
from django.urls import path, include

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from api.views import (
    EnableRetrieving,
    ForceRetrieving,
    RetrieveForGivenCodes,
    CurrencyViewSet,
    LoginView,
)
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from rest_framework.authentication import (
    BasicAuthentication,
)


router = DefaultRouter()
router.register(r"api/v1/coins", CurrencyViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Currency monitor API description",
        default_version="v1",
        description=(
            "API for monitoring crypto currency values. \n"
            "Supported cryptocurrencies: \nABC, ACP, ACT, ACT*, ADA, ADCN, "
            "ADL, ADX, ADZ, AE, AGI, AIB, AIDOC, AION, AIR, ALT, AMB, AMM, "
            "ANT, APC, APPC, ARC, ARCT, ARDR, ARK, ARN, ASAFE2, AST, ATB, "
            "ATM, AURS, AVAX, AVT, BAR, BASH, BAT, BAY, BBP, BCD, BCH, BCN, "
            "BCPT, BEE, BIO, BLC, BLOCK, BLU, BLZ, BMC, BNB, BNT, BOST, BQ, "
            "BQX, BRD, BRIT, BT1, BT2, BTC, BTCA, BTCS, BTCZ, BTG, BTLC, "
            "BTM, BTM*, BTQ, BTS, BTX, BURST, CALC, CAS, CAT, CCRB, CDT, "
            "CESC, CHAT, CJ, CL, CLD, CLOAK, CMT*, CND, CNX, CPC, CRAVE, "
            "CRC, CRE, CRW, CTO, CTR, CVC, DAS, DASH, DAT, DATA, DBC, DBET, "
            "DCN, DCR, DCT, DEEP, DENT, DGB, DGD, DIM, DIME, DMD, DNT, DOGE, "
            "DRGN, DRZ, DSH, DTA, EC, EDG, EDO, EDR, EKO, ELA, ELF, EMC, "
            "EMGO, ENG, ENJ, EOS, ERT, ETC, ETH, ETN, ETP, ETT, EVR, EVX, "
            "FCT, FLP, FOTA, FRST, FUEL, FUN, FUNC, FUTC, GAME, GAS, GBYTE, "
            "GMX, GNO, GNT, GNX, GRC, GRS, GRWI, GTC, GTO, GUP, GVT, GXS, "
            "HAC, HNC, HSR, HST, HVN, ICN, ICOS, ICX, IGNIS, ILC, INK, INS, "
            "INSN, INT, IOP, IOST, ITC, KCS, KICK, KIN, KLC, KMD, KNC, KRB, "
            "LA, LEND, LEO, LINDA, LINK, LOC, LOG, LRC, LSK, LTC, LUN, LUX, "
            "MAID, MANA, MCAP, MCO, MDA, MDS, MIOTA, MKR, MLN, MNX, MOD, "
            "MOIN, MONA, MTL, MTN*, MTX, NAS, NAV, NBT, NDC, NEBL, NEO, NEU, "
            "NEWB, NGC, NKC, NLC2, NMC, NMR, NULS, NVC, NXT, OAX, OBITS, OC, "
            "OCN, ODN, OK, OMG, OMNI, ORE, ORME, OST, OTN, OTX, OXY, PART, "
            "PAY, PBT, PCS, PIVX, PIZZA, PLBT, PLR, POE, POLY, POSW, POWR, "
            "PPC, PPT, PPY, PRC, PRES, PRG, PRL, PRO, PURA, PUT, QASH, QAU, "
            "QSP, QTUM, QUN, R, RBIES, RCN, RDD, RDN, RDN*, REBL, REE, REP, "
            "REQ, REV, RGC, RHOC, RIYA, "
            "RKC, RLC, RPX, RUFF, SALT, SAN, SBC, SC, SENT, "
            "SHIFT, SIB, SMART, "
            "SMLY, SMT*, SNC, SNGLS, SNM, SNT, SPK, SRN, STEEM, STK, STORJ, "
            "STRAT, STU, STX, SUB, SUR, SWFTC, SYS, TAAS, TESLA, THC, THETA, "
            "THS, TIO, TKN, TKY, TNB, TNT, TOA, TRC, TRIG, TRST, TRUMP, TRX, "
            "UBQ, UNO, UNRC, UQC, USDT, UTK, UTT, VEE, VEN, VERI, VIA, VIB, "
            "VIBE, VOISE, VOX, VRS, VTC, VUC, WABI, WAVES, WAX, WC, WGR, "
            "WINGS, WLK, WOP, WPR, WRC, WTC, XAUR, XBP, XBY, XCP, XCXT, XDN, "
            "XEM, XGB, XHI, XID, XLM, XMR, XNC, XRB, XRP, XTO, XTZ, XUC, XVG, "
            "XZC, YEE, YOC, YOYOW, ZBC, ZCL, ZEC, ZEN, ZIL, ZNY, ZRX, ZSC, 611"
        ),
    ),
    permission_classes=(AllowAny,),
    authentication_classes=(BasicAuthentication,),
    public=True,
)

urlpatterns = [
    path("accounts/login/", LoginView.as_view(), name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
    path(
        "api/v1/retrieve/enable",
        EnableRetrieving.as_view(),
        name="retrieve-enable",
    ),
    path(
        "api/v1/retrieve/once",
        RetrieveForGivenCodes.as_view(),
        name="retrieve-once",
    ),
    path(
        "api/v1/retrieve/force",
        ForceRetrieving.as_view(),
        name="retrieve-force",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("", include(router.urls), name="coins"),
]
