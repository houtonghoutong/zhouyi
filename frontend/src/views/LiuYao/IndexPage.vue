<script setup lang="ts">
/**
 * 六爻占卜 - 布局容器
 */
import { RouterView } from 'vue-router'
import { useDivinationStore } from '@/stores/divination'
import { onUnmounted } from 'vue'

const store = useDivinationStore()

// 离开六爻占卜时重置状态
onUnmounted(() => {
  // 如果还没有结果，重置状态
  if (!store.result) {
    store.reset()
  }
})
</script>

<template>
  <div class="liuyao-page">
    <RouterView v-slot="{ Component }">
      <transition name="slide" mode="out-in">
        <component :is="Component" />
      </transition>
    </RouterView>
  </div>
</template>

<style scoped>
.liuyao-page {
  min-height: 100vh;
  min-height: 100dvh;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.slide-leave-to {
  opacity: 0;
  transform: translateX(-30px);
}
</style>

