from django.shortcuts import render, redirect
from .models import Product, Contact, Orders, OrderUpdate
from django.contrib import messages
from math import ceil
import json

# Create your views here.
from django.http import HttpResponse

# Signup User model importing
from django.contrib.auth.models import User

# For authentication
from django.contrib.auth import authenticate, login as auth_login, logout


def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    thank=False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank=True
    return render(request, 'shop/contact.html', {'thank':thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json], default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')


def search(request):
    return render(request, 'shop/search.html')


def productView(request, myid):

    # Fetch the product using the id
    product = Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html', {'product':product[0]})


def checkout(request):
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
        return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
    return render(request, 'shop/checkout.html')

def signup(request):
    if request.method == "POST":
        # GET THE PARAMETERS
        signup_email = request.POST["signup_email"]
        fname = request.POST["fname"]
        lname = request.POST["lname"]
        pass1 = request.POST["pass1"]
        pass2 = request.POST["pass2"]
        username = fname

        if pass1 != pass2:
            messages.error(request, " Your BharaZone account has been successfully created")
            return redirect('ShopHome')


        user = User.objects.create_user(username, signup_email, pass1)
        user.first_name = fname
        user.last_name = lname
        user.save()
        messages.success(request, " Your BharaZone account has been successfully created")
        return redirect('ShopHome')
    else:
        return HttpResponse("404 - Not Found")
    
def login(request):
    if request.method == "POST":
        login_fname = request.POST["login_fname"]
        login_pass = request.POST["login_pass"]

        user=authenticate(username = login_fname, password= login_pass)
        if user is not None:
            auth_login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect("ShopHome")
        else:
            messages.error(request, "Invalid credentials! Please try again")
            return redirect("ShopHome")

    return HttpResponse("404- Not found")

def logout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect("ShopHome")