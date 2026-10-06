from rest_framework.generics import ListAPIView

from .models import Actividad
from .serializers import ActividadEventoSerializer


class ActividadListAPIView(ListAPIView):
    queryset = Actividad.objects.all()
    serializer_class = ActividadEventoSerializer
