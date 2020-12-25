from datetime import date, datetime

from app.models import Game, Genre


def func1():
    from docx import Document

    word_doc = Document('game_list.docx')

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
        if not genre:
            genre = Genre(name=genre_name)
            db.session.add(genre)
        game.genres.append(genre)
        print('title:', game.title)
        print('pub:', game.publisher)
        print('dev:', game.developer)
        print('price:', game.price)
        print('intro:', game.brief_introduction)
        print('genre:', genre)

def func2():
    t = '8 Jul, 2016'
    d = datetime.strptime(t, '%d %b, %Y')
    print(d)

if __name__ == '__main__':
    func1()