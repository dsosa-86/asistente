from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import lista_reportes, detalle_reporte, ReporteViewSet

router = DefaultRouter()
router.register(r'api/reportes', ReporteViewSet, basename='reporte')

urlpatterns = [
    path('', lista_reportes, name='lista_reportes'),
    path('<int:pk>/', detalle_reporte, name='detalle_reporte'),
    path('', include(router.urls)),
]
