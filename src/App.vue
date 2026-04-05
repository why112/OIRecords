<script setup>
import { RouterLink, RouterView } from 'vue-router';
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <RouterLink class="brand" :to="{ name: 'home' }">
        <span class="brand__eyebrow">Algorithm Training Camp</span>
        <span class="brand__title">作业完成情况追踪</span>
      </RouterLink>
    </header>

    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>
