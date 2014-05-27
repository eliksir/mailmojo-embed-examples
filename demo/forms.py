from django import forms


class EmbedForm(forms.Form):
    LANGUAGE = (
        ('en', 'English'),
        ('nb', 'Norwegian'),
    )

    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Try with the example "demoapi" user'
    }))
    lang = forms.ChoiceField(label='Choose language', choices=LANGUAGE, required=True)
    css = forms.BooleanField(label='Use custom CSS', required=False)
    skip_recipients_step = forms.BooleanField(label='Skip recipients step',
            initial=True, required=False)
