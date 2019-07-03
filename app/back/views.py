import hashlib
import os
from datetime import date, timedelta

from flask import render_template, request, flash, redirect, url_for, current_app, abort
from flask_login import login_required, current_user, logout_user
from sqlalchemy import func

from .forms import EditGameForm, EditUserForm, EditProfileForm, ChangePasswordForm, RefundProcessForm, AddNewGameForm, \
    UploadFileForm, EditOrderForm
from . import back
from ..models import Order, Game, User, Refund, RefundItem, OrderItem, GamePhoto, Genre
from ..decorators import admin_required
from .. import db


##################### User Backend START ####################
@back.route('/personal_center')
@login_required
def personal_center():
    games = current_user.games
    return render_template('back/personal_center.html',
                           games=games)


def allowed_file(filename):
    allowed_extensions = {'png', 'jpg', 'jpeg'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@back.route('/edit_profile', methods=['POST', 'GET'])
@login_required
def edit_profile():
    form = EditProfileForm(request.form, current_user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(current_user)
        print(request.files)
        if 'photo' in request.files:
            file = request.files['photo']
            if not allowed_file(file.filename):
                flash('Photo format is not supported! Please upload a png or png format file.')
            else:
                filename = hashlib.md5(file.read()).hexdigest() + '.' + file.filename.split('.')[-1]
                file.seek(0)
                photo_path = '/static/photos/' + filename
                save_path = os.path.join(current_app.config['PHOTOS_FOLDER'], filename)
                file.save(save_path)
                current_user.photo_path = photo_path
        db.session.add(current_user)
        db.session.commit()
        flash('You have successfully updated your profile!')
    return render_template('back/edit_profile.html',
                           form=form)


@back.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('back.personal_center'))
        else:
            flash('Invalid password.')
    return render_template("back/change_password.html", form=form)





@back.route('/all_orders_user')
@login_required
def all_orders_user():
    query = current_user.orders
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page,
                                per_page=20,
                                error_out=True)
    orders = pagination.items
    return render_template('back/all_orders_user.html',
                           orders=orders)


@back.route('/refund/<int:id>', methods=['POST', 'GET'])
@login_required
def refund(id):
    order = Order.query.get_or_404(id)
    if order.user_id != current_user.id:
        abort(403)
    if request.method == 'POST':
        refund_items = request.form.getlist('refund_items')
        if not refund_items:
            flash('You should choose at least one item in the order to refund!')
            return redirect(url_for('back.refund', id=order.id))
        refund = Refund()
        refund.order_id = order.id
        refund.user_id = current_user.id
        refund.status = 'pending'
        refund.date = date.today()
        for item_id in refund_items:
            refund_item = RefundItem(item_id=item_id)
            order_item = OrderItem.query.filter_by(id=item_id).first()
            order_item.status = 'refunding'
            refund.refund_items.append(refund_item)
        db.session.add(refund)
        db.session.commit()
        flash('Your refund request has been submitted!')
        return redirect(url_for('back.all_orders_user'))
    return render_template('back/refund.html',
                           order=order)


@back.route('/all_refunds_user')
@login_required
def all_refunds_user():
    query = current_user.refunds
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page,
                                per_page=20,
                                error_out=True)
    refunds = pagination.items

    return render_template('back/all_refunds_admin.html',
                           refunds=refunds,
                           pagination=pagination)


@back.route('/order_detail/<int:id>')
@login_required
def order_detail(id):
    order = Order.query.get_or_404(id)
    if order.user_id != current_user.id:
        abort(403)
    return render_template('back/refund.html',
                           order=order)


@back.route('/all_games_user')
@login_required
def all_games_user():
    query = current_user.games.order_by(Game.issued_date.desc())
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page,
                                per_page=20,
                                error_out=True)
    games = pagination.items
    return render_template('back/all_games_user.html',
                           games=games,
                           pagination=pagination)

##################### User Backend END ####################


