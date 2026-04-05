import { reactive } from 'vue';
import { buildAppPath } from './runtime';

const VALID_STATUS = new Set(['solved', 'attempted', 'unsolved']);
const LOCALE = 'zh-Hans-CN';

export const TYPE_META = {
  codeforces_div1: { label: 'Codeforces Div1', order: 1 },
  codeforces_div2: { label: 'Codeforces Div2', order: 2 },
  codeforces_div3: { label: 'Codeforces Div3', order: 3 },
  codeforces_div4: { label: 'Codeforces Div4', order: 4 },
  atcoder_abc: { label: 'AtCoder ABC', order: 5 },
  atcoder_arc: { label: 'AtCoder ARC', order: 6 },
  atcoder_agc: { label: 'AtCoder AGC', order: 7 },
  private: { label: '私有平台', order: 8 },
  luogu: { label: '洛谷', order: 9 },
  vjudge: { label: 'vjudge', order: 10 }
};

const store = reactive({
  loading: false,
  loaded: false,
  error: '',
  students: [],
  tasks: [],
  problems: [],
  taskBuckets: [],
  studentById: new Map(),
  taskById: new Map(),
  problemById: new Map(),
  problemsByTask: new Map(),
  recordMap: new Map(),
  studentSummaryById: new Map(),
  taskProgressByStudent: new Map()
});

let loadPromise = null;

function sortStudents(left, right) {
  return left.name.localeCompare(right.name, LOCALE) || left.id.localeCompare(right.id, LOCALE);
}

function sortProblems(left, right) {
  return left.id.localeCompare(right.id, LOCALE) || left.title.localeCompare(right.title, LOCALE);
}

function normalizeStatus(status) {
  return VALID_STATUS.has(status) ? status : 'unsolved';
}

function formatTypeLabel(type) {
  if (!type) {
    return '未分类';
  }

  return type
    .split('_')
    .map((chunk) => {
      if (!chunk) {
        return '';
      }

      return chunk[0].toUpperCase() + chunk.slice(1);
    })
    .join(' ');
}

function getTypeMeta(type) {
  return TYPE_META[type] || { label: formatTypeLabel(type), order: 99 };
}

function sortTasks(left, right) {
  const leftMeta = getTypeMeta(left.type);
  const rightMeta = getTypeMeta(right.type);

  return (
    leftMeta.order - rightMeta.order ||
    leftMeta.label.localeCompare(rightMeta.label, LOCALE) ||
    left.title.localeCompare(right.title, LOCALE) ||
    left.id.localeCompare(right.id, LOCALE)
  );
}

function buildTaskBuckets(tasks) {
  const groupedTasks = new Map();

  for (const task of tasks) {
    const meta = getTypeMeta(task.type);

    if (!groupedTasks.has(task.type)) {
      groupedTasks.set(task.type, {
        type: task.type,
        label: meta.label,
        order: meta.order,
        tasks: []
      });
    }

    groupedTasks.get(task.type).tasks.push(task);
  }

  return [...groupedTasks.values()]
    .sort(
      (left, right) =>
        left.order - right.order || left.label.localeCompare(right.label, LOCALE)
    )
    .map((bucket) => ({
      ...bucket,
      tasks: bucket.tasks.sort(sortTasks)
    }));
}

function resetStore() {
  store.loaded = false;
  store.students = [];
  store.tasks = [];
  store.problems = [];
  store.taskBuckets = [];
  store.studentById = new Map();
  store.taskById = new Map();
  store.problemById = new Map();
  store.problemsByTask = new Map();
  store.recordMap = new Map();
  store.studentSummaryById = new Map();
  store.taskProgressByStudent = new Map();
}

async function fetchJsonFile(fileName) {
  const response = await fetch(buildAppPath(`data/${fileName}`), {
    cache: 'no-store'
  });

  if (!response.ok) {
    throw new Error(`无法加载 ${fileName}（HTTP ${response.status}）`);
  }

  const payload = await response.json();

  if (!Array.isArray(payload)) {
    throw new Error(`${fileName} 必须是 JSON 数组。`);
  }

  return payload;
}

