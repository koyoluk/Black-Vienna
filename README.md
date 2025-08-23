# Black Vienna - React Game Frontend

A modern, modular React application for the Black Vienna deduction game. This frontend connects to a Socket.IO backend to enable real-time multiplayer gameplay.

## 🎮 About Black Vienna

Black Vienna is a deduction game where players attempt to identify three conspirators from a group of suspects. Players use investigation cards and logical deduction to eliminate suspects and solve the mystery.

## 🏗️ Project Structure

```
black-vienna-game/
├── public/
├── src/
│   ├── components/
│   │   ├── Menu.js           # Main menu component
│   │   ├── Lobby.js          # Game lobby component
│   │   └── GameBoard.js      # Active game display
│   ├── hooks/
│   │   └── useSocket.js      # Socket connection management
│   ├── styles/
│   │   └── App.css          # Main stylesheet
│   ├── App.js               # Root component
│   └── index.js             # Entry point
├── package.json
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd black-vienna-backend
   ```

2. **Add virtual environment in backend**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   
3. **Install all required dependencies**
   ```bash
   python3 app.py

4. **Install dependencies in frontend**
   ```bash
   cd ../game
   npm install
   ```

5. **Update Socket.IO connection**
   
   Edit `src/hooks/useSocket.js` and update the server URL:
   ```javascript
   const newSocket = io('http://localhost:5001'); // Change to your server URL
   ```

6. **Start the development server**
   ```bash
   npm start
   # or
   yarn start
   ```

7. **Open your browser**
   
   Navigate to `http://localhost:3000`

## 🎯 How to Play

1. **Enter Your Name**: Input your detective name on the main menu
2. **Create or Join Game**: Either create a new game or join existing one with Game ID
3. **Wait in Lobby**: Share the Game ID with friends and wait for 3+ players
4. **Start Playing**: The host can start the game once enough players have joined
5. **Deduce the Conspiracy**: Use your suspect cards and investigation cards to solve the mystery


---

**Enjoy playing Black Vienna! 🕵️‍♂️🎯**
