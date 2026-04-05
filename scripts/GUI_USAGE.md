# JSON 图形化管理器

文件：`scripts/json_admin_gui.py`

## 功能

- 图形化管理 `students.json`
- 图形化管理 `tasks.json`
- 图形化管理 `problems.json`
- 图形化管理 `record.json`
- 删除学生、作业块、题目时自动清理关联记录
- 将完成状态设置为 `unsolved` 时自动删除对应记录

## 启动方式

优先推荐双击：

- `scripts/open-json-admin-gui.bat`

也可以命令行运行：

```bash
python scripts/json_admin_gui.py
```

如果你希望不弹控制台窗口，可以使用：

```bash
pythonw scripts/json_admin_gui.py
```

## 界面说明

- `学生` 页：添加、修改、删除学生，并支持修改学生学号 / ID
- `作业块` 页：添加、修改、删除作业块
- `题目` 页：为指定作业块添加题目，或修改、删除题目
- `完成记录` 页：筛选记录，并为某个学生设置某道题的状态

所有修改都会直接保存到项目根目录的 `data/` 下。

