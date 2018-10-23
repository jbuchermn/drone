import React from 'react';
import {
    AppBar,
    Toolbar,
    IconButton,
    Typography
} from '@material-ui/core';

import MenuIcon from '@material-ui/icons/Menu';


export default props =>
    <AppBar position="sticky">
        <Toolbar>
            <Typography variant="title" color="inherit">
                Quadcopter: {props.connected ? "Connected" : "Waiting..."}
            </Typography>
        </Toolbar>
    </AppBar>
