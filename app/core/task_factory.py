from .tasks import Task,TaskA,TaskB,TaskC
class TaskFactory:
    @staticmethod
    def create_task(task_name: str) -> Task:
        tasks = {
            "task_a": TaskA(),
            "task_b": TaskB(),
            "task_c": TaskC(),
        }

        if task_name not in tasks:
            raise ValueError(f"Task '{task_name}' is not registered")

        return tasks[task_name]