export const LANGGRAPH_API_URL =
  import.meta.env.VITE_LANGGRAPH_API_URL ?? 'http://127.0.0.1:2024'

// Matches the "research_agent" key in langgraph.json's `graphs` map.
export const ASSISTANT_ID = 'research_agent'
