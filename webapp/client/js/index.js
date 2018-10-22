import React from "react";
import ReactDOM from "react-dom";
import ApolloClient from "apollo-boost";
import { ApolloProvider } from "react-apollo";
import App from "./App";
import { ADDR } from "./env";

const client = new ApolloClient({ uri: ADDR + "/graphql" });

const Root = () => (
    <ApolloProvider client={client}>
        <App />
    </ApolloProvider>
);

ReactDOM.render(<Root />, document.getElementById("content"));
