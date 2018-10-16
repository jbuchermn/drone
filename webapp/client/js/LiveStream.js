import React from "react"
import WSAvc from './wsavc'
import MJPEGplayer from './MJPEGplayer'

export default class LiveStream extends React.Component{
    constructor(props){
        super(props);
        this.canvasRef = React.createRef();
    }

    componentDidMount(){
        let PlayerClass = null;
        if(this.props.config.format == 'mjpeg'){
            PlayerClass = MJPEGplayer;
        }else if(this.props.config.format == 'h264'){
            PlayerClass = WSAvc;
        }else{
            console.log("Unsupported:", this.props.config.format)
            return;
        }

        this.player = new PlayerClass(
            this.canvasRef.current,
            {
                width: this.props.config.resolution[0],
                height: this.props.config.resolution[1]
            }
        );

        let ip = location.host;
        if(ip.includes(":")){
            ip = ip.split(":")[0];
        }
        let url = "ws://" + ip + ":" + this.props.port;

        this.ws = new WebSocket(url);
        this.ws.binaryType = "arraybuffer";

        this.ws.onopen = () => {
            console.log("Connected to " + url);
        };

        this.ws.onclose = () => {
            console.log("Connection to " + url + " closed");
            this.player.close();
        };

        this.ws.onmessage = (evt) => {
            let frame = new Uint8Array(evt.data);
            this.player.on_frame(frame);
        }
    }

    render () {
        return <canvas ref={this.canvasRef} />;
    }
}
