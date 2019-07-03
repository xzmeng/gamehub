import os
import random
from time import sleep

from sqlalchemy.exc import IntegrityError

from app import create_app
from app import db
from app.models import Game, Genre, User, GameRating, Comment, GamePhoto, OrderItem, Order, Refund, RefundItem

from datetime import date, datetime
from faker import Faker

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return dict(Game=Game,
                Genre=Genre, )


def fake_genres():
    genres = [
        Genre(name='RTS'),
        Genre(name='ACT'),
        Genre(name='RPG'),
        Genre(name='FPS'),
        Genre(name='Rhythm'),
        Genre(name='Survival'),
    ]
    for genre in genres:
        db.session.add(genre)
    db.session.commit()


def insert_100_games():
    GAME_100_IMAGE_BASE = '/static/images/100_games/'

    image_names = os.listdir('app/static/images/100_games/')

    from docx import Document

    word_doc = Document('gamesssss.docx')

    table = word_doc.tables[0]

    print(table)

    for i, row in enumerate(table.rows[1:]):
        game = Game()
        print(i, '=' * 20)
        game.title = row.cells[1].text.strip()
        date_string = row.cells[2].text.strip()
        if '.' in date_string:
            date_string = date_string.replace(' ', '').replace('.', '-')
            date = datetime.strptime(date_string, '%Y-%m-%d').date()
        else:
            date_string = date_string.replace(' ', '')
            date = datetime.strptime(date_string, '%d%b,%Y').date()
        game.issued_date = date

        game.publisher = row.cells[3].text.strip()
        game.developer = row.cells[4].text.strip()
        game.price = row.cells[5].text.strip()
        game.brief_introduction = row.cells[6].text.strip()
        genre_name = row.cells[7].text.strip()
        genre = Genre.query.filter_by(name=genre_name).first()
        game.version = 'v1.0.0'
        game.cover_path = GAME_100_IMAGE_BASE + '{}.0.jpg'.format(i)

        for image_name in image_names:
            if image_name.startswith('{}.'.format(i)):
                image = GamePhoto(photo_path=GAME_100_IMAGE_BASE + image_name)
                game.photos.append(image)

        # recommend the initial 3 games to index page
        if i < 3:
            game.is_recommended = True
        # recommend the games whose index between 3 and 8 to editor's pick
        if 3 <= i < 8:
            game.is_editor_picked = True

        if not genre:
            genre = Genre(name=genre_name)

        game.genres.append(genre)
        db.session.add(game)

        print('title:', game.title)
        print('pub:', game.publisher)
        print('dev:', game.developer)
        print('price:', game.price)
        print('intro:', game.brief_introduction)
        print('genre:', genre)
    db.session.commit()


def fake_games(game_count=500):
    print('Start faking games...')
    sleep(2)

    genres = Genre.query.all()

    fake = Faker()
    publishers = ['Tencent Games', 'Sony Interactive Entertainment',
                  'Apple', 'Xbox Game Studios', 'Activision Blizzard',
                  'Nintendo', 'Electronic Arts', 'Bandai Namco Entertainment',
                  'King', 'Nexon', 'Ubisoft', 'Capcom', 'Sega', 'Koei Tecmo']
    developers = ['0verflow', '11 bit studios', '1C Company', '2K Games',
                  '2K Sports', '38 Studios', 'Activision', 'Amazon Game Studios',
                  'Appy Entertainment', 'Atari, SA', 'Attic Entertainment Software',
                  'Bandai', 'Bizarre Creations', 'Blizzard Entertainment',
                  'Bluehole', 'Capcom', 'Crytek', 'Day 1 Studios', 'Digital Reality',
                  'Electronic Arts', 'Epic Games', 'Frontier Developments',
                  'Gameloft', 'Gravity', 'id Software', 'Konami', 'Xbox Game Studios',
                  'Rockstar Games', 'Tencent Games', 'Ubisoft', 'Zombie Studios']

    # fake games
    for i in range(game_count):
        print('Faking games {}%...'.format(round(i / game_count * 100, 1)))
        game = Game()
        game.title = fake.name()
        game.issued_date = fake.date_between(start_date='-15y', end_date='today')
        game.publisher = random.choice(publishers)
        game.developer = random.choice(developers)
        game.price = random.randint(30, 499)
        game.brief_introduction = fake.text()
        game.version = 'v{}.{}.{}'.format(random.randint(0, 10),
                                          random.randint(0, 10),
                                          random.randint(0, 10))
        game.cover_path = '/static/img/bg-img/r6s.jpg'
        genre1 = random.choice(genres)
        game.genres.append(genre1)
        genre2 = random.choice(genres)
        if genre2 != genre1:
            game.genres.append(genre2)
        db.session.add(game)
    db.session.commit()
    print('Faking games completed.')


