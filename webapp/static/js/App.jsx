import React from "react"
import Videostream from './Videostream'

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
                <Videostream addr={'172.16.0.110'} useSSL={false} alive={this.state.alive} />
            </div>
        );
	}
}
