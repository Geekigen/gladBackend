import uuid
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models

# Create your models here.


class Basemodel(models.Model):
    uuid = models.UUIDField(max_length=50, default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.uuid)


class GenericBasemodel(Basemodel):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)


class Status(Basemodel):
    name = models.CharField(max_length=200, null=False, blank=False)

    def __str__(self):
        return self.name


class Role(Basemodel):
    name = models.CharField(max_length=200, null=False, blank=False)
    # permission= models.ManyToManyField()

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    uuid = models.UUIDField(max_length=50, default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    id_no = models.CharField(max_length=20, unique=True, null=False, blank=False)
    address = models.CharField(max_length=25, unique=False, blank=False, null=False)
    contact_no = models.CharField(max_length=15, unique=True, blank=False, null=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
    emailverified = models.BooleanField(default=False)


    def __str__(self):
        return self.id_no


class Meter(Basemodel):
    meter_no = models.IntegerField(blank=False, null=False)
    installation_date = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.meter_no)


class Bill(Basemodel):
    reading_date = models.DateTimeField(auto_now=True, null=False, blank=False)
    previous_reading = models.IntegerField(unique=False)
    current_reading = models.IntegerField(unique=False)
    billing_date = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    amount_paid = models.IntegerField(blank=False, null=False)
    due_date = models.DateTimeField(null=False, blank=False)
    payment_method = models.CharField(max_length=25, blank=False, null=False)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.uuid)


class Receipt(Basemodel):
    amount_paid = models.CharField(max_length=200, null=False, blank=False)
    payment_date = models.DateTimeField(auto_now=True, blank=True, null=True)
    payment_method_used = models.CharField(max_length=200, blank=True, null=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.status.name
