from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication

schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version="v1",
        description="Your API description",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(TokenAuthentication,),
)
