import flask
from flask import jsonify, request

from src.injectors import services
from src.models import TaskCreateDTO

tasks_routers = flask.Blueprint(
    "tasks",
    __name__,
    url_prefix="/api/tasks/",
)


@tasks_routers.route("/", methods=["POST"])
def create_task():
    ts = services.task_service()
    json_data = request.get_json()
    task_data = TaskCreateDTO(**json_data)
    res = ts.create(task_data)
    return jsonify(res)


@tasks_routers.route("/<int:task_id>", methods=["GET"])
def get_task(task_id):
    ts = services.task_service()
    res = ts.get(task_id)
    return jsonify(res)
