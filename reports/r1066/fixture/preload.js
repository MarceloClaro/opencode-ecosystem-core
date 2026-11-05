const { contextBridge, ipcRenderer } = require('electron');
contextBridge.exposeInMainWorld('fixture', {
  add: (a, b) => ipcRenderer.invoke('fixture:add', a, b)
});
