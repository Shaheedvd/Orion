import React, { useEffect, useState } from 'react'

export default function SettingsPanel(){
  const [apiKey, setApiKey] = useState('')
  const [offlineModelPath, setOfflineModelPath] = useState('')
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [passphrase, setPassphrase] = useState('')

  useEffect(()=>{
    fetch('http://127.0.0.1:8000/status').then(r=>r.json()).then(js=>{
      setOfflineModelPath(js.offline_model||'')
    }).catch(()=>{})
  },[])

  const save = async ()=>{
    await fetch('http://127.0.0.1:8000/config', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({openai_api_key: apiKey, offline_model: offlineModelPath, voice: voiceEnabled})})
    alert('Settings saved (encrypted locally)')
  }

  const loadSecret = async ()=>{
    if(!passphrase) { alert('Enter passphrase to unlock secret'); return }
    const r = await fetch('http://127.0.0.1:8000/config/load_secret', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({passphrase})})
    const js = await r.json()
    if(js.ok){ alert('Secret unlocked') } else { alert('Failed to unlock: ' + (js.error || 'unknown')) }
  }

  return (
    <div className="settings">
      <h3>Settings</h3>
      <label>OpenAI API Key
        <input type="password" value={apiKey} onChange={e=>setApiKey(e.target.value)} placeholder="sk-... (optional)" />
      </label>
      <label>Offline model path
        <input value={offlineModelPath} onChange={e=>setOfflineModelPath(e.target.value)} placeholder="path/to/model.gguf" />
      </label>
      <label>Unlock stored secret (passphrase)
        <input type="password" value={passphrase} onChange={e=>setPassphrase(e.target.value)} placeholder="passphrase" />
        <button onClick={loadSecret}>Unlock</button>
      </label>
      <label>
        <input type="checkbox" checked={voiceEnabled} onChange={e=>setVoiceEnabled(e.target.checked)} /> Enable voice
      </label>
      <button onClick={save}>Save</button>
    </div>
  )
}