function hydrateStore({ students, tasks, problems, records }) {
  const normalizedStudents = [...students].sort(sortStudents);
  const normalizedTasks = [...tasks].sort(sortTasks);
  const normalizedProblems = [...problems].sort(sortProblems);

  const studentById = new Map(normalizedStudents.map((student) => [student.id, student]));
  const taskById = new Map(normalizedTasks.map((task) => [task.id, task]));
  const problemById = new Map(normalizedProblems.map((problem) => [problem.id, problem]));
  const problemsByTask = new Map(normalizedTasks.map((task) => [task.id, []]));

  for (const problem of normalizedProblems) {
    if (!problemsByTask.has(problem.taskId)) {
      problemsByTask.set(problem.taskId, []);
    }

    problemsByTask.get(problem.taskId).push(problem);
  }

  const recordMap = new Map();

  for (const record of records) {
    if (!studentById.has(record.studentId) || !problemById.has(record.problemId)) {
      continue;
    }

    recordMap.set(`${record.studentId}:${record.problemId}`, normalizeStatus(record.status));
  }

  const studentSummaryById = new Map(
    normalizedStudents.map((student) => [
      student.id,
      {
        solved: 0,
        total: normalizedProblems.length
      }
    ])
  );

  const taskProgressByStudent = new Map(
    normalizedStudents.map((student) => [
      student.id,
      new Map(
        normalizedTasks.map((task) => [
          task.id,
          {
            solved: 0,
            total: (problemsByTask.get(task.id) || []).length
          }
        ])
      )
    ])
  );

  for (const [key, status] of recordMap.entries()) {
    if (status !== 'solved') {
      continue;
    }

    const separatorIndex = key.indexOf(':');
    const studentId = key.slice(0, separatorIndex);
    const problemId = key.slice(separatorIndex + 1);
    const problem = problemById.get(problemId);

    if (!problem) {
      continue;
    }

    const studentSummary = studentSummaryById.get(studentId);
    const taskProgress = taskProgressByStudent.get(studentId)?.get(problem.taskId);

    if (studentSummary) {
      studentSummary.solved += 1;
    }

    if (taskProgress) {
      taskProgress.solved += 1;
    }
  }

  store.students = normalizedStudents;
  store.tasks = normalizedTasks;
  store.problems = normalizedProblems;
  store.taskBuckets = buildTaskBuckets(normalizedTasks);
  store.studentById = studentById;
  store.taskById = taskById;
  store.problemById = problemById;
  store.problemsByTask = problemsByTask;
  store.recordMap = recordMap;
  store.studentSummaryById = studentSummaryById;
  store.taskProgressByStudent = taskProgressByStudent;
}

export async function ensureDataLoaded() {
  if (store.loaded) {
    return store;
  }

  if (loadPromise) {
    return loadPromise;
  }

  store.loading = true;
  store.error = '';

  loadPromise = Promise.all([
    fetchJsonFile('students.json'),
    fetchJsonFile('tasks.json'),
    fetchJsonFile('problems.json'),
    fetchJsonFile('record.json')
  ])
    .then(([students, tasks, problems, records]) => {
      hydrateStore({ students, tasks, problems, records });
      store.loaded = true;
      return store;
    })
    .catch((error) => {
      resetStore();
      store.error = error instanceof Error ? error.message : '加载数据时发生未知错误。';
      throw error;
    })
    .finally(() => {
      store.loading = false;
      loadPromise = null;
    });

  return loadPromise;
}

export function useRecordsStore() {
  return store;
}

export function getTypeLabel(type) {
  return getTypeMeta(type).label;
}

export function getStudentSummary(studentId) {
  return store.studentSummaryById.get(studentId) || {
    solved: 0,
    total: store.problems.length
  };
}

export function getTaskProgress(studentId, taskId) {
  return store.taskProgressByStudent.get(studentId)?.get(taskId) || {
    solved: 0,
    total: (store.problemsByTask.get(taskId) || []).length
  };
}

export function getProblemStatus(studentId, problemId) {
  return store.recordMap.get(`${studentId}:${problemId}`) || 'unsolved';
}
