from . import app_cart


@app_cart.route('/get_cart')
def get_cart():
    return "get_cart"
