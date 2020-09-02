import React, { useState, useEffect } from 'react';
import '../App.css';
import { Form, FormGroup, Input, Button } from 'reactstrap';
//import dictionary from '../dictionary';
import { Container, Row, Col } from 'reactstrap';
import Image_Viewer from './image_viewer';
import Clipboard from './clipboard';
import Help from './help';

class Chat extends React.Component{

    timeout = 250;

    constructor(props) {
        super(props);
        this.state = {
            messages: [],
            clipboard: [],
            chat_message: '',
            ws: null,
            set_of_functions: null, //coming from backend, never get changed
            dictionary: null, //coming from message
            filtered_dictionary: null, //filtered
            //active_answer: dictionary[0].id,
            active_answer: null,
            valid_answers: [],
            regex: "",
            valid: true,
            backendConnection: false,
            selected_message: {
                text: null,
                image: null
            },
            awaiting_message: false
        }    
    }
 
    componentDidMount () {
        this.connect();
    }

    componentDidUpdate () {
        
        
    }

    escapeRegex(s) {
        return s.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    }

    matchDictionary = (input) => {
        var patt = new RegExp(this.escapeRegex(this.state.chat_message), 'i');
        let d = this.state.dictionary.filter(entry => patt.test(entry.keywords));
        this.setState({
            filtered_dictionary: d,
            active_answer: d.length > 0 ? d[0].id : null
        })
    }

    imageZoom(text, image){
        this.setState({
            selected_message: {
                text: text,
                image: image
            }
        })
    }

    imageDisable = () => {
        this.setState({
            selected_message: {
                text: null,
                image: null
            }
        })
    }

    chatinput_handler(event){
        if(!this.state.regex){
            this.setState({
                chat_message: event.target.value 
            }, () => this.matchDictionary(this.state.chat_message));
        }else{
            //let patt = /(\d+)(\.\d+)?/;
            //let patt = new RegExp('(\\d+)(\\.\\d+)?');
            let patt = new RegExp(this.state.regex)
            let match = event.target.value.match(patt)
            let dict = []
            let valid = true
            if(match !== null && match[0].length === event.target.value.length){ 
                dict = 
                    [{id : event.target.value,
                    keywords : event.target.value,
                    display : event.target.value + " is a valid answer.",
                    write: event.target.value,
                    execute : event.target.value}]    
            }else if(event.target.value.length === 0){
                dict = []
            }else{
                dict = 
                    [{id : event.target.value,
                    keywords : event.target.value,
                    display : event.target.value + " is not a valid answer.",
                    write: event.target.value,
                    execute : event.target.value}]
                valid = false
            }
            this.setState({
                filtered_dictionary: dict,
                chat_message: event.target.value,
                valid: valid,
                active_answer: dict.length > 0  ? dict[0].id : null        
            })    
        }
    }

    keyPress(event){
        console.log(this.state)
        if(event.keyCode === 9 && this.state.active_answer !== null){
            event.preventDefault();
            //get index number of active answer
            //increase the index number by one if possible else 0
            let index = this.state.filtered_dictionary.map(function(e) { return e.id; }).indexOf(this.state.active_answer)
            index < this.state.filtered_dictionary.length-1 ? index++ : index = 0
            this.setState({
                active_answer:(this.state.filtered_dictionary[index].id)
            }, () => {
                this.refs[this.state.active_answer].scrollIntoView({inline: 'center', block: 'nearest' ,behavior: 'smooth'});
            })
        }else if(event.keyCode === 13 && this.state.valid && this.state.active_answer !== null && !this.state.awaiting_message){
            event.preventDefault();
            let entry = this.state.filtered_dictionary.filter(e => {
                return e.id === this.state.active_answer
            })[0]
            this.sendMessage(entry.execute)
            let today = new Date()
            this.setState(prevState => ({
                messages: [...prevState.messages, {id: Math.floor(Math.random() * 1000000), senderId:"User", text: entry.write, time: this.getTime()}]
            }), () => {
                this.setState({ chat_message: '', filtered_dictionary: this.state.dictionary, active_answer: null });
            })
        }else if(event.keyCode === 13 && !this.state.awaiting_message){
            event.preventDefault();
            let raw_message = this.state.chat_message
            this.sendMessage(raw_message)
            let today = new Date()
            this.setState(prevState => ({
                messages: [...prevState.messages, {id: Math.floor(Math.random() * 1000000), senderId:"User", text: raw_message, time: this.getTime()}]
            }), () => {
                this.setState({ chat_message: '', filtered_dictionary: this.state.dictionary, active_answer: null });
            })
        }else if(event.keyCode === 13){
            event.preventDefault();
        }
    }

