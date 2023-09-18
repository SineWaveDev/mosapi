from django.db import models

# Create your models here.

class Company(models.Model):
    Email=models.EmailField(max_length=100)
    
    def __str__(self) -> str:
        return f"{self.Email}"
    
