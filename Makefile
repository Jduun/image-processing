build:
	docker build -t image-processing:latest . && docker compose up --build -d && docker compose logs -f

up:
	docker compose up -d

stop:
	docker compose stop
