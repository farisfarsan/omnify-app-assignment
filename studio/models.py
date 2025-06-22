from django.db import models
from django.utils.timezone import localtime

class FitnessClass(models.Model):
    name = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    instructor = models.CharField(max_length=100)
    total_slots = models.PositiveIntegerField()
    available_slots = models.PositiveIntegerField()

    def __str__(self):
        local_dt = localtime(self.date_time)
        return f"{self.name} at {local_dt.strftime('%Y-%m-%d %I:%M %p')}"

    class Meta:
        ordering = ['date_time']


class Booking(models.Model):
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField()
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client_name} booked {self.fitness_class.name} on {localtime(self.booked_at).strftime('%Y-%m-%d %I:%M %p')}"

    class Meta:
        ordering = ['-booked_at']
