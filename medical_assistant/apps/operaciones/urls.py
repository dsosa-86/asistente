from django.urls import path
from . import views

app_name = 'operaciones'

urlpatterns = [
    # URLs para Estudios Prequirúrgicos
    path('estudios/', views.lista_estudios_prequirurgicos, name='lista_estudios'),
    path('estudios/crear/', views.crear_estudio_prequirurgico, name='crear_estudio'),
    path('estudios/<int:pk>/', views.detalle_estudio_prequirurgico, name='detalle_estudio'),
    path('estudios/<int:pk>/editar/', views.editar_estudio_prequirurgico, name='editar_estudio'),
    path('estudios/<int:pk>/eliminar/', views.eliminar_estudio_prequirurgico, name='eliminar_estudio'),
    
    # URLs para Estudios de Pacientes
    path('paciente/<int:paciente_id>/estudios/', views.lista_estudios_paciente, name='lista_estudios_paciente'),
    path('estudios/paciente/<int:estudio_paciente_id>/cargar-resultado/', 
         views.cargar_resultado_estudio, name='cargar_resultado_estudio'),
    path('estudios/<int:estudio_paciente_id>/actualizar-estado/',
         views.actualizar_estado_estudio, name='actualizar_estado_estudio'),
] 