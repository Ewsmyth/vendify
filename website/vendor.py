from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, current_app, send_from_directory, jsonify
from flask_login import login_required, current_user
from website.models import User, Post, Media, LogEvent, ALLOWED_EXTENSIONS, Order, OrderItem
from website import db
from .utils import vendor_required, generate_unique_filename
import os

vendor = Blueprint('vendor', __name__)

@vendor.route('/favicon.ico')
def favicon():
    abort(404)

@vendor.route('/<username>/vendorpage')
@login_required
@vendor_required
def vendorpage(username):
    return render_template('vendorpage.html', username=username)

@vendor.route('/<username>/vendorpage/post', methods=['GET', 'POST'])
@login_required
@vendor_required
def post(username):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        quantity = int(request.form['quantity'])
        category = request.form['category']
        cover_photo = request.files['cover_photo_url']
        price = float(request.form['price'])

        if cover_photo and '.' in cover_photo.filename and cover_photo.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
            unique_filename = generate_unique_filename(current_user.username, cover_photo.filename.rsplit('.', 1)[1])
            cover_photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename))

            new_post = Post(
                title=title, 
                description=description, 
                quantity=quantity, 
                category=category, 
                price=price,
                cover_photo_url=unique_filename, 
                author_id=current_user.id
            )

            db.session.add(new_post)
            db.session.commit()

            # Handling multiple media files
            media_files = request.files.getlist('media_files')
            for media_file in media_files:
                if media_file and '.' in media_file.filename and media_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                    unique_media_filename = generate_unique_filename(current_user.username, media_file.filename.rsplit('.', 1)[1])
                    media_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], unique_media_filename))

                    new_media = Media(media_url=unique_media_filename, post_id=new_post.id)
                    db.session.add(new_media)
                    db.session.commit()

            # Log the event
            event_description = f"Vendor '{current_user.username}' posted '{new_post.title}'"
            new_event = LogEvent(event_description=event_description)
            db.session.add(new_event)
            db.session.commit()

            flash('Post created successfully', 'success')
            return redirect(url_for('vendor.post', username=username))

        flash('Invalid file or extension', 'error')
        return redirect(url_for('vendor.post', username=username))

    current_user_posts = (Post.query.filter_by(author_id=current_user.id).options(db.joinedload(Post.media)).all())
    return render_template('post.html', username=username, posts=current_user_posts)

@vendor.route('/get_media_count/<int:post_id>', methods=['GET'])
def get_media_count(post_id):
    post = Post.query.filter_by(id=post_id).first()
    if post:
        media_count = len(post.media)  # Assuming 'media' is the relationship between Post and Media models
        return jsonify({'media_count': media_count})
    else:
        return jsonify({'media_count': 0})

@vendor.route('/<username>/vendorpage/sales')
@login_required
@vendor_required
def sales(username):
    # Retrieve orders and order items for the current vendor
    vendor_orders = Order.query.join(OrderItem).join(User).join(Post).filter(
        User.id == current_user.id,
        OrderItem.vendor_id == current_user.id,
        OrderItem.post_id == Post.id,
        OrderItem.order_id == Order.id,
        Order.order_status == 'delivered'  # Filter by order status
    ).all()

    print(vendor_orders)

    return render_template('sales.html', username=username, orders=vendor_orders, Post=Post)

@vendor.route('/<username>/vendorpage/orders')
@login_required
@vendor_required
def orders(username):
    # Retrieve orders and order items for the current vendor
    vendor_orders = Order.query.join(OrderItem).join(User).join(Post).filter(
        User.id == current_user.id,
        OrderItem.vendor_id == current_user.id,
        OrderItem.post_id == Post.id,
        OrderItem.order_id == Order.id
    ).all()

    return render_template('orders.html', username=username, orders=vendor_orders, Post=Post)

@vendor.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory('D:/uploads', filename)

@vendor.route('/<username>/vendorpage/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
@vendor_required
def update_order_status(username, order_id):
    new_status = request.form.get('new_status')

    order = Order.query.filter_by(id=order_id).first()

    if not order:
        flash('Order not found', 'error')
    else:
        order.order_status = new_status
        db.session.commit()
        flash('Order status updated successfully', 'success')

    return redirect(url_for('vendor.orders', username=username))

@vendor.route('/<username>/vendorpage/account')
@login_required
@vendor_required
def account(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash('User not found')
        return redirect(url_for('user.error'))

    return render_template('vendoraccount.html', username=username, user=user)

@vendor.route('/<username>/vendorpage/account/change_username', methods=['POST'])
@login_required
@vendor_required
def change_username(username):
    new_username = request.form.get('new_username')

    if not new_username:
        flash('Please provide a new username', 'error')
        return redirect(url_for('vendor.account', username=username))

    # Check if new username already exists in the database
    existing_user = User.query.filter_by(username=new_username).first()
    if existing_user:
        flash('Username already exists. Please choose a different one.', 'warning')
        return redirect(url_for('vendor.account', username=username))

    # Store the current user's ID for logging purposes
    current_user_id = current_user.id

    try:
        # Update the current user's username
        current_user.username = new_username

        # Log the event with the user ID
        event_description = f"User '{current_user_id}' changed their username to '{new_username}'."
        new_event = LogEvent(event_description=event_description)
        db.session.add(new_event)

        db.session.commit()

        flash('Username changed successfully!', 'success')
        return render_template('logout_timer.html')

    except Exception as e:
        db.session.rollback()
        flash(f'Failed to update username due to a database error: {str(e)}', 'error')
        return redirect(url_for('vendor.account', username=username))

@vendor.route('/<username>/vendorpage/account/change_password', methods=['POST'])
@login_required
@vendor_required
def change_password(username):
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')

    if not current_password or not new_password or not confirm_new_password:
        flash('Please provide all password fields', 'warning')
        return redirect(url_for('vendor.account', username=username))

    if new_password != confirm_new_password:
        flash('Passwords must match', 'warning')
        return redirect(url_for('vendor.account', username=username))

    if not current_user.check_password(current_password):
        flash('Incorrect password', 'error')
        return redirect(url_for('vendor.account', username=username))

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

# This is a route for a form on the admin account page that allows the admin to change their account status
@vendor.route('/<username>/vendorpage/account/deactivate_account', methods=['POST'])
@login_required
@vendor_required
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
    flash('Your account has been deactivated', 'success')
    return redirect(url_for('auth.logout'))

@vendor.route('/<username>/vendorpage/account/update_theme', methods=['POST'])
@login_required
@vendor_required
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
    return redirect(url_for('vendor.account', username=username))