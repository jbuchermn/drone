import React from "react";
import Composer from "react-composer";
import { Query, Mutation } from "react-apollo";
import gql from "graphql-tag";
import {
    Button,
    TextField,
    Grid,
    Paper
} from '@material-ui/core';

import LiveStream from './LiveStream'

const LIVE_STREAM_WIDTH = 1000;
const LIVE_STREAM_HEIGHT = 600

const CAMERA_QUERY = gql`
query Camera{
    camera{
        id,
        wsPort 
        recording,
        streaming,
        videoConfig,
        streamConfig,
        imageConfig
    }
}
`

const CAMERA_START_MUTATION = gql`
mutation CameraStart($record: Boolean!, $stream: Boolean!){ 
    cameraStart(record: $record, stream: $stream){
        camera{
            id,
            wsPort 
            recording,
            streaming,
            videoConfig,
            streamConfig,
            imageConfig
        },
        gallery{
            id,
            entries{
                id,
                kind,
                name
            }
        }
    }
}
`

const CAMERA_STOP_MUTATION = gql`
mutation CameraStop{ 
    cameraStop{
        camera{
            id,
            wsPort 
            recording,
            streaming,
            videoConfig,
            streamConfig,
            imageConfig
        },
        gallery{
            id,
            entries{
                id,
                kind,
                name
            }
        }
    }
}
`

const CAMERA_IMAGE_MUTATION = gql`
mutation CameraImage{ 
    cameraImage{
        camera{
            id,
            wsPort 
            recording,
            streaming,
            videoConfig,
            streamConfig,
            imageConfig
        },
        gallery{
            id,
            entries{
                id,
                kind,
                name
            }
        }
    }
}
`

const CAMERA_SET_VIDEO_CONFIG_MUTATION = gql`
mutation CameraSetVideoConfig($config: String!){
    cameraSetVideoConfig(config: $config){
        camera{
            id,
            wsPort 
            recording,
            streaming,
            videoConfig,
            streamConfig,
            imageConfig
        },
        gallery{
            id,
            entries{
                id,
                kind,
                name
            }
        }
    }
}
`

const CAMERA_SET_STREAM_CONFIG_MUTATION = gql`
mutation CameraSetStreamConfig($config: String!){
    cameraSetStreamConfig(config: $config){
        camera{
            id,
            wsPort 
            recording,
            streaming,
            videoConfig,
            streamConfig,
            imageConfig
        },
        gallery{
            id,
            entries{
                id,
                kind,
                name
            }
        }
    }
}
`

const CAMERA_SET_IMAGE_CONFIG_MUTATION = gql`
mutation CameraSetImageConfig($config: String!){
    cameraSetImageConfig(config: $config){
        camera{
            id,
            wsPort 
            recording,
            streaming,
            videoConfig,
            streamConfig,
            imageConfig
        },
        gallery{
            id,
            entries{
                id,
                kind,
                name
            }
        }
    }
}
`

class JSONConfig extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            text: this._simplify(props.json)
        }
    }

    handleChange(text){
        this.setState({ text });
        let json = this._unsimplify(text);
        this.props.onChange(json);
    }

    _simplify(text){
        let obj = JSON.parse(text);
        let result = "";
        Object.keys(obj).forEach(key => {
            result += key + ": " + obj[key] + "\n";
        });
        return result;
    }

    _unsimplify(text){
        const fromString = (text) => {
            // List of Integers
            if(text.includes(",")){
                try{
                    return JSON.parse("[" + text + "]");
                }catch(ex){}
            }

            // Integer
            let int = parseInt(text);
            if(!isNaN(int)) return int;

            // String
            return text.trim();
        };
        let obj = {};
        text.split("\n").forEach(line => {
            if(line.includes(":")){
                obj[line.split(":")[0]] = fromString(line.split(":")[1])
            }
        });

        return JSON.stringify(obj);
    }

    render(){

        return (
            <TextField
                fullWidth
                label=""
                multiline
                rows={20}
                rowsMax={20}
                value={this.state.text}
                onChange={evt => this.handleChange(evt.target.value)}
                margin="normal"
                variant="outlined" />
        );
    }

}

class CameraInner extends React.Component{
    constructor(props){
        super(props);

        this.state = {
            streamConfig: null,
            videoConfig: null,
            imageConfig: null
        }
    }
    
