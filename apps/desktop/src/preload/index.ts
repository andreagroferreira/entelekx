import { contextBridge, ipcRenderer } from 'electron'

const exposedAPI = {
  getBackendPort: () => ipcRenderer.invoke('get-backend-port'),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
  getWizardCompleted: () => ipcRenderer.invoke('get-wizard-completed'),
  setWizardCompleted: (value: boolean) => ipcRenderer.invoke('set-wizard-completed', value),
  closeWizard: () => ipcRenderer.invoke('close-wizard'),
}

contextBridge.exposeInMainWorld('electronAPI', exposedAPI)

export type ElectronAPI = typeof exposedAPI

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
