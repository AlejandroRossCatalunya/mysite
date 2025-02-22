from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import ListCreateAPIView
from rest_framework.mixins import ListModelMixin
from django.contrib.auth.models import Group

from .serializers import GroupSerializer

@api_view()
def hello_world_view(request: Request) -> Response:
    return Response({"message": "Hello World!"})


class GroupListView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

# class GroupListView(APIView):
#     def get(self, request: Request) -> Response:
#         groups = Group.object.all()
#         #data = [group.name for group in groups]
#         #return Response({"groups": data})
#         serialized = GroupSerializer(groups, many=True)
#         return Response({"groups": serialized.data})