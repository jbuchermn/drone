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
    DialogActions
} from '@material-ui/core';

import MenuIcon from '@material-ui/icons/Menu';

const SHUTDOWN_MUTATION = gql`
mutation Shutdown{ 
    shutdownServer
}
`

export default class Header extends React.Component{
    constructor(props){
        super(props);
        this.state = { dialogOpen: false }
    }

    render(){
        return (
            <AppBar position="sticky">
                <Toolbar>
                    <Typography variant="title" color="inherit" style={{ flex: 1 }}>
                        Quadcopter: {this.props.connected ? "Connected" : "Waiting..."}
                    </Typography>
                    <Mutation mutation={SHUTDOWN_MUTATION}>
                        {(shutdown) => {
                            if(this.props.connected){
                                const handleShutdown = () => {
                                    shutdown();
                                    this.setState({ dialogOpen: false });
                                }
                                return (
                                    <React.Fragment>
                                        <Button 
                                            color="inherit" 
                                            onClick={() => this.setState({ dialogOpen: true })}
                                        >Shutdown</Button>
                                        <Dialog
                                            open={this.state.dialogOpen}
                                            keepMounted
                                            onClose={() => this.setState({ dialogOpen: false })}
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
                                                    onClick={() => this.setState({ dialogOpen: false })}
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
