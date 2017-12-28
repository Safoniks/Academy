from django import forms
from django.contrib.auth import get_user_model

AuthUser = get_user_model()


class SignUpForm(forms.ModelForm):
    class Meta:
        model = AuthUser
        fields = ('email', 'password', )

    def save(self, commit=True):
        super(SignUpForm, self).save(commit=False)
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = AuthUser.objects.create_site_user(email, password)
        if commit:
            user.save()
        return user


class SignInForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, max_length=20)