    selectionPressed(command){
        if(!this.state.awaiting_message){
            this.sendMessage(command.execute)
            let today = new Date()
            this.setState(prevState => ({
                messages: [...prevState.messages, {id: Math.floor(Math.random() * 1000000), senderId:"User", text: command.write, time: this.getTime()}]
            }), () => {
                this.setState({ chat_message: '', filtered_dictionary: this.state.dictionary });
            })
        }
    }

    connect = () => {
        var ws = new WebSocket("ws://127.0.0.1:9000");
        let that = this; // cache the this
        var connectInterval;

        // websocket onopen event listener
        ws.onopen = () => {
            console.log("Websocket connected.")
            this.setState({ ws: ws, backendConnection: true });

            that.timeout = 250; // reset timer to 250 on open of websocket connection 
            clearTimeout(connectInterval); // clear Interval on on open of websocket connection
        };

        // websocket onclose event listener
        ws.onclose = e => {
            console.log(
                `Socket is closed. Reconnect will be attempted in ${Math.min(
                    10000 / 1000,
                    (that.timeout + that.timeout) / 1000
                )} second.`,
                e.reason
            );
            this.setState({ backendConnection: false });

            that.timeout = that.timeout + that.timeout; //increment retry interval
            connectInterval = setTimeout(this.check, Math.min(10000, that.timeout)); //call check function after timeout
        };

        // websocket onerror event listener
        ws.onerror = err => {
            console.error(
                "Socket encountered error: ",
                err.message,
                "Closing socket"
            );
            this.setState({ backendConnection: false });
            ws.close();
        };

        ws.onmessage = evt => {     
            console.log("New message")    
            console.log(evt.data)
            let message = JSON.parse(evt.data)

            if(message.type === "message"){
                let today = new Date()
                this.setState(prevState => ({
                    messages: [...prevState.messages, {id: Math.floor(Math.random() * 1000000), senderId:"ERIC", text: message.text, image: message.image, time: this.getTime()}],
                    awaiting_message: false
                }), () =>{
                    console.log(this.refs)
                    console.log(this.state.messages)
                    //timeout required, otherwise it would scroll before image is rendered
                    var that = this;
                    setTimeout(function() {
                        if(that.state.messages.length != 0){
                            that.refs[that.state.messages[that.state.messages.length-1].id].scrollIntoView({ behavior: 'smooth' }) 
                        }
                    }, 10);
                })

                if(message["valid-answers"] !== ""){
                    if(message["valid-answers"].type === "selection"){
                        let dict = []
                        message["valid-answers"].value.forEach((v) =>{
                            dict.push({
                                id : v,
                                keywords : v,
                                display : v,
                                write: v,
                                execute : v
                            })
                        })
                        //dict.push({id: "cancel", keywords: "cancel", display: "cancel", write: "cancel", execute: "cancel"})
                        this.setState({
                            dictionary: dict,
                            filtered_dictionary: dict,
                            active_answer: dict.length > 0 ? dict[0].id : null
                        })
                    }else if(message["valid-answers"].type === "regex"){
                        this.setState({
                            dictionary: [],
                            filtered_dictionary: [],
                            regex: message["valid-answers"].value
                        })
                    }
                }
                else{
                    this.setState({
                        dictionary: this.state.set_of_functions,
                        filtered_dictionary: this.state.set_of_functions,
                    }, () => this.setState({
                        active_answer: this.state.dictionary[0].id
                    }))
                }
                
                if(message["clipboard"] !== ""){
                    let clip = message["clipboard"]
                    let clips = this.state.clipboard
                    for(let c of clips){
                        if(c.context === clip.id){
                            c.active = false
                        }
                    }
                    clips.unshift({
                        id: Math.random(),
                        context: clip.id,
                        text: clip.value,
                        active: true
                    })
                    this.setState({
                        clipboard: clips
                    }, ()=>{
                        //this.refs[this.state.clipboard[this.state.clipboard.length-1].id].scrollIntoView({ behavior: 'auto' })
                    })
                }
            } 
            else if(message.type === "init"){
                console.log(message.functions)
                this.setState({
                    set_of_functions: message.functions,
                    dictionary: message.functions,
                    filtered_dictionary: message.functions,
                    active_answer: message.functions[0].id
                })
            }
        }
    }

    check = () => {
        const { ws } = this.state;
        if (!ws || ws.readyState === WebSocket.CLOSED) this.connect(); //check if websocket instance is closed, if so call `connect` function.
    }

    sendMessage=(data)=>{
        const {ws} = this.state 
        try {
            ws.send(JSON.stringify({'answer' : data})) 
        } catch (error) {
            console.log(error) 
        }
        this.setState({
            regex: "",
            valid: true,
            awaiting_message: true
        }, () =>{
            this.refs["awaiting"].scrollIntoView({ behavior: 'smooth' })
        })
    }

