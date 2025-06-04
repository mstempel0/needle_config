const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');
const { spawn } = require('node:child_process');

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false,
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  win.loadFile('index.html');
}

ipcMain.handle('run-config', async (event, args) => {
  const { file1, file2, a, b, c } = args;

  return new Promise((resolve, reject) => {
    const pythonProcess = spawn('python3', [
      path.join(__dirname, 'python/run_config.py'), 
      file1,
      file2,
      a.toString(),
      b.toString(),
      c.toString(),
    ]);

    let result = '';
    let error = '';

    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      error += data.toString();
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        resolve(result);
      } else {
        reject(error || `Python script exited with code ${code}`);
      }
    });
  });
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
