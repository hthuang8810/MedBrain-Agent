<template>
  <aside class="sidebar">
    <div class="sidebar-top">
      <div class="app-brand">
        <span class="brand-icon">🏥</span>
        <span class="brand-text">MedBrain</span>
      </div>
    </div>

    <el-button class="new-chat-btn" @click="$emit('newChat')">
      <el-icon><Plus /></el-icon>
      新对话
    </el-button>

    <div class="chat-list">
      <div
        v-for="chat in chatList"
        :key="chat.id"
        class="chat-item"
        :class="{ active: chat.id === activeId }"
        @click="$emit('selectChat', chat.id)"
      >
        <el-icon class="chat-icon"><ChatDotRound /></el-icon>
        <span class="chat-title">{{ chat.title }}</span>
      </div>
    </div>

    <div class="sidebar-bottom">
      <div class="user-info">
        <div class="user-avatar">U</div>
        <span class="user-name">{{ userName }}</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { Plus, ChatDotRound } from '@element-plus/icons-vue'

const props = defineProps({
  chatList: { type: Array, required: true },
  activeId: { type: String, required: true },
})

defineEmits(['newChat', 'selectChat'])

const userName = computed(() => {
  const id = localStorage.getItem('userId') || ''
  return id.length > 8 ? id.slice(0, 8) + '...' : id || '用户'
})
</script>

<style scoped>
.sidebar {
  width: 260px;
  height: 100vh;
  background: var(--sidebar-bg);
  color: var(--sidebar-text);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

.sidebar-top {
  padding: 18px 16px 12px;
}

.app-brand {
  display: flex;
  align-items: center;
  gap: 8px;
}

.brand-icon {
  font-size: 24px;
}

.brand-text {
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.3px;
}

.new-chat-btn {
  margin: 0 12px 12px;
  width: calc(100% - 24px);
  background: var(--sidebar-hover);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--sidebar-text);
  border-radius: var(--radius-sm);
  font-weight: 500;
}

.new-chat-btn:hover {
  background: var(--sidebar-active);
  color: #fff;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 8px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 14px;
  transition: background 0.15s;
}

.chat-item:hover {
  background: var(--sidebar-hover);
}

.chat-item.active {
  background: var(--sidebar-active);
}

.chat-icon {
  font-size: 16px;
  opacity: 0.7;
}

.chat-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-bottom {
  padding: 12px 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--avatar-user);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.user-name {
  font-size: 13px;
  opacity: 0.8;
}
</style>
