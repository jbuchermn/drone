import React from 'react'
import Session from '@ndarilek/janus';
import VideoStream from './Videostream';

// Requires RTCPeerConnection, RTCSessionDescription

class JanusWrapper{
    constructor(janusEndpoint, pcConfig){
        this.janusEndpoint = janusEndpoint;
        this.pcConfig = pcConfig;
        this.onopen = (stream) => {};  // May be called multiple times!
        this.onclose = () => {};

        this._session = null;
        this._handle = null;
        this._pc = null;
    }

    _watchStream(){
        this._handle.message({ request: "list" })
            .then((data) => data.plugindata.data)
            .then(({ list }) => {
                if(!list || list.length == 0){
                    console.log("No streams available");
                    this.close();
                }else{
                    this._handle.message({
                        request: "watch",
                        id: list[0].id
                    });
                }
            });
    }

    _openPC(jsep){
        this._pc = new RTCPeerConnection(this.pcConfig || {
            iceServers: [{urls: "stun:stun.l.google.com:19302"}],
        });

        this._pc.oniceconnectionstatechange = (event) => {};

        this._pc.onicecandidate = (event) => {
            let candidate = event.candidate || { completed: true };
            this._handle.trickle(candidate);
        };

        this._pc.ontrack = (event) => {
            if(!event.streams) return;
            console.log("Janus: Got a stream");
            let stream = event.streams[0];
            this.onopen(stream);
        };

        this._pc.setRemoteDescription(new RTCSessionDescription(jsep)).then(() => {
            this._pc.createAnswer({
                mandatory: {
                    OfferToReceiveAudio: true,
                    OfferToReceiveVideo: true
                }
            }).then((answer) => {
                this._pc.setLocalDescription(answer);

                console.log("Janus: Starting stream");
                this._handle.message({ request: "start" }, answer);
            });

        });
    }

    open(onopen, onclose){
        this.onopen = onopen;
        this.onclose = onclose;

        this._session = new Session(this.janusEndpoint);
        this._session.on("connected", () => {
            console.log("Janus: connected");
            this._session.attach("janus.plugin.streaming").then((handle) => {
                this._handle = handle;

                console.log("Janus: attached");
                handle.on("event", (data) => {
                    if(data.result && data.result.status){
                        console.log("Janus: " + data.result.status);
                    }

                    if(data.jsep){
                        this._openPC(data.jsep); 
                    }
                });
                this._watchStream();
            })
        });

        this._session.on("webrtcup", () => {
            console.log("Janus: webrtcup");
        })
        this._session.on("media", (data) => {
            console.log("Janus: media", data);
        })
        this._session.on("hangup", () => {
            console.log("Janus: hangup");
            this.close();
        })
        this._session.on("destroyed", () => {
            console.log("Janus: destroyed");
            this.close();
        })

    }

    close(){
        this._session.destroy().then(() => this.onclose());
    }
}

export default class Signaling extends React.Component{
    constructor(props){
        super(props);
        this.wrapper = null;
        this.state = {
            stream: null  // Stream object, to be used as video.srcObject
        }
    }

    render(){
        /*
         * Handling this inside render() is probably not the nicest of solutions,
         * however all repercussions are async
         */
        if(!this.props.alive && this.wrapper){
            this.wrapper.close();
            this.wrapper = null;
        }else if(this.props.alive && !this.wrapper){
            this.wrapper = new JanusWrapper(this.props.janusEndpoint);
            this.wrapper.open(
                (stream) => this.setState({ stream }),
                () => this.setState({ stream: null })
            );

        }

        return React.Children.map(this.props.children,
            child => React.cloneElement(child, { stream: this.state.stream }));
    }
}
