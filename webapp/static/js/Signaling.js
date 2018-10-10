import React from 'react'
import Session from '@ndarilek/janus';
import VideoStream from './Videostream';

// Requires RTCPeerConnection, RTCSessionDescription

export default class Signaling extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            pc: null,  // RTCPeerConnection
            session: null,  // Janus session
            handle: null,  // Janus plugin handle
            stream: null  // Stream object, to be used as video.srcObject
        }
    }

    _processAnswer(data){
        if(!data){
            console.log("Empty answer");
            return null;
        }

        if(data.janus != "success"){
            console.log("Janus error");
            return null;
        }

        data = data.plugindata;
        if(!data || !data.data){
            console.log("Empty answer");
            return null;
        }

        return data.data;
    }

    _initialize(handle){
        handle.message({ request: "list" })
            .then((data) => this._processAnswer(data))
            .then(({ list }) => {
                if(list.length == 0){
                    console.log("No streams available");
                    this.setState({ stream: null });
                }else{
                    handle.message({
                        request: "watch",
                        id: list[0].id
                    });
                }
            });
    }

    _createPC(jsep){
        console.log("Got JSEP")
        let pc = new RTCPeerConnection(this.props.pcConfig || {
            iceServers: [{urls: "stun:stun.l.google.com:19302"}],
        });

        pc.oniceconnectionstatechange = (event) => {
            console.log("onicestatechange", event);
        };

        pc.onicecandidate = (event) => {
            let candidate = event.candidate || { completed: true };
            console.log("onicecandidate", candidate);
            this.state.handle.trickle(candidate);
        };

        pc.ontrack = (event) => {
            if(!event.streams) return;
            console.log("Got a stream");
            let stream = event.streams[0];

            this.setState({ stream });
        };

        pc.setRemoteDescription(new RTCSessionDescription(jsep)).then(() => {
            console.log("Sending answer");
            pc.createAnswer({
                mandatory: {
                    OfferToReceiveAudio: true,
                    OfferToReceiveVideo: true
                }
            }).then((answer) => {
                pc.setLocalDescription(answer);

                console.log("Starting stream");
                this.state.handle.message({ request: "start" }, answer).then((res) => {
                    console.log(res);
                });
            });

        });
    }

    componentDidMount(){
        let session = new Session(this.props.janusEndpoint);

        session.on("connected", () => {
            console.log("connected");
            session.attach("janus.plugin.streaming").then((handle) => {
                console.log("attached");
                this.setState({ handle });
				handle.on("event", (data) => {
                    console.log("event", data);
                    if(data.jsep) this._createPC(data.jsep);
				});
                this._initialize(handle);
            })
        });

        session.on("webrtcup", () => {
            console.log("webrtcup");
        })
        session.on("media", (data) => {
            console.log("media", data);
        })
        session.on("hangup", () => {
            console.log("hangup");
        })
        session.on("destroyed", () => {
            console.log("destroyed");
        })

        this.setState({ session });
    }

    render(){
        if(!this.state.stream) return <div />;
        else return <VideoStream stream={this.state.stream} />;
    }
}
