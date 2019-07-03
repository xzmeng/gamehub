Gamehub
=======

Gamehub is an online game shop written in python with flask framework.

1.Install dependencies
----------------------
    pip install -r requirements.txt

2.Configuration
---------------
Environment variables:

    FLASK_APP=gamehub.py
    MAIL_SERVER=smtp.tom.com
    MAIL_PORT=25
    MAIL_USE_TLS=false
    MAIL_USERNAME=gamehub@tom.com
    MAIL_PASSWORD=gamehub
    MAIL_SENDER="GameHub Admin <gamehub@tom.com>"
    DEV_DATABASE_URL=mysql+pymysql://root@localhost/gamehub
If you don't want to set the environment variables manually,
you can save the above environment variables to a .env file in the project root.

Caution: In no circumstances should you push the .env file to a public environment !
    
Make sure the database "gamehub" exists, or execute the following command in
mysql shell:
    
    mysql> create database gamehub;

3.Initialize database
-------------------
    flask init-db

4.Run test server
-----------------
    flask run
    
![screenshot1](https://github.com/xzmeng/gamehub/blob/master/screenshot/screenshot1.png)
![screenshot2](https://github.com/xzmeng/gamehub/blob/master/screenshot/screenshot2.png)
![screenshot3](https://github.com/xzmeng/gamehub/blob/master/screenshot/screenshot3.png)
![screenshot4](https://github.com/xzmeng/gamehub/blob/master/screenshot/screenshot4.png)

