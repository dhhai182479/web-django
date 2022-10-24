from django.shortcuts import render, redirect, HttpResponseRedirect
from myshop.forms import RegistrantionForm, LoginForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import authenticate, login    #authenticate giúp xác thực
from django.http.response import JsonResponse
from django.contrib.auth.models import User 

def register_user(request):
    form = RegistrantionForm()
    if request.method == "POST":
        form = RegistrantionForm(request.POST)
        if form.is_valid():  # Kiểm tra có hợp lệ hay không
            form.save()
            return redirect('login_user')
    return render(
        request=request,
        template_name='user/register.html',
        context={
            'form': form
        }
    )

def login_user(request):
    form = LoginForm()
    message=""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            # authenticate('username', 'password')
            # Hàm này xác thực khi username/password đều đúng -> trả về 1 object/instance từ class User. Sai thì return None
            user = authenticate(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password']
            )
            if user:
                # Xác thực thành công
                login(request=request, user=user) # Login/giữ trạng thái đăng nhập thành công
                if request.GET.get('next'):
                    return HttpResponseRedirect(request.GET['next'])
                return redirect('index')
            else:
                message = "Sai tài khoản hoặc mật khẩu"
    return render(
        request=request,
        template_name='user/login.html',
        context={
            'form': form,
            'message': message
        }
    )
    
def change_password(request):
    form = PasswordChangeForm(user=request.user)
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_user')
    return render(
        request=request,
        template_name='user/change_password.html',
        context={
            'form': form
        }
    )
  
# Hàm phía server nhận từ js gửi lên
# Json gửi từ js <=> server cũng phải gửi lại là Json 
def validate_username(request):
    if request.method =="POST": 
        username = request.POST['username']
        try:
            User.objects.get(username=username)
            return JsonResponse({'message': f'Tên đăng nhập đã tồn tại'}, status=409) # 409: Conflict
        except User.DoesNotExist:     
            return JsonResponse({'message': 'Hợp lệ'}, status=200)
        
def validate_email(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            User.objects.get(email=email)
            return JsonResponse({'message': f'Email đã tồn tại'}, status= 409)
        except User.DoesNotExist:
            return JsonResponse({'message': 'Hợp lệ'}, status= 200)