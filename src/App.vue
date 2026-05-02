<script setup>
import { RouterLink, RouterView } from 'vue-router';
import { ref } from 'vue';

const NOTICE_DISMISS_KEY = 'newProjectNoticeDismissed';

const isNoticeVisible = ref(window.localStorage.getItem(NOTICE_DISMISS_KEY) !== 'true');

function dismissNotice() {
  isNoticeVisible.value = false;
  window.localStorage.setItem(NOTICE_DISMISS_KEY, 'true');
}
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

    <aside v-if="isNoticeVisible" class="notice-float" aria-label="新版平台通知" aria-live="polite">
      <button class="notice-float__close" type="button" aria-label="关闭通知" @click="dismissNotice">
        ×
      </button>

      <p class="notice-float__eyebrow">新版平台通知</p>
      <h2 class="notice-float__title">学习平台已更新</h2>

      <div class="notice-float__content">
        <p>
          新项目已经部署到云服务器，请使用
          <a href="http://47.116.19.8" target="_blank" rel="noreferrer">http://47.116.19.8</a>
          访问。
        </p>
        <p>
          注意一定是 <code>http</code>，不是 <code>https</code>。建议尽量使用 Edge 浏览器访问；
          Chrome / 谷歌浏览器可能会自动强制跳转为 <code>https</code>，导致无法正常打开。
        </p>
      </div>

      <dl class="notice-float__list">
        <div>
          <dt>登录账号</dt>
          <dd>自己的学号，开头的 <code>S</code> 必须大写</dd>
        </div>
        <div>
          <dt>默认密码</dt>
          <dd><code>Aa123456</code></dd>
        </div>
      </dl>

      <p class="notice-float__warning">首次登录后，请及时修改默认密码。</p>
    </aside>
  </div>
</template>
