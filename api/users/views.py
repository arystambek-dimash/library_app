from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.users.serializers import UserSerializer


@api_view(['POST'])
def register(request: Request):
    try:
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            data = {
                'refresh': str(refresh),
                'access': str(access_token),
            }
            return Response(data, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def logout(request: Request):
    try:
        refresh = request.data.get('refresh')
        try:
            token = RefreshToken(token=refresh)
        except Exception as e:
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)

        token.blacklist()
        return Response({"status": "Logged out"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response("Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
