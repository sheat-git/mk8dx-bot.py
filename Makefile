.PHONY: maps
maps:
	python track/track_map_image.py

.PHONY: test
test:
	python test.py

.PHONY: requirements
requirements:
	pipenv requirements --exclude-markers | tail -n +2 > requirements.txt
