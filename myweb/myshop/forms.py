from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class RegistrantionForm(forms.Form):
    username = forms.CharField(
        label = "Tên đăng nhập",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label = "Mật khẩu",
        max_length=20,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        label = "Nhập lại mật khẩu",
        max_length=20,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        label = "Tên",
        max_length= 20,
        widget= forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label = "Họ",
        max_length= 20,
        widget= forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.CharField(
        label = "Email",
        max_length=50,
        widget= forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    # Kiểm tra username/email không được trùng. password và confirm_pass phải giống nhau
    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username= username)
            raise ValidationError(f"Tên đăng nhập đã tồn tại")
        except User.DoesNotExist:
            return username
        
    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email = email)
            raise ValidationError(f"Email đã tồn tại!")
        except User.DoesNotExist:
            return email
        
    def clean_confirm_password(self):
        if self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise ValidationError(f"Không giống mật khẩu")
        return self.cleaned_data['confirm_password']                              
    
    def save(self):
        User.objects.create_user( # create_user là lưu vào CSDL có password. create lưu dạng raw data
            username = self.cleaned_data['username'],
            password = self.cleaned_data['password'],
            first_name = self.cleaned_data['first_name'],
            last_name = self.cleaned_data['last_name'],
            email = self.cleaned_data['email']
        )
        
class LoginForm(forms.Form):
    username = forms.CharField(
        label= "Tên đăng nhập",
        max_length= 20,
        widget= forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label= "Mật khẩu",
        max_length= 20,
        widget= forms.PasswordInput(attrs={'class': 'form-control'})
    )
    