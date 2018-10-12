import React, { Component } from 'react'
import { StyleSheet, View, Button } from 'react-native'
import GstPlayer, { GstState } from 'react-native-gstreamer'

export default class App extends Component {

    uri1 = "http://mirrors.standaloneinstaller.com/video-sample/jellyfish-25-mbps-hd-hevc.mp4"
    uri2 = "http://mirrors.standaloneinstaller.com/video-sample/Panasonic_HDC_TM_700_P_50i.mp4"

    constructor(props, context) {
        super(props, context)
        this.state = { uri: this.uri1 }
    }

    render() {
        return (
            <View style={styles.container}>
                <GstPlayer
                    style={styles.videoPlayer}
                    uri={this.state.uri}
                    ref="GstPlayer"
                    autoPlay={true}
                />
                <View style={styles.controlBar}>
                    <Button title="uri1" onPress={() => this.setState({ uri: this.uri1 })}></Button>
                    <Button title="uri2" onPress={() => this.setState({ uri: this.uri2 })}></Button>
                    <Button title="Stop" onPress={() => this.refs.GstPlayer.stop()}></Button>
                    <Button title="Pause" onPress={() => this.refs.GstPlayer.pause()}></Button>
                    <Button title="Play" onPress={() => this.refs.GstPlayer.play()}></Button>
                </View>
            </View>
        )
    }
}

const styles = StyleSheet.create({
    container: { flex: 1 },
    controlBar: {
        flexDirection: "row",
        justifyContent: "space-between"
    },
    videoPlayer: { flex: 1 }
})
