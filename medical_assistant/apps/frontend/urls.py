from django.urls import path
from .views import landing_page, dashboard_paciente, dashboard_administrativo, dashboard_medico

app_name = 'frontend'

urlpatterns = [
    path('', landing_page, name='landing_page'),
    path('dashboard/paciente/', dashboard_paciente, name='dashboard_paciente'),
    path('dashboard/administrativo/', dashboard_administrativo, name='dashboard_administrativo'),
    path('dashboard/medico/', dashboard_medico, name='dashboard_medico'),
]
