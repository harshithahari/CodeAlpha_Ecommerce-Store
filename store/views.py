from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Product, Order, OrderItem

# Home Page
def home(request):
    query = request.GET.get('q')
    category = request.GET.get('category')

    # ഡാറ്റാബേസ് പുതിയതായതുകൊണ്ട് ആദ്യ തവണ തനിയെ പ്രൊഡക്റ്റുകൾ ഉണ്ടാക്കുന്നു
    if not Product.objects.exists():
        Product.objects.create(
            name="Dell 14 plus",
            price=73100.00,
            category="Laptops",
            description="Core 7 240H | 16GB LPDDR5X | 512GB SSD",
            image="https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=500" 
        )
        Product.objects.create(
            name="headphone",
            price=4999.00,
            category="Accessories",
            description="Small Bluetooth On Ear Headphones",
            image="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
        )
        Product.objects.create(
            name="Samsung Galaxy S25",
            price=71000.00,
            category="Mobiles",
            description="Meet the New Galaxy S25 and S25+, the smartphones with a Next-gen camera",
            image="https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=500"
        )

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category=category)

    return render(request, 'store/home.html', {'products': products})

# Add Product to Cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        user = request.user
        order, created = Order.objects.get_or_create(user=user, completed=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
        if not created:
            order_item.quantity += 1
            order_item.save()
    else:
        if not request.session.session_key:
            request.session.create()
            
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if product_id_str in cart:
            cart[product_id_str] += 1
        else:
            cart[product_id_str] = 1
            
        request.session['cart'] = cart
        request.session.modified = True

    messages.success(request, f"{product.name} added to cart.")
    return redirect('cart')

# View Cart
def cart(request):
    items = []
    total = 0

    if request.user.is_authenticated:
        user = request.user
        order = Order.objects.filter(user=user, completed=False).first()
        if order:
            items = OrderItem.objects.filter(order=order)
            total = sum(item.total_price for item in items)
    else:
        cart = request.session.get('cart', {})
        for product_id, quantity in cart.items():
            product = Product.objects.filter(id=int(product_id)).first()
            if product:
                total_price = product.price * quantity
                items.append({
                    'product': product,
                    'quantity': quantity,
                    'total_price': total_price,
                    'id': product_id
                })
                total += total_price

    return render(request, 'store/cart.html', {'items': items, 'total': total})

# Remove Item from Cart
def remove_item(request, item_id):
    if request.user.is_authenticated:
        user = request.user
        item = get_object_or_404(OrderItem, id=item_id, order__user=user)
        item.delete()
    else:
        cart = request.session.get('cart', {})
        item_id_str = str(item_id)
        if item_id_str in cart:
            del cart[item_id_str]
            request.session['cart'] = cart
            request.session.modified = True

    messages.success(request, "Item removed from cart.")
    return redirect('cart')

# Register User
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('register')

        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Registration successful! Please login.")
        return redirect('login')

    return render(request, 'store/register.html')

# Login User
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'store/login.html')

# Logout User
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

# Place Order
def place_order(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        order = Order.objects.filter(user=request.user, completed=False).first()
        
        if order:
            order.completed = True
            order.save()
            messages.success(request, "Order placed successfully!")
            
            request.session['shipping_name'] = name
            request.session['shipping_address'] = address
            request.session['shipping_phone'] = phone
            
            return redirect('order_success')
            
    return redirect('cart')

# Order Success
def order_success(request):
    name = request.session.get('shipping_name', '')
    address = request.session.get('shipping_address', '')
    phone = request.session.get('shipping_phone', '')

    context = {
        'name': name,
        'address': address,
        'phone': phone
    }
    return render(request, 'store/order_success.html', context)

# Order History
def order_history(request):
    if not request.user.is_authenticated:
        return redirect('login')

    orders = Order.objects.filter(user=request.user, completed=True)
    return render(request, 'store/order_history.html', {'orders': orders})