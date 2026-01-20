import { useEffect, useRef, useState, useCallback } from 'react'

// Use relative WebSocket URL when behind nginx, or full URL for direct dev access
const WS_URL = import.meta.env.VITE_WS_URL || (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/ws'

export const useWebSocket = (onMessage) => {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef(null)
  const onMessageRef = useRef(onMessage)

  // Update the ref when onMessage changes (without triggering reconnection)
  useEffect(() => {
    onMessageRef.current = onMessage
  }, [onMessage])

  useEffect(() => {
    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (onMessageRef.current) {
          onMessageRef.current(data)
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    ws.onclose = () => {
      setIsConnected(false)
      console.log('WebSocket disconnected')
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, []) // Empty dependency array - only connect once

  return { isConnected, wsRef }
}