    getTime(){
        let today = new Date()
        return(today.getHours() + ":" + (today.getMinutes() < 10 ? '0' : '') + today.getMinutes())
    }

    render() {
        const messages = this.state.messages
        const clipboard = this.state.clipboard
        const chat_message = this.state.chat_message
        const filtered_dictionary = this.state.filtered_dictionary
        const valid = this.state.valid
        const active_answer = this.state.active_answer
        const backendConnection = this.state.backendConnection
        const selected_image = this.state.selected_message.image
        const selected_text = this.state.selected_message.text
        const awaiting_message = this.state.awaiting_message
        if(this.state.set_of_functions){
            return (
                <Container className="chat">
                    {selected_image ? 
                        <Image_Viewer image={selected_image} text={selected_text} imageDisable={this.imageDisable}/>   
                    :""}    
                    <Row>
                        <Col xs="9">
                            <div className="messages">
                                <ul className="message-list">                 
                                    {messages.map((message, i) => (
                                        <li key={message.id} ref={message.id}> 
                                                    {message.senderId === "User" ?
                                                    <Container className="user-message">
                                                        <Row>
                                                            <Col xs={{size: 7, offset: 5}}>
                                                            <div className="message-text">
                                                                <div dangerouslySetInnerHTML={{__html: message.text}} />
                                                                <div className="time">{message.time}</div>
                                                            </div>
                                                            </Col>
                                                            {/* <Col xs="1" style={{padding:"0px"}}>
                                                                <div className="avatar">
                                                                </div>
                                                            </Col> */}
                                                        </Row>
                                                    </Container>
                                                :   
                                                    <Container className="bot-message">
                                                        <Row>
                                                            {/* <Col xs="1">
                                                                {messages[i-1].senderId !== message.senderId ?
                                                                <div className="avatar"> */}
                                                                    {/* <img src={require('./robot_dark.png')}/> */}
                                                                {/* </div>
                                                                : ''}
                                                            </Col> */}
                                                            <Col xs="7">
                                                                <div className="message-text">
                                                                    {message.image !== "" ?                                                                     
                                                                        <img src={"data:image/png;base64," +  message.image} onClick={() => this.imageZoom(message.text, message.image)}/>
                                                                        : ""
                                                                    }
                                                                    <div dangerouslySetInnerHTML={{__html: message.text}} />
                                                                    <div className="time">{message.time}</div>
                                                                </div>
                                                            </Col>
                                                            </Row>
                                                    </Container>
                                                }
                                            {/* <div className="message-info">
                                                {message.senderId === "ERIC" ? <img src={require('./robot_dark.png')}/> : ''}
                                                {message.senderId} {today.getHours() + ":" + today.getMinutes()}
                                            </div> */}
                                        </li>
                                    ))}
                                    { awaiting_message ?
                                    <li key={"awaiting"} ref={"awaiting"}>
                                        <Container className="bot-message">
                                            <Row>
                                                <Col xs="7">
                                                <div className="message-text">
                                                    <div className="awaiting"></div>
                                                </div>
                                                </Col>
                                            </Row>
                                        </Container>
                                    </li>
                                    : ""}
                                </ul>
                            </div>
                        </Col>
                        <Col xs="3" className="right-panel">
                            <Clipboard clipboard={clipboard}/>
                            {
                                filtered_dictionary.find(item => item.id === active_answer) ?
                                <Help description={filtered_dictionary.find(item => item.id === active_answer).description}/>
                                : <Help description=""/>
                            }
                            
                        </Col>
                    </Row>
                    <div className="selections">
                        {backendConnection ?
                        <ul className="selection">
                            {filtered_dictionary.map(entry => (
                                <li key={entry.id} ref={entry.id}>
                                    <Button className={entry.id === active_answer? "selection_button_selected" : "selection_button"} disabled={!valid} onClick={() => this.selectionPressed(entry)}>{entry.display}</Button>
                                </li>
                            ))
                            }
                        </ul>
                        :<div><img src={require('./robot_dark.png')}/>ERIC is offline.</div>}
                    </div>
                    <div className="input">
                        <Form>
                            <FormGroup>
                                <Input type="text" name="message" id="message" placeholder="Type a message or tab commands" disabled={!backendConnection} autoComplete="off" value={chat_message} onKeyDown={this.keyPress.bind(this)} onChange={this.chatinput_handler.bind(this)}/>
                            </FormGroup>
                        </Form>
                    </div>
                </Container>
            );
    }
    else{return ""}
    }
}

export default Chat;
