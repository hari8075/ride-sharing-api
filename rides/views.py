from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import *
from .serializers import *
from rest_framework import status, generics


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        if request.user.role != 'driver':
            return Response(
                {"detail": "Only drivers can access this endpoint."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        queryset = self.get_queryset().filter(status='PENDING')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated or self.request.user.role != 'rider':
            raise ValueError("Only authenticated riders can create rides.")
        serializer.save(rider=self.request.user)

    @action(detail=True, methods=['POST'])
    def accept_ride(self, request, pk=None):
        ride = self.get_object()

        if ride.status != 'PENDING':
            return Response({"detail": "Ride is no longer available."}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.role != 'driver':
            return Response({"detail": "Only drivers can accept rides."}, status=status.HTTP_400_BAD_REQUEST)

        active_rides = Ride.objects.filter(driver=request.user, status__in=['STARTED', 'PENDING'])
        if active_rides.exists():
            return Response(
                {"detail": "You are already assigned to an active ride. Complete your current ride first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Assign the driver and update the status
        ride.driver = request.user
        ride.status = 'ACCEPTED'
        ride.save()

        return Response(RideSerializer(ride).data, status=status.HTTP_200_OK)


    @action(detail=True, methods=['POST'])
    def complete_ride(self, request, pk=None):
        ride = self.get_object()

        # Ensure the user is a driver
        if request.user.role != 'driver':
            return Response({"detail": "Only drivers can complete rides."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the ride is assigned to this driver
        if ride.driver != request.user:
            return Response({"detail": "You are not assigned to this ride."}, status=status.HTTP_403_FORBIDDEN)

        # Ensure the ride is in 'STARTED' status
        if ride.status != 'STARTED':
            return Response({"detail": "This ride cannot be completed."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the ride status to 'COMPLETED'
        ride.status = 'COMPLETED'
        ride.save()

        return Response({"detail": "Ride has been completed successfully."}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['POST'])
    def cancel_ride(self, request, pk=None):
        ride = self.get_object()

        # Ensure the user is a rider
        if request.user.role != 'rider':
            return Response({"detail": "Only riders can cancel rides."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the ride is still in 'PENDING' status
        if ride.status != 'PENDING':
            return Response({"detail": "You can only cancel a ride that is still pending."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the ride is not already accepted by a driver
        if ride.driver is not None:
            return Response({"detail": "Ride cannot be cancelled once a driver has been assigned."}, status=status.HTTP_400_BAD_REQUEST)

        # Change the status to 'CANCELLED'
        ride.status = 'CANCELLED'
        ride.save()

        return Response({"detail": "Ride has been cancelled successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def start_ride(self, request, pk=None):
        """
        Allow the driver to start a ride only after entering the correct rider's code.
        """
        ride = self.get_object()

        # Ensure the user is a driver
        if request.user.role != 'driver':
            return Response({"detail": "Only drivers can start rides."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the ride is assigned to this driver
        if ride.driver != request.user:
            return Response({"detail": "You are not assigned to this ride."}, status=status.HTTP_403_FORBIDDEN)

        # Ensure the ride is in 'ACCEPTED' status
        if ride.status != 'ACCEPTED':
            return Response({"detail": "This ride cannot be started because it is not in 'ACCEPTED' status."}, status=status.HTTP_400_BAD_REQUEST)

        # Verify the rider's unique ride code
        rider = ride.rider
        entered_code = request.data.get('ride_code')  # Get the code provided by the driver
        if entered_code != rider.ride_code:
            return Response({"detail": "Incorrect ride code. The ride cannot be started."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the ride status to 'STARTED'
        ride.status = 'STARTED'
        ride.save()

        return Response({"detail": "The ride has been started successfully."}, status=status.HTTP_200_OK)




class CustomUserRegistrationView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def create(self, request, *args, **kwargs):
        role = request.data.get('role')
        if role not in ['rider', 'driver']:
            return Response(
                {"detail": "Role must be 'rider' or 'driver'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)


