from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render
from .models import SensorData
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_sensor_data(sensor_data):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("sensor_data_group", {"type": "sensor_data.update", "data": sensor_data})

class SensorDataAPI(APIView):
    def post(self, request):
        try:
            input_string = request.body.decode("utf-8")        
            values = input_string.split(" ")
            keys = ['acceleration_x', 'acceleration_y', 'acceleration_z', 'gyroscope_x', 'gyroscope_y', 'gyroscope_z']
            sensor_data = {key: float(value) for key, value in zip(keys, values)}
        except (ValueError, UnicodeDecodeError):
            return Response({"message": "Invalid sensor data format"}, status=status.HTTP_400_BAD_REQUEST)

        if not sensor_data:
            return Response({"message": "No sensor data received"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            SensorData.objects.create(**sensor_data)  # Store the sensor data in the database
            send_sensor_data(sensor_data)
            return Response({"message": "Sensor data received and saved successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



def sensor_data(request):
    sensor_data = SensorData.objects.order_by('-timestamp').first()

    context = {
        'sensor_data': sensor_data,
    }

    return render(request, 'imu_sensor_app/sensor_data.html', context)
