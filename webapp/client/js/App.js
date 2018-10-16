import React from "react";
import { Query } from "react-apollo";
import gql from "graphql-tag";

import LiveStream from './LiveStream';

export default function App(props){
    return [
        <Query query={gql`{ camera { id, config, wsPort } }`}>
            {({ loading, error, data }) => {
                if (loading) return <p>Loading...</p>;
                if (error) return <p>Error :(</p>;

                return (
                    <LiveStream port={data.camera.wsPort} config={JSON.parse(data.camera.config)} />
                );
            }}
        </Query>,
        <Query query={gql`{ gallery { id, entries { id, kind, name } } }`}>
            {({ loading, error, data }) => {
                if (loading) return <p>Loading...</p>;
                if (error) return <p>Error :(</p>;

                return data.gallery.entries.map(e => (
                    <p><a href={"/gallery/" + e.kind + "/" + e.name} target={"_blank"}>{e.name}</a></p>
                ));
            }}
        </Query>
    ];
    
}

