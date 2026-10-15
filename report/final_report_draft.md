# TrendPilot — Final Project Report Draft

## 1. Project Overview
TrendPilot is a local-LLM content-planning agent built with Python, Ollama, Qwen 2.5 3B, SQLite, and Streamlit. It accepts a topic, target audience, platform, tone, and video duration and returns a structured content plan.

## 2. Agent Workflow
1. Validate user inputs.
2. Construct a prompt for the requested sections.
3. Generate structured JSON with the local Ollama model.
4. Validate required sections and attempt one repair if validation fails.
5. Optionally review the content.
6. Save JSON and Markdown files.
7. Store the task and output path in SQLite memory.
8. Return the content plan and execution status.

## 3. Tools
- Idea generator
- Hashtag generator
- Caption writer
- Reel-script generator
- Title and thumbnail-text generator
- Content reviewer
- File Saver (TXT, Markdown, JSON)
- SQLite memory

## 4. Demo Outputs
Insert screenshots of the notebook's successful demo, generated JSON/Markdown, SQLite memory, and Streamlit UI. Add examples from the five-output batch after running it.

## 5. Testing
Insert the actual results from `tests/test_results.json`. Distinguish structural validation from factual accuracy; a valid JSON structure does not prove that every statement is correct.

## 6. Failure Analysis — Complete After Testing
Document five real weak responses or failures. For each one, include: input, observed output/problem, likely cause, correction made, and whether the retest improved. Do not invent failure examples if they were not observed.

## 7. Lessons Learned — Complete Based on Your Work
Write 5–7 lessons from the actual development process, such as structured output validation, local model latency, prompt design, file persistence, memory integration, UI integration, and testing. Keep only lessons that reflect what happened in this project.

## 8. Limitations
- TrendPilot does not access live social-media trend data.
- The local model may produce generic, repetitive, or incorrect suggestions.
- Validation checks structure and required fields, not full factual correctness.
- Performance depends on the local computer and model size.

## 9. Future Improvements
- Connect a reliable trend-data source.
- Improve quality scoring and evaluation.
- Add user preferences and memory-aware personalization.
- Add stronger error handling and automated regression tests.
- Connect the Streamlit UI to the same shared agent module instead of maintaining a separate execution path.

## 10. Suggested LinkedIn Post
I’m excited to share TrendPilot, a local-LLM-powered AI content planning agent developed as part of the AIRI Team PITB AI Internship Task 2. It helps generate structured social media content plans, including ideas, captions, hashtags, short-video scripts, titles, and thumbnail text. The project uses Ollama and Qwen 2.5 3B, with SQLite memory, file export, and a local Streamlit interface. This project helped me practise structured LLM output, validation, persistent storage, and building an AI workflow end to end.

## Appendix
Add the final project structure, test report, screenshots, and five saved output examples.
