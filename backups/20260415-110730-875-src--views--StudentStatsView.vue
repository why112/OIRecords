<script setup>
import { computed, onMounted, ref } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import {
  ensureDataLoaded,
  getStudentSummary,
  getTaskProgress,
  useRecordsStore
} from '../lib/data';
import { formatProgress } from '../lib/metrics';

const CHART_OPTIONS = [
  { value: 'bar', label: '\u67f1\u72b6\u56fe' },
  { value: 'pie', label: '\u997c\u56fe' }
];

const METRIC_OPTIONS = [
  { value: 'count', label: '\u5b8c\u6210\u6570\u91cf' },
  { value: 'ratio', label: '\u5b8c\u6210\u6bd4\u4f8b' }
];

const PALETTE = ['#6f94c6', '#d3b483', '#7bad8e', '#d88770', '#7d8fd6', '#b89bd9', '#5aa6a6', '#c9a257', '#7ca65d', '#cb7c9f'];

const TEXT = {
  backToStudent: '\u8fd4\u56de\u5b66\u751f\u8be6\u60c5',
  titleSuffix: '\u7684\u5b8c\u6210\u7edf\u8ba1',
  pageSummary:
    '\u53ef\u4ee5\u5728\u67f1\u72b6\u56fe\u548c\u997c\u56fe\u4e4b\u95f4\u5207\u6362\uff0c\u4e5f\u53ef\u4ee5\u5207\u6362\u6210\u201c\u5b8c\u6210\u6570\u91cf\u201d\u6216\u201c\u5b8c\u6210\u6bd4\u4f8b\u201d\u3002',
  studentMissing: '\u672a\u627e\u5230\u5b66\u751f',
  studentMissingHint:
    '\u8bf7\u8fd4\u56de\u5b66\u751f\u8be6\u60c5\u9875\u6216\u9996\u9875\u68c0\u67e5\u94fe\u63a5\u3002',
  loading: '\u6b63\u5728\u52a0\u8f7d\u7edf\u8ba1\u6570\u636e\uff0c\u8bf7\u7a0d\u5019\u3002',
  loadFailed: '\u6570\u636e\u52a0\u8f7d\u5931\u8d25\uff1a',
  summaryTaskCount: '\u6709\u9898\u9898\u5355',
  summarySolved: '\u5df2\u5b8c\u6210\u9898\u76ee',
  summaryRate: '\u603b\u5b8c\u6210\u7387',
  summaryFinishedTasks: '\u5df2\u5168\u90e8\u5b8c\u6210\u9898\u5355',
  chartGroup: '\u56fe\u8868\u7c7b\u578b',
  metricGroup: '\u7edf\u8ba1\u6307\u6807',
  chartHeading: '\u9898\u5355\u7edf\u8ba1\u89c6\u56fe',
  chartSubCount: '\u5f53\u524d\u4ee5\u6bcf\u4e2a\u9898\u5355\u7684\u5df2\u5b8c\u6210\u9898\u6570\u4f5c\u4e3a\u5c55\u793a\u6307\u6807\u3002',
  chartSubRatio: '\u5f53\u524d\u4ee5\u6bcf\u4e2a\u9898\u5355\u7684\u5b8c\u6210\u6bd4\u4f8b\u4f5c\u4e3a\u5c55\u793a\u6307\u6807\u3002',
  detailHeading: '\u9898\u5355\u660e\u7ec6',
  detailHint:
    '\u4f60\u53ef\u4ee5\u5207\u6362\u56fe\u8868\u7c7b\u578b\uff0c\u4f46\u4e0b\u9762\u7684\u9898\u5355\u6570\u636e\u4f1a\u59cb\u7ec8\u4fdd\u6301\u540c\u6b65\u3002',
  shareLabel: '\u5728\u5f53\u524d\u56fe\u8868\u4e2d\u5360\u6bd4',
  emptyPie: '\u5f53\u524d\u6ca1\u6709\u53ef\u7528\u4e8e\u751f\u6210\u997c\u56fe\u7684\u6570\u636e\u3002',
  taskCountSuffix: '\u9898',
  noProblemSet: '\u6682\u65e0\u9898\u76ee'
};

const percentFormatter = new Intl.NumberFormat('zh-Hans-CN', {
  style: 'percent',
  maximumFractionDigits: 1
});

const route = useRoute();
const store = useRecordsStore();

const chartType = ref('bar');
const metricType = ref('count');

onMounted(() => {
  ensureDataLoaded().catch(() => {});
});

const studentId = computed(() => String(route.params.id || ''));
const student = computed(() => store.studentById.get(studentId.value));
const summary = computed(() => getStudentSummary(studentId.value));
const overallRate = computed(() =>
  summary.value.total ? summary.value.solved / summary.value.total : 0
);

