/*
 * window.mozRTCPeerConnection, window.mozRTCSessionDescription, window.mozRTCIceCandidate are now deprecated
 */

RTCPeerConnection = window.RTCPeerConnection || /*window.mozRTCPeerConnection ||*/ window.webkitRTCPeerConnection;
RTCSessionDescription = /*window.mozRTCSessionDescription ||*/ window.RTCSessionDescription;
RTCIceCandidate = /*window.mozRTCIceCandidate ||*/ window.RTCIceCandidate;


export default class UV4LSignaling{
    constructor(url){
        this.url = url;
        this.ws = null
        this.pc = null;
        this.icCandidates = [];
        this.hasRemoteDesc = false;

        this.stream = null;
        this.waitingForRetry = false;
    }

    retry(){
        // Don't start a million timers
        if(this.waitingForRetry) return;

        setTimeout(() => { 
            console.log("Retrying open()");
            this.waitingForRetry = false;
            this.open();
        }, 1000);
        this.waitingForRetry = true;
    }


    open(){
        console.log("Opening web socket", this.url);
        if (!("WebSocket" in window)) {
            alert("WebSocket not supported...");
        }

        let addIceCandidates = () => {
            if (this.hasRemoteDesc) {
                this.iceCandidates.forEach((candidate) => {
                    this.pc.addIceCandidate(candidate,
                        () => {},
                        (error) => { console.error("addIceCandidate error: " + error); }
                    );
                });
                this.iceCandidates = [];
            }
        }

        this.ws = new WebSocket(this.url);

        //
        // onopen
        //
        this.ws.onopen = () => {
            /* var config = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}; */
            let config = {"iceServers": []};
            let options = {optional: []};
            this.pc = new RTCPeerConnection(config, options);
            this.iceCandidates = [];
            this.hasRemoteDesc = false;

            this.pc.onicecandidate = (event) => {
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
                    this.ws.send(JSON.stringify(request));
                } 
            };

            if ('ontrack' in this.pc) {
                this.pc.ontrack = (event) => {
                    this.stream = event.streams[0];
                };
            } else {  // onaddstream() deprecated
                this.pc.onaddstream = (event) => {
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
            this.ws.send(JSON.stringify(request));
        };

        //
        // onmessage
        //
        this.ws.onmessage = (evt) => {
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
                    this.pc.setRemoteDescription(
                        new RTCSessionDescription(JSON.parse(data)),
                        () => {
                            this.hasRemoteDesc = true;
                            addIceCandidates();
                            this.pc.createAnswer(
                                (sessionDescription) => {
                                    this.pc.setLocalDescription(sessionDescription);
                                    let request = {
                                        what: "answer",
                                        data: JSON.stringify(sessionDescription)
                                    };
                                    this.ws.send(JSON.stringify(request));
                                },
                                (error) => { onError("failed to create answer: " + error); },
                                mediaConstraints);
                        },
                        (error) => {
                            onError('failed to set the remote description: ' + event);
                            this.ws.close();
                        }
                    );
                    break;

                case "answer":
                    break;

                case "message":
                    // Assume message is "Sorry, the device is either busy streaming to another peer or 
                    // previous shutdown has not been completed yet"
                    console.log("Issuing retry due to message");
                    this.retry();
                    break;

                case "iceCandidate": // received when trickle ice is used (see the "call" request)
                    if (!msg.data) break;
                    var elt = JSON.parse(msg.data);
                    let candidate = new RTCIceCandidate({
                        sdpMLineIndex: elt.sdpMLineIndex,
                        candidate: elt.candidate
                    });

                    this.iceCandidates.push(candidate);
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
                        this.iceCandidates.push(candidate);
                    }
                    addIceCandidates();
                    break;
            }
        };

        //
        // onclose
        //
        this.ws.onclose = function (event) {
            console.log('Socket closed with code: ' + event.code);
            if (this.pc) {
                this.pc.close();
                this.pc = null;
                this.ws = null;
            }
            this.stream = null;
        };

        //
        // onerror
        //
        this.ws.onerror = (error) => {
            this.retry();
        };

    }

    close(){
        if (this.ws) {
            let request = { what: "hangup" };
            console.log("Sending message", request);
            this.ws.send(JSON.stringify(request));
        }
    };
}
