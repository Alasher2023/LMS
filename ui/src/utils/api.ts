import axios from 'axios'
import { useLoadingStore } from '@/stores/loading'

const api = axios.create({
  baseURL: '/api',
})

api.interceptors.request.use(
  (config) => {
    const loadingStore = useLoadingStore()
    loadingStore.setLoading(true)
    return config
  },
  (error) => {
    const loadingStore = useLoadingStore()
    loadingStore.setLoading(false)
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => {
    const loadingStore = useLoadingStore()
    loadingStore.setLoading(false)
    return response
  },
  (error) => {
    const loadingStore = useLoadingStore()
    loadingStore.setLoading(false)
    return Promise.reject(error)
  }
)

export default api
