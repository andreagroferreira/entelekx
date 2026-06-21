import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  getBackendPort: () => ipcRenderer.invoke('get-backend-port'),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  openExternal: (url: string) => ipcRenderer.invoke('open-external', url),
})

export type ElectronAPI = typeof window.electronAPI

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