function formatPercent(value) {
  return percentFormatter.format(Number.isFinite(value) ? value : 0);
}

const taskStats = computed(() =>
  store.tasks.map((task, index) => {
    const progress = getTaskProgress(studentId.value, task.id);
    const ratio = progress.total ? progress.solved / progress.total : 0;

    return {
      id: task.id,
      title: task.title,
      solved: progress.solved,
      total: progress.total,
      ratio,
      color: PALETTE[index % PALETTE.length]
    };
  })
);

const taskSetsWithProblems = computed(
  () => taskStats.value.filter((entry) => entry.total > 0).length
);

const finishedTaskSets = computed(
  () => taskStats.value.filter((entry) => entry.total > 0 && entry.solved === entry.total).length
);

const chartEntries = computed(() =>
  taskStats.value.map((entry) => {
    const metricValue = metricType.value === 'count' ? entry.solved : entry.ratio;

    return {
      ...entry,
      metricValue,
      metricLabel:
        metricType.value === 'count'
          ? `${entry.solved} ${TEXT.taskCountSuffix}`
          : formatPercent(entry.ratio),
      progressLabel:
        entry.total > 0
          ? `${formatProgress(entry.solved, entry.total)} | ${formatPercent(entry.ratio)}`
          : TEXT.noProblemSet
    };
  })
);

const maxMetricValue = computed(() =>
  Math.max(1, ...chartEntries.value.map((entry) => entry.metricValue))
);

const barEntries = computed(() =>
  chartEntries.value.map((entry) => {
    if (entry.metricValue <= 0) {
      return {
        ...entry,
        barWidth: '0%'
      };
    }

    const width = (entry.metricValue / maxMetricValue.value) * 100;
    return {
      ...entry,
      barWidth: `${Math.max(6, width).toFixed(2)}%`
    };
  })
);

const pieEntries = computed(() => {
  const positiveEntries = chartEntries.value.filter((entry) => entry.metricValue > 0);
  const totalValue = positiveEntries.reduce((sum, entry) => sum + entry.metricValue, 0);

  if (!positiveEntries.length || totalValue <= 0) {
    return [];
  }

  return positiveEntries.map((entry) => ({
    ...entry,
    share: entry.metricValue / totalValue
  }));
});

const pieStyle = computed(() => {
  if (!pieEntries.value.length) {
    return {};
  }

  let cursor = 0;
  const slices = pieEntries.value.map((entry) => {
    const start = cursor;
    cursor += entry.share * 100;
    return `${entry.color} ${start.toFixed(2)}% ${cursor.toFixed(2)}%`;
  });

  return {
    background: `conic-gradient(${slices.join(', ')})`
  };
});

const activeChartLabel = computed(
  () => CHART_OPTIONS.find((option) => option.value === chartType.value)?.label || CHART_OPTIONS[0].label
);

const activeMetricLabel = computed(
  () =>
    METRIC_OPTIONS.find((option) => option.value === metricType.value)?.label ||
    METRIC_OPTIONS[0].label
);

const chartDescription = computed(() =>
  metricType.value === 'count' ? TEXT.chartSubCount : TEXT.chartSubRatio
);

const pieCenterValue = computed(() =>
  metricType.value === 'count'
    ? `${summary.value.solved} ${TEXT.taskCountSuffix}`
    : formatPercent(overallRate.value)
);
</script>

