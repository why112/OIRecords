#!/usr/bin/env node

import { createInterface } from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const dataDirectory = path.resolve(projectRoot, 'data');
const backupsDirectory = path.resolve(projectRoot, 'backups');

const DATA_FILES = {
  students: 'students.json',
  tasks: 'tasks.json',
  problems: 'problems.json',
  records: 'record.json'
};

const VALID_STATUS = new Set(['solved', 'attempted', 'unsolved']);
const KNOWN_TYPES = [
  'codeforces_div1',
  'codeforces_div2',
  'codeforces_div3',
  'codeforces_div4',
  'atcoder_abc',
  'atcoder_arc',
  'atcoder_agc',
  'private',
  'luogu',
  'vjudge'
];

function normalizeText(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function sortById(left, right) {
  return String(left.id).localeCompare(String(right.id), 'zh-Hans-CN');
}

function parseArgs(argv) {
  const [command, ...rest] = argv;
  const options = {};

  for (let index = 0; index < rest.length; index += 1) {
    const token = rest[index];

    if (token.startsWith('--')) {
      const key = token.slice(2);
      const nextToken = rest[index + 1];

      if (nextToken && !nextToken.startsWith('--')) {
        options[key] = nextToken;
        index += 1;
      } else {
        options[key] = true;
      }
    } else {
      if (!Array.isArray(options._)) {
        options._ = [];
      }

      options._.push(token);
    }
  }

  return { command, options };
}

async function ensureDataDirectory() {
  await fs.mkdir(dataDirectory, { recursive: true });
}

async function ensureBackupsDirectory() {
  await fs.mkdir(backupsDirectory, { recursive: true });
}

function createBackupStamp() {
  const now = new Date();
  const datePart = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, '0'),
    String(now.getDate()).padStart(2, '0')
  ].join('');
  const timePart = [
    String(now.getHours()).padStart(2, '0'),
    String(now.getMinutes()).padStart(2, '0'),
    String(now.getSeconds()).padStart(2, '0'),
    String(now.getMilliseconds()).padStart(3, '0')
  ].join('');

  return `${datePart}-${timePart}`;
}

async function backupFileIfNeeded(name, currentText, nextText) {
  if (currentText === nextText) {
    return;
  }

  await ensureBackupsDirectory();
  const backupFileName = `${createBackupStamp()}-${DATA_FILES[name]}`;
  const backupPath = path.join(backupsDirectory, backupFileName);
  await fs.writeFile(backupPath, currentText, 'utf8');
}

async function readCollection(name) {
  await ensureDataDirectory();
  const filePath = path.join(dataDirectory, DATA_FILES[name]);

  try {
    const rawText = await fs.readFile(filePath, 'utf8');
    const payload = JSON.parse(rawText);

    if (!Array.isArray(payload)) {
      throw new Error(`${DATA_FILES[name]} 必须是 JSON 数组。`);
    }

    return payload;
  } catch (error) {
    if (error && error.code === 'ENOENT') {
      await writeCollection(name, []);
      return [];
    }

    throw error;
  }
}

async function writeCollection(name, payload) {
  await ensureDataDirectory();
  const filePath = path.join(dataDirectory, DATA_FILES[name]);
  const nextText = `${JSON.stringify(payload, null, 2)}\n`;

  try {
    const currentText = await fs.readFile(filePath, 'utf8');
    await backupFileIfNeeded(name, currentText, nextText);

    if (currentText === nextText) {
      return;
    }
  } catch (error) {
    if (!error || error.code !== 'ENOENT') {
      throw error;
    }
  }

  await fs.writeFile(filePath, nextText, 'utf8');
}

async function loadAllData() {
  const [students, tasks, problems, records] = await Promise.all([
    readCollection('students'),
    readCollection('tasks'),
    readCollection('problems'),
    readCollection('records')
  ]);

  return { students, tasks, problems, records };
}

function generateId(prefix, items) {
  let maxNumber = 0;

  for (const item of items) {
    const rawId = typeof item === 'string' ? item : item?.id;

    if (typeof rawId !== 'string') {
      continue;
    }

    const match = rawId.match(new RegExp(`^${prefix}(\\d+)$`));

    if (match) {
      maxNumber = Math.max(maxNumber, Number.parseInt(match[1], 10));
    }
  }

  return `${prefix}${String(maxNumber + 1).padStart(3, '0')}`;
}

