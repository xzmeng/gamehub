from datetime import date

from flask import render_template, request, abort, redirect, url_for, flash, current_app
from flask_login import current_user, login_required
from sqlalchemy import cast, Float

from ..models import Game, Genre, Comment, GameRating, Cart, Order, OrderItem, WishList
# from .cart import Cart, WishList
from .forms import CommentForm

from . import main
from .. import db


@main.route('/')
def index():
    available_games = Game.query.filter_by(enabled=True)
    carousel_games = available_games.filter_by(is_recommended=True)
    editor_pick_games = available_games.filter_by(is_editor_picked=True)
    popular_games = available_games.order_by(
        (cast(Game.rating_total, Float) / cast(Game.rating_count, Float)).desc()
    )[:5]
    latest_games = available_games.order_by(Game.issued_date.desc())[:5]
    return render_template('index.html',
                           carousel_games=carousel_games,
                           popular_games=popular_games,
                           latest_games=latest_games,
                           editor_pick_games=editor_pick_games)


@main.route('/game_list')
def game_list():
    available_games = Game.query.filter_by(enabled=True)
    query = available_games
    genre_name = request.args.get('genre_name')
    genre = None
    if genre_name:
        genre = Genre.query.filter_by(name=genre_name).first()
        if not genre:
            abort(404)
        query = genre.games.filter_by(enabled=True)
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page, per_page=10,
        error_out=False
    )
    games = pagination.items
    genres = Genre.query.all()
    return render_template('game_list.html',
                           games=games,
                           pagination=pagination,
                           genre=genre,
                           genres=genres,
                           genre_name=genre_name)


@main.route('/game_detail/<int:id>', methods=['POST', 'GET'])
def game_detail(id):
    form = CommentForm(request.form)
    if request.method == 'POST' and form.validate():
        if not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()

        comment = Comment(game_id=id,
                          user_id=current_user.id,
                          body=form.body.data)
        db.session.add(comment)
        db.session.commit()
        flash('You commented successfully!')
    game = Game.query.get_or_404(id)
    if not game.enabled:
        abort(404)
    print('*' * 30)
    print(game.rating_count, game.rating_total)
    comment_query = game.comments
    page = request.args.get('page', 1, type=int)
    pagination = comment_query.paginate(
        page, per_page=10,
        error_out=False
    )
    comments = pagination.items
    return render_template('game_detail.html',
                           game=game,
                           photos=game.photos,
                           comments=comments,
                           pagination=pagination,
                           form=form)


@main.route('/rating/<int:id>')
@login_required
def rating(id):
    game = Game.query.get_or_404(id)
    if not game.enabled:
        abort(404)
    star_num = request.args.get('rating', type=int)
    if star_num not in [1, 2, 3, 4, 5]:
        flash('You must choose one of the 5 ranks!')
        return redirect(url_for('main.game_detail', id=id))

    game_rating = current_user.game_ratings.filter_by(game_id=id).first()
    if game_rating:
        flash('You have already rated the game!')
    else:
        game_rating = GameRating(user_id=current_user.id,
                                 game_id=id,
                                 rating=star_num * 2)
        game.rating_count += 1
        game.rating_total += star_num * 2
        db.session.add(game_rating)
        db.session.add(game)
        db.session.commit()
        flash('You have rated successfully!')
    return redirect(url_for('main.game_detail', id=id))



@main.route('/search')
def search():
    keyword = request.args.get('keyword')
    if not keyword:
        pass
    query = Game.query.filter(Game.title.contains(keyword)).filter_by(enabled=True)
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(
        page, per_page=10,
        error_out=False
    )
    games = pagination.items
    return render_template('search.html',
                           games=games,
                           pagination=pagination,
                           keyword=keyword)


@main.route('/cart_detail')
@login_required
def cart_detail():
    cart = current_user.cart
    if not cart:
        cart = Cart()
        cart.user = current_user
        db.session.add(cart)
        db.session.commit()
    total_num = cart.games.count()
    total_price = sum(game.price for game in cart.games)

    return render_template('cart_detail.html',
                           games=cart.games,
                           total_num=total_num,
                           total_price=total_price)