##################### Admin Backend START ####################
@back.route('/admin_center')
@admin_required
def admin_center():
    TOP_X_MAX = 5
    top_x_games = db.session.query(func.count(Game.id), Game, Order, OrderItem). \
        filter(Order.id == OrderItem.order_id, Game.id == OrderItem.game_id). \
        filter(Order.date > (date.today()-timedelta(days=7))). \
        group_by(Game.id). \
        order_by(func.count(Game.id).desc())[:TOP_X_MAX]
    top_x_lengths = []
    if top_x_games:
        max_count = top_x_games[0][0]
        for item in top_x_games:
            length = round(item[0] / max_count * 100)
            top_x_lengths.append(length)

    daily_earnings = 0
    monthly_earnings = 0
    daily_refunds = Refund.query.filter_by(date=date.today()).count()
    pending_refunds = Refund.query.filter_by(status='pending').count()

    for order in Order.query.filter_by(date=date.today()):
        daily_earnings += order.total_cost
    for order in Order.query.filter(Order.date > (date.today()-timedelta(days=30))):
        monthly_earnings += order.total_cost

    return render_template('back/admin_center.html',
                           daily_earnings=daily_earnings,
                           monthly_earnings=monthly_earnings,
                           daily_refunds=daily_refunds,
                           pending_refunds=pending_refunds,
                           top_x_games=top_x_games,
                           top_x=len(top_x_games),
                           top_x_lengths=top_x_lengths)


@back.route('/all_orders_admin')
@admin_required
def all_orders_admin():
    query = Order.query
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page,
                                per_page=20,
                                error_out=True)
    orders = pagination.items
    return render_template('back/all_orders_admin.html',
                           orders=orders,
                           pagination=pagination)


@back.route('/edit_order/<int:id>', methods=['POST', 'GET'])
@admin_required
def edit_order(id):
    order = Order.query.get_or_404(id)
    form = EditOrderForm(request.form, order)
    if request.method == 'POST' and form.validate():
        form.populate_obj(order)
        db.session.add(order)
        db.session.commit()
        flash('Order updated!')
        return redirect(url_for('back.all_orders_admin'))
    return render_template('back/edit_order.html',
                           form=form)


@back.route('/edit_order_by_id')
@admin_required
def edit_order_by_id():
    id = request.args.get('order_id')

    try:
        id = int(id)
    except ValueError:
        flash('Please Enter a valid order id!')
        return redirect(url_for('back.admin_center'))
    return redirect(url_for('back.edit_order', id=id))


@back.route('/all_refunds_admin')
@admin_required
def all_refunds_admin():
    query = Refund.query
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page,
                                per_page=20,
                                error_out=True)
    refunds = pagination.items
    return render_template('back/all_refunds_admin.html',
                           refunds=refunds,
                           pagination=pagination)


@back.route('/refund_process/<int:id>', methods=['POST', 'GET'])
@admin_required
def refund_process(id):
    refund = Refund.query.get_or_404(id)
    if refund.status != 'pending':
        abort(404)
    form = RefundProcessForm(request.form)
    if request.method == 'POST' and form.validate():
        form.populate_obj(refund)
        if form.status.data == 'accepted':
            print('*****************')
            print(refund.refund_items)
            for refund_item in refund.refund_items:
                print('*****************')
                print(refund_item)
                refund.user.games.remove(refund_item.order_item.game)
                refund_item.order_item.status = 'refunded'
                db.session.add(refund_item.order_item)
            db.session.add(current_user)
        elif form.status.data == 'rejected':
            for refund_item in refund.refund_items:
                refund_item.order_item.status = 'available'
                db.session.add(refund_item.order_item)
        db.session.add(refund)
        db.session.commit()
        flash('Successfully process the refund!')
        return redirect(url_for('back.all_refunds_admin'))
    return render_template('back/refund_process.html',
                           refund=refund,
                           form=form)


@back.route('/process_refund_by_id')
@admin_required
def process_refund_by_id():
    refund_id = request.args.get('refund_id')
    try:
        refund_id = int(refund_id)
    except ValueError:
        flash('Please Enter a valid refund id!')
        return redirect(url_for('back.admin_center'))
    return redirect(url_for('back.refund_process', id=refund_id))


@back.route('/all_users_admin')
@admin_required
def all_users_admin():
    query = User.query
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page,
                                per_page=20,
                                error_out=True)
    users = pagination.items
    return render_template('back/all_users_admin.html',
                           users=users,
                           pagination=pagination)


@back.route('/user_management/<int:id>')
@admin_required
def user_management(id):
    user = User.query.get_or_404(id)
    return render_template('back/user_management.html',
                           user=user)



