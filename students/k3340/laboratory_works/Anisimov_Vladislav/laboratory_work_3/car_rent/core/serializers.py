from rest_framework import serializers
from .models import *

class CarInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarInfo
        fields = "__all__"

class CarSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['car_info'] = CarInfoSerializer(instance.car_info).data
        return representation

    class Meta:
        model = Car
        fields = "__all__"

class FineSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['car_instance'] = instance.car_instance.__str__()
        return representation
    
    class Meta:
        model = Fine
        fields = "__all__"

class CarCrashSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['car_instance'] = instance.car_instance.__str__()
        return representation
    
    class Meta:
        model = CarCrash
        fields = "__all__"

class CarInstanceSerializer(serializers.ModelSerializer):
    fines = FineSerializer(many=True, read_only=True)
    crashes = CarCrashSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['car'] = CarSerializer(instance.car).data
        representation['fines'] = list(map(lambda el: el["description"], representation['fines']))
        representation['crashes'] = list(map(lambda el: el["info"], representation['crashes']))
        return representation
    
    class Meta:
        model = CarInstance
        fields = "__all__"

class ClientSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = User.objects.get(id=representation['user'])
        representation['user'] = f"{user.first_name} {user.last_name}"
        return representation
        
    class Meta:
        model = Client
        fields = "__all__"

class WorkerSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = User.objects.get(id=representation['user'])
        representation['user'] = f"{user.first_name} {user.last_name}"
        return representation
    
    class Meta:
        model = Worker
        fields = "__all__"

class RentContractSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['worker'] = WorkerSerializer(instance.worker).data['user']
        representation['client'] = ClientSerializer(instance.client).data['user']
        representation['car_instance'] = instance.car_instance.__str__()
        return representation
    
    class Meta:
        model = RentContract
        fields = "__all__"