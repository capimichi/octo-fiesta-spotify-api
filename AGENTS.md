This file defines the responsibilities and capabilities of the various AI agents that contribute to this project. These agents assist in development, testing, documentation, and maintenance tasks.

## Agent Types

### opencode-agent
- **Description**: The primary conversational agent. It understands user requests, plans tasks, executes actions using available tools (like bash, read, write, glob, grep), and interacts with other specialized agents.
- **Tools**: bash, read, write, glob, grep, task, question, submit_plan, todowrite, webfetch, skill, mystatus, gemini_quota
- **Purpose**: Orchestrates the entire development workflow, from understanding user needs to delivering solutions.

### gsd-agent (General Software Development Agent)
- **Description**: A suite of specialized agents designed for various software engineering tasks, typically invoked by the `opencode-agent` via the `task` tool. These agents focus on specific phases of the development lifecycle.
- **Types**:
    - **explore**: Fast agent specialized for exploring codebases. Use this when you need to quickly find files by patterns (eg. "src/components/**/*.tsx"), search code for keywords (eg. "API endpoints"), or answer questions about the codebase (eg. "how do API endpoints work?"). When calling this agent, specify the desired thoroughness level: "quick" for basic searches, "medium" for moderate exploration, or "very thorough" for comprehensive analysis across multiple locations and naming conventions.
    - **general**: General-purpose agent for researching complex questions and executing multi-step tasks. Use this agent to execute multiple units of work in parallel.
    - **gsd-codebase-mapper**: Explores codebase and writes structured analysis documents. Spawned by map-codebase with a focus area (tech, arch, quality, concerns). Writes documents directly to reduce orchestrator context load.
    - **gsd-debugger**: Investigates bugs using scientific method, manages debug sessions, handles checkpoints. Spawned by /gsd-debug orchestrator.
    - **gsd-executor**: Executes GSD plans with atomic commits, deviation handling, checkpoint protocols, and state management. Spawned by execute-phase orchestrator or execute-plan command.
    - **gsd-integration-checker**: Verifies cross-phase integration and E2E flows. Checks that phases connect properly and user workflows complete end-to-end.
    - **gsd-nyquist-auditor**: Fills Nyquist validation gaps by generating tests and verifying coverage for phase requirements
    - **gsd-phase-researcher**: Researches how to implement a phase before planning. Produces RESEARCH.md consumed by gsd-planner. Spawned by /gsd-plan-phase orchestrator.
    - **gsd-plan-checker**: Verifies plans will achieve phase goal before execution. Goal-backward analysis of plan quality. Spawned by /gsd-plan-phase orchestrator.
    - **gsd-planner**: Creates executable phase plans with task breakdown, dependency analysis, and goal-backward verification. Spawned by /gsd-plan-phase orchestrator.
    - **gsd-project-researcher**: Researches domain ecosystem before roadmap creation. Produces files in .planning/research/ consumed during roadmap creation. Spawned by /gsd-new-project or /gsd-new-milestone orchestrators.
    - **gsd-research-synthesizer**: Synthesizes research outputs from parallel researcher agents into SUMMARY.md. Spawned by /gsd-new-project after 4 researcher agents complete.
    - **gsd-roadmapper**: Creates project roadmaps with phase breakdown, requirement mapping, success criteria derivation, and coverage validation. Spawned by /gsd-new-project orchestrator.
    - **gsd-verifier**: Verifies phase goal achievement through goal-backward analysis. Checks codebase delivers what phase promised, not just that tasks completed. Creates VERIFICATION.md report.
- **Purpose**: Handles complex, multi-step tasks autonomously, providing structured outputs and leveraging specialized knowledge.

## Collaboration Guidelines

- **Clear Communication**: Agents should clearly state their intentions, actions, and results.
- **Tool Usage**: Use the most appropriate tool for each task. Explain the use of `bash` commands that modify the filesystem.
- **Verification**: Verify changes and actions whenever possible, especially for code modifications.
- **Context Preservation**: Maintain context across interactions, especially when using specialized agents.

## How to Interact

- The `opencode-agent` will guide the overall process.
- When specialized tasks are needed, `opencode-agent` will invoke `gsd-agent` types using the `task` tool.
- Users can interact with the `opencode-agent` to provide instructions, clarify ambiguities, or request specific actions.
