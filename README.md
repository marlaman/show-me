# Show-Me: A Visual and Transparent Reasoning Agent

Show-Me is an open-source application designed to provide a visual and transparent alternative to traditional Large Language Model (LLM) interactions. It breaks down complex questions into a series of reasoned sub-tasks, allowing users to understand the LLM's step-by-step thought process.  The application uses LangChain to interact with LLMs and visualizes the reasoning process using a dynamic graph interface.

## Demo

https://x.com/i/status/1838590157265539307

## Key Features

* **Self-Healing Reasoning:** The system iteratively refines its answers based on automated checks, improving accuracy and demonstrating a form of "self-healing" behavior.
* **Visual Reasoning Graph:**  Provides a dynamic graph visualization of the LLM's reasoning process, making it transparent and understandable.
* **Task Decomposition:** Breaks down complex questions into smaller, more manageable sub-tasks, facilitating more accurate and efficient problem-solving.
* **Code Generation and Execution (Limited):**  Can generate and execute basic Python Pandas code for data manipulation and analysis tasks within specific contexts.  (Further code execution capabilities are a planned feature).
* **Software Reasoning (Experimental):** Includes an experimental mode (`/software` route) designed to handle software-related reasoning tasks, showcasing the framework's adaptability to different domains.
* **Interactive Chat Interface:**  Allows users to ask questions and receive answers in a conversational format.
* **Real-time Updates:** Uses SocketIO to provide real-time updates to the visualization graph as the LLM processes the question.


## Architecture

Show-Me consists of two main components:

1. **Frontend (React):**  Built using React, React Flow, Material UI, and Framer Motion.  Responsible for:
    * **User Interface:** Presents the chat interface, question input area, and the reasoning graph visualization.
    * **User Interaction:** Handles user input, submits questions to the backend, and manages the display of chat messages.
    * **Graph Rendering:** Dynamically renders the reasoning graph based on real-time updates from the backend.
    * **Component Breakdown:**
        * **`src/App.js`:** The main application component.  Handles routing and renders either the general reasoning or software reasoning interface.
        * **`src/SoftwareAgent.js`:**  Renders the interface for software-related questions.
        * **`src/components/ImageNode.js`:**  Renders image nodes in the graph (currently not actively used, but the infrastructure is present).
        * **`src/components/DisplayNode.js`:** Displays text-based answers to sub-tasks and the final answer.
        * **`src/components/CodeAnswerNode.js`:** Displays code-based answers from the Python interpreter.
        * **`src/components/TextUpdaterNode.js`:** Represents sub-tasks in the graph, displaying the task description.
        * `src/components/MainTaskNode.js`, `src/components/SubTaskNode.js`, `src/components/TestNode.js`: Specialized node components to visually distinguish between different task types.
        * **`src/Devtools.js`:**  Provides developer tools, including a change logger for debugging React Flow.
        * **`src/components/QuestionBar.js`:** (Not currently used but could be implemented) A component for a dedicated question input area.
        * **`src/components/ui/Card.js`, `src/components/ui/Input.js`:**  Basic UI components for styling.


2. **Backend (Flask):**  Built using Flask, Flask-SocketIO, and Flask-CORS.  Responsible for:
    * **API Endpoints:**  Provides API endpoints for receiving questions and sending responses.
    * **LLM Interaction:**  Uses LangChain to interact with the `gpt-4o-mini` LLM. Implements the Reasoning, Refinement, and Update (RRU) algorithm.
    * **Task Complexity Analysis:**  Evaluates the complexity of a task to determine if it needs further decomposition.
    * **Task Generation:** Generates sub-tasks based on the main question and automated checks.
    * **Task Ordering:**  Orders sub-tasks logically to mimic human problem-solving.
    * **Answer Aggregation:** Combines the answers from sub-tasks to form the final answer.
    * **Answer Checking:** Generates checks to validate the accuracy of answers.
    * **Answer Fixing:**  Refines answers that fail the checks using feedback from the LLM.
    * **Answer Shortening:**  Concisely presents the final answer.
    * **SocketIO Communication:**  Sends real-time updates about the reasoning process to the frontend using SocketIO.
    * **File Breakdown:**
        * **`backend/app.py`:**  The main Flask application file.  Handles routing, SocketIO connections, and API requests.
        * **`backend/llm_stuff.py`:**  Contains the core LangChain logic for general reasoning tasks.
        * **`backend/software_llm_stuff.py`:** Contains similar LangChain logic for software-related reasoning tasks.



## Reasoning, Refinement, and Update (RRU) Algorithm

The backend uses the RRU algorithm to process questions:

1. **Reasoning/Decomposition:** The LLM assesses the complexity of the task.  If complex, it is broken down into sub-tasks.
2. **LLM Interaction:**  The LLM generates answers for each sub-task (or the main task if it's not decomposed). Code generation and execution are handled for Python-related sub-tasks.
3. **Refinement (Self-Healing):** The system automatically generates checks for each answer. If an answer fails a check, the LLM is used to refine the answer based on the failed check. This process repeats until the answer passes all checks or a retry limit is reached.
4. **Update/Aggregation:** Results of sub-tasks are aggregated.  The backend sends updates to the frontend via SocketIO throughout the process, allowing for dynamic visualization of the reasoning steps.


## Installation and Setup

1. **Clone the Repository:** `git clone [repository url]`
2. **Backend Setup:**
    * `cd backend`
    * `python3 -m venv .venv`
    * `source .venv/bin/activate`
    * `pip install -r requirements.txt`
    * Create a `.env` file and add your OpenAI API Key: `OPENAI_API_KEY=[your key]`
3. **Frontend Setup:**
    * `cd ..` (go to project root)
    * `npm install` (or `yarn install`)
4. **Run the Application:**
    * **Backend:**  `python app.py` (or `flask run`) in the `backend` directory.
    * **Frontend:** `npm start` (or `yarn start`) in the project root directory.


## Future Work

* **Enhanced Code Execution:** Expand code generation and execution capabilities beyond basic Python Pandas.
* **Improved Visualization:**  Refine the graph layout and add more interactive elements.
* **Pluggable LLMs:** Allow users to select different LLMs for greater flexibility.
* **More Robust Checking:**  Develop more sophisticated and context-aware answer checking mechanisms.
* **User Authentication and Data Persistence:**  Add user accounts and allow users to save their reasoning graphs.


## Contributing

Open a Github issue please.

## License

Unknown
