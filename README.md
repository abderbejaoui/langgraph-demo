# langgraph-demo

A minimal [LangGraph](https://langchain-ai.github.io/langgraph/) agent that answers a question by calling [Anthropic Claude](https://www.anthropic.com/) and searching the web with [Tavily](https://tavily.com/). The agent loops between a model node and a tool node until it produces a final answer, printing each step as it runs.

## Setup

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with your API keys:

```
ANTHROPIC_API_KEY=your-anthropic-key
TAVILY_API_KEY=your-tavily-key
```

> `.env` is git-ignored — never commit your real keys.

## Run

```bash
python agent.py
```

To ask a different question, edit the `question` variable near the bottom of `agent.py`.

## How it works

- **State** holds the conversation as a list of messages (`Annotated[list, add_messages]`, so new messages are appended rather than replacing history).
- The **agent** node calls Claude, which may request a Tavily search.
- The **tools** node runs the search and feeds results back to the agent.
- The loop ends once the model returns an answer with no further tool calls.
