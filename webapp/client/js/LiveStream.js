import React from "react"
import WSAvc from './wsavc'
import MJPEGplayer from './MJPEGplayer'

export default class LiveStream extends React.Component{
    constructor(props){
        super(props);
        this.state = { 
            player: null,
            ws: null, 
            url: null,
            width: null,
            height: null, 
            format: null
        };
        this._canvasRef = React.createRef();
        this._interval = null;
    }

    setup(){
        let ip = location.host;
        if(ip.includes(":")){
            ip = ip.split(":")[0];
        }

        let url = "ws://" + ip + ":" + this.props.port;
        let width = this.props.config.resolution[0];
        let height = this.props.config.resolution[1];
        let format = this.props.config.format

        if(this.state.player && this.state.ws){
            if(
                (this.state.url == url) &&
                (this.state.width == width) &&
                (this.state.height == height) &&
                (this.state.format == format)){

                // All good
            }else{

                // Reopen
                this.state.ws.close();
            }

            return;
        }

        let PlayerClass = null;
        if(format == 'mjpeg'){
            PlayerClass = MJPEGplayer;
        }else if(format == 'h264'){
            PlayerClass = WSAvc;
        }else{
            console.log("Unsupported:", this.props.config.format)
            return;
        }

        let player = new PlayerClass(
            this._canvasRef.current,
            { width, height }
        );


        let ws = new WebSocket(url);
        ws.binaryType = "arraybuffer";

        ws.onopen = () => {
            console.log("Connected to " + url);
            this.setState({ 
                player, 
                ws, 
                url,
                width,
                height,
                format
            });
        };

        ws.onclose = () => {
            if(this.state.player) this.state.player.close();
            this.setState({ 
                player: null, 
                ws: null,
                url: null,
                width: null,
                height: null,
                format: null
            });
        };

        ws.onmessage = (evt) => {
            let frame = new Uint8Array(evt.data);
            if(this.state.player) this.state.player.on_frame(frame);
        }

    }

    componentDidMount(){
        this._interval = setInterval(() => this.setup(), 1000);
    }

    componentWillUnmount(){
        clearInterval(this._interval);
    }

    render () {
        return <canvas ref={this._canvasRef} />;
    }
}
