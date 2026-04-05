<script setup>
import { computed, onMounted } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import TaskPanel from '../components/TaskPanel.vue';
import {
  ensureDataLoaded,
  getProblemStatus,
  getStudentSummary,
  getTaskProgress,
  useRecordsStore
} from '../lib/data';
import { formatProgress } from '../lib/metrics';

const route = useRoute();
const store = useRecordsStore();

onMounted(() => {
  ensureDataLoaded().catch(() => {});
});

const studentId = computed(() => String(route.params.id || ''));
const student = computed(() => store.studentById.get(studentId.value));
const summary = computed(() => getStudentSummary(studentId.value));

const taskEntries = computed(() =>
  store.tasks.map((task) => ({
    task,
    progress: getTaskProgress(studentId.value, task.id),
    problems: (store.problemsByTask.get(task.id) || []).map((problem) => ({
      ...problem,
      status: getProblemStatus(studentId.value, problem.id)
    }))
  }))
);
</script>

<template>
  <section class="page-head">
    <RouterLink class="back-link" :to="{ name: 'home' }">{{ '返回首页' }}</RouterLink>

    <div v-if="student" class="page-head__content">
      <p class="page-head__eyebrow">Student Detail</p>
      <h1 class="page-head__title">{{ student.name }}</h1>
      <p class="page-head__description">{{ '总完成情况：' }}{{ formatProgress(summary.solved, summary.total) }}</p>
    </div>

    <div v-else class="page-head__content">
      <p class="page-head__eyebrow">Student Detail</p>
      <h1 class="page-head__title">{{ '未找到学生' }}</h1>
      <p class="page-head__description">{{ '请返回首页确认学生 ID 是否存在。' }}</p>
    </div>
  </section>

  <section v-if="store.loading && !store.loaded" class="panel">
    {{ '正在加载学生详情，请稍候。' }}
  </section>

  <section v-else-if="store.error" class="panel panel--danger">
    {{ '数据加载失败：' }}{{ store.error }}
  </section>

  <section v-else-if="!student" class="panel">
    {{ '该学生不存在，可能是链接有误，或数据文件中尚未创建对应的学生记录。' }}
  </section>

  <template v-else>
    <section v-if="taskEntries.length === 0" class="panel">
      {{ '当前还没有任何作业块，可以先通过本地脚本补充 tasks.json 和 problems.json。' }}
    </section>

    <section v-else class="task-stack task-stack--page">
      <TaskPanel
        v-for="entry in taskEntries"
        :key="entry.task.id"
        :task="entry.task"
        :progress="entry.progress"
        :problems="entry.problems"
      />
    </section>
  </template>
</template>
