const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('oriun', {
  submitPassphrase: (p) => ipcRenderer.invoke('passphrase:submit', p),
  onPassphraseResult: (cb) => ipcRenderer.on('passphrase:result', (event, arg) => cb(arg))
})