def insert_test_users():
    fake = Faker()
    # test_user
    test_user = User()
    test_user.name = 'test_user'
    test_user.email = 'test@test.com'
    test_user.gender = 'M'
    test_user.bill_address = fake.address()
    test_user.personal_introduction = fake.text()
    test_user.phone_no = fake.phone_number()
    test_user.password = 'test'
    test_user.is_admin = False
    test_user.confirmed = True
    db.session.add(test_user)

    # test_user: admin
    test_user = User()
    test_user.name = 'admin'
    test_user.email = 'admin@test.com'
    test_user.gender = 'M'
    test_user.bill_address = fake.address()
    test_user.personal_introduction = fake.text()
    test_user.phone_no = fake.phone_number()
    test_user.password = 'admin'
    test_user.is_admin = True
    test_user.confirmed = True
    db.session.add(test_user)

    db.session.commit()


def fake_users(user_count=1000):
    fake = Faker()
    print('Start faking users...')
    sleep(2)

    # fake users
    genders = ['F', 'M']
    i = 0
    email_set = set()
    while i < user_count:
        print('Faking users {}%...'.format(round(i / user_count * 100, 1)))
        user = User()
        user.name = fake.name()
        email = fake.email()
        if email in email_set:
            continue
        email_set.add(email)
        user.email = email
        user.gender = random.choice(genders)
        user.bill_address = fake.address()
        user.personal_introduction = fake.text()
        user.phone_no = fake.phone_number()
        user.password = '123456'
        user.confirmed = True
        db.session.add(user)
        i += 1
    db.session.commit()
    print('Faking users completed.')


def fake_comments(comment_count_per_game=1):
    print('Start faking game comments...')
    sleep(2)

    fake = Faker()
    users = User.query.all()
    games = Game.query.all()
    for i, game in enumerate(games):
        print('Faking game comments {}%...'.format(round(i / len(games) * 100, 1)))
        for _ in range(comment_count_per_game):
            user = random.choice(users)
            comment = Comment(user=user,
                              game=game,
                              body=fake.text())
            db.session.add(comment)
    db.session.commit()
    print('Faking game comments completed.')


def fake_ratings(rating_count_per_game=1):
    print('Start faking game ratings...')
    sleep(2)
    users = User.query.all()
    games = Game.query.all()
    for i, game in enumerate(games):
        print('Faking game ratings {}%...'.format(round(i / len(games) * 100, 1)))
        rating_total = 0
        rating_count = 0
        user_offset = random.randint(0, len(users) - rating_count_per_game)
        tmp_users = users[user_offset: user_offset + rating_count_per_game]
        for user in tmp_users:
            rating = random.randint(0, 10)
            game_rating = GameRating(user=user,
                                     game=game,
                                     rating=rating)
            rating_total += rating
            rating_count += 1
            db.session.add(game_rating)
        game.rating_total = rating_total
        game.rating_count = rating_count
        db.session.add(game)
    db.session.commit()
    print('Faking game ratings completed!')


def fake_orders(bought_count_per_game=1):
    print('Start faking Orders...')
    sleep(2)
    users = User.query.all()
    games = Game.query.all()
    for i, game in enumerate(games):
        print('Faking Orders {}%...'.format(round(i / len(games) * 100, 1)))
        user_offset = random.randint(0, len(users) - bought_count_per_game)
        tmp_users = users[user_offset: user_offset + bought_count_per_game]
        for user in tmp_users:
            order = Order(user=user)
            order_item = OrderItem(game=game)
            order.order_items.append(order_item)
            order.bill_address = user.bill_address
            order.date = date.today()
            order.total_cost = game.price
            db.session.add(order)
            user.games.append(game)
            db.session.add(user)
    db.session.commit()
    print('Faking Orders completed!')


def fake_refunds(refund_percentage=0.1):
    print('Start faking Refunds...')

    orders = Order.query.all()
    refund_count = round(len(orders) * refund_percentage)
    for i in range(refund_count):
        print('Faking Refunds {}%...'.format(round(i / refund_count) * 100, 1))

        order = orders[i]
        refund = Refund(order_id=order.id, user_id=order.user_id)
        refund_item = RefundItem(order_item=order.order_items[0])
        refund.refund_items.append(refund_item)
        refund.date = date.today()
        x = random.random()
        if x < 0.1:
            refund.status = 'pending'
            order.order_items[0].status = 'refunding'
        elif x < 0.9:
            refund.status = 'accepted'
            refund.msg = 'okkkkkk'
            order.user.games.remove(order.order_items[0].game)
            db.session.add(order.user)
            order.order_items[0].status = 'refunded'
        else:
            refund.status = 'rejected'
            refund.msg = 'nooooooooo'
            order.order_items[0].status = 'available'
        db.session.add(refund)
    db.session.commit()
    print('Faking Refund completed!')


def fake_test():
    insert_100_games()
    insert_test_users()


def fake_all():
    pass


@app.cli.command()
def init_db():
    game_count = 1000
    user_count = 5000
    comment_per_game = 5
    rating_count_per_game = 1
    bought_count_per_game = 1
    refund_percentage = 0.1

    db.drop_all()
    db.create_all()

    insert_100_games()
    insert_test_users()
    fake_games(game_count)
    fake_users(user_count)
    fake_comments(comment_per_game)
    fake_ratings(rating_count_per_game)
    fake_orders(bought_count_per_game)
    fake_refunds(refund_percentage)