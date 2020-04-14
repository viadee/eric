import React from 'react';
import '../App.css';

class Image_Viewer extends React.Component {
  
  render() {
    const text = this.props.text
    const image = this.props.image
    return (
      <div className="image_viewer" onClick={this.props.imageDisable}>
          <img src={"data:image/png;base64," +  image}/>
          <div className="text">
              <div dangerouslySetInnerHTML={{__html: text}}/>
          </div>
      </div>
    );
  }
}

export default Image_Viewer;