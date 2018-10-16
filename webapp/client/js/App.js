import React from "react";
import { Query } from "react-apollo";
import gql from "graphql-tag";

import LiveStream from './LiveStream';

export default function App(props){
    return (
        <Query query={gql`{ camera { config, wsPort }}`}>
            {({ loading, error, data }) => {
                if (loading) return <p>Loading...</p>;
                if (error) return <p>Error :(</p>;

                return (
                    <LiveStream port={data.camera.wsPort} config={JSON.parse(data.camera.config)} />
                );
            }}
        </Query>
    );
    
}

