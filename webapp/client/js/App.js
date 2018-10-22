import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';

import { ADDR } from './env';
import Camera from './Camera';
import Streams from './Streams';

export default function App(props){
    return (
        <div>
            <Camera width={1280} height={720}/>
            <Streams width={1280} height={720}/>
            <Query query={gql`{ gallery { id, entries { id, kind, name } } }`} pollInterval={1000}>
                {({ loading, error, data }) => {
                    if (loading) return <p>Loading...</p>;
                    if (error) return <p>Error</p>;

                    return data.gallery.entries.map(e => (
                        <p><a 
                            href={ADDR + "/gallery/" + e.kind + "/" + e.name} 
                            target={"_blank"}>{e.name}</a></p>
                    ));
                }}
            </Query>
        </div>
    );
    
}

