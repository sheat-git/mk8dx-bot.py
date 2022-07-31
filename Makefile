.PHONY: maps
maps:
	python track/track_map_image.py

.PHONY: test
test:
	python test.py
