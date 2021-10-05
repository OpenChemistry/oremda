var webSocket: WebSocket | undefined

export const useWebSocket = () => {

    return webSocket;
}

export const setWebSocket = (ws: WebSocket) => {
    webSocket = ws;
}

