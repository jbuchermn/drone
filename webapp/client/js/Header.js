import React from 'react';
import { Mutation } from "react-apollo";
import gql from "graphql-tag";

import {
    AppBar,
    Toolbar,
    IconButton,
    Typography,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
    FormControlLabel,
    Checkbox
} from '@material-ui/core';

import MenuIcon from '@material-ui/icons/Menu';

const SHUTDOWN_MUTATION = gql`
mutation Shutdown{ 
    shutdownServer
}
`

const AUTOHOTSPOT_MUTATION = gql`
mutation AutoHotspot($config: String){
    autoHotspot(config: $config)
}
`

export default class Header extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            autoHotspotOpen: false,
            autoHotspotConfig: '',
            shutdownOpen: false
        };
    }

    render(){
        return (
            <AppBar position="sticky">
                <Toolbar>
                    <Typography variant="title" color="inherit" style={{ flex: 1 }}>
                        Quadcopter: {this.props.connected ? "Connected" : "Waiting..."}
                    </Typography>
                    <Mutation mutation={AUTOHOTSPOT_MUTATION}>
                        {(shutdown) => {
                            if(this.props.connected){
                                const handleAutoHotspot = () => {
                                    autoHotspot({ variables: { config: this.state.autoHotspotConfig } });
                                    this.setState({ autoHotspotOpen: false });
                                }

                                return (
                                    <React.Fragment>
                                        <Button 
                                            color="inherit" 
                                            onClick={() => this.setState({ autoHotspotOpen: true })}
                                        >Hotspot</Button>
                                        <Dialog
                                            open={this.state.autoHotspotOpen}
                                            keepMounted
                                            onClose={() => this.setState({ autoHotspotOpen: false })}
                                        >
                                            <DialogTitle>
                                                Open Hotspot
                                            </DialogTitle>
                                            <DialogContent>
                                                <FormControlLabel
                                                    control={
                                                        <Checkbox
                                                            checked={this.state.autoHotspotConfig != 'force'}
                                                            onChange={() => this.setState(state => ({
                                                                autoHotspotConfig: state.autoHotspotConfig == 
                                                                    'force' ? '' : 'force'
                                                            }))}
                                                        />
                                                    }
                                                    label="Search for known Wifis first"
                                                />
                                            </DialogContent>
                                            <DialogActions>
                                                <Button 
                                                    onClick={() => this.setState({ autoHotspotOpen: false })}
                                                    color="primary">
                                                    Cancel
                                                </Button>
                                                <Button onClick={handleAutoHotspot} color="primary">
                                                    Restart Wifi
                                                </Button>
                                            </DialogActions>
                                        </Dialog>
                                    </React.Fragment>
                                );
                            }else{
                                return null;
                            }
                        }}
                    </Mutation>
                    <Mutation mutation={SHUTDOWN_MUTATION}>
                        {(shutdown) => {
                            if(this.props.connected){
                                const handleShutdown = () => {
                                    shutdown();
                                    this.setState({ shutdownOpen: false });
                                }
                                return (
                                    <React.Fragment>
                                        <Button 
                                            color="inherit" 
                                            onClick={() => this.setState({ shutdownOpen: true })}
                                        >Shutdown</Button>
                                        <Dialog
                                            open={this.state.shutdownOpen}
                                            keepMounted
                                            onClose={() => this.setState({ shutdownOpen: false })}
                                        >
                                            <DialogTitle>
                                                Shutdown
                                            </DialogTitle>
                                            <DialogContent>
                                                <DialogContentText>
                                                    Confirm shutdown?
                                                </DialogContentText>
                                            </DialogContent>
                                            <DialogActions>
                                                <Button 
                                                    onClick={() => this.setState({ shutdownOpen: false })}
                                                    color="primary">
                                                    Cancel
                                                </Button>
                                                <Button onClick={handleShutdown} color="primary">
                                                    Shutdown
                                                </Button>
                                            </DialogActions>
                                        </Dialog>
                                    </React.Fragment>
                                );
                            }else{
                                return null;
                            }
                        }}
                    </Mutation>
                </Toolbar>
            </AppBar>
        );
    }
}
