test:
	pytest --cov=timcam

lint:
	ruff check timcam
	python -m checkdeps timcam --allow-names timcam,pyvoronoi

format:
	ruff format timcam tests

