from django.contrib import admin
from .models import BoxData, TruckData
# Register your models here.

class BoxAdmin(admin.ModelAdmin):
    list_display=("sku_name", "net_weight", "length", "breadth", "height")

class TruckAdmin(admin.ModelAdmin):
    list_display=("number", "type_id", "length", "breadth", "height")

admin.site.register(BoxData,BoxAdmin)
admin.site.register(TruckData,TruckAdmin)


