<script setup>
import { computed, onMounted } from 'vue';
import StudentCard from '../components/StudentCard.vue';
import { ensureDataLoaded, getStudentSummary, useRecordsStore } from '../lib/data';

const store = useRecordsStore();

onMounted(() => {
  ensureDataLoaded().catch(() => {});
});

const students = computed(() =>
  store.students.map((student) => ({
    ...student,
    summary: getStudentSummary(student.id)
  }))
);

const headlineStats = computed(() => [
  { label: '学生人数', value: store.students.length },
  { label: '作业块数量', value: store.tasks.length },
  { label: '题目总数', value: store.problems.length }
]);
</script>

<template>
  <section class="hero">
    <div class="hero__copy">
      <p class="hero__eyebrow">Overview</p>
      <h1 class="hero__title">{{ '训练营作业总览' }}</h1>
    </div>

    <div class="hero__stats">
      <article v-for="item in headlineStats" :key="item.label" class="hero-stat">
        <span class="hero-stat__label">{{ item.label }}</span>
        <strong class="hero-stat__value">{{ item.value }}</strong>
      </article>
    </div>
  </section>

  <section v-if="store.loading && !store.loaded" class="panel">
    {{ '正在加载数据，请稍候。' }}
  </section>

  <section v-else-if="store.error" class="panel panel--danger">
    {{ '数据加载失败：' }}{{ store.error }}
  </section>

  <section v-else-if="students.length === 0" class="panel">
    {{ '当前还没有学生数据，可以先用本地脚本添加学生、作业块和题目。' }}
  </section>

  <section v-else class="student-grid">
    <StudentCard
      v-for="student in students"
      :key="student.id"
      :student="student"
      :summary="student.summary"
    />
  </section>
</template>
