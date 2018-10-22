import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';

import Gallery from './Gallery';
import Camera from './Camera';
import Streams from './Streams';

const HEARTBEAT_QUERY = gql`
query {
    camera {
        id
    }
}
`;

function NotConnected(props){
    return <p>Not connected</p>
}

export default function App(props){
    return (
        <Query
            query={HEARTBEAT_QUERY}
            fetchPolicy={"network-only"}
            pollInterval={1000}>
            {({ loading, error, data }) => {
                if (loading || error) return <NotConnected />;
                return (
                    <div>
                        <Camera width={1280} height={720}/>
                        <Streams width={1280} height={720}/>
                        <Gallery />
                    </div>
                );
            }}
        </Query>
    );
    
}

