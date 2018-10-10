import Janus from './janus-mobile'


export default class JanusSignaling{
    constructor(addr, useSSL){
        this.addr = addr;
        this.useSSL = useSSL;
        this.stream = null;

        // this._url = (this.useSSL ? "https" : "http") + "://" + this.addr + ":" + 
        //     (this.useSSL ? "8089" : "8088") + "/janus";
        this._url = "https://janus.conf.meetecho.com/janus";
        this._opaque = "JanusSignaling-" + Janus.randomString(12);
        this._janus = null;
        this._streaming = null;
    }

    _startStream(){
        this._streaming.send({
            message: { request: "list" },
            success: (result) => {
                if(result && result.list){
                    if(result.list.length == 0){
                        Janus.debug("No streams available");
                        return;
                    }

                    this._streaming.send({
                        message: { request: "watch", id: result.list[0].id }
                    });
                }else{
                    Janus.debug("Could not retrieve stream list", result);
                }
            }
        })
    };

    _initializeJanus() {
        this._janus.attach({
            plugin: "janus.plugin.streaming",
            opaqueId: this._opaque,
            success: (pluginHandle) => {
                Janus.debug("Successfully attached to plugin");
                this._streaming = pluginHandle;

                this._startStream();
            },
            error: (error) => {
                Janus.debug("Error attaching to plugin", error);
            },
            onmessage: (msg, jsep) => {
                console.log("Got message", msg, jsep);
                if(msg.result){
                    Janus.debug("Message", msg.result);
                }else if(msg.error){
                    Janus.debug("Error message", msg.error);
                }

                if(jsep) {
                    Janus.debug("Handling SDP as well...");
                    Janus.debug(jsep);
                    this._streaming.createAnswer({
                        jsep,
                        media: { audioSend: false, videoSend: false },
                        success: (jsep)  => {
                            Janus.debug("Got SDP!");
                            Janus.debug(jsep);
                            this._streaming.send({
                                message: { request: "start" }, 
                                jsep
                            });
                        },
                        error: (error) => {
                            Janus.error("WebRTC error:", error);
                        }
                    });
                }
            },
            onremotestream: (stream) => {
                this.stream = stream;
            },
            oncleanup: () => {
                Janus.debug("Janus cleanup");
            }
        }); 
    }

    open(){
        Janus.init({
            debug: 'all',
            callback: () => {
                if(!Janus.isWebrtcSupported()) {
                    Janus.debug("No WebRTC support... ");
                    return;
                }

                this._janus = new Janus({
                    server: this._url,
                    success: () => this._initializeJanus(),
                    error: (err) => {
                        Janus.debug("Error creating Janus instance", err);
                    },
                    destroyed: () => {
                        Janus.debug("Janus instance destroyed");
                    }
                })
            }
        })

    }

    close(){
        if(!this._streaming) return;
        this._streaming.send({
            message: { request: "stop" }
        });
        this._streaming.hangup();
    }
}
