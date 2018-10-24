import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';

import Header from './Header';
import Footer, { FooterPlaceHolder } from './Footer';

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


export default class App extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            selectedPage: 0
        };
    }

    render(){
        return (
            <Query
                query={HEARTBEAT_QUERY}
                fetchPolicy={"network-only"}
                pollInterval={1000}>
                {({ loading, error, data }) => {
                    const connected = !(loading || error);
                    return (
                        <React.Fragment>
                            <Header connected={connected} />
                            {connected && this.state.selectedPage == 0 && <Camera />}
                            {connected && this.state.selectedPage == 1 && <Gallery />}
                            {connected && this.state.selectedPage == 2 && <div/>}
                            {connected && this.state.selectedPage == 3 && <Streams />}
                            {connected && 
                                <Footer 
                                    currentTab={this.state.selectedPage}
                                    onTabChange={(evt, value) => this.setState({ selectedPage: value })}/>}
                            <FooterPlaceHolder />
                        </React.Fragment>
                    );
                }}
            </Query>
        );
    }
}

