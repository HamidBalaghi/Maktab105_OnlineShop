# Online Shop

## Description

Online Shop is a Django-based e-commerce platform that allows admins to manage products and customers to browse, sign up, and order products. The platform features multiple admin roles with different permissions and includes advanced user authentication methods.

## Features

- **Admin Management**:
  - Custom admin panel with multilingual support (English and Persian) using `django-modeltranslation`.
  - Superuser, Supervisor, and Operator roles with different permissions.
  - Add, update, and remove products.

- **Customer Management**:
  - Signup and login with email, username, and OTP code.
  - Manage multiple addresses and orders.
  - Use discount codes for orders.

- **Order Management**:
  - Customers can create orders and update their carts.
  - Orders can be saved in cookies for unauthenticated users.
  - Ajax-based functionality for improved user experience.

- **Backend**:
  - Custom authentication backend with Redis for OTP code verification.
  - Celery tasks for deleting inactive accounts and expired discounts.
  - Logical delete functionality for soft deleting records.
  
- **Frontend**:
  - Built using Django Templates.
  - Utilizes JavaScript, HTML, CSS, and Tailwind CSS for styling.

- **APIs**:
  - Most apps are built using Django Class-Based Views (CBV).
  - The Order app is built using Django Rest Framework (DRF).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/HamidBalaghi/Maktab105_OnlineShop.git
   cd online-shop
   
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
4. Make the migrations:
   ```bash
   python manage.py makemigrations
5. Run the migrations:
   ```bash
   python manage.py migrate
6. Start Celery in a new tab by this:
   ```bash
   celery -A config worker --loglevel=info
7. Start Celery beat by in a new tb by this:
   ```bash
    celery -A config beat -l info
8. Run the development server:
   ```bash
   python manage.py runserver

## Usage

1. **Admin Panel**: Access the custom admin panel at `/admin` to manage products and users.
2. **Customer Signup/Login**: Customers can sign up or log in using their email, username, and OTP code.
3. **Product Browsing**: Customers can browse products, add them to their cart, and place orders.
4. **Order Management**: Customers can view and manage their orders and addresses.

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and commit them with clear and concise messages.
4. Push your changes to your fork.
5. Create a pull request to the main repository.


## Photos:
ERD
![HamidBalaghi_OnlineShop_ERD.png](ERD%2FHamidBalaghi_OnlineShop_ERD.png)


Front
![1.png](images%2F1.png)
![2.png](images%2F2.png)
![3.png](images%2F3.png)
![4.png](images%2F4.png)
![5.png](images%2F5.png)
![6.png](images%2F6.png)
![7.png](images%2F7.png)


## Contact

For support or inquiries, please contact [Balaghi.hamid.72@gmail.com](mailto:Balaghi.hamid.72@gmail.com).

