from django import forms

LOCALES = (
    ('en_US', 'English'),
    ('nb_NO', 'Norwegian'),
)


class TransparentIntegrationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Try with the example "demoapi" user'
    }))
    locale = forms.ChoiceField(label='Choose language', choices=LOCALES,
                               required=True)
    enable_theme = forms.BooleanField(label='Enable theme', required=False)
    enable_newsletters_index = forms.BooleanField(
        label='Enable newsletter index', required=False, initial=True)


class LoginIntegrationForm(forms.Form):
    locale = forms.ChoiceField(label='Choose language', choices=LOCALES,
                               required=True)
    enable_theme = forms.BooleanField(label='Enable theme', required=False)
    enable_newsletters_index = forms.BooleanField(
        label='Enable newsletters index', required=False, initial=True)