@back.route('/edit_user/<int:id>', methods=['POST', 'GET'])
@admin_required
def edit_user(id):

    user = User.query.get_or_404(id)
    form = EditUserForm(request.form, user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        flash('The changes to the user has been successfully saved!')
        return redirect(url_for('back.user_management', id=user.id))
    return render_template('back/edit_user.html',
                           user=user,
                           form=form)


@back.route('/edit_user_by_id')
@admin_required
def edit_user_by_id():
    user_id = request.args.get('user_id')
    try:
        user_id = int(user_id)
    except ValueError:
        flash('Please Enter a valid user id!')
        return redirect(url_for('back.admin_center'))
    return redirect(url_for('back.edit_user', id=user_id))


@back.route('/all_games_admin')
@admin_required
def all_games_admin():
    # query = Game.query.order_by(Game.issued_date.desc())
    query = Game.query
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page,
                                per_page=20,
                                error_out=True)
    games = pagination.items
    return render_template('back/all_games_admin.html',
                           games=games,
                           pagination=pagination)


@back.route('/add_new_game', methods=['POST', 'GET'])
@admin_required
def add_new_game():
    form = AddNewGameForm(request.form)
    if request.method == 'POST' and form.validate():
        game = Game()
        game.title = form.title.data
        game.issued_date = form.issued_date.data
        game.publisher = form.publisher.data
        game.developer = form.developer.data
        game.price = form.price.data
        game.brief_introduction = form.brief_introduction.data
        game.version = form.version.data
        for genre_name in form.genres.data:
            genre = Genre.query.filter_by(name=genre_name).first()
            if genre:
                game.genres.append(genre)
        db.session.add(game)
        db.session.commit()
        flash('New Game added!')
        return redirect(url_for('back.all_games_admin'))
    return render_template('back/add_new_game.html',
                           form=form)


@back.route('/game_management/<int:id>')
@admin_required
def game_management(id):
    game = Game.query.get_or_404(id)

    return render_template('back/game_management.html',
                           game=game)


@back.route('/edit_game/<int:id>', methods=['POST', 'GET'])
@admin_required
def edit_game(id):
    game = Game.query.get_or_404(id)
    form = EditGameForm(request.form, game)
    if request.method == 'POST' and form.validate():
        game.title = form.title.data
        game.issued_date = form.issued_date.data
        game.publisher = form.publisher.data
        game.developer = form.developer.data
        game.price = form.price.data
        game.brief_introduction = form.brief_introduction.data
        game.version = form.version.data
        for genre in game.genres:
            game.genres.remove(genre)

        for genre_name in form.genres.data:
            genre = Genre.query.filter_by(name=genre_name).first()
            if genre:
                game.genres.append(genre)
        db.session.add(game)
        db.session.commit()
        flash('The changes to the game has been successfully saved!')
        return redirect(url_for('back.game_management', id=game.id))
    return render_template('back/edit_game.html',
                           game=game,
                           form=form)


@back.route('/edit_game_by_id')
@admin_required
def edit_game_by_id():
    game_id = request.args.get('game_id')
    try:
        game_id = int(game_id)
    except ValueError:
        flash('Please Enter a valid game id!')
        return redirect(url_for('back.admin_center'))
    return redirect(url_for('back.edit_game', id=game_id))


@back.route('/enable_game/<int:id>')
@admin_required
def enable_game(id):
    game = Game.query.get_or_404(id)
    game.enabled = True
    db.session.add(game)
    db.session.commit()
    flash('The game has been successfully enabled!')
    return redirect(url_for('back.game_management', id=game.id))


@back.route('/disable_game/<int:id>')
@admin_required
def disable_game(id):
    game = Game.query.get_or_404(id)
    game.enabled = False
    db.session.add(game)
    db.session.commit()
    flash('The game has been successfully disabled!')
    return redirect(url_for('back.game_management', id=game.id))


@back.route('/recommend_add/<int:id>')
@admin_required
def recommend_add(id):
    game = Game.query.get_or_404(id)
    game.is_recommended = True
    db.session.add(game)
    db.session.commit()
    flash('{} has been successfully recommended to the home page!'.format(game.title))
    if request.args.get('from_list'):
        return redirect(url_for('back.recommendation_carousel_management'))

    return redirect(url_for('back.game_management', id=game.id))


