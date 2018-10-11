import React from 'react'
import {
    View,
    StyleSheet,
    Dimensions
} from 'react-native'

import {
    RTCView
} from 'react-native-webrtc'

export default class Videostream extends React.Component {
	render () {
        return (
            <View>
                {this.props.stream && 
                        <RTCView streamURL={this.props.stream.toURL()} style={styles.stream}/>}
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
