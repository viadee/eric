import React from 'react';
import '../App.css';

class Help extends React.Component {
  
  render() {
    const description = this.props.description
    return (
      <div className="help">
        <div className="help-inner">
          <h1>- Help -</h1>
          <p>{description}</p>
        </div>
      </div>
    );
  }
}

export default Help;