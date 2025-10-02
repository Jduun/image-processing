import os

from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from pydantic import BaseModel

from src.config import config
from src.exceptions import ModuleException
from src.injectors import connections
from src.models import *  # noqa
from src.routers import tasks_routers


def setup_app() -> Flask:
    current_app = Flask(__name__)
    connections.setup_pg()
    return current_app


class PydanticJSONEncoder(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)


app = setup_app()
app.register_blueprint(tasks_routers)
app.json = PydanticJSONEncoder(app)


@app.errorhandler(ModuleException)
def handle_app_exception(e: ModuleException):
    if e.code == 500 or os.getenv("DEBUG", "False") == "True":
        import traceback

        traceback.print_exc()
    return jsonify(e.json()), e.code


if __name__ == "__main__":
    app.run(
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=os.getenv("APP_PORT", 80),
        debug=(os.getenv("DEBUG", "False") == "True"),
    )
