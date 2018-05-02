
.PHONY: test
test:
	python manage.py check
	python manage.py test

.PHONY: coverage
coverage:
	python manage.py check
	coverage run --source='.' manage.py test
