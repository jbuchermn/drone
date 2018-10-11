import React from 'react';
import Videostream from './Videostream';
import Signaling from './Signaling';

export default class App extends React.Component {
    constructor(props){
        super(props);
        this.state = { alive: true };
    }
	render () {
        return (
            <div>
                <input 
                    type="checkbox" 
                    onChange={()=>this.setState({ alive: !this.state.alive })} 
                    defaultChecked={this.state.alive}/> Alive
                <Signaling alive={this.state.alive} janusEndpoint={'/janus'} >
                    <Videostream />
                </Signaling>
            </div>
        );
    }
}
