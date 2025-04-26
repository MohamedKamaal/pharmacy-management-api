from django.contrib import admin
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from dj_rest_auth.views import PasswordResetConfirmView


import orders , sales, reports

# Schema view configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Pharmacy Management Api",
        default_version="v1",
        description="API documentation using Swagger and ReDoc",
        terms_of_service="https://www.yoursite.com/terms/",
        contact=openapi.Contact(email="support@yoursite.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,  # Accessible without authentication
    permission_classes=[permissions.AllowAny],  # Change if authentication is required
)

urlpatterns = [
    # Django Admin interface
    path("admin/", admin.site.urls),
    path('accounts/', view=include('allauth.urls')), 

    path("api/v1/medicine/", include("medicine.urls")),

    path("api/v1/orders/", include("orders.urls")),
    path("api/v1/sales/", include("sales.urls")),
     path('api/v1/reports/', include('reports.urls')),  # Include the reports app URLs

    path("api/v1/auth/", include("dj_rest_auth.urls")),
    path("api/v1/auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/v1/auth/password/reset/confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(),name="password_reset_confirm"),

    # Swagger UI
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),

    # ReDoc UI
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
# Admin site customization
admin.site.site_header = "Pharmacy Management API Admin"
admin.site.site_title = "Pharmacy Management API Admin Portal"
admin.site.index_title = "Welcome to Pharmacy Management API Admin Portal"