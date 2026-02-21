# Human Understanding Research Engine

A multi-agent project for building unbiased, evidence-based understanding of a user’s interests and skills by analyzing their projects and conversational artifacts.

## Overview

This project studies user behavior across:

- GitHub projects (repositories, PR history, issue context, code patterns)
- Chatbot export logs (e.g., ChatGPT conversations)
- YouTube interactions (watch history, comments, transcripts, notes)

The system converts each source into structured observations, maps them to skills/interests, runs AI agents to generate hypotheses, and then reaches consensus before presenting a profile of the user.

## Goals

1. Build a durable model of a user’s profile from behavioral data.
2. Extract likely interests and skills from multiple evidence channels.
3. Reduce bias by separating evidence collection, interpretation, and arbitration.
4. Return a clear, explainable summary for each user interaction.
5. Support conversational follow-up that refines understanding over time.

## High-level Architecture

```text
Sources -> Ingestion -> Normalization -> Skill/Interest Extraction ->
Agent Analysis -> Weighted Consensus -> Profile Hypotheses -> User Chat Interface
```

## Components

- `Ingestion`
  - Pulls GitHub project artifacts.
  - Imports ChatGPT conversation exports (JSON/HTML/text).
  - Imports YouTube activity artifacts (metadata/transcripts/notes).

- `Normalization`
  - Cleans identifiers and timestamps.
  - Removes duplicates.
  - Maps project names, topics, and artifacts into a shared canonical schema.

- `Extraction Agents`
  - `Project-Agent`: identifies skills, tools, concepts from repos and activity.
  - `Communication-Agent`: extracts preferences, motivations, values from chats/videos.
  - `Behavior-Agent`: detects consistency patterns and frequency signals.

- `Consensus Engine`
  - Multiple hypothesis agents each propose skill/interest probabilities.
  - A neutral `Arbitrator-Agent` aggregates signals and reconciles conflicts.
  - Optional `Devil’s Advocate` run to stress test for bias.

- `Profile Builder`
  - Produces ranked skill/interests lists with confidence scores.
  - Stores uncertainty and evidence references.

- `Dialogue Layer`
  - Generates neutral follow-up questions to validate hypotheses.
  - Updates profile with confirmed/updated evidence after each interaction.

## Data Model (concept)

- `User`
- `SourceArtifact`
- `Project`
- `ConversationSnippet`
- `ObservedSkill`
- `ObservedInterest`
- `Hypothesis`
- `Evidence`
- `ConfidenceScore`
- `BiasFlag`

## Bias and Accuracy Principles

- Evidence-first: every claim links to artifact snippets.
- Neutral prompting: avoid leading language in follow-up conversations.
- Disagreement visibility: show when agents disagree and why.
- Confidence-aware: every inference includes confidence + rationale.
- Continuous revision: user correction is treated as a first-class signal.

## Example Output

- `Top Skills`: [Skill, evidence count, confidence, recency trend]
- `Top Interests`: [Interest, evidence confidence, supporting sources]
- `Hypotheses`: ranked with risk tags (`high-confidence`, `weak`, `needs-validation`)
- `Conversation Prompts`: next unbiased questions to clarify ambiguous signals

## Setup (local)

1. Install dependencies
2. Configure API keys for source providers and LLM services
3. Run ingestion jobs for:
   - GitHub export
   - Chat export
   - YouTube data
4. Start the agent pipeline
5. Review consensus results and launch follow-up conversation

## Suggested File Structure

```text
/src
  /ingestion
  /normalize
  /agents
  /consensus
  /profiles
  /conversation
  /api
/config
/data
/models
/tests
```

## Minimal API Surface

- `POST /ingest/github`
- `POST /ingest/chat`
- `POST /ingest/youtube`
- `GET /profile/{userId}`
- `POST /conversation/{userId}/next-question`
- `POST /profile/{userId}/feedback`

## Privacy and Compliance

- Store raw artifacts separately from derived profiles.
- Hash and minimize PII in logs.
- Add opt-in/opt-out controls for each source.
- Provide user-visible deletion and correction flows.
- Keep export records auditable for transparency.

## Roadmap

- Add more sources: resumes, LinkedIn, project management tools.
- Add skill ontology versioning and taxonomy expansion.
- Improve multi-lingual extraction.
- Add uncertainty calibration and human-review mode.

## Contributing

- Follow a bias-aware review checklist for every agent prompt change.
- Add tests for consensus edge cases and contradictory evidence.
- Keep prompts versioned and auditable.
- Document every heuristic that affects scoring.

## License

TBD
