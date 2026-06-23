.PHONY: install run train export docker-build docker-run clean validate-external train-medical

install:
	pip install -r requirements.txt
	pip install opencv-python tensorflowjs

run:
	python app.py

train:
	python main.py

export:
	python export_model.py

docker-build:
	docker build -t chest-ct-ai:latest .

docker-run:
	docker run -p 8080:8080 chest-ct-ai:latest

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf Artifacts/Model_Training/SavedModel/*
	rm -rf Artifacts/Model_Training/TFJS_Model/*

validate-external:
	python external_validation.py

train-medical:
	python train_medical_pretrained.py
