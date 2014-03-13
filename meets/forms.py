from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory

from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User

from meets.models import (
    Venue,
    BookMeeting,
)

from meets.selecttime import SelectTimeWidget
from captcha.fields import CaptchaField

TO_HIDE_ATTRS = {'class': 'hidden'}

class VenueForm(forms.ModelForm):

    venue_name = forms.CharField(label="Venue Name", widget=forms.TextInput(attrs = {'size': '22'}))
    venue_capacity = forms.CharField(label="Venue Capacity", widget=forms.TextInput(attrs = {'size': '22'}))
    
    class Meta:
        model = Venue
        exclude = ('code',) 
        abstract = True

    def __init__(self, *args, **kwargs):
        return super(VenueForm, self).__init__(*args, **kwargs)

    def clean(self):
        return self.cleaned_data

    


class MeetBookForm(forms.ModelForm):

    
    request_by = forms.CharField(label="Request By", widget=forms.TextInput(attrs = {'size': '22'}))
    purpose = forms.CharField(label="Purpose For", widget=forms.Textarea(attrs = {'cols': '22', 'rows': '7'}))
    venue = forms.ModelChoiceField(queryset = Venue.objects.all(), empty_label=None)
    user = forms.ModelChoiceField(queryset = User.objects.all(), widget=forms.HiddenInput(), empty_label=None) 
    
    book_date = forms.DateField(label='Book Date', widget=forms.DateInput(attrs = {'class': 'vDateField', 'size': '22'}))

    from_time = forms.TimeField(label='Start Time', widget=SelectTimeWidget(hour_step=1, minute_step=5, second_step=60))
    to_time = forms.TimeField(label='End Time', widget=SelectTimeWidget(hour_step=1, minute_step=5, second_step=60))


    class Meta:
        model = BookMeeting
        exclude = ('create_at', 'processed_at', 'book_status', ) 
        abstract = True

    def __init__(self, usera, *args, **kwargs):  #  
        self.usera = usera
        return super(MeetBookForm, self).__init__(*args, **kwargs)

    def clean(self):
        return self.cleaned_data
        
    def save(self, *args, **kwargs):
        super(MeetBookForm, self).save(*args, **kwargs) # Call the "real" save() method.  


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(label='Old password',
        widget=forms.PasswordInput(render_value=False, attrs={'pattern': r'.{3,}', 'title': '3 characters are required', 'required': None}))
    new_password1 = forms.CharField(label='New password', min_length=3,
        widget=forms.PasswordInput(render_value=False, attrs={'pattern': r'.{3,}', 'title': '3 characters are required', 'required': None}))
    new_password2 = forms.CharField(label='New password again', min_length=3,
        widget=forms.PasswordInput(render_value=False, attrs={'pattern': r'.{3,}', 'title': '3 characters are required', 'required': None}))

    def __init__(self, current_user, *args, **kwargs):
        self.current_user = current_user
        
        if self.current_user is None:
            raise AttributeError('current_user missing')
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        if not self.current_user.check_password(old_password):
            raise forms.ValidationError('Please enter your current password correctly.')
        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data['new_password1']
        new_password2 = self.cleaned_data['new_password2']
        if new_password1 != new_password2:
            raise forms.ValidationError("The password doesn't match the other.")
        return new_password2

    def save(self):
        self.current_user.set_password(self.cleaned_data['new_password1'])
        self.current_user.save()


class UserCreationForm(forms.ModelForm):

    error_messages = {
        'duplicate_username': ("A user with that username already exists."),
        'password_mismatch': ("The two password fields didn't match."),
    }

    username = forms.RegexField(regex=r'^[\w.@+-]+$',max_length=30,label='Username')
    email = forms.EmailField(label="E-mail")
    password1 = forms.CharField(widget=forms.PasswordInput,label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput,label="Repeat Password")
    captcha = CaptchaField() 

    class Meta:
        model = User
        #fields = '__all__' 
        fields = ('username','email','password1','password2','captcha')

    def __init__(self, *args, **kwargs):
        print ('1b')    
        return super(UserCreationForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        print ('2b')  
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'], code='duplicate_username',)

    def clean_password2(self):
        print ('3b') 
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def clean(self):
        print ('4b')  
        return self.cleaned_data
        

    def save(self, commit=True):
        print ('5b') 
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user



