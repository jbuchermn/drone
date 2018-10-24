import React from 'react';
import Composer from "react-composer";
import { Query, Mutation } from 'react-apollo';
import gql from 'graphql-tag';
import { 
    Paper,
    Typography,
    Grid,
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogContentText,
    DialogActions,
    TextField
} from '@material-ui/core';

import { ADDR } from './env';

const MAVLINK_QUERY = gql`
query {
    mavlinkProxy{
        id,
        addr
    }
}
`

const START_MAVLINK_MUTATION = gql`
mutation StartMAVLinkProxy($addr: String){
    startMAVLinkProxy(addr: $addr){
        id,
        addr
    }
}
`

const STOP_MAVLINK_MUTATION = gql`
mutation StopMAVLinkProxy{
    stopMAVLinkProxy{
        id,
        addr
    }
}
`

const AddressDialog = props =>
    <Dialog
        open={props.open}
        onClose={props.onClose}
    >
        <DialogTitle>Open MAVLink Connection</DialogTitle>
        <DialogContent>
            <DialogContentText>
                Enter IP:Port of GCS
            </DialogContentText>
            <TextField
                autoFocus
                margin="dense"
                label="Address"
                value={props.addr}
                onChange={evt => props.onAddrChange(evt.target.value)}
                fullWidth
            />
        </DialogContent>
        <DialogActions>
            <Button onClick={props.onClose} color="primary">
                Cancel
            </Button>
            <Button onClick={props.onConfirm} color="primary">
                Open Connection
            </Button>
        </DialogActions>
    </Dialog>


class MAVLinkInner extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            dialogOpen: false,
            dialogAddr: ''
        }
    }

    render(){
        const handleConfirm = () => {
            this.props.startMAVLink(this.state.dialogAddr);
            this.setState({ dialogOpen: false, dialogAddr: '' });
        }

        return (
            <React.Fragment>
                <Grid container spacing={16}>
                    <Grid item xs={12}>
                        <Paper style={{ padding: 16, marginTop: 24 }}>
                            <Typography variant="overline" align="center">
                                {this.props.mavlinkProxy.addr
                                    ? "Connected to '" + this.props.mavlinkProxy.addr + "'"
                                        : "Not connected"}
                            </Typography>
                        </Paper>
                    </Grid>
                    <Grid item xs={4}>
                        <Button variant="contained" color="secondary" fullWidth
                            disabled={!this.props.mavlinkProxy.addr} onClick={this.props.stopMAVLink}>
                            Disconnect
                        </Button>
                    </Grid>
                    <Grid item xs={4}>
                        <Button variant="contained" color="primary" fullWidth 
                            onClick={() => this.props.startMAVLink(null)}>
                            Connect here
                        </Button>
                    </Grid>
                    <Grid item xs={4}>
                        <Button variant="contained" color="primary" fullWidth
                            onClick={() => this.setState({ dialogOpen: true })}>
                            Connect to other GCS
                        </Button>
                    </Grid>
                </Grid>
                <AddressDialog 
                    open={this.state.dialogOpen}
                    addr={this.state.dialogAddr}
                    onAddrChange={addr => this.setState({ dialogAddr: addr })}
                    onClose={() => this.setState({ dialogOpen: false, dialogAddr: '' })}
                    onConfirm={handleConfirm}
                />
            </React.Fragment>

        );
    }

}

export default props =>
    <Composer components={[
        <Query query={MAVLINK_QUERY} pollInterval={1000}/>,
        <Mutation mutation={START_MAVLINK_MUTATION}/>,
        <Mutation mutation={STOP_MAVLINK_MUTATION}/>,
    ]}>
        {([query, startMAVLink, stopMAVLink]) => {

            let { loading, error, data } = query;
            if (loading) return <p>Loading...</p>;
            if (error) return <p>Error</p>;

            const startMAVLinkHere = () => {
                startMAVLink({
                    variables: {
                        addr: null
                    }
                });
            };


            return <MAVLinkInner
                        mavlinkProxy={data.mavlinkProxy}
                        startMAVLink={addr => startMAVLink({ variables: { addr } })}
                        stopMAVLink={stopMAVLink} />

        }}

    </Composer>
