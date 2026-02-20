from flask import Flask, render_template_string, request, jsonify, session
import uuid
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

# ---------------- PRODUCTS ---------------- #

products = [
    {
        "id": 1,
        "name": "Wireless Headphones",
        "price": 99.99,
        "image": "https://picsum.photos/300/200?random=1",
        "category": "Electronics",
        "description": "High-quality wireless headphones",
        "rating": 4.5,
        "inStock": True
    },
    {
        "id": 2,
        "name": "Smart Watch",
        "price": 199.99,
        "image": "https://picsum.photos/300/200?random=2",
        "category": "Electronics",
        "description": "Smartwatch with health tracking",
        "rating": 4.2,
        "inStock": True
    },
    {
        "id": 3,
        "name": "Running Shoes",
        "price": 79.99,
        "image": "https://picsum.photos/300/200?random=3",
        "category": "Fashion",
        "description": "Comfortable running shoes",
        "rating": 4.7,
        "inStock": True
    }
]

# ---------------- STORAGE ---------------- #

orders = {}
product_reviews = {}
user_profiles = {}

# ---------------- HTML ---------------- #

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ShopEasy</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
</head>

<body class="bg-gray-100">

<div class="max-w-5xl mx-auto p-6">

<h1 class="text-3xl font-bold mb-6">🛒 ShopEasy</h1>

<div class="grid grid-cols-1 md:grid-cols-3 gap-6">

{% for p in products %}
<div class="bg-white p-4 rounded shadow">

<img src="{{p.image}}" class="w-full h-40 object-cover rounded">

<h2 class="font-bold mt-2">{{p.name}}</h2>

<p>${{p.price}}</p>

<button onclick="addToCart({{p.id}})"
class="bg-blue-600 text-white px-4 py-2 mt-2 rounded">
Add to Cart
</button>

</div>
{% endfor %}

</div>

<hr class="my-6">

<h2 class="text-xl font-bold">Cart</h2>
<div id="cart"></div>

</div>

<script>

function loadCart(){
fetch('/get_cart')
.then(r=>r.json())
.then(data=>{
document.getElementById('cart').innerHTML =
data.map(i=>`<p>${i.name} x${i.quantity}</p>`).join("")
})
}

function addToCart(id){
fetch('/add_to_cart',{
method:'POST',
headers:{'Content-Type':'application/json'},
body:JSON.stringify({product_id:id})
})
.then(()=>loadCart())
}

loadCart()

</script>

</body>
</html>
"""

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE, products=products)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    if 'cart' not in session:
        session['cart'] = []

    data = request.get_json()
    product_id = data.get('product_id')

    product = next((p for p in products if p['id'] == product_id), None)

    if product:
        cart = session['cart']
        item = next((i for i in cart if i['id'] == product_id), None)

        if item:
            item['quantity'] += 1
        else:
            cart.append({
                "id": product['id'],
                "name": product['name'],
                "price": product['price'],
                "quantity": 1
            })

        session['cart'] = cart
        return jsonify({"success": True, "cart": cart})

    return jsonify({"success": False})


@app.route("/get_cart")
def get_cart():
    return jsonify(session.get('cart', []))


@app.route("/checkout", methods=["POST"])
def checkout():

    if 'cart' not in session or not session['cart']:
        return jsonify({"success": False})

    order_id = str(uuid.uuid4())

    orders[order_id] = {
        "id": order_id,
        "items": session['cart'],
        "timestamp": datetime.now().isoformat()
    }

    session['cart'] = []

    return jsonify({"success": True, "order_id": order_id})


# ---------------- RUN ---------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)