function printHelp() {
  console.log(`用法:
  node scripts/manage-data.js add-student --name 张三
  node scripts/manage-data.js add-task --title "Codeforces Div2 寒假训练" --type codeforces_div2
  node scripts/manage-data.js add-problem --taskId t001 --title "A. Way Too Long Words"
  node scripts/manage-data.js set-status --studentId s001 --problemId p001 --status solved
  node scripts/manage-data.js list [students|tasks|problems|records|all]

不带参数运行时，会进入交互式菜单。`);
}

async function addStudent(name) {
  const cleanName = normalizeText(name);

  if (!cleanName) {
    throw new Error('学生姓名不能为空。');
  }

  const students = await readCollection('students');
  const student = {
    id: generateId('s', students),
    name: cleanName
  };

  students.push(student);
  students.sort(sortById);
  await writeCollection('students', students);

  console.log(`已添加学生：${student.id} ${student.name}`);
}

async function addTask(title, type) {
  const cleanTitle = normalizeText(title);
  const cleanType = normalizeText(type).toLowerCase();

  if (!cleanTitle) {
    throw new Error('作业块标题不能为空。');
  }

  if (!cleanType) {
    throw new Error('作业块类型不能为空。');
  }

  const tasks = await readCollection('tasks');
  const task = {
    id: generateId('t', tasks),
    title: cleanTitle,
    type: cleanType
  };

  tasks.push(task);
  tasks.sort(sortById);
  await writeCollection('tasks', tasks);

  if (!KNOWN_TYPES.includes(cleanType)) {
    console.log(`已添加扩展类型作业块：${task.id} ${task.title} (${task.type})`);
    return;
  }

  console.log(`已添加作业块：${task.id} ${task.title} (${task.type})`);
}

async function addProblem(taskId, title) {
  const cleanTaskId = normalizeText(taskId);
  const cleanTitle = normalizeText(title);

  if (!cleanTaskId) {
    throw new Error('taskId 不能为空。');
  }

  if (!cleanTitle) {
    throw new Error('题目标题不能为空。');
  }

  const [tasks, problems] = await Promise.all([
    readCollection('tasks'),
    readCollection('problems')
  ]);

  if (!tasks.some((task) => task.id === cleanTaskId)) {
    throw new Error(`未找到作业块：${cleanTaskId}`);
  }

  const problem = {
    id: generateId('p', problems),
    taskId: cleanTaskId,
    title: cleanTitle
  };

  problems.push(problem);
  problems.sort(sortById);
  await writeCollection('problems', problems);

  console.log(`已添加题目：${problem.id} ${problem.title} -> ${problem.taskId}`);
}

async function setStatus(studentId, problemId, status) {
  const cleanStudentId = normalizeText(studentId);
  const cleanProblemId = normalizeText(problemId);
  const cleanStatus = normalizeText(status).toLowerCase();

  if (!cleanStudentId || !cleanProblemId) {
    throw new Error('studentId 和 problemId 都不能为空。');
  }

  if (!VALID_STATUS.has(cleanStatus)) {
    throw new Error('状态必须是 solved、attempted 或 unsolved。');
  }

  const { students, problems, records } = await loadAllData();

  if (!students.some((student) => student.id === cleanStudentId)) {
    throw new Error(`未找到学生：${cleanStudentId}`);
  }

  if (!problems.some((problem) => problem.id === cleanProblemId)) {
    throw new Error(`未找到题目：${cleanProblemId}`);
  }

  const nextRecords = records.filter(
    (record) =>
      !(record.studentId === cleanStudentId && record.problemId === cleanProblemId)
  );

  if (cleanStatus !== 'unsolved') {
    nextRecords.push({
      studentId: cleanStudentId,
      problemId: cleanProblemId,
      status: cleanStatus
    });
  }

  nextRecords.sort((left, right) => {
    return (
      String(left.studentId).localeCompare(String(right.studentId), 'zh-Hans-CN') ||
      String(left.problemId).localeCompare(String(right.problemId), 'zh-Hans-CN')
    );
  });

  await writeCollection('records', nextRecords);

  if (cleanStatus === 'unsolved') {
    console.log(`已清除状态记录：${cleanStudentId} / ${cleanProblemId}`);
    return;
  }

  console.log(`已更新状态：${cleanStudentId} / ${cleanProblemId} -> ${cleanStatus}`);
}

