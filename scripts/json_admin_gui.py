from __future__ import annotations

import json
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
BACKUPS_DIR = PROJECT_ROOT / "backups"

STUDENT_FILE = DATA_DIR / "students.json"
TASK_FILE = DATA_DIR / "tasks.json"
PROBLEM_FILE = DATA_DIR / "problems.json"
RECORD_FILE = DATA_DIR / "record.json"

TASK_TYPES = [
    "codeforces_div1",
    "codeforces_div2",
    "codeforces_div3",
    "codeforces_div4",
    "atcoder_abc",
    "atcoder_arc",
    "atcoder_agc",
    "private",
    "luogu",
    "vjudge",
    "gesp_6",
    "gesp_7",
    "gesp_8",
]

VALID_STATUSES = ["solved", "attempted", "unsolved"]


def read_json_array(path: Path) -> list[dict]:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]\n", encoding="utf-8")
        return []

    raw_text = path.read_text(encoding="utf-8")
    payload = json.loads(raw_text)
    if not isinstance(payload, list):
        raise ValueError(f"{path.name} must be a JSON array.")
    return payload


def create_backup_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]


def backup_json_file_if_needed(path: Path, current_text: str, next_text: str) -> None:
    if current_text == next_text:
        return

    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUPS_DIR / f"{create_backup_stamp()}-{path.name}"
    backup_path.write_text(current_text, encoding="utf-8")


