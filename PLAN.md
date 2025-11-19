# Poker Bot Project Plan

This document outlines a roadmap for building an online poker bot that can read game state information, reason about optimal actions, and execute plays autonomously. The focus is on modularity, observability, and safety so that individual subsystems can be improved independently.

## 1. Goals & Success Criteria
1. **Functional play:** Bot reliably reads state from a supported poker client, decides on actions, and issues those actions within latency targets (<300 ms from opponent action to our response).
2. **Poker intelligence:** Underlying decision logic is competitive against reasonable human opponents in NLHE six-max cash games and designed for future variants.
3. **Safety & control:** Includes guardrails such as max-loss limits, opt-in confirmation modes, and replay logging for audits.
4. **Extensibility:** Architecture supports plugging in improved perception modules, game engines, or strategy models without rewriting everything else.

## 2. High-Level Architecture
| Layer | Responsibilities | Key Tech |
| --- | --- | --- |
| **Capture & Vision** | Screen capture, template matching, OCR of cards/stacks, opponent action detection. | OpenCV, pytesseract, pyautogui, GPU optional |
| **State Reconstruction** | Transform visual signals into structured game state (seats, stacks, pot, cards). | Custom parsing, Kalman filters for noisy data |
| **Poker Engine** | Deterministic representation of game rules, hand evaluator, simulator. | Python/C++ engine, fast combinatorics, Monte Carlo |
| **Strategy Brain** | Choose action from state: heuristic strategies or learned policy models; bankroll/risk modules. | PyTorch, rule-based modules |
| **Action Execution** | Mapping chosen actions to mouse/keyboard events with anti-detection practices. | pyautogui/OS-level automation |
| **Data & Control Plane** | Logging, analytics, configuration, safety checks, UI for monitoring. | SQLite/Postgres, gRPC/REST |

## 3. Detailed Component Plans

### 3.1 Capture & Image Recognition
- **Screen acquisition:** Implement cross-platform window selector; capture at 30–60 FPS. Use OS APIs for direct window buffer to avoid artifacts.  
- **Table detection:** Template match table layout; align coordinate system even if the window moves.  
- **Element recognition:** 
  - Card recognition via CNN classifier trained on card sprites plus synthetic noise.  
  - OCR for stack sizes, pot, bet controls (consider Tesseract with custom whitelist).  
  - Icon detection to know seat actions (fold/check/raise).  
- **Change detection:** Frame differencing to detect when new decision state occurs; throttle downstream processing when idle.  
- **Calibration tooling:** Build labeling GUI to annotate screenshots, generating datasets for CV models.  
- **Testing:** Unit tests on synthetic frames and replay-based integration tests.

### 3.2 Game State Reconstruction
- **State machine:** Parse rounds (preflop/flop/turn/river/showdown) using events from capture layer.  
- **Data model:** Define protobuf/JSON schema describing seats, blinds, pot, hole cards, actions, time remaining.  
- **Error handling:** Confidence scores per field; fallback to “uncertain” state requiring manual confirm.  
- **Synchronization:** Track hand IDs; align with historical logs for debugging.  
- **Latency budget:** <50 ms for state assembly once frame is processed.

### 3.3 Poker Game Engine
- **Core rules:** Encode betting mechanics, side pots, showdown resolution, rake, table configuration.  
- **Hand evaluator:** Precompute lookup tables or use bit masks for 7-card hand strength; ensure microsecond evaluation.  
- **Simulation tools:** 
  - Monte Carlo rollouts for EV estimation given ranges.  
  - Counterfactual regret minimization (CFR) module to refine strategies offline.  
- **APIs:** Provide deterministic interfaces for the Strategy Brain (e.g., `evaluate_action(state, action)`).

### 3.4 Strategy Brain
- **Mode 1 – Heuristic strategy:** Start with rule-based strategy (preflop charts, postflop heuristics).  
- **Mode 2 – Learning-based:** 
  - Data ingestion pipeline to store hand histories and outcomes.  
  - Option to train neural nets (policy/value networks) using imitation learning or reinforcement learning.  
- **Action selection:** Combine long-term EV with risk constraints (stop-loss, bankroll fraction).  
- **Exploit detection:** Model opponent tendencies (VPIP, aggression) using running stats.  
- **Configuration:** Strategy profiles per stake/site; YAML or UI for runtime switching.  
- **Testing:** Simulated matches against bots/historical data; integration with poker engine to verify decisions.

### 3.5 Action Execution & Anti-Detection
- **Input driver:** Map actions to mouse movements/clicks; randomize timing and paths to reduce detectability.  
- **Safety interlocks:** Global pause hotkey, daily stop-loss, confirm mode.  
- **Multi-table support:** Scheduler to manage focus and action across tables with priority queue.  
- **Regulatory considerations:** Research terms of service/legalities for each target site; optional “observer mode” to run without executing actions.

### 3.6 Data, Control & Tooling
- **Logging:** Structured event logs (state snapshots, decisions, rewards) stored locally; integrate with analytics dashboards.  
- **Replay viewer:** GUI/CLI for step-by-step review of hands with overlays from image captures.  
- **Monitoring:** Real-time HUD showing inferred state, chosen action, confidence, timers.  
- **Configuration management:** Environment-specific configs for resolutions, table skins, strategy parameters.  
- **Deployment:** Containerized services for headless operation; CI pipeline with lint/tests; packaging for Windows/macOS.

## 4. Project Phases & Milestones
1. **Foundation (Weeks 1–3):** Repo setup, coding standards, choose primary language (likely Python), build basic poker engine and CLI harness.  
2. **Perception MVP (Weeks 3–6):** Implement screen capture + manual calibration; read player stacks and cards for a single site at fixed resolution.  
3. **State Machine & Logging (Weeks 5–8):** Translate perception outputs to structured hands; add logging/replay to validate accuracy.  
4. **Heuristic Strategy (Weeks 7–10):** Implement baseline decision rules and action executor; test in sandbox or play-money tables.  
5. **Learning Pipeline (Weeks 10–16):** Collect data, train initial models (supervised preflop charts, simple postflop nets).  
6. **Advanced Features (Weeks 16+):** Multi-table support, opponent modeling, configurable risk management, UI dashboards.  
7. **Optimization & Hardening:** Performance tuning, failover, detection risk mitigation, compliance review.

## 5. Technical Risks & Mitigations
- **OCR/vision accuracy:** Mitigate by building large labeled dataset, using ensemble methods, and adding human override mode.  
- **Latency spikes:** Profile capture and inference pipeline; pre-allocate buffers; consider GPU acceleration.  
- **Site detection countermeasures:** Use non-intrusive capture methods, randomize behavior, keep bot private.  
- **Strategy quality:** Start with proven theory (GTO charts); iteratively refine via simulations and logs.  
- **Legal/ethical concerns:** Research jurisdictions, maintain manual override, restrict use to allowed environments.

## 6. Tooling & Stack Recommendations
- **Languages:** Python for glue + ML, C++/Rust for hot paths (hand evaluator, CFR).  
- **ML stack:** PyTorch, TensorBoard, Hydra config system.  
- **CV stack:** OpenCV, ONNX Runtime, Tesseract; custom datasets stored in DVC.  
- **Infrastructure:** Poetry/pipenv for dependency management, pre-commit hooks, pytest suite, Docker for reproducibility.

## 7. Next Steps
1. Choose target poker site(s) and capture baseline screenshots to guide CV work.  
2. Prototype core poker engine (hand evaluator + rule enforcement).  
3. Build capture calibration tool to assemble training data.  
4. Draft heuristic strategy specification and risk limits before integrating automation.

