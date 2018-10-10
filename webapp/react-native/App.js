import React, { Component } from 'react';
import {
    StyleSheet,
    Text,
    View
} from 'react-native';

import Videostream from './js/Videostream'

export default class App extends Component {
    render() {
        return (
            <View style={styles.container}>
                <Videostream alive={true} addr={'janus.conf.meetecho.com'} useSSL={true} />
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
