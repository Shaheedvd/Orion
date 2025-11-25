import React, { useEffect, useState } from 'react'

export default function PermissionsPanel(){
  const [perms, setPerms] = useState({drive:false,screen:false,automation:false})

  useEffect(()=>{ fetch('http://127.0.0.1:8000/config/permissions').then(r=>r.json()).then(js=>setPerms(js)).catch(()=>{}) },[])

  const toggle = async (k)=>{
    const v = !perms[k]
    await fetch('http://127.0.0.1:8000/config/permissions',{method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({[k]: v})})
    setPerms(p=>({...p, [k]: v}))
  }

  return (
    <div className="permissions">
      <h3>Permissions</h3>
      <div>
        <label><input type="checkbox" checked={perms.drive} onChange={()=>toggle('drive')} /> Local drive access</label>
      </div>
      <div>
        <label><input type="checkbox" checked={perms.screen} onChange={()=>toggle('screen')} /> Screen automation / capture</label>
      </div>
      <div>
        <label><input type="checkbox" checked={perms.automation} onChange={()=>toggle('automation')} /> Run automation tasks</label>
      </div>
    </div>
  )
}
