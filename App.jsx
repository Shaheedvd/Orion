import React, { useEffect, useState } from 'react'
import ChatWindow from './ChatWindow'
import SettingsPanel from './SettingsPanel'
import PermissionsPanel from './PermissionsPanel'
import ReactModal, {useState} from 'react'

function FirstRunModal({onUnlock}){
  const [pass, setPass] = React.useState('')
  const [exists, setExists] = React.useState(null)
  React.useEffect(()=>{ fetch('http://127.0.0.1:8000/config/secret_exists').then(r=>r.json()).then(js=>setExists(js.exists)).catch(()=>setExists(false)) },[])
  if(exists === null) return null
  if(!exists) return null
  const submit = async ()=>{
    if(window.oriun && window.oriun.submitPassphrase){
      const res = await window.oriun.submitPassphrase(pass)
      if(res && res.ok){ onUnlock(pass); return }
      alert('Failed to spawn backend with passphrase')
    }
    // dev fallback: call backend endpoint directly
    const r = await fetch('http://127.0.0.1:8000/config/load_secret', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({passphrase:pass})})
    const js = await r.json()
    if(js.ok){ onUnlock(pass) } else { alert('Failed to unlock: ' + (js.error||'unknown')) }
  }

  return (
    <div className="first-run-modal">
      <h3>Unlock your secrets</h3>
      <p>Enter your passphrase to unlock encrypted API keys stored on disk.</p>
      <input type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder="passphrase" />
      <button onClick={submit}>Unlock</button>
    </div>
  )
}

export default function App(){
  const [connected, setConnected] = useState(false)
  const [unlocked, setUnlocked] = useState(false)
  useEffect(()=>{
    // ping backend status
    fetch('http://127.0.0.1:8000/status').then(r=>r.json()).then(()=>setConnected(true)).catch(()=>setConnected(false))
  },[])

  return (
    <div className="app-root">
      {!unlocked && <FirstRunModal onUnlock={async (pass) => { const r = await fetch('http://127.0.0.1:8000/config/load_secret', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({passphrase:pass})}); const js = await r.json(); if(js.ok) setUnlocked(true); else alert('Failed to unlock: '+(js.error||'unknown')) }} />}
      <header className="topbar">
        <h1>Oriun Desktop AI</h1>
        <div className="status">{connected? 'Backend: Connected' : 'Backend: Offline'}</div>
      </header>
      <main className="main">
        <ChatWindow />
        <aside className="sidebar">
          <SettingsPanel />
          <PermissionsPanel />
        </aside>
      </main>
    </div>
  )
}
