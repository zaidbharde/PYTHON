import threading
import time
import json
import os

class Task:
    def __init__(self, title, description):
        self.title = title
        self.description = description
        self.completed = False

    def mark_completed(self):
        self.completed = True

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'completed': self.completed
        }

    @staticmethod
    def from_dict(data):
        task = Task(data['title'], data['description'])
        task.completed = data['completed']
        return task

class TaskManager:
    def __init__(self, filename='tasks.json'):
        self.tasks = []
        self.filename = filename
        self.lock = threading.Lock()
        self.load_tasks()

    def add_task(self, task):
        with self.lock:
            self.tasks.append(task)
            self.save_tasks()

    def complete_task(self, title):
        with self.lock:
            for task in self.tasks:
                if task.title == title:
                    task.mark_completed()
                    self.save_tasks()
                    return True
            return False

    def list_tasks(self):
        with self.lock:
            return [task.to_dict() for task in self.tasks]

    def save_tasks(self):
        with open(self.filename, 'w') as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4)

    def load_tasks(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                try:
                    data = json.load(f)
                    self.tasks = [Task.from_dict(item) for item in data]
                except json.JSONDecodeError:
                    self.tasks = []

def background_task(manager, interval=10):
    while True:
        time.sleep(interval)
        tasks = manager.list_tasks()
        print(f"\n[Background] You have {len(tasks)} tasks:")
        for task in tasks:
            status = 'Done' if task['completed'] else 'Pending'
            print(f" - {task['title']} [{status}]")
        print()

def main():
    manager = TaskManager()
    threading.Thread(target=background_task, args=(manager,), daemon=True).start()

    while True:
        print("\nTask Manager")
        print("1. Add Task")
        print("2. Complete Task")
        print("3. List Tasks")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            title = input("Task Title: ")
            description = input("Task Description: ")
            task = Task(title, description)
            manager.add_task(task)
            print("Task added.")
        elif choice == '2':
            title = input("Enter the title of the task to complete: ")
            if manager.complete_task(title):
                print("Task marked as completed.")
            else:
                print("Task not found.")
        elif choice == '3':
            tasks = manager.list_tasks()
            if not tasks:
                print("No tasks found.")
            else:
                for task in tasks:
                    status = 'Done' if task['completed'] else 'Pending'
                    print(f"{task['title']}: {task['description']} [{status}]")
        elif choice == '4':
            print("Exiting Task Manager.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
