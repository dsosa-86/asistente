from django.urls import path
from . import views

app_name = 'importacion_excel'

urlpatterns = [
    # Vistas principales
    path('', views.importar_excel, name='importar_excel'),
    path('previsualizar/<int:pk>/', views.previsualizar_excel, name='previsualizar_excel'),
    path('revisar/', views.revisar_excel, name='revisar_excel'),
    path('guardar-correcciones/', views.guardar_correcciones, name='guardar_correcciones'),
    path('resultados/<int:pk>/', views.ver_resultados, name='ver_resultados'),
    
    # Descargas
    path('descargar-errores/<int:importacion_id>/', views.descargar_errores, name='descargar_errores'),
    path('descargar-plantilla/<str:tipo>/', views.descargar_plantilla, name='descargar_plantilla'),
    
    # Configuración
    path('mapeo/', views.lista_mapeos, name='lista_mapeos'),
    path('mapeo/crear/', views.crear_mapeo, name='crear_mapeo'),
    path('mapeo/<int:pk>/editar/', views.editar_mapeo, name='editar_mapeo'),
    path('mapeo/<int:pk>/eliminar/', views.eliminar_mapeo, name='eliminar_mapeo'),
    
    # Reglas de corrección
    path('reglas/', views.lista_reglas, name='lista_reglas'),
    path('reglas/crear/', views.crear_regla, name='crear_regla'),
    path('reglas/<int:pk>/editar/', views.editar_regla, name='editar_regla'),
    path('reglas/<int:pk>/eliminar/', views.eliminar_regla, name='eliminar_regla'),
    
    # API para validaciones asíncronas
    path('api/validar-columna/', views.validar_columna, name='validar_columna'),
    path('api/sugerir-correccion/', views.sugerir_correccion, name='sugerir_correccion'),
    
    # Historial y estadísticas
    path('historial/', views.historial_importaciones, name='historial'),
    path('estadisticas/', views.estadisticas_importaciones, name='estadisticas'),
    path('estadisticas/actualizar/', views.actualizar_estadisticas, name='actualizar_estadisticas'),
    path('historial/filtrar/', views.filtrar_importaciones_ajax, name='filtrar_importaciones_ajax'),
    path('exportar/', views.exportar_datos, name='exportar_datos'),
]