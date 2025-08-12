# Code Writer with Human Feedback

This project demonstrates an agentic AI workflow for collaborative code generation using the Society of Mind architecture and a human-in-the-loop approach. It leverages multiple AI agents for planning, coding, and reviewing, with a user proxy agent for human feedback and approval.

## Features

- **Society of Mind Agent:** Coordinates a team of specialized agents (planner, coder, reviewer) to solve coding tasks.
- **Human Proxy Agent:** Allows a human user to interact, provide feedback, and approve solutions.
- **RoundRobinGroupChat:** Manages agent interactions and turn-taking.
- **OpenAI Model Integration:** Uses GPT-based models for agent intelligence.

## How It Works

1. The user submits a coding request.
2. The planner agent breaks down the request into actionable steps.
3. The coder agent implements the solution.
4. The reviewer agent checks code quality and correctness.
5. The human proxy agent can provide feedback or approve the solution.
6. The process terminates when the reviewer or human proxy responds with `APPROVE`.

## Usage

1. Set your OpenAI API key in the code or via environment variable.

2. Run the notebook `Code writer with human feedback.ipynb` in Jupyter or VS Code.

3. Follow the prompts in the console to interact as the human proxy.

## Example Task

The default task is:
> Write a Python function that takes two numbers and returns their sum. Include one test case.

The output demonstrates the Human User providing a feedback to incorporate additional functionality (function to multiply two numbers).
Agent gets human feedback and incorporates additional functionality, before the user says 'APPROVE' to complete the run
