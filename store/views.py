from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from store.models import Customer
from .serializers import CustomerSerializer, CreateCustomerSerializer, UpdateCustomerSerializer

# Create your views here.

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related('user').all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateCustomerSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UpdateCustomerSerializer
        return CustomerSerializer
