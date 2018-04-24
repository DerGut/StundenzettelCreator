
.PHONY: test
test:
	python manage.py check
	python manage.py check --deploy
