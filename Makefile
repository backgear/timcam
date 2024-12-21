test:
	pytest

lint:
	ruff check timcam
	python -m checkdeps timcam --allow-names timcam,pyvoronoi
