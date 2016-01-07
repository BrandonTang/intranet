# DORIS Intranet Site
Intranet site for the Department of Records and Information Services

## Setup Instructions
After cloning, enter the following in the command line:

    createdb intranet
    python manage.py db upgrade
    python manage.py shell
        >> db.create_all()
        >> Role.insert_roles()
        >> db.session.commit()
        >> exit()
    python manage.py runserver

If dropping the database is required, enter the following in the command line and reenter the above:

    dropdb intranet