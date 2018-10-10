import React from 'react'

export default class Videostream extends React.Component {
    constructor(props){
        super(props);
        this.videoRef = React.createRef();
    }


    setupVideo(){
        if(!this.videoRef.current) return;
        if(!this.props.stream) return;

        if(this.videoRef.current.srcObject !== this.props.stream){
            this.videoRef.current.srcObject = this.props.stream;
            this.videoRef.current.play();
        }
    }


	render () {
        if(this.props.stream) this.setupVideo();
        return (
            <div>
                <video ref={this.videoRef} />
            </div>
        );
	}
}