function buildLookupMap(items, key = 'id') {
  return new Map(items.map((item) => [item[key], item]));
}

async function listData(scope = 'all') {
  const normalizedScope = normalizeText(scope).toLowerCase() || 'all';
  const { students, tasks, problems, records } = await loadAllData();
  const studentMap = buildLookupMap(students);
  const taskMap = buildLookupMap(tasks);
  const problemMap = buildLookupMap(problems);

  if (normalizedScope === 'students' || normalizedScope === 'all') {
    console.log('\n学生列表');
    console.table(students);
  }

  if (normalizedScope === 'tasks' || normalizedScope === 'all') {
    console.log('\n作业块列表');
    console.table(tasks);
  }

  if (normalizedScope === 'problems' || normalizedScope === 'all') {
    console.log('\n题目列表');
    console.table(
      problems.map((problem) => ({
        ...problem,
        taskTitle: taskMap.get(problem.taskId)?.title || '(未知作业块)'
      }))
    );
  }

  if (normalizedScope === 'records' || normalizedScope === 'all') {
    console.log('\n完成记录');
    console.table(
      records.map((record) => ({
        ...record,
        studentName: studentMap.get(record.studentId)?.name || '(未知学生)',
        problemTitle: problemMap.get(record.problemId)?.title || '(未知题目)'
      }))
    );
  }
}

async function runInteractiveMode() {
  const rl = createInterface({ input, output });

  try {
    while (true) {
      console.log('\n算法竞赛作业完成情况数据维护');
      console.log('1. 添加学生');
      console.log('2. 添加作业块');
      console.log('3. 添加题目');
      console.log('4. 更新完成状态');
      console.log('5. 列出当前数据');
      console.log('0. 退出');

      const action = normalizeText(await rl.question('请选择操作编号：'));

      if (action === '0') {
        break;
      }

      if (action === '1') {
        const name = await rl.question('请输入学生姓名：');
        await addStudent(name);
        continue;
      }

      if (action === '2') {
        const title = await rl.question('请输入作业块标题：');
        const type = await rl.question(
          `请输入作业块类型（例如 ${KNOWN_TYPES.join(' / ')}）：`
        );
        await addTask(title, type);
        continue;
      }

      if (action === '3') {
        const taskId = await rl.question('请输入作业块 ID：');
        const title = await rl.question('请输入题目标题：');
        await addProblem(taskId, title);
        continue;
      }

      if (action === '4') {
        const studentId = await rl.question('请输入学生 ID：');
        const problemId = await rl.question('请输入题目 ID：');
        const status = await rl.question(
          '请输入状态（solved / attempted / unsolved，设置 unsolved 会删除记录）：'
        );
        await setStatus(studentId, problemId, status);
        continue;
      }

      if (action === '5') {
        const scope = await rl.question(
          '请输入查看范围（students / tasks / problems / records / all）：'
        );
        await listData(scope);
        continue;
      }

      console.log('无效选项，请重新输入。');
    }
  } finally {
    rl.close();
  }
}

async function main() {
  const { command, options } = parseArgs(process.argv.slice(2));

  if (!command) {
    await runInteractiveMode();
    return;
  }

  if (command === 'help' || command === '--help' || command === '-h') {
    printHelp();
    return;
  }

  if (command === 'add-student') {
    await addStudent(options.name);
    return;
  }

  if (command === 'add-task') {
    await addTask(options.title, options.type);
    return;
  }

  if (command === 'add-problem') {
    await addProblem(options.taskId, options.title);
    return;
  }

  if (command === 'set-status') {
    await setStatus(options.studentId, options.problemId, options.status);
    return;
  }

  if (command === 'list') {
    await listData(options._?.[0] || 'all');
    return;
  }

  throw new Error(`未知命令：${command}`);
}

main().catch((error) => {
  console.error(`错误：${error instanceof Error ? error.message : String(error)}`);
  process.exitCode = 1;
});