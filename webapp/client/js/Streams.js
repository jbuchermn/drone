import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import { Paper } from '@material-ui/core';
import 'react-vis/dist/style';
import {
    FlexibleWidthXYPlot,
    XAxis,
    YAxis,
    HorizontalGridLines,
    LineSeries,
    DiscreteColorLegend
} from 'react-vis';

const PLOT_HEIGHT = 600;

const Plot = props => {
    let time = new Date().getTime()/1000;

    return (
        <Paper style={styles.paper}>
            <DiscreteColorLegend items={props.streams.map(s=>s.name)} />
            <div style={{ height: PLOT_HEIGHT }}>
                <FlexibleWidthXYPlot
                    height={PLOT_HEIGHT}>
                    <HorizontalGridLines />
                    {props.streams.map(s=>{
                        let data = s.t.map((t, i) => ({x: t - time, y: s.val[i]}));
                        return (
                            <LineSeries
                                key={s.name}
                                data={data}/>
                        );

                    })}
                    <XAxis />
                    <YAxis />
                </FlexibleWidthXYPlot>
            </div>
        </Paper>
    );
}

export default props =>
    <Query query={gql`{ streams { id, name, t, val } }`} pollInterval={1000}>
        {({ loading, error, data }) => {
            if (loading) return <p>Loading...</p>;
            if (error) return <p>Error</p>;

            let cameraStreams = data.streams.filter(s => 
                s.name.includes("Camera") || s.name.includes("File") || s.name.includes("Websocket"));
            let otherStreams = data.streams.filter(s => !cameraStreams.includes(s));

            cameraStreams = cameraStreams.sort((a, b) => a.name.localeCompare(b.name));
            otherStreams = otherStreams.sort((a, b) => a.name.localeCompare(b.name));

            return (
                <React.Fragment>
                    {cameraStreams.length > 0 && <Plot streams={cameraStreams} />}
                    {otherStreams.map(s =>
                        <Plot streams={[s]} key={s.name}/>)}
                </React.Fragment>
            )
        }}
    </Query>

const styles = {
    paper: {
        padding: 16,
        marginLeft: 16,
        marginRight: 16,
        marginTop: 16,
        marginBottom: 0,
    }
}
