from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required


def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    
    if movie_ids:
        # Convert string keys to integers for database query
        movie_ids_int = [int(mid) for mid in movie_ids]
        movies_in_cart = Movie.objects.filter(id__in=movie_ids_int)
        cart_total = calculate_cart_total(cart, movies_in_cart)

    template_data = {
        'title': 'Cart',
        'movies_in_cart': movies_in_cart,
        'cart_total': cart_total,
        'cart': cart,  # Pass cart to template for quantity display
    }
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    
    # Get quantity from GET parameters with default value of 1
    quantity = request.GET.get('quantity', 1)
    
    try:
        # Convert quantity to integer
        quantity = int(quantity)
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    # Convert id to string for consistent session storage
    movie_id_str = str(id)
    cart[movie_id_str] = quantity
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())

    if not movie_ids:
        return redirect('cart.index')
    
    # Convert string keys to integers for database query
    movie_ids_int = [int(mid) for mid in movie_ids]
    movies_in_cart = Movie.objects.filter(id__in=movie_ids_int)
    cart_total = calculate_cart_total(cart, movies_in_cart)

    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()

    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]  # Use string key
        item.save()

    request.session['cart'] = {}
    template_data = {
        'title': 'Purchase confirmation',
        'order_id': order.id,
    }
    return render(request, 'cart/purchase.html', {'template_data': template_data})