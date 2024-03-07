from .models import Product
class Cart():
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if 'cart' not in request.session:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {'price': str(product.price)}
            self.session.modified = True

    def delete(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
    
    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        poducts_id = self.cart.keys()
        products = Product.objects.filter(id__in=poducts_id)
        return products