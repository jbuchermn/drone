import React from "react";
import Composer from "react-composer";
import { Query, Mutation } from "react-apollo";
import gql from "graphql-tag";
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';


import LiveStream from './LiveStream'

const CAMERA_QUERY = gql`
query Camera{
    camera{
        id,
        recording,
        config,
        wsPort 
    }
}
`

const TAKE_VIDEO_MUTATION = gql`
mutation TakeVideo($config: String!, $stream: Boolean!){ 
    takeVideo(config: $config, stream: $stream){
        camera{
            id,
            recording,
            config,
            wsPort
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

const TAKE_PICTURE_MUTATION = gql`
mutation TakePicture($config: String!){ 
    takePicture(config: $config){
        camera{
            id,
            recording,
            config,
            wsPort
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

const START_STREAM_MUTATION = gql`
mutation StartStream($config: String!){ 
    startStream(config: $config){
        camera{
            id,
            recording,
            config,
            wsPort
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


function CameraButtons(props){
    const record = props.recording ? props.startStream : props.takeVideo;
    return (
        <div>
            <Button variant="contained" color="primary" onClick={record}>
                {props.recording ? "Recording" : "Record"}
            </Button>
            <Button variant="contained" color="primary" onClick={props.takePicture}>
                Picture
            </Button>
            <Button variant="contained" color="primary" onClick={props.startStream}>
                Update
            </Button>
        </div>
    )
}

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
              label={""}
              multiline
              rows={20}
              rowsMax={20}
              value={this.state.text}
              onChange={evt => this.handleChange(evt.target.value)}
              margin={"normal"}
              helperText={this.props.name}
              variant={"outlined"}
            />
        );
    }

}

class CameraInner extends React.Component{
    constructor(props){
        super(props);

        this.state = {
            videoConfig: JSON.stringify({
                format: "h264",
                resolution: [1920, 1080],
                bitrate: 20000000,
                framerate: 24
            }),
            pictureConfig: JSON.stringify({}),
            streamConfig: null
        };
    }

    static getDerivedStateFromProps(props, state){
        return {
            streamConfig: state.streamConfig || props.camera.config
        };
    }

    render(){
        const _takePicture = () => {
            this.props.takePicture({
                variables: {
                    config: this.state.pictureConfig
                }
            });
        };
        const _takeVideo = () => {
            this.props.takeVideo({
                variables: {
                    config: this.state.videoConfig,
                    stream: true
                }
            });
        };
        const _startStream = () => {
            this.props.startStream({
                variables: {
                    config: this.state.streamConfig
                }
            });
        };
        return (
            <div>
                <LiveStream 
                    port={this.props.camera.wsPort}
                    config={JSON.parse(this.props.camera.config)}
                    width={this.props.width}
                    height={this.props.height} />
                <CameraButtons
                    recording={this.props.camera.recording}
                    takeVideo={_takeVideo}
                    takePicture={_takePicture}
                    startStream={_startStream} />
                <JSONConfig
                    name={"Video"}
                    json={this.state.videoConfig}
                    onChange={json => this.setState({ videoConfig: json })} />
                <JSONConfig
                    name={"Picture"}
                    json={this.state.pictureConfig}
                    onChange={json => this.setState({ pictureConfig: json })} />
                <JSONConfig
                    name={"Stream"}
                    json={this.state.streamConfig}
                    onChange={json => this.setState({ streamConfig: json })} />
            </div>
        );
    }
}

export default function Camera(props){
    return (
        <Composer components={[
            <Query query={CAMERA_QUERY} pollInterval={1000}/>,
            <Mutation mutation={TAKE_VIDEO_MUTATION}/>,
            <Mutation mutation={TAKE_PICTURE_MUTATION}/>,
            <Mutation mutation={START_STREAM_MUTATION}/>,
        ]}>
            {([query, takeVideo, takePicture, startStream]) => {


                let { loading, error, data } = query;
                if (loading) return <p>Loading...</p>;
                if (error) return <p>Error</p>;

                return (
                    <CameraInner 
                        width={props.width}
                        height={props.height}
                        camera={data.camera}
                        takeVideo={takeVideo}
                        takePicture={takePicture}
                        startStream={startStream} />
                );

            }}

        </Composer>
    );
}
