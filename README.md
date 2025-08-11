# Black Vienna - React Game Frontend

A modern, modular React application for the Black Vienna deduction game. This frontend connects to a Socket.IO backend to enable real-time multiplayer gameplay.

## 🎮 About Black Vienna

Black Vienna is a deduction game where players attempt to identify three conspirators from a group of suspects. Players use investigation cards and logical deduction to eliminate suspects and solve the mystery.

## ✨ Features

- **Modern UI/UX**: Beautiful gradient backgrounds with glassmorphism effects
- **Real-time Multiplayer**: Socket.IO integration for live game updates
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Modular Architecture**: Clean, maintainable component structure
- **Smooth Animations**: Loading states, hover effects, and transitions
- **Professional Styling**: Modern design with proper typography and spacing

## 🏗️ Project Structure

```
black-vienna-frontend/
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
- A running Black Vienna backend server

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd black-vienna-frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Update Socket.IO connection**
   
   Edit `src/hooks/useSocket.js` and update the server URL:
   ```javascript
   const newSocket = io('http://localhost:5001'); // Change to your server URL
   ```

4. **Start the development server**
   ```bash
   npm start
   # or
   yarn start
   ```

5. **Open your browser**
   
   Navigate to `http://localhost:3000`

## 🎯 How to Play

1. **Enter Your Name**: Input your detective name on the main menu
2. **Create or Join Game**: Either create a new game or join existing one with Game ID
3. **Wait in Lobby**: Share the Game ID with friends and wait for 3+ players
4. **Start Playing**: The host can start the game once enough players have joined
5. **Deduce the Conspiracy**: Use your suspect cards and investigation cards to solve the mystery

## 🔧 Configuration

### Backend Connection

The frontend expects a Socket.IO server running on `http://localhost:5001`. To change this:

1. Open `src/hooks/useSocket.js`
2. Modify the connection URL in the `io()` function
3. Ensure your backend server supports the following events:
   - `create_game`
   - `join_game`
   - `start_game`
   - `game_created`
   - `player_joined`
   - `game_started`
   - `error`

### Styling Customization

The main stylesheet is located at `src/styles/App.css`. Key design elements include:

- **Color Scheme**: Purple gradient background (`#667eea` to `#764ba2`)
- **Typography**: Segoe UI font family
- **Effects**: Glassmorphism, shadows, and smooth transitions
- **Responsive**: Mobile-first design approach

## 📱 Responsive Design

The application is fully responsive and includes:

- **Desktop**: Full-featured layout with grid systems
- **Tablet**: Optimized spacing and component sizing
- **Mobile**: Single-column layouts and touch-friendly buttons

## 🛠️ Development

### Component Architecture

- **App.js**: Main application logic and state management
- **Menu.js**: Player name input and game creation/joining
- **Lobby.js**: Pre-game waiting area with game ID sharing
- **GameBoard.js**: Active game interface with cards and player status
- **useSocket.js**: Custom hook for Socket.IO connection management

### Adding New Features

1. **New Components**: Add to `src/components/`
2. **Styling**: Update `src/styles/App.css` or create component-specific styles
3. **State Management**: Use React hooks or consider adding Context API for complex state
4. **Socket Events**: Extend `useSocket.js` for new real-time features

## 🎨 UI Components

### Buttons
- `.btn-primary`: Main action buttons (Create Game, Start Game)
- `.btn-secondary`: Secondary actions (Join Game)
- `.btn-ghost`: Subtle buttons (Back, Copy)
- Size variants: `.btn-lg`, `.btn-sm`, `.btn-xs`

### Cards
- `.menu-card`, `.lobby-card`: Main content containers
- `.suspect-card`: Player's suspect cards
- `.investigation-card`: Investigation deck displays
- `.player-card`: Player status indicators

### Animations
- Loading spinner for connection states
- Bouncing dots for waiting states
- Hover effects on interactive elements
- Smooth transitions for state changes

## 📦 Dependencies

### Production
- **react**: ^18.2.0 - Core React library
- **react-dom**: ^18.2.0 - React DOM rendering
- **socket.io-client**: ^4.7.2 - Real-time communication

### Development
- **react-scripts**: 5.0.1 - Create React App build tools
- **@testing-library/***: Testing utilities

## 🚀 Deployment

### Building for Production

```bash
npm run build
# or
yarn build
```

This creates a `build/` directory with optimized production files.

### Deployment Options

1. **Netlify**: Drag and drop the `build` folder
2. **Vercel**: Connect your GitHub repository
3. **AWS S3**: Upload build files to S3 bucket
4. **Traditional Hosting**: Upload build files to web server

### Environment Variables

For production deployment, you may want to use environment variables:

```bash
REACT_APP_SOCKET_URL=https://your-backend-server.com
```

Then update `useSocket.js`:
```javascript
const newSocket = io(process.env.REACT_APP_SOCKET_URL || 'http://localhost:5001');
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Ensure backend server is running
   - Check CORS settings on backend
   - Verify Socket.IO server URL

2. **Styling Issues**
   - Clear browser cache
   - Check for CSS conflicts
   - Ensure all imports are correct

3. **Build Errors**
   - Delete `node_modules` and `package-lock.json`
   - Run `npm install` again
   - Check for outdated dependencies

### Debug Mode

Enable Socket.IO debugging:
```javascript
// In useSocket.js
const newSocket = io('http://localhost:5001', {
  debug: true
});
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- Use functional components with hooks
- Follow React best practices
- Maintain consistent naming conventions
- Add comments for complex logic
- Keep components focused and reusable

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## 🙏 Acknowledgments

- React team for the amazing framework
- Socket.IO team for real-time capabilities
- Black Vienna game designers for the original game concept
- Modern web design trends for UI inspiration

## 📞 Support

For questions or support:
- Create an issue on GitHub
- Check existing documentation
- Review Socket.IO and React documentation

---

**Enjoy playing Black Vienna! 🕵️‍♂️🎯**