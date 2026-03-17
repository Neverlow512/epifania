// Shared workshop client ID utility
// Ensures the same client ID is used across DeviceDetails and WorkshopTab

const STORAGE_KEY = 'workshop-client-id'

export function getWorkshopClientId() {
  let clientId = sessionStorage.getItem(STORAGE_KEY)
  if (!clientId) {
    clientId = `workshop-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    sessionStorage.setItem(STORAGE_KEY, clientId)
  }
  return clientId
}

