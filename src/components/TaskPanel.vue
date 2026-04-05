<script setup>
import { computed, ref } from 'vue';
import {
  formatProgress,
  getProblemStatusText,
  getProblemTone,
  getProgressTone
} from '../lib/metrics';

const props = defineProps({
  task: {
    type: Object,
    required: true
  },
  progress: {
    type: Object,
    required: true
  },
  problems: {
    type: Array,
    required: true
  }
});

const isExpanded = ref(false);
const progressClassName = computed(
  () => `progress-chip--${getProgressTone(props.progress.solved, props.progress.total)}`
);

function toggleExpanded() {
  isExpanded.value = !isExpanded.value;
}
</script>

<template>
  <article class="task-panel">
    <button
      class="task-panel__summary"
      type="button"
      :aria-expanded="isExpanded"
      @click="toggleExpanded"
    >
      <div class="task-panel__copy">
        <h3 class="task-panel__title">{{ task.title }}</h3>
        <p class="task-panel__hint">
          {{ problems.length === 0 ? '当前作业块暂无题目。' : '点击展开或收起该作业块的题目列表。' }}
        </p>
      </div>

      <div class="task-panel__side">
        <span class="progress-chip" :class="progressClassName">
          {{ formatProgress(progress.solved, progress.total) }}
        </span>
        <span class="task-panel__chevron" :class="{ 'task-panel__chevron--open': isExpanded }">
          v
        </span>
      </div>
    </button>

    <transition name="expand">
      <div v-if="isExpanded" class="task-panel__details">
        <p v-if="problems.length === 0" class="empty-state empty-state--compact">
          {{ '管理员可以先在本地脚本里补充题目，再回到这里查看进度。' }}
        </p>

        <ul v-else class="problem-list">
          <li
            v-for="problem in problems"
            :key="problem.id"
            class="problem-list__item"
            :class="`problem-list__item--${getProblemTone(problem.status)}`"
          >
            <span class="problem-list__title">{{ problem.title }}</span>
            <span class="problem-list__status">{{ getProblemStatusText(problem.status) }}</span>
          </li>
        </ul>
      </div>
    </transition>
  </article>
</template>
