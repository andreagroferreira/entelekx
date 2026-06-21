import { app, BrowserWindow, ipcMain, shell } from 'electron'
import path from 'node:path'
import { spawn } from 'node:child_process'
import log from 'electron-log'

const DEFAULT_BACKEND_PORT = 7349

let mainWindow: BrowserWindow | null = null
let backendProcess: ReturnType<typeof spawn> | null = null

function getBackendPort(): number {
  // In a real app we would scan for an available port.
  return DEFAULT_BACKEND_PORT
}

async function startBackend(): Promise<boolean> {
  const port = getBackendPort()
  log.info(`Starting EntelekX backend on port ${port}`)

  // Phase 0: assume the backend wheel/venv is unpacked next to the app.
  const backendExe = path.join(process.resourcesPath, 'backend', 'bin', 'entelekx')
  const args = ['serve', '--host', '127.0.0.1', '--port', String(port)]

  return new Promise((resolve) => {
    try {
      backendProcess = spawn(backendExe, args, {
        cwd: process.resourcesPath,
        env: { ...process.env, ENTELEKX_PORT: String(port) },
        stdio: 'pipe',
      })

      backendProcess.stdout?.on('data', (data: Buffer) => {
        log.info(`[backend] ${data.toString().trim()}`)
      })

      backendProcess.stderr?.on('data', (data: Buffer) => {
        log.error(`[backend] ${data.toString().trim()}`)
      })

      backendProcess.on('error', (err) => {
        log.error('Failed to start backend', err)
        resolve(false)
      })

      backendProcess.on('exit', (code) => {
        log.warn(`Backend exited with code ${code}`)
        backendProcess = null
      })

      // Give the backend a moment to start, then health-check.
      setTimeout(async () => {
        try {
          const res = await fetch(`http://127.0.0.1:${port}/health`)
          resolve(res.ok)
        } catch {
          resolve(false)
        }
      }, 2000)
    } catch (err) {
      log.error('Backend spawn error', err)
      resolve(false)
    }
  })
}

function stopBackend() {
  if (backendProcess) {
    backendProcess.kill()
    backendProcess = null
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  const port = getBackendPort()
  mainWindow.loadURL(`http://127.0.0.1:${port}`)

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

app.whenReady().then(async () => {
  const ok = await startBackend()
  if (!ok) {
    log.error('Backend failed to start; opening window anyway for diagnostics')
  }
  createWindow()
})

app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

app.on('before-quit', () => {
  stopBackend()
})

ipcMain.handle('get-backend-port', () => getBackendPort())
ipcMain.handle('get-app-version', () => app.getVersion())
ipcMain.handle('open-external', (_event, url: string) => {
  shell.openExternal(url)
})
