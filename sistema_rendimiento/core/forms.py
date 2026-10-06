from django import forms

from .models import Actividad, Objetivo, RegistroRendimiento


class ActividadForm(forms.ModelForm):
    class Meta:
        model = Actividad
        fields = ['titulo', 'objetivo', 'fecha_inicio', 'fecha_fin', 'nota']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Series de velocidad 8x400m',
            }),
            'objetivo': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'fecha_fin': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'nota': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe una nota sobre esta actividad...',
            }),
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        fin = cleaned.get('fecha_fin')
        if inicio and fin and fin <= inicio:
            raise forms.ValidationError('La fecha de fin debe ser posterior a la de inicio.')
        return cleaned


class RegistroRendimientoForm(forms.ModelForm):
    TIPOS = [
        ('tiempo', 'Tiempo (min)'),
        ('distancia', 'Distancia (km)'),
        ('repeticiones', 'Repeticiones'),
    ]

    tipo_indicador = forms.ChoiceField(
        choices=TIPOS, widget=forms.Select(attrs={'class': 'form-control'})
    )
    calificacion = forms.IntegerField(
        min_value=1, max_value=5, initial=3,
        label='Calificación de satisfacción',
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'class': 'form-range',
            'min': 1,
            'max': 5,
            'step': 1,
        }),
    )

    class Meta:
        model = RegistroRendimiento
        fields = ['tipo_indicador', 'valor', 'calificacion']
        widgets = {
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Valor obtenido, ej: 32',
            }),
        }


class ObjetivoForm(forms.ModelForm):
    class Meta:
        model = Objetivo
        fields = ['titulo', 'categoria', 'estado', 'prioridad', 'fecha_inicio', 'fecha_meta']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Correr 10K antes de diciembre',
            }),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-control'}),
            'fecha_inicio': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'fecha_meta': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('fecha_inicio')
        meta = cleaned.get('fecha_meta')
        if inicio and meta and meta <= inicio:
            raise forms.ValidationError('La fecha meta debe ser posterior a la de inicio.')
        return cleaned
