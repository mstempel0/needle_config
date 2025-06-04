const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  runPython: (file1, file2, a, b, c) =>
    ipcRenderer.invoke('run-config', { file1, file2, a, b, c }),
});

contextBridge.exposeInMainWorld('versions', {
  node: () => process.versions.node,
  chrome: () => process.versions.chrome,
  electron: () => process.versions.electron,
});