@back.route('/recommend_remove/<int:id>')
@admin_required
def recommend_remove(id):
    game = Game.query.get_or_404(id)
    game.is_recommended = False
    db.session.add(game)
    db.session.commit()
    flash('{} has been removed from the home page recommendation!'.format(game.title))
    if request.args.get('from_list'):
        return redirect(url_for('back.recommendation_carousel_management'))

    return redirect(url_for('back.game_management', id=game.id))


@back.route('/editor_pick_add/<int:id>')
@admin_required
def editor_pick_add(id):
    game = Game.query.get_or_404(id)
    game.is_editor_picked = True
    db.session.add(game)
    db.session.commit()
    flash('{} has been successfully add to the Editor\'s Pick!'.format(game.title))
    if request.args.get('from_list'):
        return redirect(url_for('back.editor_pick_management'))

    return redirect(url_for('back.game_management', id=game.id))


@back.route('/editor_pick_remove/<int:id>')
@admin_required
def editor_pick_remove(id):
    game = Game.query.get_or_404(id)
    game.is_editor_picked = False
    db.session.add(game)
    db.session.commit()
    flash('{} has been successfully add to the Editor\'s Pick!'.format(game.title))
    if request.args.get('from_list'):
        return redirect(url_for('back.editor_pick_management'))

    return redirect(url_for('back.game_management', id=game.id))


@back.route('/recommendation_carousel_management')
@admin_required
def recommendation_carousel_management():
    games = Game.query.filter_by(is_recommended=True)
    return render_template('back/recommendation_carousel_management.html',
                           games=games)


@back.route('/editor_pick_management')
@admin_required
def editor_pick_management():
    games = Game.query.filter_by(is_editor_picked=True)
    return render_template('back/editor_pick_management.html',
                           games=games)


@back.route('/change_game_cover/<int:id>', methods=['POST', 'GET'])
@admin_required
def change_game_cover(id):
    game = Game.query.get_or_404(id)
    form = UploadFileForm(request.form)
    if request.method == 'POST' and form.validate():
        if 'photo' in request.files:
            file = request.files['photo']
            if not allowed_file(file.filename):
                flash('Photo format is not supported! Please upload a png or png format file.')
            else:
                filename = hashlib.md5(file.read()).hexdigest() + '.' + file.filename.split('.')[-1]
                file.seek(0)
                photo_path = '/static/photos/' + filename
                save_path = os.path.join(current_app.config['PHOTOS_FOLDER'], filename)
                file.save(save_path)
                game.cover_path = photo_path
                db.session.add(game)
                db.session.commit()
                flash('Game Cover changed successfully!')
            return redirect(url_for('back.game_management', id=game.id))
    return render_template('back/change_game_cover.html',
                           form=form)

@back.route('/add_game_image/<int:id>', methods=['POST', 'GET'])
@admin_required
def add_game_image(id):
    game = Game.query.get_or_404(id)
    form = UploadFileForm(request.form)
    if request.method == 'POST' and form.validate():
        if 'photo' in request.files:
            file = request.files['photo']
            if not allowed_file(file.filename):
                flash('Photo format is not supported! Please upload a png or png format file.')
            else:
                filename = hashlib.md5(file.read()).hexdigest() + '.' + file.filename.split('.')[-1]
                file.seek(0)
                photo_path = '/static/photos/' + filename
                save_path = os.path.join(current_app.config['PHOTOS_FOLDER'], filename)
                file.save(save_path)
                game_photo = GamePhoto(game_id=game.id, photo_path=photo_path)
                game.photos.append(game_photo)
                db.session.add(game)
                db.session.commit()
                flash('Game Image added successfully!')
            return redirect(url_for('back.game_management', id=game.id))
    return render_template('back/add_game_image.html',
                           form=form)

@back.route('/remove_game_image/<int:id>')
@admin_required
def remove_game_image(id):
    game_photo = GamePhoto.query.get_or_404(id)
    game_id = game_photo.game_id
    db.session.delete(game_photo)
    db.session.commit()
    flash('You have successfully deleted the photo!')
    return redirect(url_for('back.manage_photos', id=game_id))


@back.route('/manage_photos/<int:id>')
@admin_required
def manage_photos(id):
    game = Game.query.get_or_404(id)

    return render_template('back/manage_photos.html',
                           game=game,
                           photos=game.photos)


##################### Admin Backend END ####################
@back.errorhandler(404)
def page_not_found(e):
    return render_template('back/404.html')

@back.errorhandler(403)
def forbidden(e):
    return render_template('back/403.html')