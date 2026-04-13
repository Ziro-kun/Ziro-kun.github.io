import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

export async function askClaude(prompt, { maxTokens = 4000, temperature = 0.8 } = {}) {
  const message = await client.messages.create({
    model: "claude-haiku-4-5-20251001",
    max_tokens: maxTokens,
    temperature,
    messages: [{ role: "user", content: prompt }],
  });

  let text = message.content[0].text;
  // 마크다운 코드펜스 제거 (```yaml, ```markdown, ```md 등 모두 처리)
  text = text.replace(/^```[a-z]*\n?/i, "").replace(/\n?```$/i, "");
  return text.trim();
}
