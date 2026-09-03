<template>
  <div class="chat-message" :class="message.role">
    <!-- AI 头像 -->
    <div v-if="message.role === 'assistant'" class="avatar assistant">
      🤖
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
  margin: 20px 0;
}

.chat-message.user {
  justify-content: flex-end;
}

/* AI 头像 */
.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.avatar.assistant {
  background: #eef1f4;
}

/* 气泡 */
.bubble-wrap {
  max-width: 72%;
}

.bubble {
  display: inline-block;
  padding: 12px 18px;
  border-radius: 16px;
  word-break: break-word;
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 15px;
}

/* 用户气泡（浅绿色，右对齐） */
.user .bubble {
  background: #e9f6ef;
  color: #238a5f;
  border-bottom-right-radius: 4px;
}

/* AI 气泡（白色，左对齐） */
.assistant .bubble {
  background: #ffffff;
  color: #2f3a48;
  border: 1px solid #eef1f4;
  border-bottom-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}
</style>
