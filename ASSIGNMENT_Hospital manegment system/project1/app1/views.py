from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer,DoctorSerializer, PatientSerializer, AppointmentSerializer, AvailabilitySerializer
from .models import Doctor, Patient, Appointment, Availability
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class DoctorLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'message': 'Login successful.'})
        else:
            return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)


class DoctorAvailabilityView(APIView):
    def post(self, request):
        serializer = AvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            doctor = get_object_or_404(Doctor, pk=request.data['doctor_id'])
            availability = Availability(doctor=doctor, date=request.data['date'], available_time_slots=request.data['available_time_slots'])
            availability.save()
            return Response({'message': 'Availability saved successfully.'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = AvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            doctor = get_object_or_404(Doctor, pk=request.data['doctor_id'])
            availability = Availability.objects.get(doctor=doctor, date=request.data['date'])
            availability.available_time_slots = request.data['available_time_slots']
            availability.save()
            return Response({'message': 'Availability updated successfully.'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientAvailabilityView(APIView):
    def get(self, request, doctor_id, date):
        doctor = get_object_or_404(Doctor, pk=doctor_id)
        availability = get_object_or_404(Availability, doctor=doctor, date=date)
        return Response({'available_time_slots': availability.available_time_slots})

class PatientAppointmentView(APIView):
    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            doctor = get_object_or_404(Doctor, pk=request.data['doctor_id'])
            patient = get_object_or_404(Patient, pk=request.data['patient_id'])
            availability = get_object_or_404(Availability, doctor=doctor, date=request.data['date'])
            if request.data['time_slot'] not in availability.available_time_slots:
                return Response({'message': 'Time slot not available.'}, status=status.HTTP_400_BAD_REQUEST)
            appointment = Appointment(doctor=doctor, patient=patient, date=request.data['date'], time_slot=request.data['time_slot'])
            appointment.save()
            return Response({'message': 'Appointment booked successfully.'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
