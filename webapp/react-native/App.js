import React, { Component } from 'react';
import {
    StyleSheet,
    Text,
    View
} from 'react-native';

import Signaling from './js/Signaling'
import Videostream from './js/Videostream'

export default class App extends Component {
    render() {
        return (
            <View style={styles.container}>
                <Signaling alive={true} janusEndpoint='http://172.16.0.105:5000/janus'>
                    <Videostream />
                </Signaling>
            </View>
        );
    }
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        backgroundColor: '#F5FCFF',
    },
});
