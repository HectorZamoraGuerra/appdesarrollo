from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Actividad
from .serializers import ActividadEventoSerializer


class ActividadListAPIView(ListAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadEventoSerializer
    permission_classes = [IsAuthenticated]
