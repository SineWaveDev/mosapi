from django.db import models

# Create your models here.

class Company(models.Model):
    Bucket=models.IntegerField()
    lot_size=models.IntegerField()
    Share_name=models.CharField(max_length=100)
    Price_from=models.DateField()
    Buy_percentage=models.IntegerField()
    Sale_percentage=models.IntegerField()
    max_look_back_period = models.IntegerField()
    
    def __str__(self) -> str:
        return f"{self.Bucket} {self.Share_name}"