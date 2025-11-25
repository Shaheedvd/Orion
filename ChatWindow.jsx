import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'

function Message({m}){
  return <div className={`message ${m.role}`}><div className="bubble">{m.text}</div></div>
}

export default function ChatWindow(){
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const messagesRef = useRef(null)

  useEffect(()=>{ // load recent conversation
    fetch('http://127.0.0.1:8000/memory/search?query=_recent&limit=20').then(r=>r.json()).then(js=>{ if(js.items) setMessages(js.items.map(i=>({role:i.role||'assistant', text:i.text||i.summary||JSON.stringify(i)}))) }).catch(()=>{})
  },[])

  const send = async () =>{
    const payload = { message: input, tools: [] }
    setMessages(prev => [...prev, {role:'user', text: input}])
    setInput('')
    setStreaming(true)
    try{
      // Try streaming endpoint
      const r = await fetch('http://127.0.0.1:8000/chat/stream', {method:'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload)})
      if (!r.ok) throw new Error('Stream request failed')
      const reader = r.body.getReader()
      let decoder = new TextDecoder('utf-8')
      let assistantText = ''
      setMessages(prev=>[...prev, {role:'assistant', text: ''}])
      while(true){
        const {done, value} = await reader.read()
        if(done) break
        const chunk = decoder.decode(value)
        assistantText += chunk
        // update last assistant message
        setMessages(prev=>{
          const copy = [...prev]
          copy[copy.length-1] = {role:'assistant', text: assistantText}
          return copy
        })
      }
    }catch(e){
      setMessages(prev=>[...prev, {role:'assistant', text: 'Error: '+String(e)}])
    }
    setStreaming(false)
  }

  const uploadImage = async (ev) =>{
    const f = ev.target.files[0]
    if(!f) return
    const fd = new FormData(); fd.append('file', f)
    const r = await fetch('http://127.0.0.1:8000/tools/image/upload', {method:'POST', body: fd})
    const js = await r.json()
    setMessages(prev=>[...prev, {role:'system', text: `Image uploaded: ${js.path || js.name}` }])
  }

  return (
    <div className="chat-window">
      <div className="messages" ref={messagesRef}>
        {messages.map((m, i)=><Message key={i} m={m} />)}
      </div>
      <div className="composer">
        <input value={input} onChange={e=>setInput(e.target.value)} placeholder="Ask Oriun..." />
        <input type="file" accept="image/*" onChange={uploadImage} />
        <button onClick={send} disabled={streaming || !input}>Send</button>
      </div>
    </div>
  )
}
