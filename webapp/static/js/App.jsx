import React from "react"
import UV4LVideo from './UV4LVideo'

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
                <UV4LVideo url={'ws://172.16.0.110:8081/webrtc'} alive={this.state.alive} />
            </div>
        );
	}
}
