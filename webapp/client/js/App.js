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

import { IP, PORT } from './env';
import Camera from './Camera';

export default function App(props){
    return [
        <Camera />,
        <Query query={gql`{ gallery { id, entries { id, kind, name } } }`}>
            {({ loading, error, data }) => {
                if (loading) return <p>Loading...</p>;
                if (error) return <p>Error</p>;

                return data.gallery.entries.map(e => (
                    <p><a 
                        href={"http://" + IP +":" + PORT + "/gallery/" + e.kind + "/" + e.name} 
                        target={"_blank"}>{e.name}</a></p>
                ));
            }}
        </Query>,
        <Query query={gql`{ streams { id, name, t, val } }`} pollInterval={1000}>
            {({ loading, error, data }) => {
                if (loading) return <p>Loading...</p>;
                if (error) return <p>Error</p>;

                let time = new Date().getTime()/1000;

                return (
                    <XYPlot
                        width={1280}
                        height={720}>
                        <HorizontalGridLines />
                        {data.streams.map(s=>{
                            let data = s.t.map((t, i) => ({x: t - time, y: s.val[i]}));
                            return (
                                <LineSeries
                                    data={data}/>
                            );

                        })}
                        <XAxis />
                        <YAxis />
                        <DiscreteColorLegend items={data.streams.map(s=>s.name)} />
                    </XYPlot>
                );
            }}

        </Query>
    ];
    
}

