from django.contrib import admin

# Register your models here.
from . models import Meter, Bill, Receipt, Status, Role, CustomUser

admin.site.register(Meter)
admin.site.register(Bill)
admin.site.register(Receipt)
admin.site.register(Status)
admin.site.register(Role)
admin.site.register(CustomUser)
