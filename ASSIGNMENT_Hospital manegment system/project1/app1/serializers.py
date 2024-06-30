from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Doctor, Patient, Appointment, Availability


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Doctor
        fields =  "__all__"


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Patient
        fields = "__all__"


class AvailabilitySerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer()

    class Meta:
        model = Availability
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer()
    patient = PatientSerializer()

    class Meta:
        model = Appointment
        fields = "__all__"
