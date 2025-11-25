const { app, BrowserWindow, ipcMain, dialog } = require('electron')
const path = require('path')

function createWindow(){
  const win = new BrowserWindow({
    width: 1100,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
    }
  })
  const url = process.env.ELECTRON_START_URL || `file://${path.join(__dirname, 'src', 'index.html')}`
  win.loadURL(url)
}

function spawnBackendWithPassphrase(passphrase){
  const { spawn } = require('child_process')
  const fs = require('fs')
  const exePath = path.join(process.resourcesPath || process.cwd(), 'backend.exe')
  if (!fs.existsSync(exePath)) return false
  try{
    // pass passphrase via environment variable for the spawned process only
    const env = Object.assign({}, process.env)
    env['ORIUN_PASSPHRASE'] = passphrase
    const child = spawn(exePath, [], { detached: true, stdio: 'ignore', env })
    child.unref()
    return true
  }catch(e){ console.error('Failed to spawn backend exe:', e); return false }
}

ipcMain.handle('passphrase:submit', async (event, passphrase) => {
  // spawn backend if packaged; else just return OK
  if (app.isPackaged) {
    const ok = spawnBackendWithPassphrase(passphrase)
    return { ok }
  }
  // not packaged: set env var for current process (dev) and return ok
  process.env.ORIUN_PASSPHRASE = passphrase
  return { ok: true }
})

app.whenReady().then(()=>{ createWindow() })
app.on('window-all-closed', ()=>{ if(process.platform !== 'darwin') app.quit() })

app.whenReady().then(createWindow)
app.on('window-all-closed', ()=>{ if(process.platform !== 'darwin') app.quit() })
