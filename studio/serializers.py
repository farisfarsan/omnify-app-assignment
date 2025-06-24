from rest_framework import serializers
from .models import FitnessClass, Booking
import pytz

class FitnessClassSerializer(serializers.ModelSerializer):
    date_time = serializers.SerializerMethodField()

    class Meta:
        model = FitnessClass
        fields = ['id', 'name', 'date_time', 'instructor', 'total_slots', 'available_slots']

    def get_date_time(self, obj):
        request=self.context.get('request')
        tz_name=request.query_params.get('timezone') if request else None
        try:
            if tz_name in pytz.all_timezones:
                user_tz = pytz.timezone(tz_name)
                return obj.date_time.astimezone(user_tz).isoformat()
        except Exception:
            pass
        
        return obj.date_time.astimezone(pytz.UTC).isoformat()    

class BookingSerializer(serializers.ModelSerializer):
    class_id = serializers.PrimaryKeyRelatedField(
        source='fitness_class',
        queryset=FitnessClass.objects.all(),
        write_only=True
    )
    class_name = serializers.CharField(source='fitness_class.name', read_only=True)
    date_time = serializers.SerializerMethodField()

    def get_date_time(self, obj):
        request=self.context.get('request')
        tz_name=request.query_params.get('timezone') if request else None
        try:
            if tz_name in pytz.all_timezones:
                user_tz = pytz.timezone(tz_name)
                return obj.fitness_class.date_time.astimezone(user_tz).isoformat()
        except Exception:
            pass
        
        return obj.fitness_class.date_time.astimezone(pytz.UTC).isoformat()


    class Meta:
        model = Booking
        fields = ['id', 'class_id', 'class_name', 'date_time', 'client_name', 'client_email']

    
