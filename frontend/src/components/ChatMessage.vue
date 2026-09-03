<template>
  <div class="chat-message" :class="message.role">
    <!-- 头像 -->
    <div class="avatar" :class="message.role">
      <template v-if="message.role === 'user'">U</template>
      <template v-else>🏥</template>
    </div>

    <!-- 气泡 -->
    <div class="bubble-wrap">
      <div
        v-if="message.role === 'assistant'"
        class="bubble markdown-body"
        v-html="renderedContent"
      ></div>
      <div v-else class="bubble">{{ message.content }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { renderMarkdown } from '@/utils/markdown'

const props = defineProps({
  message: {
    type: Object,
    required: true,
  },
})

const renderedContent = computed(() => {
  if (props.message.role === 'assistant') {
    return renderMarkdown(props.message.content)
  }
  return props.message.content
})
</script>

<style scoped>
.chat-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin: 16px 0;
}

.chat-message.user {
  flex-direction: row-reverse;
}

/* 头像 */
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
  color: #fff;
}

.avatar.user {
  background: var(--avatar-user);
}

.avatar.assistant {
  background: var(--avatar-ai);
  font-size: 18px;
}

/* 气泡 */
.bubble-wrap {
  max-width: calc(100% - 60px);
}

.bubble {
  display: inline-block;
  padding: 10px 18px;
  border-radius: var(--radius-md);
  word-break: break-word;
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 15px;
}

.user .bubble {
  background: var(--user-bubble);
  color: var(--text-on-primary);
  border-bottom-right-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}

.assistant .bubble {
  background: var(--ai-bubble);
  color: var(--text-primary);
  border: 1px solid var(--ai-bubble-border);
  border-bottom-left-radius: var(--radius-sm);
  box-shadow: var(--shadow-sm);
}
</style>
