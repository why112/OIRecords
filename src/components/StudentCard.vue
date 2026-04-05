<script setup>
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { formatProgress, getProgressTone } from '../lib/metrics';

const props = defineProps({
  student: {
    type: Object,
    required: true
  },
  summary: {
    type: Object,
    required: true
  }
});

const progressClassName = computed(
  () => `progress-chip--${getProgressTone(props.summary.solved, props.summary.total)}`
);
</script>

<template>
  <RouterLink class="student-card" :to="{ name: 'student', params: { id: student.id } }">
    <div class="student-card__meta">
      <span class="student-card__label">{{ '学生' }}</span>
      <span class="student-card__id">{{ student.id }}</span>
    </div>

    <h2 class="student-card__name">{{ student.name }}</h2>

    <div class="student-card__footer">
      <span class="student-card__caption">{{ '总完成情况' }}</span>
      <span class="progress-chip" :class="progressClassName">
        {{ formatProgress(summary.solved, summary.total) }}
      </span>
    </div>
  </RouterLink>
</template>
