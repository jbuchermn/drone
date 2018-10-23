import React from 'react';
import {
    Paper,
    Tabs,
    Tab
} from '@material-ui/core';

export const FooterPlaceHolder = props =>
    <div style={{position: 'absolute', width: '100%', height: 80, zIndex: -1000}} />

export default props => 
    <div style={{position: 'fixed', left: 8, bottom: 8, right: 8}}>
        <Paper>
            <Tabs 
                value={props.currentTab}
                onChange={props.onTabChange}
                indicatorColor="primary"
                textColor="primary"
                centered>
                <Tab label="Camera" />
                <Tab label="Gallery" />
                <Tab label="MAVLink" />
                <Tab label="Stats" />
            </Tabs>
        </Paper>
    </div>
