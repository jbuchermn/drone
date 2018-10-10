import React from 'react'
import {
    View,
    StyleSheet,
    Dimensions
} from 'react-native'
import {
    RTCView
} from 'react-native-webrtc'
import UV4LSignaling from './UV4LSignaling'
import JanusSignaling from './JanusSignaling'

const Signaling = JanusSignaling;

export default class Videostream extends React.Component {
    constructor(props){
        super(props);
        this.state = { stream: null, signaling: null };
        this.timer = null;
    }


    tick() {
        let stream = this.state.signaling ? this.state.signaling.stream : null;
        if(stream !== this.state.stream){
            this.setState({ stream });
        }
    }

    componentDidMount(){
        this.timer = setInterval(
            () => this.tick(),
            200
        );
    }

    componentWillUnmount() {
        clearInterval(this.timer);
    }

    /*
     * Misuse getDerivedStateFromProps to take care of signaling state changes
     */
    static getDerivedStateFromProps(nextProps, prevState){
        let setupSignaling = () => {
            let signaling = new Signaling(nextProps.addr, nextProps.useSSL);
            signaling.open();
            return signaling;
        }

        if(!nextProps.alive && prevState.signaling){
            prevState.signaling.close();
            return { stream: null, signaling: null };

        }else if(nextProps.alive && !prevState.signaling){
            return { signaling: setupSignaling() };

        }else if(nextProps.alive && prevState.signaling){
            if(prevState.signaling.addr != nextProps.addr || prevState.signaling.useSSL != nextProps.useSSL){
                prevState.signaling.close();
                return { stream: null, signaling: setupSignaling() };
            }
        }

        return null;
    }

	render () {
        if(this.state.stream) console.log(this.state.stream.toURL());
        return (
            <View>
                {this.state.stream && <RTCView streamURL={this.state.stream.toURL()} key={"stream"} style={styles.stream}/>}
            </View>
        );
	}
}

const styles = StyleSheet.create({
    stream: {
        width: Dimensions.get('window').width,
        height: Dimensions.get('window').height
    },
})
