import React from 'react';
import '../App.css';

class Header_Bar extends React.Component {
  
  render() {
    return (
      <div className="App">
        <div className="header-bar">
          <h2> <img src={require('./robot_bright.png')}/> ERIC: XAI Bot</h2>
        </div>
      </div>
    );
  }
}

export default Header_Bar;