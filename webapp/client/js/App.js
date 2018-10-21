import React from "react";
import { Query } from "react-apollo";
import gql from "graphql-tag";


import { IP, PORT } from './env';
import Camera from './Camera';

export default function App(props){
    return [
        <Camera />,
        <Query query={gql`{ gallery { id, entries { id, kind, name } } }`}>
            {({ loading, error, data }) => {
                if (loading) return <p>Loading...</p>;
                if (error) return <p>Error :(</p>;

                return data.gallery.entries.map(e => (
                    <p><a 
                        href={"http://" + IP +":" + PORT + "/gallery/" + e.kind + "/" + e.name} 
                        target={"_blank"}>{e.name}</a></p>
                ));
            }}
        </Query>
    ];
    
}

