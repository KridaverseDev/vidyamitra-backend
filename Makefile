# Variables
MODE ?= local
APP ?= silicon

# echo color
GREEN = \033[0;32m
BLUE = \033[0;34m
YELLOW = \033[0;33m
NC = \033[0m

run:
	APP_MODE=$(MODE) pants run silicon/_microservices/admin/manage.py -- runserver

fmt:
	PANTS_CONCURRENT=True pants fmt ::

mm:
	PANTS_CONCURRENT=True APP_MODE=$(MODE) pants run silicon/_microservices/admin/manage.py -- makemigrations


migrate:
	PANTS_CONCURRENT=True APP_MODE=$(MODE) pants run silicon/_microservices/admin/manage.py -- migrate

su:
	PANTS_CONCURRENT=True APP_MODE=$(MODE) pants run silicon/_microservices/admin/manage.py -- createsuperuser
csu:
	PANTS_CONCURRENT=True APP_MODE=$(MODE) pants run silicon/_microservices/admin/manage.py -- create_super_users

setup_knowledge:
	PANTS_CONCURRENT=True APP_MODE=$(MODE) pants run silicon/_microservices/admin/manage.py -- setup_knowledge

collectstatic:
	PANTS_CONCURRENT=True APP_MODE=$(MODE) pants run silicon/_microservices/admin/manage.py -- collectstatic


clear_db:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc"  -delete