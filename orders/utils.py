from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings


def render_to_pdf(template_path, context_dict):
    template = get_template(template_path)
    html = template.render(context_dict)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="sales_report.pdf"'

    pisa_status = pisa.CreatePDF(
        html, dest=response
    )
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response



def send_order_confirmation_email(order):
    full_name = order.full_name()
    order_number = order.order_number
    
    context = {
        'full_name' : full_name,
        'order_number' : order_number,
    }

    email_content = render_to_string('email_order_placed.html', context)

    send_mail(
        "TechTrove - Order placed: ",
        email_content,
        settings.EMAIL_HOST_USER,
        [order.email], 
        fail_silently=False,
        html_message=email_content
    )


def send_order_cancellation_email(order):
    full_name = order.full_name()
    order_number = order.order_number
    
    context = {
        'full_name' : full_name,
        'order_number' : order_number,
    }

    email_content = render_to_string('email_order_cancel.html', context)

    send_mail(
        "TechTrove - Order Cancelled: ",
        email_content,
        settings.EMAIL_HOST_USER,
        [order.email], 
        fail_silently=False,
        html_message=email_content
    )
