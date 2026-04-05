# 算法竞赛作业完成情况追踪系统

一个基于 Vue 3 + Vue Router + Vite 的轻量级 Web 应用，用于追踪算法竞赛训练营学生的作业完成情况。项目没有后端，所有数据都存放在项目根目录的 `data/` 下，通过 Git 管理即可。

## 项目特点

- 前端静态部署，适合 GitHub Pages
- 数据使用 JSON 文件维护，结构清晰
- 提供命令行数据维护脚本
- 提供 Python 图形化 JSON 管理器
- 所有数据改动前都会自动生成备份
- 项目文本文件统一使用 `UTF-8 without BOM`

## 目录结构

- `data/`
  学生、作业块、题目和完成记录数据文件
- `scripts/manage-data.js`
  命令行数据维护脚本
- `scripts/json_admin_gui.py`
  Python 图形化管理器
- `scripts/open-json-admin-gui.bat`
  Windows 双击启动图形化管理器
- `scripts/check-encoding.py`
  编码巡检脚本
- `backups/`
  JSON 修改前自动生成的备份文件
- `src/`
  前端页面、组件、样式和数据加载逻辑
- `vite.config.js`
  Vite 配置，开发时读取根目录 `data/`，构建时复制到 `dist/data/`

## 本地运行

```bash
npm install
npm run dev
```

## 构建

```bash
npm run build
```

构建完成后，静态文件会输出到 `dist/`，同时自动包含 `dist/data/`。

## 数据维护方式

### 1. 命令行脚本

```bash
npm run data
```

也可以直接调用：

```bash
node scripts/manage-data.js add-student --name 张三
node scripts/manage-data.js add-task --title "Codeforces Div2 寒假训练" --type codeforces_div2
node scripts/manage-data.js add-problem --taskId t001 --title "A. Way Too Long Words"
node scripts/manage-data.js set-status --studentId s001 --problemId p001 --status solved
node scripts/manage-data.js list all
```

说明：

- 将状态设置为 `unsolved` 时，会自动删除对应记录，避免 `record.json` 冗余
- 在脚本写入 JSON 前，会先把旧版本备份到 `backups/`

### 2. 图形化管理器

优先推荐双击：

- `scripts/open-json-admin-gui.bat`

也可以命令行运行：

```bash
python scripts/json_admin_gui.py
```

图形化管理器支持：

- 添加、修改、删除学生
- 修改学生学号 / ID
- 添加、修改、删除作业块
- 添加、修改、删除题目
- 添加、修改、删除完成记录
- 修改前自动备份 JSON 文件

## 编码规范

项目文本文件统一规定为：

- 编码：`UTF-8`
- 推荐形式：`UTF-8 without BOM`

仓库内已经配置：

- `.editorconfig`
- `.gitattributes`

可以使用下面的命令检查当前项目文件编码：

```bash
python scripts/check-encoding.py
```

## 备份机制

所有通过维护脚本或图形化管理器触发的 JSON 写入，在真正覆盖文件前都会先备份旧内容。

备份目录：

- `backups/`

备份文件命名类似：

- `20260405-113527-938-problems.json`

这样即使误操作，也能快速恢复。

## 前端页面说明

### 首页

- 展示所有学生卡片
- 显示每个学生的总完成情况
- 点击卡片进入学生详情页

### 学生详情页

- 展示学生总完成情况
- 直接按作业块展示，不再显示作业块类型分组
- 每个作业块可展开查看题目列表
- 题目状态会作用到整条样式，不只是标题颜色

## GitHub Pages 说明

- 项目使用 Vue Router 的 History 路由
- 附带 `404.html` 回退文件，适配 GitHub Pages 深链接访问
- 页面在运行时按基路径读取 `data/*.json`

部署后可访问：

- `https://<username>.github.io/<repository>/`

## 当前常用命令

```bash
npm run dev
npm run build
npm run data
python scripts/check-encoding.py
python scripts/json_admin_gui.py
```
