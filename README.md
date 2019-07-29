# gtt-backend

## Project setup
```
pipenv install
pipenv shell
```

### Django setup
```
cd gtt/
python manage.py migrate
```

### Run django server
```
python manage.py runserver localhost:8000
```

### Set up admin
```
python manage.py createsuperuser
```
Go to [http://localhost:8000/admin](http://localhost:8000/admin).

### Run tests
```
python manage.py test
```
or if you want to run more specific tests
```
python manage.py test --tag=posts
python manage.py test --tag=comments
python manage.py test --tag=replies
python manage.py test --tag=ratings
python manage.py test --tag=bookmarks
```


