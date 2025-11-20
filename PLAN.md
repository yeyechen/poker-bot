# Online Poker Bot - Project Plan

## 1. Vision
To create an autonomous bot that plays online poker. The bot will work by observing the game through screen capture, understanding the game's rules with a core engine, and making intelligent decisions using a "brain" component.

## 2. Core Components

### a. Perception (The Eyes)
This component's job is to see and interpret the game state from the online poker client.

*   **Function:** It will capture the screen and use computer vision and OCR (Optical Character Recognition) to read all relevant information.
*   **Key Information to Capture:**
    *   Hole cards and community cards.
    *   Player stack sizes and the current pot size.
    *   Positions, blinds, and whose turn it is.
    *   Opponent actions (fold, check, bet, raise).
*   **Output:** A structured, machine-readable summary of the current game state.

### b. Poker Engine (The Rulebook)
This is the foundation of the bot, providing a perfect understanding of the rules of poker.

*   **Function:** It will act as a deterministic and fast simulator for the game.
*   **Key Capabilities:**
    *   Enforce game rules (e.g., legal moves, betting order).
    *   Evaluate hand strength (e.g., determine the winning hand at showdown).
    *   Calculate pot and side-pot splits.
*   **Output:** The ability to validate game states and simulate future possibilities for the "Brain" to use.

### c. Strategy (The Brain)
This component is the decision-making center. It takes the game state and decides what action to take.

*   **Function:** To select the most profitable action (check, bet, fold, raise) in any given situation.
*   **Implementation Strategy:** This is a major design choice with two primary paths:
    1.  **GTO (Game Theory Optimal) Approach:** Use a pre-solved GTO database. The bot would look up the current game situation and play the theoretically "correct" move. This is a logic-based approach.
    2.  **Machine Learning Approach:** Train a neural network model to play. This would involve collecting a large dataset of hands and using it to teach the model how to respond to different scenarios. This is a data-driven approach.
*   **Output:** A specific action to be taken (e.g., "Raise to $15.50").

### d. Action (The Hands)
This component executes the decision made by the "Brain."

*   **Function:** To translate the bot's desired action into user inputs on the poker client.
*   **Key Capabilities:**
    *   Control the mouse to click buttons (e.g., "Fold," "Bet").
    *   Enter bet amounts into text boxes.
*   **Output:** The bot successfully performs its chosen action in the live game.

## 3. Development Approach
The project should be built in a modular and incremental way.

1.  **Build the Poker Engine first.** This is the logical core that everything else depends on.
2.  **Develop the Perception component** for a single, specific poker site.
3.  **Implement a simple, rule-based Strategy** to start (e.g., using standard pre-flop charts). This allows for end-to-end testing before tackling the more complex "Brain" logic.
4.  **Connect all components** to create a functional, baseline bot.
5.  **Iterate and Improve.** Once the baseline is working, focus can shift to the main challenge: developing the advanced GTO or ML-based "Brain."