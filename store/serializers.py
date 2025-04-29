import os
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import Customer

User = get_user_model()

customer_fields = ['id','phone_number', 'nationality', 'travel_date','preferred_destination']


class CreateCustomerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'})
    username = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = ['email', 'password', 'username', 'name', 'nationality',
                  'phone_number', 'travel_date', 'preferred_destination']

    def validate_email(self, value):
        """Ensure email is unique across users"""
        if User.objects.filter(email=value).exists():
            raise ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Ensure email is unique across users"""
        if User.objects.filter(username=value).exists():
            raise ValidationError("A user with this username already exists.")
        return value

    def get_name(self, customer: Customer):
        return customer.user.name

    @transaction.atomic()
    def create(self, validated_data):
        email = validated_data.pop('email')
        name = validated_data.pop('name')
        username = validated_data.pop('username')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            email=email, password=password, name=name, username=username)
        customer = Customer.objects.create(user=user, **validated_data)

        # subject = "Welcome to Walls Printing!"
        # template = "email/welcome_email.html"
        # context = {
        #     "user": user,
        #     "temporary_password": password,
        #     "login_url": os.getenv('CUSTOMER_LOGIN_URL')
        # }

        # send_email(user=user, context=context,
        #            subject=subject, template=template)

        # if groups:
        #     customer.groups.set(groups)

        return customer

class UpdateCustomerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)

    class Meta:
        model = Customer
        fields = [*customer_fields, 'name']

    @transaction.atomic()
    def update(self, instance, validated_data):
        name = validated_data.pop('name')

        customer = super().update(instance, validated_data)

        if name is not None:
            user = instance.user

            if name:
                user.name = name
            user.save()

        return customer


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [*customer_fields,
                  'name', 'email', 'username']

    def get_email(self, customer: Customer):
        return customer.user.email

    def get_username(self, customer: Customer):
        return customer.user.username

    def get_name(self, customer: Customer):
        return customer.user.name
