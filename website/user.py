from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user
from website.models import User, Post, Media, Cart, Order, LogEvent, OrderItem
from website import db
from .utils import user_required
from sqlalchemy import or_
from datetime import datetime
from random import sample
import os

user = Blueprint('user', __name__)

@user.route('/favicon.ico')
def favicon():
    abort(404)

@user.route('/<username>/home', methods=['GET', 'POST'])
@login_required
@user_required
def home(username):
    if request.method == 'GET' and 'keyword' in request.args:
        keyword = request.args.get('keyword')
        category = request.args.get('category')

        # Check if both keyword and category are empty
        if not keyword and not category:
            flash('Please enter search criteria.', 'warning')
            return redirect(url_for('user.home', username=username))

        return redirect(url_for('user.search_results', username=username, keyword=keyword, category=category))

    # Get all posts from the database
    all_posts = Post.query.all()

    # Select 30 random posts
    selected_posts = sample(all_posts, min(30, len(all_posts)))

    return render_template('home.html', username=username, posts=selected_posts)

@user.route('/<username>/home/searchresults', methods=['GET', 'POST'])
@login_required
@user_required
def search_results(username):
    keyword = request.args.get('keyword')
    category = request.args.get('category')

    if not keyword and not category:
        flash('Please provide search criteria')
        return redirect(url_for('user.home', username=username))

    if keyword and category:
        posts = Post.query.filter(and_(
            or_(Post.title.ilike(f'%{keyword}%'), Post.description.ilike(f'%{keyword}%')),
            Post.category == category
        )).all()
    elif keyword:
        posts = Post.query.filter(or_(
            Post.title.ilike(f'%{keyword}%'), Post.description.ilike(f'%{keyword}%'))
        ).all()
    elif category:
        posts = Post.query.filter_by(category=category).all()
    else:
        flash('No results found')

    return render_template('search_results.html', username=username, posts=posts, keyword=keyword, category=category)

@user.route('/<username>/home/product/<post_id>', methods=['GET', 'POST'])
@login_required
@user_required
def product(username, post_id):
    # Fetch the post
    post = Post.query.get(post_id)
    if not post:
        flash('Post not found')
        return redirect(url_for('user.home', username=username))

    in_cart = Cart.query.filter_by(user=current_user, post=post).first() is not None

    return render_template('product.html', username=username, post=post, in_cart=in_cart)

@user.route('/<username>/user/cart/remove/<int:post_id>', methods=['POST'])
@login_required
@user_required
def remove_from_cart(username, post_id):
    # Fetch the current user
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('some_error_route'))

    # Find the item in the user's cart
    cart_item = Cart.query.filter_by(user_id=user.id, post_id=post_id).first()

    if not cart_item:
        flash('Item not found in the cart', 'error')
        return redirect(url_for('some_error_route'))
        
    # Remove the item from the cart
    db.session.delete(cart_item)
    db.session.commit()

    flash('Item removed from the cart', 'success')
    return redirect(url_for('user.product', username=username, post_id=post_id))

@user.route('/<username>/user/cart/add_to_cart/<int:post_id>', methods=['POST'])
@login_required
@user_required
def add_to_cart(username, post_id):
    post = Post.query.get(post_id)

    if not post:
        flash('Post not found', 'error')
        return redirect(url_for('user.home'))

    cart_item = Cart.query.filter_by(user=current_user, post=post).first()

    if cart_item:
        flash('Item already in cart', 'warning')
    else:
        new_cart_item = Cart(user=current_user, post=post)
        db.session.add(new_cart_item)
        db.session.commit()
        flash('Item added to cart successfully', 'success')

    return redirect(url_for('user.product', username=username, post_id=post_id))

@user.route('/<username>/home/cart')
@login_required
@user_required
def cart(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('user.home', username=username))

    cart_items = Cart.query.filter_by(user=user).all()
    cart_total = user.calculate_cart_total()
    posts_in_cart = [item.post for item in cart_items]

    return render_template('cart.html', username=username, posts=posts_in_cart, cart_total=cart_total)

@user.route('/<username>/home/cart/order_confirmation', methods=['POST'])
@login_required
@user_required
def order_confirmation(username):
    selected_items = request.form.getlist('selected_items[]')

    if not selected_items:
        flash('Your cart is empty. Please add items before proceeding to checkout.', 'warning')
        return redirect(url_for('user.cart', username=username))

    posts_in_cart = Post.query.filter(Post.id.in_(selected_items)).all()

    return render_template('order_confirmation.html', 
        username=username, 
        selected_items=posts_in_cart)

