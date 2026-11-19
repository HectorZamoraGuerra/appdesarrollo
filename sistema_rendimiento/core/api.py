from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Actividad
from .serializers import ActividadEventoSerializer


class ActividadListAPIView(ListAPIView):
    serializer_class = ActividadEventoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Actividad.objects.filter(objetivo__usuario=self.request.user)