@main.route('/cart_add/<int:id>')
@login_required
def cart_add(id):
    game = Game.query.get_or_404(id)
    if not game.enabled:
        abort(404)
    cart = current_user.cart
    if not cart:
        cart = Cart()
        cart.user = current_user
    if game in current_user.games:
        flash('You have already owned the game!')
    elif game in cart.games:
        flash('The game has already been added to your cart!')
    else:
        cart.games.append(game)
        flash('Successfully added game to your cart !')
    db.session.add(cart)
    db.session.commit()
    return redirect(url_for('main.cart_detail'))


@main.route('/cart_remove/<int:id>')
@login_required
def cart_remove(id):
    game = Game.query.get_or_404(id)
    cart = current_user.cart
    if not cart:
        abort(404)
    cart.games.remove(game)
    db.session.add(cart)
    db.session.commit()
    flash('Successfully remove the game from your cart!')
    return redirect(url_for('main.cart_detail'))


@main.route('/cart_checkout')
@login_required
def cart_checkout():
    cart = current_user.cart
    if not cart:
        abort(404)

    order = Order(user_id=current_user.id,
                  total_cost=0)
    for game in cart.games:
        if not game.enabled:
            cart.games.remove(game)
            continue
        current_user.games.append(game)
        order_item = OrderItem(game_id=game.id,
                               status='available')
        order.order_items.append(order_item)
        order.date = date.today()
        order.bill_address = current_user.bill_address
        order.total_cost += game.price
        cart.games.remove(game)
    db.session.add(current_user)
    db.session.add(order)
    db.session.commit()

    flash('You\' payed the money successfully!')
    return redirect(url_for('main.after_cart_checkout'))


@main.route('/wishlist_detail')
@login_required
def wishlist_detail():
    wishlist = current_user.wishlist
    if not wishlist:
        wishlist = WishList()
        wishlist.user = current_user
        db.session.add(wishlist)
        db.session.commit()
    total_num = wishlist.games.count()
    total_price = sum(game.price for game in wishlist.games)

    return render_template('wishlist_detail.html',
                           games=wishlist.games,
                           total_num=total_num,
                           total_price=total_price)


@main.route('/wishlist_add/<int:id>')
@login_required
def wishlist_add(id):
    game = Game.query.get_or_404(id)
    if not game.enabled:
        abort(404)

    wishlist = current_user.wishlist
    if not wishlist:
        wishlist = WishList()
        wishlist.user = current_user
    if game in current_user.games:
        flash('You have already owned the game!')
    elif game in wishlist.games:
        flash('The game has already been added to your wishlist!')
    else:
        wishlist.games.append(game)
        flash('Successfully added game to your wishlist !')
    db.session.add(wishlist)
    db.session.commit()
    return redirect(url_for('main.wishlist_detail'))


@main.route('/wishlist_remove/<int:id>')
@login_required
def wishlist_remove(id):
    game = Game.query.get_or_404(id)
    wishlist = current_user.wishlist
    if not wishlist:
        abort(404)
    wishlist.games.remove(game)
    db.session.add(wishlist)
    db.session.commit()
    flash('Successfully remove the game from your wishlist!')
    return redirect(url_for('main.wishlist_detail'))


@main.route('/wishlist_checkout')
@login_required
def wishlist_checkout():
    cart = current_user.cart
    if not cart:
        cart = Cart()
        cart.user = current_user

    wishlist = current_user.wishlist
    if not wishlist:
        abort(404)

    for game in wishlist.games:
        if not game.enabled:
            wishlist.games.remove(game)
            continue
        if game not in cart.games:
            cart.games.append(game)
        wishlist.games.remove(game)
    db.session.add(current_user)
    db.session.commit()

    flash('You\'ve add the games in wishlist to cart successfully!')
    return redirect(url_for('main.cart_detail'))


@main.route('/after_checkout')
@login_required
def after_cart_checkout():
    return render_template('after_cart_checkout.html')


@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@main.errorhandler(403)
def forbidden(e):
    return render_template('403.html')