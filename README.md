# Audio_Gorilla

**Audio_Gorilla** is a multistep, multiturn dataset for fine-tuning LLMs on **voice-driven API function calling**. It bridges the gap between conversational speech transcriptions and executable API sequences.

---

## Core Components

* **12 Mock APIs**: Realistic schemas for Amazon, Spotify, YouTube, Gmail, Google Drive, Google Calendar, Simple Note, Smart Things, Tesla Fleet, X, Venmo, and CommuniLink.
* **Stateful Backends**: Persistent JSON environments populated with synthetic data to support realistic queries and state changes.
* **Testing Framework**: Comprehensive unit tests for every API function to ensure ground-truth accuracy.

---

## Dataset Features

* **Speech-to-Function**: Focuses on extracting intent/parameters from natural, vague, or conversational transcriptions.
* **Multistep Tool-Use**: Trains models to orchestrate sequences across different services (e.g., Calendar + Gmail).
* **Contextual Awareness**: Supports multiturn dialogue where subsequent commands rely on previous turn history.

---

## Data Structure

Data is located in `Prompts/Prompt.json`. 

| Field | Description | Example |
| :--- | :--- | :--- |
| **prompt** | Transcribed user instruction | "Email Dominic about the project status." |
| **tools** | Available API definitions | `["GmailApis"]` |
| **context** | User IDs or session state | `{"gmail_user": "73e6974e..."}` |
| **ground_truth** | Executable API call | `sendEmail(to='Dominic', subject='...', ...)` |

---

## Repository Map

* `Backends/`: Simulated service states and backend generation scripts.
* `Prompts/`: API JSON definitions and the fine-tuning dataset.
* `unittests/`: Functional validation for API endpoints.
