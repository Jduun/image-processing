from src.injectors import services, connections


def run_worker():
    worker = services.tasks_worker()
    worker.run()


if __name__ == "__main__":
    connections.setup_pg()
    run_worker()
