import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import { Paper } from '@material-ui/core';

import { ADDR } from './env';

export default function Gallery(props){
    return (
        <Paper>
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
        </Paper>
    );
}
