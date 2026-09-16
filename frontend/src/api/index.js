import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: false, // 项目不依赖cookie，关闭以支持CORS通配符Origin
  headers: { 'Content-Type': 'application/json' },
})

// 用户名密码登录
export const login = (userName, password) =>
  api.post('/login', { userName, password })

// 用户注册
export const register = (userName, password, email) =>
  api.post('/register', { userName, password, email })

// 发送邮箱验证码
export const sendCode = (email) =>
  api.post('/send_code', { email })

// 验证码登录
export const codeVerify = (email, code) =>
  api.post('/code_verify', { email, code })

// 语音识别
export const speechToText = (formData) =>
  api.post('/speech_to_text', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })

/**
 * 流式聊天 — 使用 fetch + ReadableStream 消费 SSE
 * 返回一个异步生成器，每次 yield 一个 token 字符串
 */
export async function* chatStream(questions, sessionId) {
  const res = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ questions, sessionId }),
  })

  if (!res.ok) {
    throw new Error(`HTTP error: ${res.status}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() // 保留未完成的行

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      // 只把「解析失败」当成非 JSON 行忽略。
      // 后端下发的 error 事件必须能抛出去 —— 之前 throw 和这个 catch 在同一个
      // try 里，被下面的 catch 吞掉，服务端报错会静默变成一条空回复。
      let data
      try {
        data = JSON.parse(line.slice(6))
      } catch {
        continue
      }
      if (data.done) return
      if (data.error) throw new Error(data.error)
      if (data.token) yield { type: 'token', text: data.token }
      else if (data.tool) yield { type: 'tool', name: data.tool }
    }
  }
}
