from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider

from src.config import config
from src.base.module.exceptions import ModuleException
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

        if isinstance(obj, datetime):
            return obj.isoformat().replace("+00:00", "")

        return super().default(obj)


app = setup_app()
app.register_blueprint(tasks_routers)
app.json = PydanticJSONEncoder(app)


@app.errorhandler(ModuleException)
def handle_app_exception(e: ModuleException):
    if e.code == 500 or config.image_processing.debug:
        import traceback

        traceback.print_exc()

    return jsonify(e.json()), e.code


if __name__ == "__main__":
    app.run(
        host=config.image_processing.host,
        port=config.image_processing.port,
        debug=config.image_processing.debug,
    )
