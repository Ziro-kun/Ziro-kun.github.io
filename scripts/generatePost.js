import fs from "fs";
import path from "path";
import { generateAndSavePost } from "./lib/post.js";

const INPUT_FILE = path.resolve("input.txt");
const STYLE_FILE = path.resolve("style.md");

if (!fs.existsSync(INPUT_FILE)) {
  console.error("input.txt 파일이 없습니다.");
  process.exit(1);
}

const input = fs.readFileSync(INPUT_FILE, "utf-8").trim();
const style = fs.existsSync(STYLE_FILE)
  ? fs.readFileSync(STYLE_FILE, "utf-8")
  : "";

if (!input) {
  console.log("input.txt가 비어있습니다. 스킵합니다.");
  process.exit(0);
}

await generateAndSavePost(input, style);
