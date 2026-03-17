import { ref } from 'vue'
import axios from 'axios'
import { useToast } from '../../../../composables/useToast'

const ERROR_KEY_METRICS = 'system-metrics'
const ERROR_KEY_CONNECTIONS = 'network-connections'

export function useSystemMetrics(deviceSerial) {
  const toast = useToast()

  const cpu = ref({
    overall_percent: 0,
    top_consumers: []
  })

  const memory = ref({
    total_mb: 0,
    used_mb: 0,
    free_mb: 0,
    available_mb: 0,
    buffers_mb: 0,
    cached_mb: 0
  })

  const storage = ref({
    partition: '/data',
    total_gb: 0,
    used_gb: 0,
    free_gb: 0,
    percent_used: 0
  })

  const partitions = ref([])

  const network = ref({
    throughput: {
      bytes_sent_per_sec: 0,
      bytes_recv_per_sec: 0
    },
    recent_endpoints: []
  })

  const networkConnections = ref([])
  const networkConnectionsCount = ref(0)

  const fetchSystemMetrics = async () => {
    try {
      const baseUrl = `http://localhost:8000/api/devices/${deviceSerial}`

      const [
        cpuResult,
        memoryResult,
        storageResult,
        partitionsResult,
        networkResult
      ] = await Promise.allSettled([
        axios.get(`${baseUrl}/system/cpu`, { params: { top_n: 5 } }),
        axios.get(`${baseUrl}/system/memory`),
        axios.get(`${baseUrl}/system/storage`, { params: { partition: '/data' } }),
        axios.get(`${baseUrl}/system/storage/all`),
        axios.get(`${baseUrl}/system/network`)
      ])

      if (cpuResult.status === 'fulfilled') {
        cpu.value = cpuResult.value.data || cpu.value
      } else {
        console.error('Failed to fetch CPU stats:', cpuResult.reason)
      }

      if (memoryResult.status === 'fulfilled') {
        memory.value = {
          total_mb: memoryResult.value.data.total_mb ?? 0,
          used_mb: memoryResult.value.data.used_mb ?? 0,
          free_mb: memoryResult.value.data.free_mb ?? 0,
          available_mb: memoryResult.value.data.available_mb ?? 0,
          buffers_mb: memoryResult.value.data.buffers_mb ?? 0,
          cached_mb: memoryResult.value.data.cached_mb ?? 0
        }
      } else {
        console.error('Failed to fetch memory stats:', memoryResult.reason)
      }

      if (storageResult.status === 'fulfilled') {
        storage.value = storageResult.value.data || storage.value
      } else {
        console.error('Failed to fetch storage stats:', storageResult.reason)
      }

      if (partitionsResult.status === 'fulfilled') {
        partitions.value = partitionsResult.value.data?.partitions ?? []
      } else {
        console.error('Failed to fetch storage partitions:', partitionsResult.reason)
      }

      if (networkResult.status === 'fulfilled') {
        network.value = networkResult.value.data || network.value
      } else {
        console.error('Failed to fetch network stats:', networkResult.reason)
      }

      const hasFailures = [
        cpuResult,
        memoryResult,
        storageResult,
        partitionsResult,
        networkResult
      ].some(result => result.status === 'rejected')

      if (hasFailures) {
        toast.error('Some system metrics could not be fetched', ERROR_KEY_METRICS)
      } else {
        toast.clearError(ERROR_KEY_METRICS)
      }
    } catch (err) {
      console.error('Failed to fetch system metrics:', err)
      toast.error('Failed to fetch system metrics', ERROR_KEY_METRICS)
    }
  }

  const fetchNetworkConnections = async () => {
    try {
      const baseUrl = `http://localhost:8000/api/devices/${deviceSerial}`
      const response = await axios.get(`${baseUrl}/system/network/connections`)
      networkConnections.value = response.data.connections || []
      networkConnectionsCount.value = response.data.count ?? networkConnections.value.length
      toast.clearError(ERROR_KEY_CONNECTIONS)
    } catch (err) {
      console.error('Failed to fetch network connections:', err)
      toast.error('Failed to fetch network connections', ERROR_KEY_CONNECTIONS)
    }
  }

  return {
    cpu,
    memory,
    storage,
    partitions,
    network,
    networkConnections,
    networkConnectionsCount,
    fetchSystemMetrics,
    fetchNetworkConnections
  }
}


