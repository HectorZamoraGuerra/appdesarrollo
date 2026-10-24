from django.contrib.auth.forms import UserCreationForm


class RegistroForm(UserCreationForm):
    """UserCreationForm con etiquetas en español; cifra la contraseña y valida que coincidan."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirmar contraseña'
        for field in self.fields.values():
            field.help_text = ''
            field.widget.attrs['class'] = 'form-control'
