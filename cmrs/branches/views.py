from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Branch
from .serializers import BranchSerializer


class BranchListView(ListAPIView):
    serializer_class = BranchSerializer
    permission_classes = [IsAuthenticated]
    queryset = Branch.objects.all().order_by("id")