import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import { Paper } from '@material-ui/core';
import Gallery from 'react-grid-gallery';

import { ADDR } from './env';

const GALLERY_QUERY = gql`
query {
    gallery {
        id,
        entries {
            id,
            kind,
            name,
            path,
            thumbnailPath,
            thumbnailWidth,
            thumbnailHeight
        }
    }
}
`

export default props =>
    <Query query={GALLERY_QUERY} pollInterval={1000}>
        {({ loading, error, data }) => {
            if (loading) return <p>Loading...</p>;
            if (error) return <p>Error</p>;

            const img = data.gallery.entries.map(e => ({
                src: ADDR + "/gallery/" + e.path,
                thumbnail: ADDR + "/gallery/" + e.thumbnailPath,
                thumbnailWidth: e.thumbnailWidth,
                thumbnailHeight: e.thumbnailHeight
            }));

            return (
                <div style={{ margin: 16 }} >
                    <Gallery images={img} enableImageSelection={false} />
                </div>
            );
        }}
    </Query>
