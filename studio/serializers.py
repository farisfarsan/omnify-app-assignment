from rest_framework import serializers
from .models import FitnessClass, Booking
from django.utils.timezone import localtime


class FitnessClassSerializer(serializers.ModelSerializer):
    date_time = serializers.SerializerMethodField()

    class Meta:
        model = FitnessClass
        fields = ['id', 'name', 'date_time', 'instructor', 'total_slots', 'available_slots']

    def get_date_time(self, obj):
        # Convert UTC to local time (IST assumed if TIME_ZONE is set in settings.py)
        return localtime(obj.date_time).isoformat()


class BookingSerializer(serializers.ModelSerializer):
    class_id = serializers.PrimaryKeyRelatedField(
        source='fitness_class',
        queryset=FitnessClass.objects.all(),
        write_only=True
    )
    class_name = serializers.CharField(source='fitness_class.name', read_only=True)
    date_time = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id', 'class_id', 'class_name', 'date_time', 'client_name', 'client_email']

    def get_date_time(self, obj):
        return localtime(obj.fitness_class.date_time).isoformat()
