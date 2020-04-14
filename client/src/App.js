import React from 'react';
import './App.css';
import Header_Bar from './components/header_bar';
import Chat from './components/chat';

function App() {
  return (
    <div className="App">
      <Header_Bar></Header_Bar>
      <Chat></Chat>
    </div>
  );
}

export default App;
