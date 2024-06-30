from django.urls import path
from .views import DoctorLoginView, DoctorAvailabilityView, PatientAvailabilityView,  PatientAppointmentView
urlpatterns = [
    path('d_login/', DoctorLoginView.as_view()),
    path('d_availability/',DoctorAvailabilityView.as_view()),
    path('p_availability/',PatientAvailabilityView.as_view()),
    path('p_appointment/', PatientAppointmentView.as_view()),
]


