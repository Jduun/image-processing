# Image Processing

## Установка

### [docker-compose.yml](./docker-compose.example.yml)
```yaml
services:
  file-storage:
    image: file-storage:latest
    restart: unless-stopped
    volumes:
      - ~/root_folder:/root_folder
    ports:
      - "127.0.0.1:5000:80"
    env_file:
      - ~/file-storage/.env

  file-storage-db:
    image: postgres:13
    restart: unless-stopped
    environment:
      POSTGRES_USER: "postgres"
      POSTGRES_PASSWORD: "postgres"
      POSTGRES_DB: "postgres"
    volumes:
      - ~/postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"

  image-processing:
    image: image-processing:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:5001:80"

  image-processing-worker:
    image: image-processing:latest
    restart: "unless-stopped"
    deploy:
      replicas: 3
    volumes:
      - ~/images:/images
    command: ["python3", "-u", "/app/src/scripts/tasks_worker.py"]

  image-processing-db:
    image: postgres:13
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres_image_processing
    volumes:
      - ~/image_processing_db/postgres:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5600:5432"

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "127.0.0.1:5672:5672"
      - "127.0.0.1:15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: user
      RABBITMQ_DEFAULT_PASS: password
```

### Пояснение к архитектуре
`file-storage` - сервис, предоставляющий API для работы с файлами

`file-storage-db` - база данных PostgreSQL 

`image-processing` - сервис, предоставляющий API для создания задач по обработке изображений и получения информации об этих задачах

`image-processing-db` - база данных PostgreSQL для хранения информации о задачах

`image-processing-worker` - обработчик задач из очереди 

`rabbitmq` - очередь для хранения задач, позволяющая сделать обработку изображений асинхронной 

### [config.yaml](./src/config/config.example.yaml)
```yaml
image_processing:
  host: "0.0.0.0"
  port: 80
  folder: "/images"
  debug: false

file_storage:
  host: "file-storage"
  port: 80

postgres:
  user: "postgres"
  password: "postgres"
  host: "image-processing-db"
  db: "postgres"

rabbit:
  host: "rabbitmq"
  port: 5672
  user: "user"
  password: "password"
  routing_key: "image-processing"
  queue_name: "image-processing"
```
---

## API
### Создание задачи
#### Пример запроса на изменение разрешения
**Запрос**: `POST /api/tasks/` `application/json`
```json
{
    "input_image_id": 34,
    "operation_type": "resizing",
    "parameters": {
        "width": 6000,
        "height": 7000,
        "resample_alg": "cubic"
    }
}
```
Значения по умолчанию:
- `width` - ширина исходного растра
- `height` - высота исходного растра
- `resample_alg` - "bilinear"

**Ответ**: `application/json` `200 OK`
```json
{
    "created_at": "Thu, 02 Oct 2025 08:13:11 GMT",
    "duration_ms": 0,
    "id": 138,
    "input_image_id": 34,
    "operation_type": "resize",
    "output_image_id": null,
    "parameters": {
        "width": 6000,
        "height": 7000,
        "resample_alg": "cubic"
    },
    "status": "queued",
    "updated_at": "Thu, 02 Oct 2025 08:13:11 GMT"
}
```
**Ошибки**:
- `500` - не удалось добавить задачу в очередь

#### Пример запроса на перепроецирование
**Запрос**: `POST /api/tasks/` `application/json`
```json
{
    "input_image_id": 34,
    "operation_type": "resizing",
    "parameters": {
        "dst_srs": "EPSG:3857"
    }
}
```
Значения по умолчанию:
- `dst_srs` - "EPSG:4326"

**Ответ**: `application/json` `200 OK`
```json
{
    "created_at": "Thu, 02 Oct 2025 08:14:00 GMT",
    "duration_ms": 0,
    "id": 139,
    "input_image_id": 34,
    "operation_type": "reprojection",
    "output_image_id": null,
    "parameters": {
        "dst_srs": "EPSG:3857"
    },
    "status": "queued",
    "updated_at": "Thu, 02 Oct 2025 08:14:00 GMT"
}
```

**Ошибки**:
- `500` - не удалось добавить задачу в очередь

### Получение информации о задаче
**Запрос**: `GET /api/tasks/139` `application/json`

**Ответ**: `application/json` `200 OK`
```json
{
    "created_at": "Thu, 02 Oct 2025 08:14:00 GMT",
    "duration_ms": 555,
    "id": 139,
    "input_image_id": 34,
    "operation_type": "reprojection",
    "output_image_id": 98,
    "parameters": {
        "dst_srs": "EPSG:3857"
    },
    "status": "done",
    "updated_at": "Thu, 02 Oct 2025 08:14:01 GMT"
}
```

**Ошибки**:
- `404` - информация о задаче не найдена