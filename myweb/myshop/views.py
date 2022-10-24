from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from .models import Category, Brand, Product, Order, OrderDetail, Promotion
from django.db.models import Min, Max
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.utils.timezone import now
from django.contrib.humanize.templatetags.humanize import intcomma
# Create your views here.

def index(request):
    #Category parent, k lấy category con
    categories = Category.objects.filter(category_parent__isnull=True)
    products = Product.objects.all()
    category_search = request.GET.get('category')
    category_display = ''
    if category_search:
        category_display = Category.objects.get(name=category_search)
        products = Product.objects.filter(category=category_display)
        
    brands = Brand.objects.all()
    brand_search = request.GET.get('brand')
    brand_display = ''
    if brand_search:
        brand_display = Brand.objects.get(name=brand_search)
        products= Product.objects.filter(brand=brand_display)
        
    minimum_price = products.aggregate(Min('price')) #SELECT ....
    maximum_price = products.aggregate(Max('price')) 
    
    paginator = Paginator(object_list=products, per_page=12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    product_promotions = Promotion.objects.filter(start_date__lte=now(), end_date__gt=now())
    
    
    return render(
        request=request,
        template_name='index.html',
        context={
            'categories': categories,
            'brands': brands,
            'products': products,
            'category_display': category_display,
            'brand_display': brand_display,
            'products': products,
            'maximum_price': maximum_price['price__max'],
            'minimum_price': minimum_price['price__min'],
            'page_obj': page_obj,
            'product_promotions': product_promotions,
        }
    )
    
# @login_required(login_url='/user/login')
def view_product(request, product_id):
    try:
        product_data = Product.objects.get(id=product_id)
        return render(
            request=request,
            template_name='product/product-details.html',
            context={
                'product_data': product_data,
            }
        )
    except Product.DoesNotExist:
        return render(
            request=request,
            template_name='404.html'
        )

@login_required(login_url='/user/login')       
def add_product_to_cart(request, product_id):
    #Xác định về người dùng đăng nhập
    # print(request.user)
    try:
        logged_user = request.user
        product_data = Product.objects.get(id=product_id)
        # Kiểm tra xem người dùng có tồn tại sp trong giỏ hàng k (status=0)
        user_has_odered = Order.objects.get(user=logged_user, status=0)
        order = user_has_odered
        #Người dùng có 1 order chưa thành công
        # 2 TH: 
        # TH1: người dùng thêm 1 sản phẩm mới (không trùng sp trong giỏ hàng) => Thêm mới 1 dòng OrderDetail với sp mới 
        
        # TH2: thêm 1 sp trùng với sp đã có trong giỏ hàng => cập nhật OrderDetail với sp đó và tăng quantity lên 
        orderdetail = OrderDetail.objects.get(order=order, product = product_data)
        # orderdetail = order.orderdetail_set.get(product=product_data)
        # Qua dòng này thì đồng nghĩa với sp thêm mới trùng với sp trong giỏ hàng.
        # Tăng quantity lên 1, tăng amount
        orderdetail.quantity +=1
        orderdetail.amount = orderdetail.quantity * product_data.price
        orderdetail.save()
    except Product.DoesNotExist:
        pass
    except Order.DoesNotExist:
        # Rớt vào except thì đơn hàng chưa thành công (không có đơn hàng hoặc có nhưng mà thanh toán rồi status=1)
        #Tạo mới 1 Oder với logged_user
        new_order = Order.objects.create(
            user = logged_user,
            status = 0,
            create_date = now(),
            total_amount = 0,
            phone = '',
            address = ''
        )
        # Order không có thông tin về sannr phẩm, tạo tiếp 1 OrderDetail
        OrderDetail.objects.create(
            product = product_data,
            order = new_order,
            quantity = 1,
            amount = product_data.price
        )
    except OrderDetail.DoesNotExist:
        # TH1: người dùng thêm 1 sản phẩm mới (không trùng sp trong giỏ hàng) => Thêm mới 1 dòng OrderDetail với sp mới 
        OrderDetail.objects.create(
            product = product_data,
            order = order,
            quantity = 1,
            amount = product_data.price
        )
    user_ordered = Order.objects.get(user=logged_user, status=0)
    quantity = sum([item.quantity for item in user_ordered.orderdetail_set.all()])
    return JsonResponse(data={'quantity':quantity})


@login_required(login_url='/user/login')
def show_cart(request):
    orderdetail = []
    message = ""
    total_amount=0
    try:
        logged_user = request.user
        order = Order.objects.get(user=logged_user, status=0)
        orderdetail = order.orderdetail_set.all()
        if len(orderdetail) ==0:
            message = "Không có sản phẩm nào trong giỏ hàng"
        else:
            total_amount = sum([item.amount for item in orderdetail])
    except:
        message = "Không có sản phẩm nào trong giỏ hàng"
    return render(
        request=request,
        template_name='cart/cart.html',
        context={
            'data_orderdetail': orderdetail,
            'message': message,
            'total_amount': total_amount,
        }
    )
    
    
# Hàm hỗ trợ tăng, giảm sản phẩm
@login_required(login_url='/user/login')
def change_product_quantity(request, action, product_id):
    #action: increase/decrease
    logged_user = request.user
    product_data = Product.objects.get(id=product_id)
    order = Order.objects.get(user=logged_user, status=0)
    orderdetail = OrderDetail.objects.get(order=order, product=product_data)  
    
    if action == 'increase':
        orderdetail.quantity +=1
        orderdetail.amount = orderdetail.quantity * product_data.price
        orderdetail.save()
    else: #decrease. Khi quantity==1 nếu giảm tiếp thì xoá khỏi giỏ hàng
        if orderdetail.quantity == 1:
            orderdetail.delete()
        else:
            orderdetail.quantity -=1
            orderdetail.amount = orderdetail.quantity * product_data.price
            orderdetail.save()
    return redirect('show_cart')

@login_required(login_url='/user/login')
def delete_product_quantity(request, product_id):
    logged_user = request.user
    product_data = Product.objects.get(id=product_id)
    order = Order.objects.get(user=logged_user, status=0)
    orderdetail = OrderDetail.objects.get(order=order, product=product_data)  
    orderdetail.delete()
    return redirect('show_cart')

@login_required(login_url='/user/login')
def checkout(request):
    orderdetail = []
    total_amount=0
    logged_user = request.user
    order = Order.objects.get(user=logged_user, status=0)
    orderdetail = order.orderdetail_set.all()
    if request.method == "POST":
        phone = request.POST['phone']
        address = request.POST['address']
        order.phone = phone
        order.address = address
        order.total_amount = sum([item.amount for item in orderdetail])
        order.status = 1 # Đơn thành cong
        order.save()
        for od_detail in orderdetail:
            od_detail.product.stock_quantity -= od_detail.quantity
            od_detail.product.save() 
            
        from_email = settings.EMAIL_HOST_USER
        subject = "Cảm ơn đã mua hàng ở shop-django"
        message = f''' Hi {logged_user.username}
    Cảm ơn đã mua hàng bên shop
    Tổng giá trị đơn hàng là: {intcomma(order.total_amount)} ₫
        
    Thanks
    Shop-django
'''
        recipient_list = [logged_user.email]
        send_mail(subject, message, from_email, recipient_list)
        return redirect('index')
    return render(
        request=request,
        template_name='cart/checkout.html',
        context={
            'data_orderdetail': orderdetail,
            'total_amount': total_amount,
        }
    )