
import React from "react"
import UV4LSignaling from './UV4LSignaling'

export default class UV4LVideo extends React.Component {
    constructor(props){
        super(props);
        this.state = { stream: null, signaling: null };
        this.videoRef = React.createRef();
        this.timer = null;
    }


    setupVideo(){
        if(!this.videoRef.current) return;
        if(!this.state.stream) return;

        if(this.videoRef.current.srcObject !== this.state.stream){
            this.videoRef.current.srcObject = this.state.stream;
            this.videoRef.current.play();
        }
    }

    tick() {
        let stream = this.state.signaling ? this.state.signaling.stream : null;
        if(stream !== this.state.stream){
            this.setState({ stream });
        }
    }

    componentDidMount(){
        this.setupVideo();
        this.timer = setInterval(
            () => this.tick(),
            200
        );
    }

    componentDidUpdate(){
        this.setupVideo();
    }

    componentWillUnmount() {
        clearInterval(this.timer);
    }

    /*
     * Misuse getDerivedStateFromProps to take care of signaling state changes
     */
    static getDerivedStateFromProps(nextProps, prevState){
        let setupSignaling = () => {
            let signaling = new UV4LSignaling(nextProps.url);
            signaling.open();
            return signaling;
        }

        if(!nextProps.alive && prevState.signaling){
            prevState.signaling.close();
            return { stream: null, signaling: null };

        }else if(nextProps.alive && !prevState.signaling){
            return { signaling: setupSignaling() };

        }else if(nextProps.alive && prevState.signaling){
            if(prevState.signaling.url != nextProps.url){
                prevState.signaling.close();
                return { stream: null, signaling: setupSignaling() };
            }
        }

        return null;
    }

	render () {
        return (
            <div>
                {this.state.stream && <video ref={this.videoRef} />}
            </div>
        );
	}
}
