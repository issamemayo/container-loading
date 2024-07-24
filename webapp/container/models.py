from django.db import models

# Create your models here.
class BoxData(models.Model):
    sku_name = models.CharField(max_length=255, primary_key=True)
    net_weight = models.FloatField(null=False)
    length = models.IntegerField(null=False)
    breadth = models.IntegerField(null=False)
    height = models.IntegerField(null=False)
    crushing_strength=models.IntegerField(default=70)

    class Meta:
        db_table = 'box_data'

    def __str__(self):
        return self.sku_name

class TruckData(models.Model):

    TYPE_CHOICES = [
        ('Type 1', 'Type 1'),
        ('Type 2', 'Type 2'),
        ('Type 3', 'Type 3'),
        ('Z020', 'Z020')
        
    ]
    number = models.CharField(max_length=255, primary_key=True)
    type_id = models.CharField(max_length=255, choices=TYPE_CHOICES, null=False)
    length = models.IntegerField(null=False)
    breadth = models.IntegerField(null=False)
    height = models.IntegerField(null=False)

    class Meta:
        db_table = 'truck_data'
   
    def __str__(self):
        return self.number