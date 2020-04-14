import React from 'react';
import '../App.css';

class Clipboard extends React.Component {
  
  render() {
    const clipboard = this.props.clipboard
    return (
      <div className="clipboard">
        <div className="clipboard-inner">
          <h1>- Clipboard -</h1>
          <div className="clipboard-list">
            <ul>
              {clipboard.map(clip => (
                <li className={clip.active ? "clipboard-item" : "clipboard-item-crossed"} key={clip.id} ref={clip.id}>
                  <div className="new-item">1</div>
                  <div dangerouslySetInnerHTML={{__html: clip.text}} />
                  <hr/>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    );
  }
}

export default Clipboard;