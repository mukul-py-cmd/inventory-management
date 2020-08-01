from rest_framework import serializers
from .models import Box

class staff_BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = '__all__'


class BoxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ['id','length','breadth','height','area','volume']



class Box_create_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Box
        fields = ['length','breadth','height','area','volume']