    static getDerivedStateFromProps(props, prevState){
        return { 
            streamConfig: prevState.streamConfig || props.camera.streamConfig,
            videoConfig: prevState.streamConfig || props.camera.videoConfig,
            imageConfig: prevState.streamConfig || props.camera.imageConfig
        };
    }

    render(){
        const record = () => {
            if(this.props.camera.recording){
                this.props.stop();
            }else{
                this.props.start({ variables: { stream: false, record: true } });
            }
        };

        const stream = () => {
            if(this.props.camera.streaming){
                this.props.stop();
            }else{
                this.props.start({ variables: { stream: true, record: false } });
            }
        };

        const updateVideo = () => this.props.setVideoConfig({ variables: { config: this.state.videoConfig } });
        const updateImage = () => this.props.setImageConfig({ variables: { config: this.state.imageConfig } });
        const updateStream = () => {
            this.props.setStreamConfig({ variables: { config: this.state.streamConfig } });
            if(this.props.camera.streaming){
                this.props.start({ variables: { stream: true, record: false } });
            }
        };
        

        return (
            <Grid container spacing={24}>
                <Grid item xs={12}>
                    <div style={{ marginTop: 24 }}>
                        {this.props.camera.streaming && <LiveStream 
                            port={this.props.camera.wsPort}
                            config={JSON.parse(this.props.camera.streamConfig)}
                            width={LIVE_STREAM_WIDTH}
                            height={LIVE_STREAM_HEIGHT} />}
                    </div>
                </Grid>
                <Grid item xs={4}>
                    <Button variant="contained" color="primary" onClick={record} fullWidth >
                        {this.props.camera.recording ? "Recording..." : "Record"}
                    </Button>
                </Grid>
                <Grid item xs={4}>
                    <Button variant="contained" color="primary" onClick={this.props.image} fullWidth >
                        Picture
                    </Button>
                </Grid>
                <Grid item xs={4}>
                    <Button variant="contained" color="primary" onClick={stream} fullWidth >
                        {this.props.camera.streaming ? "Streaming..." : "Stream"}
                    </Button>
                </Grid>

                <Grid item xs={4}>
                    <JSONConfig
                        name={"Video"}
                        json={this.state.videoConfig}
                        onChange={json => this.setState({ videoConfig: json })} />
                </Grid>
                <Grid item  xs={4}>
                    <JSONConfig
                        name={"Picture"}
                        json={this.state.imageConfig}
                        onChange={json => this.setState({ imageConfig: json })} />
                </Grid>
                <Grid item xs={4}>
                    <JSONConfig
                        name={"Stream"}
                        json={this.state.streamConfig}
                        onChange={json => this.setState({ streamConfig: json })} />
                </Grid>

                <Grid item xs={4}>
                    <Button variant="contained" color="primary" onClick={updateVideo} fullWidth >
                        Update
                    </Button>
                </Grid>
                <Grid item xs={4}>
                    <Button variant="contained" color="primary" onClick={updateImage} fullWidth >
                        Update
                    </Button>
                </Grid>
                <Grid item xs={4}>
                    <Button variant="contained" color="primary" onClick={updateStream} fullWidth >
                        Update
                    </Button>
                </Grid>
            </Grid>
        );
    }
}

export default function Camera(props){
    return (
        <Composer components={[
            <Query query={CAMERA_QUERY} pollInterval={1000}/>,
            <Mutation mutation={CAMERA_START_MUTATION}/>,
            <Mutation mutation={CAMERA_STOP_MUTATION}/>,
            <Mutation mutation={CAMERA_IMAGE_MUTATION}/>,
            <Mutation mutation={CAMERA_SET_VIDEO_CONFIG_MUTATION}/>,
            <Mutation mutation={CAMERA_SET_STREAM_CONFIG_MUTATION}/>,
            <Mutation mutation={CAMERA_SET_IMAGE_CONFIG_MUTATION}/>,
        ]}>
            {([query, start, stop, image, setVideoConfig, setStreamConfig, setImageConfig]) => {

                let { loading, error, data } = query;
                if (loading) return <p>Loading...</p>;
                if (error) return <p>Error</p>;

                return (
                    <CameraInner 
                        camera={data.camera}
                        start={start}
                        stop={stop}
                        image={image}
                        setVideoConfig={setVideoConfig}
                        setStreamConfig={setStreamConfig}
                        setImageConfig={setImageConfig}
                    />
                );

            }}

        </Composer>
    );
}
