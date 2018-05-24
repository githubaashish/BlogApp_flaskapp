from flask import Blueprint, render_template, request
import stripe


payments = Blueprint('payments', __name__)
# use your own pub_key and the secret_key
pub_key = ''
secret_key = ''

stripe.api_key = secret_key

@payments.route('/initiate_pay')
def initiate_pay(): 
    return render_template("payment.html", pub_key=pub_key)


@payments.route('/payment_done')
def payment_done(): 
    return render_template("thanks.html")

@payments.route('/pay', methods=['POST'])
def pay():
    customer = stripe.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])
    charge = stripe.Charge.create(
    customer=customer.id, 
    amount=100,
    currency='usd',
    description='Payment of product')
    return render_template('thanks.html')

