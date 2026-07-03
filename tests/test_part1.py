import datetime
import unittest


# --------------------------
# Core Task Model
# --------------------------
class Task:
    def __init__(self, task_id: int, title: str, description: str, due_date: datetime.date, status: str = "pending"):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.due_date = due_date
        self.status = status

    def mark_complete(self):
        self.status = "completed"

    def __str__(self):
        return (f"Task {self.task_id} | Title: {self.title} | Status: {self.status} | "
                f"Due: {self.due_date.strftime('%Y-%m-%d')} | Description: {self.description}")


# --------------------------
# Task Manager (CRUD + Filters)
# --------------------------
class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def create_task(self, title: str, description: str, due_date: datetime.date) -> Task:
        new_task = Task(self.next_id, title, description, due_date)
        self.tasks.append(new_task)
        self.next_id += 1
        return new_task

    def get_task_by_id(self, task_id: int) -> Task | None:
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def update_task(self, task_id: int, new_title: str = None, new_description: str = None):
        task = self.get_task_by_id(task_id)
        if task:
            if new_title:
                task.title = new_title
            if new_description:
                task.description = new_description
        return task

    def delete_task(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

    def filter_tasks_by_status(self, status: str) -> list[Task]:
        return [task for task in self.tasks if task.status == status]


# --------------------------
# Unit Tests (Successful)
# --------------------------
class TestTaskManagement(unittest.TestCase):
    def setUp(self):
        self.manager = TaskManager()
        self.due_date = datetime.date(2024, 12, 31)
        self.task = self.manager.create_task("Test Task", "Test Description", self.due_date)

    def test_create_task(self):
        self.assertEqual(len(self.manager.tasks), 1)
        self.assertEqual(self.task.title, "Test Task")

    def test_mark_complete(self):
        self.task.mark_complete()
        self.assertEqual(self.task.status, "completed")

    def test_delete_task(self):
        result = self.manager.delete_task(1)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.tasks), 0)

    def test_filter_tasks(self):
        self.task.mark_complete()
        completed_tasks = self.manager.filter_tasks_by_status("completed")
        self.assertEqual(len(completed_tasks), 1)


# --------------------------
# Main Function (Demo Scenario)
# --------------------------
def main():
    print("=== TASK MANAGEMENT SYSTEM - MIDTERM DEMO ===\n")

    # 1. Initialize manager
    manager = TaskManager()

    # 2. Create 2 tasks
    due_date_1 = datetime.date(2024, 11, 15)
    task1 = manager.create_task("Midterm Project", "Finish code + tests", due_date_1)
    due_date_2 = datetime.date(2024, 11, 20)
    task2 = manager.create_task("Grocery Shopping", "Buy milk, eggs, bread", due_date_2)
    print("Step 1: Created 2 tasks:")
    print(task1)
    print(task2, "\n")

    # 3. Update task 1's title
    updated_task1 = manager.update_task(1, new_title="Task Management Midterm")
    print("Step 2: Updated Task 1's title:")
    print(updated_task1, "\n")

    # 4. Mark task 2 as complete
    task2.mark_complete()
    print("Step 3: Marked Task 2 as completed:")
    print(task2, "\n")

    # 5. Filter pending tasks (only Task 1 should show)
    pending_tasks = manager.filter_tasks_by_status("pending")
    print("Step 4: Filtered pending tasks (only Task 1):")
    for task in pending_tasks:
        print(task)
    print("")

    # 6. Delete task 2
    delete_success = manager.delete_task(2)
    print(f"Step 5: Deleted Task 2 (success: {delete_success})")
    print("Remaining tasks after deletion:")
    for task in manager.tasks:
        print(task)


if __name__ == "__main__":
    # Run main demo
    main()

    # Uncomment below to run unit tests
    #unittest.main()
