import { app, BrowserWindow, ipcMain, shell } from 'electron'
import fs from 'node:fs'
import path from 'node:path'
import { spawn } from 'node:child_process'
import log from 'electron-log'

const DEFAULT_BACKEND_PORT = 7349

let mainWindow: BrowserWindow | null = null
let wizardWindow: BrowserWindow | null = null
let backendProcess: ReturnType<typeof spawn> | null = null

function getDataDir(): string {
  const dir = path.join(app.getPath('home'), '.entelekx')
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true })
  }
  return dir
}

function getWizardFlagPath(): string {
  return path.join(getDataDir(), 'wizard-completed')
}

function isWizardCompleted(): boolean {
  try {
    return fs.existsSync(getWizardFlagPath())
  } catch {
    return false
  }
}

function setWizardCompleted(value: boolean): void {
  const flagPath = getWizardFlagPath()
  if (value) {
    fs.writeFileSync(flagPath, new Date().toISOString(), 'utf-8')
  } else {
    try {
      fs.unlinkSync(flagPath)
    } catch {
      // ignore
    }
  }
}

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

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 900,
    minHeight: 600,
    titleBarStyle: 'hiddenInset',
    show: false,
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

  mainWindow.once('ready-to-show', () => {
    mainWindow?.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

function createWizardWindow() {
  wizardWindow = new BrowserWindow({
    width: 900,
    height: 680,
    minWidth: 760,
    minHeight: 560,
    resizable: true,
    title: 'Welcome to EntelekX',
    titleBarStyle: 'default',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, '../preload/index.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  const port = getBackendPort()
  wizardWindow.loadURL(`http://127.0.0.1:${port}/setup`)

  wizardWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  wizardWindow.once('ready-to-show', () => {
    wizardWindow?.show()
  })

  wizardWindow.on('closed', () => {
    wizardWindow = null
  })
}

async function launch() {
  const ok = await startBackend()
  if (!ok) {
    log.error('Backend failed to start; opening window anyway for diagnostics')
  }

  if (isWizardCompleted()) {
    createMainWindow()
  } else {
    createWizardWindow()
  }
}

app.whenReady().then(launch)

app.on('window-all-closed', () => {
  stopBackend()
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    if (isWizardCompleted()) {
      createMainWindow()
    } else {
      createWizardWindow()
    }
  }
})

app.on('before-quit', () => {
  stopBackend()
})

ipcMain.handle('get-backend-port', () => getBackendPort())
ipcMain.handle('get-app-version', () => app.getVersion())
ipcMain.handle('open-external', (_event, url: string) => {
  shell.openExternal(url)
})
ipcMain.handle('get-wizard-completed', () => isWizardCompleted())
ipcMain.handle('set-wizard-completed', (_event, value: boolean) => {
  setWizardCompleted(value)
})
ipcMain.handle('close-wizard', () => {
  if (wizardWindow) {
    wizardWindow.close()
    wizardWindow = null
  }
  if (!mainWindow) {
    createMainWindow()
  }
})
