/*
 * window.mozRTCPeerConnection, window.mozRTCSessionDescription, window.mozRTCIceCandidate are now deprecated
 */

RTCPeerConnection = window.RTCPeerConnection || /*window.mozRTCPeerConnection ||*/ window.webkitRTCPeerConnection;
RTCSessionDescription = /*window.mozRTCSessionDescription ||*/ window.RTCSessionDescription;
RTCIceCandidate = /*window.mozRTCIceCandidate ||*/ window.RTCIceCandidate;


export default class UV4LSignaling{
    constructor(addr, useSSL){
        this.addr = addr;
        this.useSSL = useSSL;
        this.stream = null;

        this._url = (this.useSSL ? "wss" : "ws") + "://" + this.addr + ":8081/webrtc";
        this._ws = null
        this._pc = null;
        this._iceCandidates = [];
        this._hasRemoteDesc = false;

        this._waitingForRetry = false;
    }

    _retry(){
        // Don't start a million timers
        if(this._waitingForRetry) return;

        setTimeout(() => { 
            console.log("Retrying open()");
            this._waitingForRetry = false;
            this.open();
        }, 1000);
        this._waitingForRetry = true;
    }


    open(){
        console.log("Opening web socket", this._url);
        if (!("WebSocket" in window)) {
            alert("WebSocket not supported...");
        }

        let addIceCandidates = () => {
            if (this._hasRemoteDesc) {
                this._iceCandidates.forEach((candidate) => {
                    this._pc.addIceCandidate(candidate,
                        () => {},
                        (error) => { console.error("addIceCandidate error: " + error); }
                    );
                });
                this._iceCandidates = [];
            }
        }

        this._ws = new WebSocket(this._url);

        //
        // onopen
        //
        this._ws.onopen = () => {
            /* var config = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}; */
            let config = {"iceServers": []};
            let options = {optional: []};
            this._pc = new RTCPeerConnection(config, options);
            this._iceCandidates = [];
            this._hasRemoteDesc = false;

            this._pc.onicecandidate = (event) => {
                if (event.candidate) {
                    let candidate = {
                        sdpMLineIndex: event.candidate.sdpMLineIndex,
                        sdpMid: event.candidate.sdpMid,
                        candidate: event.candidate.candidate
                    };
                    let request = {
                        what: "addIceCandidate",
                        data: JSON.stringify(candidate)
                    };
                    this._ws.send(JSON.stringify(request));
                } 
            };

            if ('ontrack' in this._pc) {
                this._pc.ontrack = (event) => {
                    this.stream = event.streams[0];
                };
            } else {  // onaddstream() deprecated
                this._pc.onaddstream = (event) => {
                    this.stream = event.stream;
                };
            }

            let request = {
                what: "call",
                options: {
                    // If forced, the hardware codec depends on the arch.
                    // (e.g. it's H264 on the Raspberry Pi)
                    // Make sure the browser supports the codec too.
                    force_hw_vcodec: true,
                    vformat: 30, /* 30=640x480, 30 fps */
                    trickle_ice: true
                }
            };
            console.log("Sending message", request);
            this._ws.send(JSON.stringify(request));
        };

        //
        // onmessage
        //
        this._ws.onmessage = (evt) => {
            let msg = JSON.parse(evt.data);
            let what = msg.what;
            let data = msg.data;

            console.log("Received message", msg);

            switch (what) {
                case "offer":
                    let mediaConstraints = {
                        optional: [],
                        mandatory: {
                            OfferToReceiveAudio: true,
                            OfferToReceiveVideo: true
                        }
                    };
                    this._pc.setRemoteDescription(
                        new RTCSessionDescription(JSON.parse(data)),
                        () => {
                            this._hasRemoteDesc = true;
                            addIceCandidates();
                            this._pc.createAnswer(
                                (sessionDescription) => {
                                    this._pc.setLocalDescription(sessionDescription);
                                    let request = {
                                        what: "answer",
                                        data: JSON.stringify(sessionDescription)
                                    };
                                    this._ws.send(JSON.stringify(request));
                                },
                                (error) => { onError("failed to create answer: " + error); },
                                mediaConstraints);
                        },
                        (error) => {
                            onError('failed to set the remote description: ' + event);
                            this._ws.close();
                        }
                    );
                    break;

                case "answer":
                    break;

                case "message":
                    // Assume message is "Sorry, the device is either busy streaming to another peer or 
                    // previous shutdown has not been completed yet"
                    console.log("Issuing retry due to message");
                    this._retry();
                    break;

                case "iceCandidate": // received when trickle ice is used (see the "call" request)
                    if (!msg.data) break;
                    var elt = JSON.parse(msg.data);
                    let candidate = new RTCIceCandidate({
                        sdpMLineIndex: elt.sdpMLineIndex,
                        candidate: elt.candidate
                    });

                    this._iceCandidates.push(candidate);
                    addIceCandidates();

                    break;

                case "iceCandidates": // received when trickle ice is NOT used (see the "call" request)
                    let candidates = JSON.parse(msg.data);
                    for(let i = 0; candidates && i < candidates.length; i++) {
                        var elt = candidates[i];
                        let candidate = new RTCIceCandidate({
                            sdpMLineIndex: elt.sdpMLineIndex, 
                            candidate: elt.candidate
                        });
                        this._iceCandidates.push(candidate);
                    }
                    addIceCandidates();
                    break;
            }
        };

        //
        // onclose
        //
        this._ws.onclose = function (event) {
            console.log('Socket closed with code: ' + event.code);
            if (this._pc) {
                this._pc.close();
                this._pc = null;
                this._ws = null;
            }
            this.stream = null;
        };

        //
        // onerror
        //
        this._ws.onerror = (error) => {
            this._retry();
        };

    }

    close(){
        if (this._ws) {
            let request = { what: "hangup" };
            console.log("Sending message", request);
            this._ws.send(JSON.stringify(request));
        }
    };
}
