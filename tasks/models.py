from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class Task(models):
    DEPENDENCIES = {}
    title = models.CharField(max_length = 200)
    due_date = models.DateField()
    estimated_hours = models.IntegerField()
    importance = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Value must be at least 1."),
            MaxValueValidator(10, message="Value cannot exceed 10.")
        ]
    )
    dependencies = models.CharField(max_length=1,choices=DEPENDENCIES)