# buddha
test task for BuddhaSoft

Local deployment
================================

### Install python version 3.6 (you can do it with pyenv)
    $ pyenv install 3.6.1
    
### Create virtual environment (ypu can do it with mkvirtualenv for example)
    $ mkvirtualenv -p PYTHON_DIR VENV_NAME
    
### Go to project dir
    # cd /home/project_dir

### Install project requirements
    $ pip install -r requirements.txt

### Run migrations
    $ python manage.py migrate

### Run tests
    $ python manage.py test

### Run server
    $ python manage.py runserver

### Swagger used as docs
    $ 127.0.0.1/docs/