def write_json_array(path: Path, payload: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    next_text = f"{json.dumps(payload, ensure_ascii=False, indent=2)}\n"

    if path.exists():
        current_text = path.read_text(encoding="utf-8")
        backup_json_file_if_needed(path, current_text, next_text)
        if current_text == next_text:
            return

    path.write_text(next_text, encoding="utf-8")


def parse_display_id(value: str) -> str:
    return value.split(" | ", 1)[0].strip() if " | " in value else value.strip()


class JsonRepository:
    def __init__(self) -> None:
        self.students: list[dict] = []
        self.tasks: list[dict] = []
        self.problems: list[dict] = []
        self.records: list[dict] = []
        self.reload()

    def reload(self) -> None:
        self.students = read_json_array(STUDENT_FILE)
        self.tasks = read_json_array(TASK_FILE)
        self.problems = read_json_array(PROBLEM_FILE)
        self.records = read_json_array(RECORD_FILE)
        self.sort_all()

    def save_all(self) -> None:
        self.sort_all()
        write_json_array(STUDENT_FILE, self.students)
        write_json_array(TASK_FILE, self.tasks)
        write_json_array(PROBLEM_FILE, self.problems)
        write_json_array(RECORD_FILE, self.records)

    def sort_all(self) -> None:
        self.students.sort(key=lambda item: item["id"])
        self.tasks.sort(key=lambda item: item["id"])
        self.problems.sort(key=lambda item: item["id"])
        self.records.sort(key=lambda item: (item["studentId"], item["problemId"]))

    def generate_id(self, prefix: str, items: list[dict]) -> str:
        max_number = 0
        for item in items:
            raw_id = str(item.get("id", ""))
            if raw_id.startswith(prefix):
                suffix = raw_id[len(prefix):]
                if suffix.isdigit():
                    max_number = max(max_number, int(suffix))
        return f"{prefix}{max_number + 1:03d}"

    def student_by_id(self) -> dict[str, dict]:
        return {student["id"]: student for student in self.students}

    def task_by_id(self) -> dict[str, dict]:
        return {task["id"]: task for task in self.tasks}

    def problem_by_id(self) -> dict[str, dict]:
        return {problem["id"]: problem for problem in self.problems}

    def add_student(self, name: str, student_id: str = "") -> dict:
        clean_name = name.strip()
        clean_student_id = student_id.strip()
        if not clean_name:
            raise ValueError("Student name cannot be empty.")
        if clean_student_id:
            if clean_student_id in self.student_by_id():
                raise ValueError("Student ID already exists.")
        else:
            clean_student_id = self.generate_id("s", self.students)
        student = {"id": clean_student_id, "name": clean_name}
        self.students.append(student)
        self.save_all()
        return student

    def update_student(self, student_id: str, new_student_id: str, name: str) -> None:
        clean_name = name.strip()
        clean_student_id = new_student_id.strip()
        if not clean_name:
            raise ValueError("Student name cannot be empty.")
        if not clean_student_id:
            raise ValueError("Student ID cannot be empty.")
        if clean_student_id != student_id and clean_student_id in self.student_by_id():
            raise ValueError("New student ID already exists.")
        for student in self.students:
            if student["id"] == student_id:
                student["id"] = clean_student_id
                student["name"] = clean_name
                for record in self.records:
                    if record["studentId"] == student_id:
                        record["studentId"] = clean_student_id
                self.save_all()
                return
        raise ValueError("Student not found.")

    def delete_student(self, student_id: str) -> None:
        before_count = len(self.students)
        self.students = [student for student in self.students if student["id"] != student_id]
        if len(self.students) == before_count:
            raise ValueError("Student not found.")
        self.records = [record for record in self.records if record["studentId"] != student_id]
        self.save_all()

    def add_task(self, title: str, task_type: str) -> dict:
        clean_title = title.strip()
        clean_type = task_type.strip().lower()
        if not clean_title:
            raise ValueError("Task title cannot be empty.")
        if not clean_type:
            raise ValueError("Task type cannot be empty.")
        task = {"id": self.generate_id("t", self.tasks), "title": clean_title, "type": clean_type}
        self.tasks.append(task)
        self.save_all()
        return task

    def update_task(self, task_id: str, title: str, task_type: str) -> None:
        clean_title = title.strip()
        clean_type = task_type.strip().lower()
        if not clean_title:
            raise ValueError("Task title cannot be empty.")
        if not clean_type:
            raise ValueError("Task type cannot be empty.")
        for task in self.tasks:
            if task["id"] == task_id:
                task["title"] = clean_title
                task["type"] = clean_type
                self.save_all()
                return
        raise ValueError("Task not found.")

    def delete_task(self, task_id: str) -> None:
        problem_ids = {problem["id"] for problem in self.problems if problem["taskId"] == task_id}
        before_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        if len(self.tasks) == before_count:
            raise ValueError("Task not found.")
        self.problems = [problem for problem in self.problems if problem["taskId"] != task_id]
        self.records = [record for record in self.records if record["problemId"] not in problem_ids]
        self.save_all()
    def add_problem(self, task_id: str, title: str) -> dict:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Problem title cannot be empty.")
        if task_id not in self.task_by_id():
            raise ValueError("Selected task does not exist.")
        problem = {"id": self.generate_id("p", self.problems), "taskId": task_id, "title": clean_title}
        self.problems.append(problem)
        self.save_all()
        return problem

    def update_problem(self, problem_id: str, task_id: str, title: str) -> None:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Problem title cannot be empty.")
        if task_id not in self.task_by_id():
            raise ValueError("Selected task does not exist.")
        for problem in self.problems:
            if problem["id"] == problem_id:
                problem["taskId"] = task_id
                problem["title"] = clean_title
                self.save_all()
                return
        raise ValueError("Problem not found.")

    def delete_problem(self, problem_id: str) -> None:
        before_count = len(self.problems)
        self.problems = [problem for problem in self.problems if problem["id"] != problem_id]
        if len(self.problems) == before_count:
            raise ValueError("Problem not found.")
        self.records = [record for record in self.records if record["problemId"] != problem_id]
        self.save_all()

    def upsert_record(self, student_id: str, problem_id: str, status: str) -> None:
        clean_status = status.strip().lower()
        if student_id not in self.student_by_id():
            raise ValueError("Selected student does not exist.")
        if problem_id not in self.problem_by_id():
            raise ValueError("Selected problem does not exist.")
        if clean_status not in VALID_STATUSES:
            raise ValueError("Status must be solved, attempted, or unsolved.")

        self.records = [
            record
            for record in self.records
            if not (record["studentId"] == student_id and record["problemId"] == problem_id)
        ]

        if clean_status != "unsolved":
            self.records.append({"studentId": student_id, "problemId": problem_id, "status": clean_status})

        self.save_all()

    def delete_record(self, student_id: str, problem_id: str) -> None:
        self.records = [
            record
            for record in self.records
            if not (record["studentId"] == student_id and record["problemId"] == problem_id)
        ]
        self.save_all()


class JsonAdminApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("OI Records JSON Manager")
        self.geometry("1420x860")
        self.minsize(1200, 760)

        self.repo = JsonRepository()
        self.status_var = tk.StringVar(value="Loaded data folder.")
        self.summary_var = tk.StringVar()

        self.student_id_var = tk.StringVar()
        self.student_name_var = tk.StringVar()
        self.task_title_var = tk.StringVar()
        self.task_type_var = tk.StringVar(value=TASK_TYPES[0])
        self.problem_title_var = tk.StringVar()
        self.problem_task_var = tk.StringVar()

        self.record_student_var = tk.StringVar()
        self.record_task_var = tk.StringVar()
        self.record_problem_var = tk.StringVar()
        self.record_status_var = tk.StringVar(value="solved")

        self.record_filter_student_var = tk.StringVar(value="All students")
        self.record_filter_task_var = tk.StringVar(value="All tasks")
        self.record_filter_status_var = tk.StringVar(value="All statuses")

        self._configure_style()
        self._build_shell()
        self.refresh_all()

    def _configure_style(self) -> None:
        self.option_add("*Font", ("Microsoft YaHei UI", 10))
        self.configure(bg="#071015")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background="#071015", foreground="#eafff6")
        style.configure("TFrame", background="#071015")
        style.configure("TLabel", background="#071015", foreground="#eafff6")
        style.configure("Muted.TLabel", background="#071015", foreground="#8db0aa")
        style.configure("Title.TLabel", background="#071015", foreground="#eafff6", font=("Consolas", 20, "bold"))
        style.configure("TButton", background="#12303a", foreground="#eafff6", borderwidth=0, padding=(12, 8))
        style.map("TButton", background=[("active", "#1a4956"), ("pressed", "#0b2730")], foreground=[("disabled", "#71928c")])
        style.configure("Accent.TButton", background="#15b887", foreground="#05100d")
        style.map("Accent.TButton", background=[("active", "#38f2ba"), ("pressed", "#0ea978")])
        style.configure("Danger.TButton", background="#7b2f39", foreground="#fff2f3")
        style.map("Danger.TButton", background=[("active", "#aa4351"), ("pressed", "#5b1f29")])
        style.configure("TLabelframe", background="#071015", foreground="#9be9ff", bordercolor="#1a3944", relief="solid")
        style.configure("TLabelframe.Label", background="#071015", foreground="#9be9ff")
        style.configure("TEntry", fieldbackground="#0f1b22", foreground="#ecfff8", bordercolor="#1a3944", insertcolor="#43f5b7")
        style.configure("TCombobox", fieldbackground="#0f1b22", foreground="#ecfff8", bordercolor="#1a3944", arrowcolor="#53d7ff")
        style.map("TCombobox", fieldbackground=[("readonly", "#0f1b22")])
        style.configure("Treeview", background="#0b1419", fieldbackground="#0b1419", foreground="#eafff6", bordercolor="#1a3944", rowheight=30)
        style.map("Treeview", background=[("selected", "#124653")], foreground=[("selected", "#ffffff")])
        style.configure("Treeview.Heading", background="#12242c", foreground="#9be9ff", relief="flat", font=("Microsoft YaHei UI", 10, "bold"))
        style.configure("TNotebook", background="#071015", borderwidth=0)
        style.configure("TNotebook.Tab", background="#0d1a20", foreground="#9ab8b1", padding=(16, 10))
        style.map("TNotebook.Tab", background=[("selected", "#12303a"), ("active", "#183e49")], foreground=[("selected", "#ecfff8")])

    def _build_shell(self) -> None:
        shell = ttk.Frame(self, padding=18)
        shell.pack(fill="both", expand=True)
        header = ttk.Frame(shell)
        header.pack(fill="x", pady=(0, 14))
        ttk.Label(header, text="OI Records JSON Manager", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Manage JSON files with automatic backups.", style="Muted.TLabel").pack(anchor="w", pady=(4, 0))

        toolbar = ttk.Frame(shell)
        toolbar.pack(fill="x", pady=(0, 12))
        ttk.Button(toolbar, text="Reload", command=self.handle_reload).pack(side="left")
        ttk.Button(toolbar, text="Show data folder", command=self.handle_show_data_path).pack(side="left", padx=(10, 0))
        ttk.Label(toolbar, textvariable=self.summary_var, style="Muted.TLabel").pack(side="right")

        self.notebook = ttk.Notebook(shell)
        self.notebook.pack(fill="both", expand=True)
        self.students_tab = ttk.Frame(self.notebook, padding=12)
        self.tasks_tab = ttk.Frame(self.notebook, padding=12)
        self.problems_tab = ttk.Frame(self.notebook, padding=12)
        self.records_tab = ttk.Frame(self.notebook, padding=12)
        self.notebook.add(self.students_tab, text="Students")
        self.notebook.add(self.tasks_tab, text="Tasks")
        self.notebook.add(self.problems_tab, text="Problems")
        self.notebook.add(self.records_tab, text="Records")
        self._build_students_tab()
        self._build_tasks_tab()
        self._build_problems_tab()
        self._build_records_tab()
        footer = ttk.Frame(shell)
        footer.pack(fill="x", pady=(12, 0))
        ttk.Label(footer, textvariable=self.status_var, style="Muted.TLabel").pack(anchor="w")

    def _create_split_area(self, parent: ttk.Frame) -> Tuple[ttk.Frame, ttk.Frame]:
        paned = ttk.Panedwindow(parent, orient="horizontal")
        paned.pack(fill="both", expand=True)
        left = ttk.Frame(paned)
        right = ttk.Frame(paned)
        paned.add(left, weight=4)
        paned.add(right, weight=3)
        return left, right

    def _build_students_tab(self) -> None:
        left, right = self._create_split_area(self.students_tab)
        self.students_tree = ttk.Treeview(left, columns=("id", "name"), show="headings")
        self.students_tree.heading("id", text="Student ID")
        self.students_tree.heading("name", text="Name")
        self.students_tree.column("id", width=140, anchor="center")
        self.students_tree.column("name", width=240, anchor="w")
        self.students_tree.pack(fill="both", expand=True)
        self.students_tree.bind("<<TreeviewSelect>>", self.handle_student_select)
        form = ttk.LabelFrame(right, text="Student Actions", padding=14)
        form.pack(fill="both", expand=True)
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text="Student ID").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.student_id_var).grid(row=1, column=0, sticky="ew", pady=(6, 12))
        ttk.Label(form, text="Name").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.student_name_var).grid(row=3, column=0, sticky="ew", pady=(6, 12))
        row = ttk.Frame(form)
        row.grid(row=4, column=0, sticky="ew")
        ttk.Button(row, text="Add", style="Accent.TButton", command=self.handle_add_student).pack(side="left")
        ttk.Button(row, text="Update", command=self.handle_update_student).pack(side="left", padx=8)
        ttk.Button(row, text="Delete", style="Danger.TButton", command=self.handle_delete_student).pack(side="left")
        ttk.Button(row, text="Clear", command=self.clear_student_form).pack(side="left", padx=(8, 0))

    def _build_tasks_tab(self) -> None:
        left, right = self._create_split_area(self.tasks_tab)
        self.tasks_tree = ttk.Treeview(left, columns=("id", "title", "type"), show="headings")
        self.tasks_tree.heading("id", text="Task ID")
        self.tasks_tree.heading("title", text="Title")
        self.tasks_tree.heading("type", text="Type")
        self.tasks_tree.column("id", width=120, anchor="center")
        self.tasks_tree.column("title", width=280, anchor="w")
        self.tasks_tree.column("type", width=180, anchor="center")
        self.tasks_tree.pack(fill="both", expand=True)
        self.tasks_tree.bind("<<TreeviewSelect>>", self.handle_task_select)
        form = ttk.LabelFrame(right, text="Task Actions", padding=14)
        form.pack(fill="both", expand=True)
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text="Task Title").grid(row=0, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.task_title_var).grid(row=1, column=0, sticky="ew", pady=(6, 12))
        ttk.Label(form, text="Task Type").grid(row=2, column=0, sticky="w")
        ttk.Combobox(form, textvariable=self.task_type_var, values=TASK_TYPES).grid(row=3, column=0, sticky="ew", pady=(6, 12))
        row = ttk.Frame(form)
        row.grid(row=4, column=0, sticky="ew")
        ttk.Button(row, text="Add", style="Accent.TButton", command=self.handle_add_task).pack(side="left")
        ttk.Button(row, text="Update", command=self.handle_update_task).pack(side="left", padx=8)
        ttk.Button(row, text="Delete", style="Danger.TButton", command=self.handle_delete_task).pack(side="left")
        ttk.Button(row, text="Clear", command=self.clear_task_form).pack(side="left", padx=(8, 0))
    def _build_problems_tab(self) -> None:
        left, right = self._create_split_area(self.problems_tab)
        self.problems_tree = ttk.Treeview(left, columns=("id", "task_id", "task_title", "title"), show="headings")
        self.problems_tree.heading("id", text="Problem ID")
        self.problems_tree.heading("task_id", text="Task ID")
        self.problems_tree.heading("task_title", text="Task")
        self.problems_tree.heading("title", text="Problem Title")
        self.problems_tree.column("id", width=110, anchor="center")
        self.problems_tree.column("task_id", width=110, anchor="center")
        self.problems_tree.column("task_title", width=220, anchor="w")
        self.problems_tree.column("title", width=260, anchor="w")
        self.problems_tree.pack(fill="both", expand=True)
        self.problems_tree.bind("<<TreeviewSelect>>", self.handle_problem_select)
        form = ttk.LabelFrame(right, text="Problem Actions", padding=14)
        form.pack(fill="both", expand=True)
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text="Task").grid(row=0, column=0, sticky="w")
        self.problem_task_combo = ttk.Combobox(form, textvariable=self.problem_task_var, state="readonly")
        self.problem_task_combo.grid(row=1, column=0, sticky="ew", pady=(6, 12))
        ttk.Label(form, text="Problem Title").grid(row=2, column=0, sticky="w")
        ttk.Entry(form, textvariable=self.problem_title_var).grid(row=3, column=0, sticky="ew", pady=(6, 12))
        row = ttk.Frame(form)
        row.grid(row=4, column=0, sticky="ew")
        ttk.Button(row, text="Add", style="Accent.TButton", command=self.handle_add_problem).pack(side="left")
        ttk.Button(row, text="Update", command=self.handle_update_problem).pack(side="left", padx=8)
        ttk.Button(row, text="Delete", style="Danger.TButton", command=self.handle_delete_problem).pack(side="left")
        ttk.Button(row, text="Clear", command=self.clear_problem_form).pack(side="left", padx=(8, 0))

    def _build_records_tab(self) -> None:
        filters = ttk.LabelFrame(self.records_tab, text="Filters", padding=12)
        filters.pack(fill="x", pady=(0, 12))
        filters.columnconfigure(1, weight=1)
        filters.columnconfigure(3, weight=1)
        filters.columnconfigure(5, weight=1)
        ttk.Label(filters, text="Student").grid(row=0, column=0, sticky="w")
        self.record_filter_student_combo = ttk.Combobox(filters, textvariable=self.record_filter_student_var, state="readonly")
        self.record_filter_student_combo.grid(row=0, column=1, sticky="ew", padx=(8, 14))
        self.record_filter_student_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_records_tree())
        ttk.Label(filters, text="Task").grid(row=0, column=2, sticky="w")
        self.record_filter_task_combo = ttk.Combobox(filters, textvariable=self.record_filter_task_var, state="readonly")
        self.record_filter_task_combo.grid(row=0, column=3, sticky="ew", padx=(8, 14))
        self.record_filter_task_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_records_tree())
        ttk.Label(filters, text="Status").grid(row=0, column=4, sticky="w")
        self.record_filter_status_combo = ttk.Combobox(filters, textvariable=self.record_filter_status_var, state="readonly", values=["All statuses", *VALID_STATUSES])
        self.record_filter_status_combo.grid(row=0, column=5, sticky="ew", padx=(8, 0))
        self.record_filter_status_combo.bind("<<ComboboxSelected>>", lambda _event: self.refresh_records_tree())

        left, right = self._create_split_area(self.records_tab)
        self.records_tree = ttk.Treeview(left, columns=("student", "task", "problem", "status"), show="headings")
        self.records_tree.heading("student", text="Student")
        self.records_tree.heading("task", text="Task")
        self.records_tree.heading("problem", text="Problem")
        self.records_tree.heading("status", text="Status")
        self.records_tree.column("student", width=180, anchor="w")
        self.records_tree.column("task", width=230, anchor="w")
        self.records_tree.column("problem", width=260, anchor="w")
        self.records_tree.column("status", width=120, anchor="center")
        self.records_tree.pack(fill="both", expand=True)
        self.records_tree.bind("<<TreeviewSelect>>", self.handle_record_select)

        form = ttk.LabelFrame(right, text="Record Actions", padding=14)
        form.pack(fill="both", expand=True)
        form.columnconfigure(0, weight=1)
        ttk.Label(form, text="Missing records are treated as unsolved. Saving unsolved removes the record.", style="Muted.TLabel", wraplength=360).grid(row=0, column=0, sticky="w", pady=(0, 12))
        ttk.Label(form, text="Student").grid(row=1, column=0, sticky="w")
        self.record_student_combo = ttk.Combobox(form, textvariable=self.record_student_var, state="readonly")
        self.record_student_combo.grid(row=2, column=0, sticky="ew", pady=(6, 12))
        ttk.Label(form, text="Task").grid(row=3, column=0, sticky="w")
        self.record_task_combo = ttk.Combobox(form, textvariable=self.record_task_var, state="readonly")
        self.record_task_combo.grid(row=4, column=0, sticky="ew", pady=(6, 12))
        self.record_task_combo.bind("<<ComboboxSelected>>", self.handle_record_task_change)
        ttk.Label(form, text="Problem").grid(row=5, column=0, sticky="w")
        self.record_problem_combo = ttk.Combobox(form, textvariable=self.record_problem_var, state="readonly")
        self.record_problem_combo.grid(row=6, column=0, sticky="ew", pady=(6, 12))
        ttk.Label(form, text="Status").grid(row=7, column=0, sticky="w")
        self.record_status_combo = ttk.Combobox(form, textvariable=self.record_status_var, state="readonly", values=VALID_STATUSES)
        self.record_status_combo.grid(row=8, column=0, sticky="ew", pady=(6, 12))
        row = ttk.Frame(form)
        row.grid(row=9, column=0, sticky="ew")
        ttk.Button(row, text="Save", style="Accent.TButton", command=self.handle_save_record).pack(side="left")
        ttk.Button(row, text="Set unsolved", command=self.handle_clear_record).pack(side="left", padx=8)
        ttk.Button(row, text="Delete", style="Danger.TButton", command=self.handle_delete_record).pack(side="left")
        ttk.Button(row, text="Clear", command=self.clear_record_form).pack(side="left", padx=(8, 0))

    def formatted_students(self) -> list[str]:
        return [f'{student["id"]} | {student["name"]}' for student in self.repo.students]

    def formatted_tasks(self) -> list[str]:
        return [f'{task["id"]} | {task["title"]}' for task in self.repo.tasks]

    def formatted_problems(self, task_id: Optional[str] = None) -> list[str]:
        task_map = self.repo.task_by_id()
        values = []
        for problem in self.repo.problems:
            if task_id and problem["taskId"] != task_id:
                continue
            task_title = task_map.get(problem["taskId"], {}).get("title", "Unknown task")
            values.append(f'{problem["id"]} | {problem["title"]} [{task_title}]')
        return values

    def current_tree_value(self, tree: ttk.Treeview) -> Optional[str]:
        selection = tree.selection()
        if not selection:
            return None
        return str(tree.item(selection[0], "values")[0])

    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def refresh_all(self) -> None:
        self.refresh_students_tree()
        self.refresh_tasks_tree()
        self.refresh_problems_tree()
        self.refresh_record_choices()
        self.refresh_records_tree()
        self.summary_var.set(f"Students {len(self.repo.students)} | Tasks {len(self.repo.tasks)} | Problems {len(self.repo.problems)} | Records {len(self.repo.records)}")

    def refresh_students_tree(self) -> None:
        self.students_tree.delete(*self.students_tree.get_children())
        for student in self.repo.students:
            self.students_tree.insert("", "end", values=(student["id"], student["name"]))

    def refresh_tasks_tree(self) -> None:
        self.tasks_tree.delete(*self.tasks_tree.get_children())
        for task in self.repo.tasks:
            self.tasks_tree.insert("", "end", values=(task["id"], task["title"], task["type"]))

    def refresh_problems_tree(self) -> None:
        self.problems_tree.delete(*self.problems_tree.get_children())
        task_map = self.repo.task_by_id()
        for problem in self.repo.problems:
            task_title = task_map.get(problem["taskId"], {}).get("title", "Unknown task")
            self.problems_tree.insert("", "end", values=(problem["id"], problem["taskId"], task_title, problem["title"]))

    def refresh_record_choices(self) -> None:
        student_values = self.formatted_students()
        task_values = self.formatted_tasks()
        self.problem_task_combo["values"] = task_values
        self.record_student_combo["values"] = student_values
        self.record_task_combo["values"] = task_values
        self.record_filter_student_combo["values"] = ["All students", *student_values]
        self.record_filter_task_combo["values"] = ["All tasks", *task_values]
        current_task_id = parse_display_id(self.record_task_var.get()) if self.record_task_var.get() else None
        self.record_problem_combo["values"] = self.formatted_problems(current_task_id)
    def refresh_records_tree(self) -> None:
        self.records_tree.delete(*self.records_tree.get_children())
        student_map = self.repo.student_by_id()
        task_map = self.repo.task_by_id()
        problem_map = self.repo.problem_by_id()
        student_filter = parse_display_id(self.record_filter_student_var.get())
        task_filter = parse_display_id(self.record_filter_task_var.get())
        status_filter = self.record_filter_status_var.get()

        for record in self.repo.records:
            student = student_map.get(record["studentId"])
            problem = problem_map.get(record["problemId"])
            if not student or not problem:
                continue
            task = task_map.get(problem["taskId"])
            if student_filter and self.record_filter_student_var.get() != "All students" and record["studentId"] != student_filter:
                continue
            if task_filter and self.record_filter_task_var.get() != "All tasks" and problem["taskId"] != task_filter:
                continue
            if status_filter != "All statuses" and record["status"] != status_filter:
                continue
            task_title = task["title"] if task else "Unknown task"
            item_id = f'{record["studentId"]}:{record["problemId"]}'
            self.records_tree.insert("", "end", iid=item_id, values=(f'{record["studentId"]} | {student["name"]}', task_title, problem["title"], record["status"]))

    def clear_student_form(self) -> None:
        self.student_id_var.set("")
        self.student_name_var.set("")
        self.students_tree.selection_remove(self.students_tree.selection())

    def clear_task_form(self) -> None:
        self.task_title_var.set("")
        self.task_type_var.set(TASK_TYPES[0])
        self.tasks_tree.selection_remove(self.tasks_tree.selection())

    def clear_problem_form(self) -> None:
        self.problem_title_var.set("")
        self.problem_task_var.set("")
        self.problems_tree.selection_remove(self.problems_tree.selection())

    def clear_record_form(self) -> None:
        self.record_student_var.set("")
        self.record_task_var.set("")
        self.record_problem_var.set("")
        self.record_status_var.set("solved")
        self.record_problem_combo["values"] = []
        self.records_tree.selection_remove(self.records_tree.selection())

    def handle_reload(self) -> None:
        try:
            self.repo.reload()
            self.refresh_all()
            self.set_status("Reloaded all JSON files.")
        except Exception as error:
            messagebox.showerror("Reload failed", str(error))

    def handle_show_data_path(self) -> None:
        messagebox.showinfo("data folder", str(DATA_DIR))

    def handle_student_select(self, _event: tk.Event) -> None:
        student_id = self.current_tree_value(self.students_tree)
        if not student_id:
            return
        student = self.repo.student_by_id().get(student_id)
        if student:
            self.student_id_var.set(student["id"])
            self.student_name_var.set(student["name"])

    def handle_task_select(self, _event: tk.Event) -> None:
        task_id = self.current_tree_value(self.tasks_tree)
        if not task_id:
            return
        task = self.repo.task_by_id().get(task_id)
        if task:
            self.task_title_var.set(task["title"])
            self.task_type_var.set(task["type"])

    def handle_problem_select(self, _event: tk.Event) -> None:
        problem_id = self.current_tree_value(self.problems_tree)
        if not problem_id:
            return
        problem = self.repo.problem_by_id().get(problem_id)
        task = self.repo.task_by_id().get(problem["taskId"]) if problem else None
        if problem and task:
            self.problem_title_var.set(problem["title"])
            self.problem_task_var.set(f'{task["id"]} | {task["title"]}')

    def handle_record_select(self, _event: tk.Event) -> None:
        selection = self.records_tree.selection()
        if not selection:
            return
        student_id, problem_id = selection[0].split(":", 1)
        student = self.repo.student_by_id().get(student_id)
        problem = self.repo.problem_by_id().get(problem_id)
        task = self.repo.task_by_id().get(problem["taskId"]) if problem else None
        record = next((item for item in self.repo.records if item["studentId"] == student_id and item["problemId"] == problem_id), None)
        if student and task and problem and record:
            self.record_student_var.set(f'{student["id"]} | {student["name"]}')
            self.record_task_var.set(f'{task["id"]} | {task["title"]}')
            self.handle_record_task_change()
            self.record_problem_var.set(f'{problem["id"]} | {problem["title"]} [{task["title"]}]')
            self.record_status_var.set(record["status"])

    def handle_record_task_change(self, _event: Optional[tk.Event] = None) -> None:
        task_id = parse_display_id(self.record_task_var.get()) if self.record_task_var.get() else None
        problem_values = self.formatted_problems(task_id)
        self.record_problem_combo["values"] = problem_values
        current_problem_id = parse_display_id(self.record_problem_var.get())
        if current_problem_id and any(value.startswith(current_problem_id) for value in problem_values):
            return
        self.record_problem_var.set(problem_values[0] if problem_values else "")

    def handle_add_student(self) -> None:
        try:
            student = self.repo.add_student(self.student_name_var.get(), self.student_id_var.get())
            self.refresh_all()
            self.student_id_var.set(student["id"])
            self.student_name_var.set(student["name"])
            self.set_status(f'Added student: {student["id"]}.')
        except Exception as error:
            messagebox.showerror("Add student failed", str(error))

    def handle_update_student(self) -> None:
        student_id = self.current_tree_value(self.students_tree)
        if not student_id:
            messagebox.showwarning("No selection", "Please select a student first.")
            return
        new_student_id = self.student_id_var.get().strip()
        try:
            self.repo.update_student(student_id, new_student_id, self.student_name_var.get())
            self.refresh_all()
            self.student_id_var.set(new_student_id)
            self.set_status(f"Updated student: {student_id} -> {new_student_id}.")
        except Exception as error:
            messagebox.showerror("Update student failed", str(error))

    def handle_delete_student(self) -> None:
        student_id = self.current_tree_value(self.students_tree)
        if not student_id:
            messagebox.showwarning("No selection", "Please select a student first.")
            return
        if not messagebox.askyesno("Confirm delete", "Deleting the student will also delete all of their records. Continue?"):
            return
        try:
            self.repo.delete_student(student_id)
            self.refresh_all()
            self.clear_student_form()
            self.set_status(f"Deleted student: {student_id}.")
        except Exception as error:
            messagebox.showerror("Delete student failed", str(error))
    def handle_add_task(self) -> None:
        try:
            task = self.repo.add_task(self.task_title_var.get(), self.task_type_var.get())
            self.refresh_all()
            self.task_type_var.set(task["type"])
            self.task_title_var.set(task["title"])
            self.set_status(f'Added task: {task["id"]}.')
        except Exception as error:
            messagebox.showerror("Add task failed", str(error))

    def handle_update_task(self) -> None:
        task_id = self.current_tree_value(self.tasks_tree)
        if not task_id:
            messagebox.showwarning("No selection", "Please select a task first.")
            return
        try:
            self.repo.update_task(task_id, self.task_title_var.get(), self.task_type_var.get())
            self.refresh_all()
            self.set_status(f"Updated task: {task_id}.")
        except Exception as error:
            messagebox.showerror("Update task failed", str(error))

    def handle_delete_task(self) -> None:
        task_id = self.current_tree_value(self.tasks_tree)
        if not task_id:
            messagebox.showwarning("No selection", "Please select a task first.")
            return
        if not messagebox.askyesno("Confirm delete", "Deleting the task will also delete its problems and related records. Continue?"):
            return
        try:
            self.repo.delete_task(task_id)
            self.refresh_all()
            self.clear_task_form()
            self.clear_problem_form()
            self.clear_record_form()
            self.set_status(f"Deleted task: {task_id}.")
        except Exception as error:
            messagebox.showerror("Delete task failed", str(error))

    def handle_add_problem(self) -> None:
        task_id = parse_display_id(self.problem_task_var.get())
        try:
            problem = self.repo.add_problem(task_id, self.problem_title_var.get())
            self.refresh_all()
            self.problem_title_var.set(problem["title"])
            self.set_status(f'Added problem: {problem["id"]}.')
        except Exception as error:
            messagebox.showerror("Add problem failed", str(error))

    def handle_update_problem(self) -> None:
        problem_id = self.current_tree_value(self.problems_tree)
        if not problem_id:
            messagebox.showwarning("No selection", "Please select a problem first.")
            return
        task_id = parse_display_id(self.problem_task_var.get())
        try:
            self.repo.update_problem(problem_id, task_id, self.problem_title_var.get())
            self.refresh_all()
            self.set_status(f"Updated problem: {problem_id}.")
        except Exception as error:
            messagebox.showerror("Update problem failed", str(error))

    def handle_delete_problem(self) -> None:
        problem_id = self.current_tree_value(self.problems_tree)
        if not problem_id:
            messagebox.showwarning("No selection", "Please select a problem first.")
            return
        if not messagebox.askyesno("Confirm delete", "Deleting the problem will also delete its records. Continue?"):
            return
        try:
            self.repo.delete_problem(problem_id)
            self.refresh_all()
            self.clear_problem_form()
            self.clear_record_form()
            self.set_status(f"Deleted problem: {problem_id}.")
        except Exception as error:
            messagebox.showerror("Delete problem failed", str(error))

    def handle_save_record(self) -> None:
        student_id = parse_display_id(self.record_student_var.get())
        problem_id = parse_display_id(self.record_problem_var.get())
        try:
            self.repo.upsert_record(student_id, problem_id, self.record_status_var.get())
            self.refresh_all()
            if self.record_status_var.get() == "unsolved":
                self.set_status(f"Cleared record to unsolved: {student_id} / {problem_id}.")
            else:
                self.set_status(f"Saved record: {student_id} / {problem_id} -> {self.record_status_var.get()}.")
        except Exception as error:
            messagebox.showerror("Save record failed", str(error))

    def handle_clear_record(self) -> None:
        student_id = parse_display_id(self.record_student_var.get())
        problem_id = parse_display_id(self.record_problem_var.get())
        if not student_id or not problem_id:
            messagebox.showwarning("Missing info", "Please select both a student and a problem.")
            return
        try:
            self.repo.upsert_record(student_id, problem_id, "unsolved")
            self.refresh_all()
            self.record_status_var.set("solved")
            self.set_status(f"Cleared record: {student_id} / {problem_id}.")
        except Exception as error:
            messagebox.showerror("Clear record failed", str(error))

    def handle_delete_record(self) -> None:
        selection = self.records_tree.selection()
        if not selection:
            messagebox.showwarning("No selection", "Please select a record first.")
            return
        student_id, problem_id = selection[0].split(":", 1)
        if not messagebox.askyesno("Confirm delete", "Deleting the record will mark this problem as unsolved. Continue?"):
            return
        try:
            self.repo.delete_record(student_id, problem_id)
            self.refresh_all()
            self.clear_record_form()
            self.set_status(f"Deleted record: {student_id} / {problem_id}.")
        except Exception as error:
            messagebox.showerror("Delete record failed", str(error))


def main() -> None:
    app = JsonAdminApp()
    app.mainloop()


if __name__ == "__main__":
    main()
