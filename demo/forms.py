from django import forms

LANGUAGE = (
    ('en', 'English'),
    ('nb', 'Norwegian'),
)


class TransparentIntegrationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Try with the example "demoapi" user'
    }))
    lang = forms.ChoiceField(label='Choose language', choices=LANGUAGE, required=True)
    skip_recipients_step = forms.BooleanField(label='Skip recipients step',
            initial=True, required=False)
    css = forms.BooleanField(label='Use custom CSS', required=False)


class LoginIntegrationForm(forms.Form):
    lang = forms.ChoiceField(label='Choose language', choices=LANGUAGE, required=True)
    skip_recipients_step = forms.BooleanField(label='Skip recipients step',
            initial=True, required=False)