@user.route('/<username>/home/cart/complete_purchase', methods=['POST'])
@login_required
@user_required
def complete_purchase(username):
    if request.method == 'POST':
        # Get form data
        shipping_address = request.form.get('shipping_address')
        shipping_city = request.form.get('shipping_city')
        shipping_state = request.form.get('shipping_state')
        shipping_country = request.form.get('shipping_country')
        shipping_zipcode = request.form.get('shipping_zipcode')
        phone_number = request.form.get('phone_number')
        card_number = request.form.get('card_number')
        card_holder = request.form.get('card_holder')
        card_expiry_date = request.form.get('card_expiry_date')
        card_cvv = request.form.get('card_cvv')
        selected_items = request.form.getlist('selected_items[]')
        quantities = request.form.getlist('quantity')

        # Get user and vendor IDs for the order
        user_id = current_user.id
        # Assuming you have a way to associate a vendor ID with the selected items
        # Replace this logic with your own logic to retrieve vendor IDs
        vendor_ids = [post.author_id for post in Post.query.filter(Post.id.in_(selected_items)).all()]

        # Calculate total amount
        total_amount = 0.0
        order_items = []
        for index, post_id in enumerate(selected_items):
            post = Post.query.get(post_id)
            quantity = int(quantities[index])

            # Calculate total amount for the order
            total_amount += post.price * quantity

            # Create OrderItem instances
            order_item = OrderItem(post_id=post.id, quantity=quantity)
            order_items.append(order_item)

        # Create the Order instance
        new_order = Order(
            purchaser_id=current_user.id,  # Assuming current_user holds the purchaser's details
            order_date=datetime.utcnow(),
            shipping_address=shipping_address,
            shipping_city=shipping_city,
            shipping_state=shipping_state,
            shipping_country=shipping_country,
            shipping_zipcode=shipping_zipcode,
            phone_number=phone_number,
            card_number=card_number,
            card_holder=card_holder,
            card_expiry_date=card_expiry_date,
            card_cvv=card_cvv,
            order_status='pending',
            total_amount=total_amount  # Calculate the total amount based on purchased items
        )

        # Add and commit the new order to the database
        db.session.add(new_order)
        db.session.commit()

        # Update: Remove purchased items from the cart
        for index, post_id in enumerate(selected_items):
            post = Post.query.get(post_id)
            quantity = int(quantities[index])

            # Get the vendor_id for each post
            vendor_id = post.author_id  # Assuming author_id represents the vendor ID

            # Create OrderItem instances with vendor IDs
            order_item = OrderItem(
                order=new_order,
                post_id=post_id,
                quantity=quantity,
                vendor_id=vendor_id  # Assign the vendor ID to the OrderItem
            )
            db.session.add(order_item)

            # Remove the purchased item from the cart
            cart_item = Cart.query.filter_by(user_id=current_user.id, post_id=post_id).first()
            if cart_item:
                db.session.delete(cart_item)

        db.session.commit()

        flash('Order placed successfully!')
        return redirect(url_for('user.home', username=username))

    flash('Invalid request')
    return redirect(url_for('user.cart', username=username))

@user.route('/<username>/home/account')
@login_required
@user_required
def account(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.error'))

    return render_template('account.html', username=username, user=user)

@user.route('/<username>/home/account/update_theme', methods=['POST'])
@login_required
@user_required
def update_theme(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.error'))

    # Get the theme preference from the form
    theme_preference = request.form.get('theme_preference')

    # Convert the received value to a boolean
    if theme_preference == '1':
        user.theme = True
    else:
        user.theme = False

    # Update the user's theme preference in the database
    db.session.commit()

    flash('Theme preference updated successfully!', 'success')
    return redirect(url_for('user.account', username=username))

@user.route('/<username>/home/account/change_username', methods=['POST'])
@login_required
@user_required
def change_username(username):
    new_username = request.form.get('new_username')

    if not new_username:
        flash('Please provide a new username')
        return redirect(url_for('user.account', username=username))

    existing_user = User.query.filter_by(username=new_username).first()

    if existing_user:
        flash('Username already exists. Please choose a different one.', 'warning')
        return redirect(url_for('user.account', username=username))

    # Store the current user's ID for logging purposes
    current_user_id = current_user.id

    try:
        # Update the current user's username
        current_user.username = new_username

        # Log the event with user ID
        event_description = f"User '{current_user_id}' changed their username to '{new_username}'."
        new_event = LogEvent(event_description=event_description)
        db.session.add(new_event)

        db.session.commit()

        flash('Username changed successfully!', 'success')
        return render_template('logout_timer.html')

    except Exception as e:
        db.session.rollback()  # Rollback changes in case of an exception
        flash(f'Failed to update username due to a database error: {str(e)}', 'error')
        return redirect(url_for('user.account', username=username))

@user.route('/<username>/home/account/change_password', methods=['POST'])
@login_required
@user_required
def change_password(username):
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')

    if not current_password or not new_password or not confirm_new_password:
        flash('Please provide all password fields', 'warning')
        return redirect(url_for('user.account', username=username))

    if new_password != confirm_new_password:
        flash('Passwords must match.', 'warning')
        return redirect(url_for('user.account', username=username))

    if not current_user.check_password(current_password):
        flash('Incorrect current password', 'error')
        return redirect(url_for('user.account', username=username))

    # Store the current user's ID for logging purposes
    current_user_id = current_user.id

    # Set the new password for the current user
    current_user.set_password(new_password)

    # Log the event with user ID
    event_description = f"User '{current_user_id}' changed their password."
    new_event = LogEvent(event_description=event_description)
    db.session.add(new_event)

    db.session.commit()

    flash('Password changed successfully!', 'success')
    return render_template('logout_timer.html')

@user.route('/<username>/home/account/deactivate_account', methods=['POST'])
@login_required
@user_required
def deactivate_account(username):
    # Store the current user's ID for logging purposes
    current_user_id = current_user.id

    # Deactivate the current user's account
    current_user.is_active = False

    # Log the event with user ID
    event_description = f"User '{current_user_id}' deactivated their account."
    new_event = LogEvent(event_description=event_description)
    db.session.add(new_event)

    db.session.commit()

    # You might want to handle additional cleanup or logic here
    flash('Your account has been deactivated')
    return redirect(url_for('auth.logout'))
