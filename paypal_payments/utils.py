from orders.models import Payment

# Helper function to update Payment details after PayPal execution
def update_payment_details(payment, paypal_response):
    # Use the details obtained from the executed PayPal payment
    # to update the placeholder Payment object in your system
    payment.status = 'Completed'  # Use the actual PayPal status

    # Access transaction_id from the PayPal response
    try:
        transaction_id = paypal_response.transactions[0].related_resources[0].sale.id
        payment.transaction_id = transaction_id
        payment.save()
    except (AttributeError, IndexError) as e:
        # Handle the case where the expected attributes are not present in the PayPal response
        print(f"Error updating payment details: {e}")
        payment.status = 'Failed'  # Update the status to indicate a failure
        payment.save()