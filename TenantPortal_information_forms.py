from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib import messages
from django.forms import ModelForm
from .models import Tenant, Complaint, Visitor


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email_name = self.cleaned_data['email']

        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('This user does not exist.')
            if not user.check_password(password):
                raise forms.ValidationError('Incorrect Password.')
            if not user.is_active:
                raise forms.ValidationError('This user is not active.')
        return super(UserLoginForm, self).clean(*args, **kwargs)


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['unit', 'contact', 'work_address', 'birthday']


class ComplaintForm(forms.ModelForm):
    COMPLAINTS_NAME = (
        ('Maintenance', 'Maintenance Problem'),
        ('Staff', 'Staff Conflict'),
        ('Neighbour', 'Neighbor/s Issue'),
        ('Pest', 'Pest Invasion'),
        ('Property_Condition', 'Condition of Property'),
        ('Safety', 'Safety Concern'),
        ('Billing', 'Billing'),
        ('Others', 'Others'),
    )
    complain = forms.ChoiceField(choices=COMPLAINTS_NAME)
    class Meta:
        model = Complaint
        fields = '__all__'
        exclude = ("info_tenant",)


class VisitorForm(forms.ModelForm):
    PURPOSE = (
        ('Vacation', 'Vacation'),
        ('One_Day', 'One Day Visit'),
        ('Overnight', 'Overnight'),
        ('Event', 'Event'),
        ('Pool_Gym', 'Use Pool/Gym')
    )
    purpose = forms.ChoiceField(choices=PURPOSE)
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Declined', 'Declined'),
        ('Processing', 'Processing'),
        ('Done', 'Done')
    )
    status = forms.ChoiceField(choices=STATUS)

    class Meta:
        model = Visitor
        fields = '__all__'
        exclude = ("info_tenant",)
