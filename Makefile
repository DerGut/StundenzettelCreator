
.PHONY: test
test:
	python manage.py check
	python manage.py test
	export PRODUCTION=True
	python manage.py test

.PHONY: coverage
coverage:
	python manage.py check
	coverage run --source='.' manage.py test
	export PRODUCTION=True
	coverage run --source='.' manage.py test
