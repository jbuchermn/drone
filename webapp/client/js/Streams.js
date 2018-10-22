import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import 'react-vis/dist/style';
import {
    XYPlot,
    XAxis,
    YAxis,
    HorizontalGridLines,
    LineSeries,
    DiscreteColorLegend
} from 'react-vis';

function Plot(props){
    let time = new Date().getTime()/1000;

    return (
        <div>
            <DiscreteColorLegend items={props.streams.map(s=>s.name)} />
            <XYPlot
                width={props.width}
                height={props.height}>

                <HorizontalGridLines />
                {props.streams.map(s=>{
                    let data = s.t.map((t, i) => ({x: t - time, y: s.val[i]}));
                    return (
                        <LineSeries
                            data={data}/>
                    );

                })}
                <XAxis />
                <YAxis />
            </XYPlot>
        </div>
    );

}

export default function Streams(props){
    return (
        <Query query={gql`{ streams { id, name, t, val } }`} pollInterval={1000}>
            {({ loading, error, data }) => {
                if (loading) return <p>Loading...</p>;
                if (error) return <p>Error</p>;

                let cameraStreams = data.streams.filter(s => 
                    s.name.includes("raspicam") || s.name.includes("file") || s.name.includes("websocket"));
                let otherStreams = data.streams.filter(s => !cameraStreams.includes(s));

                cameraStreams = cameraStreams.sort((a, b) => a.name.localeCompare(b.name));
                otherStreams = otherStreams.sort((a, b) => a.name.localeCompare(b.name));

                return (
                    <div>
                        <Plot streams={cameraStreams} width={props.width} height={props.height}/>
                        {otherStreams.map(s =>
                            <Plot streams={[s]} width={props.width} height={props.height}/>)}
                    </div>
                )
            }}

        </Query>
    );
}
