from django.shortcuts import render ,redirect
from django.views import View
from .models import Customer,Product,Cart,Orderplaced
from .forms import CustomerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

# def home(request):
#  return render(request, 'app/home.html')

class ProductView(View):
 def get(self,request):
  totalitem = 0
  mobiles = Product.objects.filter(category='M')
  watch = Product.objects.filter(category='W')
  airpods = Product.objects.filter(category='A')
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
  return render(request,'app/home.html',{'mobiles':mobiles,'watch':watch,'airpods':airpods,'totalitem':totalitem})

# def product_detail(request):
#  return render(request, 'app/productdetail.html')

class ProductDetailView(View):
 def get(self,request,pk):
  totalitem = 0
  product = Product.objects.get(pk=pk)
  item_already_in_cart = False
  if request.user.is_authenticated:
    item_already_in_cart = Cart.objects.filter(Q(product=product.id) & Q(user=request.user)).exists()  
    totalitem = len(Cart.objects.filter(user=request.user))   
  return render(request,'app/productdetail.html',{'product':product,'item_already_in_cart':item_already_in_cart,'totalitem':totalitem})

@login_required
def add_to_cart(request):
 user = request.user
 product_id = request.GET.get('prod_id')
 product = Product.objects.get(id=product_id)
 Cart(user=user,product=product).save()
 return redirect('/cart')


@login_required
def show_cart(request):
  totalitem = 0
  if request.user.is_authenticated:
    user = request.user
    totalitem = len(Cart.objects.filter(user=request.user))   
    cart = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 50.0
    total_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == user ]
    if cart_product:
      for p in cart_product:
        tempamount = (p.quantity * p.product.discounted_price)
        amount +=tempamount
        totalamount = amount + shipping_amount
      return render(request, 'app/addtocart.html' ,{'carts':cart,'totalamount':totalamount ,'amount':amount,'totalitem':totalitem})
    else:    
      return render(request,'app/emptycart.html')
    
def plus_cart(request):
  if request.method =='GET':
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
    c.quantity+=1
    c.save()
    amount = 0.0
    shipping_amount = 50.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user ]
    for p in cart_product:
      tempamount = (p.quantity * p.product.discounted_price)
      amount +=tempamount

    data = {
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':amount + shipping_amount
    }
    return JsonResponse(data)


def minus_cart(request):
  if request.method =='GET':
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
    c.quantity-=1
    c.save()
    amount = 0.0
    shipping_amount = 50.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user ]
    for p in cart_product:
      tempamount = (p.quantity * p.product.discounted_price)
      amount +=tempamount   

    data = {
      'quantity':c.quantity,
      'amount':amount,
      'totalamount':amount + shipping_amount
    }
    return JsonResponse(data)



def remove_cart(request):
  if request.method =='GET':
    prod_id = request.GET['prod_id']
    c = Cart.objects.get(Q(product = prod_id) & Q(user = request.user))
    c.delete()
    amount = 0.0
    shipping_amount = 50.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user ]
    for p in cart_product:
      tempamount = (p.quantity * p.product.discounted_price)
      amount +=tempamount 

    data = {
      'amount':amount,
      'totalamount':amount + shipping_amount
    }
    return JsonResponse(data)


def buy_now(request):
 return render(request, 'app/buynow.html')

# def profile(request):
#  return render(request, 'app/profile.html')

@login_required
def address(request):
 totalitem = 0
 add = Customer.objects.filter(user=request.user)
 if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
 return render(request, 'app/address.html',{'add':add,'active':'btn-primary','totalitem':totalitem})

@login_required
def orders(request):
 totalitem = 0
 op = Orderplaced.objects.filter(user=request.user)
 if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
 return render(request, 'app/orders.html',{'order_placed':op,'totalitem':totalitem})

@login_required
def change_password(request):
 totalitem = 0
 if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
 return render(request, 'app/changepassword.html',{'totalitem':totalitem})

def mobile(request,data=None):
  totalitem = 0
  if data == None:
    mobiles = Product.objects.filter(category='M')
  elif data == 'APPLE' or data == 'SAMSUNG' or data == 'REDMI' or data == 'OnePlus' or data == 'realme':
    mobiles = Product.objects.filter(category='M').filter(brand=data)  
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
  return render(request, 'app/mobile.html',{'mobiles':mobiles,'totalitem':totalitem})

# def login(request):
#  return render(request, 'app/login.html')

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')

class CustomerRegistrationView(View):
  def get(self,request):
    form = CustomerRegistrationForm()
    return render(request,'app/customerregistration.html',{'form':form})
  def post(self,request):
    form = CustomerRegistrationForm(request.POST)
    if form.is_valid():
      messages.success(request,'Congratulatins!! Registered Successfully')
      form.save()
    return render(request,'app/customerregistration.html',{'form':form})

@login_required
def checkout(request):
  totalitem = 0
  user = request.user
  add = Customer.objects.filter(user=user)
  cart_items = Cart.objects.filter(user=user)
  amount = 0.0
  shipping_amount = 50.0
  totalamount = 0.0
  cart_product = [p for p in Cart.objects.all() if p.user == request.user ]
  if cart_product:
    for p in cart_product:
      tempamount = (p.quantity * p.product.discounted_price)
      amount +=tempamount
    totalamount = amount + shipping_amount
  if request.user.is_authenticated:
    totalitem = len(Cart.objects.filter(user=request.user))
  return render(request, 'app/checkout.html',{'add':add, 'totalamount':totalamount, 'cart_items':cart_items,'totalitem':totalitem})

@login_required
def payment_done(request):
  user = request.user
  custid = request.GET.get('custid')
  customer = Customer.objects.get(id=custid)
  cart = Cart.objects.filter(user=user)
  for c in cart:
    Orderplaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
    c.delete()
  return redirect('orders')

@method_decorator(login_required,name='dispatch')
class ProfileView(View):
  def get(self,request):
    totalitem = 0
    form = CustomerProfileForm()
    if request.user.is_authenticated:
      totalitem = len(Cart.objects.filter(user=request.user))
    return render(request,'app/profile.html',{'form':form,'active':'btn-primary','totalitem':totalitem})
  def post(self,request):
    form = CustomerProfileForm(request.POST)
    if form.is_valid():
      usr = request.user
      name = form.cleaned_data['name']
      locality = form.cleaned_data['locality']
      city = form.cleaned_data['city']
      state = form.cleaned_data['state']
      zipcode = form.cleaned_data['zipcode']
      reg = Customer( user=usr,name=name,locality=locality,city=city,
                     state=state,zipcode=zipcode)
      reg.save()
    messages.success(request,'Congratulations!! Profile Updated Successfully')
    return render(request,'app/profile.html',{'form':form,'active':'btn-primary'})
  