<template>
  <section class="page-head">
    <div class="page-head__actions">
      <RouterLink class="back-link" :to="{ name: 'student', params: { id: studentId } }">
        {{ TEXT.backToStudent }}
      </RouterLink>
    </div>

    <div v-if="student" class="page-head__content">
      <p class="page-head__eyebrow">Student Analytics</p>
      <h1 class="page-head__title">{{ student.name }}{{ TEXT.titleSuffix }}</h1>
      <p class="page-head__description">{{ TEXT.pageSummary }}</p>
    </div>

    <div v-else class="page-head__content">
      <p class="page-head__eyebrow">Student Analytics</p>
      <h1 class="page-head__title">{{ TEXT.studentMissing }}</h1>
      <p class="page-head__description">{{ TEXT.studentMissingHint }}</p>
    </div>
  </section>

  <section v-if="store.loading && !store.loaded" class="panel">
    {{ TEXT.loading }}
  </section>

  <section v-else-if="store.error" class="panel panel--danger">
    {{ TEXT.loadFailed }}{{ store.error }}
  </section>

  <section v-else-if="!student" class="panel">
    {{ TEXT.studentMissingHint }}
  </section>

  <template v-else>
    <section class="hero__stats stats-summary-grid">
      <article class="hero-stat">
        <span class="hero-stat__label">{{ TEXT.summaryTaskCount }}</span>
        <strong class="hero-stat__value">{{ taskSetsWithProblems }}</strong>
      </article>
      <article class="hero-stat">
        <span class="hero-stat__label">{{ TEXT.summarySolved }}</span>
        <strong class="hero-stat__value">{{ formatProgress(summary.solved, summary.total) }}</strong>
      </article>
      <article class="hero-stat">
        <span class="hero-stat__label">{{ TEXT.summaryRate }}</span>
        <strong class="hero-stat__value">{{ formatPercent(overallRate) }}</strong>
      </article>
      <article class="hero-stat">
        <span class="hero-stat__label">{{ TEXT.summaryFinishedTasks }}</span>
        <strong class="hero-stat__value">{{ finishedTaskSets }}</strong>
      </article>
    </section>

    <section class="stats-toolbar">
      <article class="stats-control-group">
        <span class="stats-control-group__label">{{ TEXT.chartGroup }}</span>
        <div class="stats-control-group__options">
          <button
            v-for="option in CHART_OPTIONS"
            :key="option.value"
            class="toggle-chip"
            :class="{ 'toggle-chip--active': chartType === option.value }"
            type="button"
            :aria-pressed="chartType === option.value"
            @click="chartType = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </article>

      <article class="stats-control-group">
        <span class="stats-control-group__label">{{ TEXT.metricGroup }}</span>
        <div class="stats-control-group__options">
          <button
            v-for="option in METRIC_OPTIONS"
            :key="option.value"
            class="toggle-chip"
            :class="{ 'toggle-chip--active': metricType === option.value }"
            type="button"
            :aria-pressed="metricType === option.value"
            @click="metricType = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </article>
    </section>

    <section class="stats-grid">
      <article class="stats-panel stats-panel--chart">
        <div class="stats-panel__header">
          <div>
            <p class="stats-panel__eyebrow">Analytics</p>
            <h2 class="stats-panel__title">{{ TEXT.chartHeading }}</h2>
          </div>
          <div class="stats-panel__badge">{{ activeChartLabel }} / {{ activeMetricLabel }}</div>
        </div>

        <p class="stats-panel__hint">{{ chartDescription }}</p>

        <div v-if="chartType === 'bar'" class="bar-chart">
          <article v-for="entry in barEntries" :key="entry.id" class="bar-chart__row">
            <div class="bar-chart__head">
              <div class="bar-chart__copy">
                <strong class="bar-chart__title">{{ entry.title }}</strong>
                <span class="bar-chart__meta">{{ entry.progressLabel }}</span>
              </div>
              <strong class="bar-chart__value">{{ entry.metricLabel }}</strong>
            </div>
            <div class="bar-chart__track">
              <div
                class="bar-chart__fill"
                :style="{ width: entry.barWidth, background: entry.color }"
              ></div>
            </div>
          </article>
        </div>

        <div v-else-if="pieEntries.length" class="donut-chart">
          <div class="donut-chart__ring" :style="pieStyle">
            <div class="donut-chart__center">
              <strong class="donut-chart__center-value">{{ pieCenterValue }}</strong>
              <span class="donut-chart__center-label">{{ activeMetricLabel }}</span>
            </div>
          </div>

          <div class="donut-chart__legend">
            <article v-for="entry in pieEntries" :key="entry.id" class="chart-legend__item">
              <span class="chart-legend__swatch" :style="{ background: entry.color }"></span>
              <div class="chart-legend__copy">
                <strong class="chart-legend__title">{{ entry.title }}</strong>
                <span class="chart-legend__meta">
                  {{ entry.metricLabel }} ? {{ TEXT.shareLabel }} {{ formatPercent(entry.share) }}
                </span>
              </div>
            </article>
          </div>
        </div>

        <section v-else class="panel stats-panel__empty">
          {{ TEXT.emptyPie }}
        </section>
      </article>

      <article class="stats-panel stats-panel--detail">
        <div class="stats-panel__header">
          <div>
            <p class="stats-panel__eyebrow">Detail</p>
            <h2 class="stats-panel__title">{{ TEXT.detailHeading }}</h2>
          </div>
        </div>

        <p class="stats-panel__hint">{{ TEXT.detailHint }}</p>

        <div class="stats-detail-list">
          <article v-for="entry in chartEntries" :key="entry.id" class="stats-detail-card">
            <span class="stats-detail-card__swatch" :style="{ background: entry.color }"></span>
            <div class="stats-detail-card__main">
              <strong class="stats-detail-card__title">{{ entry.title }}</strong>
              <span class="stats-detail-card__meta">
                {{ entry.total > 0 ? formatProgress(entry.solved, entry.total) : TEXT.noProblemSet }}
              </span>
            </div>
            <div class="stats-detail-card__metrics">
              <strong>{{ entry.solved }} / {{ entry.total }}</strong>
              <span>{{ formatPercent(entry.ratio) }}</span>
            </div>
          </article>
        </div>
      </article>
    </section>
  </template>
</template>
