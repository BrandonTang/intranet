# DORIS Intranet Site
Intranet site for the Department of Records and Information Services

## Setup Instructions
After cloning, create a virtual environment and install the requirements:

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

Initialize the database by entering the following in the command line:

    createdb intranet
    python manage.py db upgrade
    python manage.py shell
        >> db.create_all()
        >> Role.insert_roles()
        >> db.session.commit()
        >> exit()

If dropping the database is required, enter the following in the command line and reenter the above:

    dropdb intranet

Locally run the intranet by entering the following in the command line:

    python manage.py runserver