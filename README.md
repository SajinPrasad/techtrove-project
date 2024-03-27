# TechTrove Ecommerce Web App

TechTrove is a modern ecommerce web application designed to provide users with a seamless shopping experience. Built on Django framework, TechTrove offers a wide range of features for both customers and administrators.

## Features

- **User Authentication:** Secure user authentication system allows users to register, login, and manage their accounts.
- **Product Catalog:** Browse through a diverse range of products organized into categories for easy navigation.
- **Shopping Cart:** Add products to your cart, update quantities, and proceed to checkout with ease.
- **Order Management:** Track your orders, view order history, and manage order details.
- **Coupon System:** Apply discount coupons during checkout to avail special offers and discounts.
- **Admin Panel:** Powerful admin panel for managing products, orders, users, and coupons.
- **Responsive Design:** Enjoy a seamless shopping experience on any device - desktop, tablet, or mobile.

## Installation

1. Clone the repository:

   git clone https://github.com/SajinPrasad/techtrove-project.git

3. Navigate to the project directory:

4. Install dependencies:

    pip install -r requirements.txt
  
6. Set up environment variables:

- Create a `.env` file in the project root directory.
- Define the required environment variables (e.g., `SECRET_KEY`, `DATABASE_URL`, etc.).

5. Run migrations:

   -python manage.py makemigrations
   -python manage.py migrate


6. Start the development server:

     python manage.py runserver


7. Open your web browser and navigate to `http://localhost:8000` to access the TechTrove web app.

## Contributing

Contributions are welcome! Feel free to open issues or pull requests for bug fixes, new features, or improvements.


