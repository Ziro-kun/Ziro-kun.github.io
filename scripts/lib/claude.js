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
  // frontmatter 시작(---)이전의 모든 내용 제거 (코드펜스, 설명문 등)
  const frontmatterStart = text.indexOf("---");
  if (frontmatterStart > 0) {
    text = text.slice(frontmatterStart);
  }
  // 닫는 코드펜스 제거
  text = text.replace(/\n?```\s*$/i, "");
  return text.trim();
}
