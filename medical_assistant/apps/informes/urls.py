from django.urls import path
from . import views

app_name = 'informes'

urlpatterns = [
    path('editar/<int:informe_id>/', views.editar_informe, name='editar_informe'),
    path('version/<int:version_id>/', views.ver_version_informe, name='ver_version_informe'),
    path('comparar-versiones/', views.comparar_versiones, name='comparar_versiones'),
    path('ver/<int:informe_id>/', views.ver_informe, name='ver_informe'),
    path('firmar/<int:informe_id>/', views.firmar_informe, name='firmar_informe'),
    path('verificar-firma/<int:firma_id>/', views.verificar_firma, name='verificar_firma'),
    path('verificar-integridad/<int:informe_id>/', views.verificar_integridad_firmas, name='verificar_integridad'),
    path('registro-firmas/<int:informe_id>/pdf/', views.generar_pdf_registro_firmas, name='generar_pdf_registro_firmas'),
] 