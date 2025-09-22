from django.db import models

class Institution(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=255)
    years_of_study = models.PositiveIntegerField(default=4)
    total_tuition_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} at {self.institution.name}"

