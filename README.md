# 🎫 Ticket Agent

An intelligent support ticket agent powered by **LangGraph** and **Snowflake Cortex**. This agent automatically handles customer support inquiries by evaluating priority, retrieving relevant context using semantic search, and generating helpful responses.

## ✨ Features

- **Priority Classification** – Automatically classifies incoming messages as URGENT, HIGH, MEDIUM, or LOW priority
- **Semantic Context Retrieval** – Uses Snowflake Cortex Search to find relevant past tickets and knowledge base articles
- **AI-Powered Responses** – Generates helpful, context-aware support responses using LLMs
- **Ticket Management** – Creates new tickets or updates existing conversations
- **Conversation History** – Stores all messages for audit and continuity

## 🏗️ Architecture

The agent uses a LangGraph state machine with the following workflow:

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌────────────────┐
│  START  │───▶│ Priority │───▶│ Retrieve │───▶│    Generate    │
└─────────┘    └──────────┘    └──────────┘    └───────┬────────┘
                                                       │
                                          ┌────────────┴────────────┐
                                          ▼                         ▼
                                  ┌──────────────┐         ┌──────────────┐
                                  │ Create Ticket│         │Update Ticket │
                                  └──────┬───────┘         └──────┬───────┘
                                         │                        │
                                         └──────────┬─────────────┘
                                                    ▼
                                          ┌──────────────────┐
                                          │ Store Agent Msg  │
                                          └────────┬─────────┘
                                                   ▼
                                              ┌─────────┐
                                              │   END   │
                                              └─────────┘
```

### Nodes

| Node | Description |
|------|-------------|
| `priority` | Classifies the user message priority using an LLM |
| `retrieve` | Fetches relevant context from Snowflake Cortex Search |
| `generate` | Generates a support response based on priority and context |
| `create_ticket` | Creates a new ticket in the database |
| `update_ticket` | Adds a message to an existing ticket |
| `store_agent_message` | Persists the agent's response |

## 📁 Project Structure

```
ticket_agent/
├── backend/
│   ├── agent.py              # Main agent entry point
│   ├── db/
│   │   ├── snowflake.py      # Snowflake session management
│   │   ├── zen_repo.py       # Ticket repository operations
│   │   └── tables/           # SQL table definitions
│   ├── graph/
│   │   ├── graph.py          # LangGraph workflow definition
│   │   ├── router.py         # Conditional routing logic
│   │   ├── state.py          # State schema definition
│   │   └── nodes/            # Individual graph nodes
│   └── llm/
│       └── model.py          # LLM configuration
├── scripts/
│   └── chat_with_agent.py    # CLI chat interface
├── requirements.txt
├── Makefile
└── .env.example
```

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Snowflake account with Cortex enabled
- OpenAI API key (or Snowflake Cortex LLM endpoint)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ticket_agent
   ```

2. **Create and activate a virtual environment**
   ```bash
   make venv
   source venv/bin/activate
   ```

3. **Configure environment variables**
   
   Copy the example file and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

   Required variables:
   | Variable | Description |
   |----------|-------------|
   | `SNOWFLAKE_ACCOUNT` | Your Snowflake account identifier |
   | `SNOWFLAKE_USER` | Snowflake username |
   | `SNOWFLAKE_TOKEN` | Snowflake password/token |
   | `OPENAI_API_KEY` | API key (same as SNOWFLAKE_TOKEN for Cortex) |
   | `OPENAI_BASE_URL` | Snowflake Cortex API endpoint |
   | `SNOWFLAKE_WAREHOUSE` | Compute warehouse name |
   | `SNOWFLAKE_DATABASE` | Database containing your data |
   | `SNOWFLAKE_SCHEMA` | Schema name |
   | `SNOWFLAKE_CORTEX_SEARCH_SERVICE` | Cortex Search service name |

### Running the Agent

Start the interactive chat interface:

```bash
make run_agent
```

Or run directly:
```bash
PYTHONPATH=.:backend python scripts/chat_with_agent.py
```

### Running the Frontend

Start the ticketing system UI:

```bash
streamlit run frontend/app.py
```

### Usage Example

```
Zen agent (type 'exit' to quit)

You: I can't log into my account
Agent: I understand you're having trouble logging into your account...
(ticket_id=TKT-001)

You: I tried resetting my password but it didn't work
Agent: I'm sorry the password reset didn't resolve your issue...
(ticket_id=TKT-001)

You: exit
```

## 🛠️ Technologies

- **[LangGraph](https://github.com/langchain-ai/langgraph)** – Stateful agent orchestration
- **[LangChain](https://github.com/langchain-ai/langchain)** – LLM integration
- **[Snowflake Cortex](https://www.snowflake.com/en/data-cloud/cortex/)** – Semantic search & LLM inference
- **[Snowpark](https://docs.snowflake.com/en/developer-guide/snowpark/index)** – Python connector for Snowflake

## 📄 License

This project is licensed under the MIT License.