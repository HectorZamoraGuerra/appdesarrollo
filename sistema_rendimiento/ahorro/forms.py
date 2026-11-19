from django import forms

from .models import MetaAhorro, Movimiento


class MetaAhorroForm(forms.ModelForm):
    class Meta:
        model = MetaAhorro
        fields = ['nombre', 'monto_meta', 'fecha_meta']
        labels = {'monto_meta': 'Monto meta ($)', 'fecha_meta': 'Fecha meta'}
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Fondo de emergencia',
            }),
            'monto_meta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Ej: 50000',
            }),
            'fecha_meta': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }


class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['tipo', 'monto', 'fecha', 'nota']
        labels = {'monto': 'Monto ($)'}
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Ej: 1500',
            }),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'nota': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Depósito quincenal',
            }),
        }

    def __init__(self, *args, meta, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = meta

    def clean(self):
        cleaned = super().clean()
        monto = cleaned.get('monto')
        if cleaned.get('tipo') == Movimiento.Tipo.RETIRO and monto:
            ahorrado = self.meta.movimientos.saldo()
            if monto > ahorrado:
                raise forms.ValidationError(f'El retiro (${monto:,.2f}) es mayor a lo ahorrado (${ahorrado:,.2f}).')
        return cleaned
