import {useWebSocket} from '../websocket';
import { decodeAsync } from "@msgpack/msgpack";


export interface NotificationEvent {
    type: string
    data: any
}

interface NotificationEventListener {
    (evt: NotificationEvent): void;
}

class NotificationEventListenerObject implements EventListenerObject {
    listener: NotificationEventListener

    constructor(listener: NotificationEventListener) {
        this.listener = listener;
    }

    async decodeFromBlob(blob: Blob) {
        return await decodeAsync(blob.stream());
    }

    handleEvent(event: MessageEvent) {
        const type = event.type;
        this.decodeFromBlob(event.data).then((data) => {
            this.listener({type, data});
        });
    }
}

export class NotificationsEventSource {
    ws: WebSocket
    listeners: Map<NotificationEventListener, NotificationEventListenerObject>;

    constructor(ws: WebSocket) {
        this.ws = ws;
        this.listeners = new Map<NotificationEventListener, NotificationEventListenerObject>();
    }

    addNotificationEventListener(type: string, listener: NotificationEventListener ) {
        const webSocketListener = new NotificationEventListenerObject(listener);
        this.ws.addEventListener(type, webSocketListener);
        this.listeners.set(listener, webSocketListener);
    }

    removeNotificationEventListener(type: string, listener: NotificationEventListener) {
        const webSocketListener = this.listeners.get(listener);

        if (webSocketListener !== undefined) {
            this.ws.removeEventListener(type, webSocketListener);
        }
    }
}

var notifications: NotificationsEventSource | undefined;

export const useNotifications = () => {
    const ws = useWebSocket();

    if (notifications === undefined && ws !== undefined ) {
        notifications = new NotificationsEventSource(ws);
    }

    return notifications;
}
