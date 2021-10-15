import {useWebSocket} from '../websocket';
import { decodeAsync } from "@msgpack/msgpack";


export interface NotificationEvent {
    action: string
    payload: any
}

interface NotificationEventListener {
    (evt: NotificationEvent): void;
}

class NotificationEventListenerObject implements EventListenerObject {
    listeners: Map<string, NotificationEventListener[]>

    constructor() {
        this.listeners = new Map<string, NotificationEventListener[]>();
    }

    async decodeFromBlob(blob: Blob) {
        return await decodeAsync(blob.stream());
    }

    handleEvent(event: MessageEvent) {
        const type = event.type;
        this.decodeFromBlob(event.data).then((data: any) => {
            if (data.type !== '@@OREMDA') {
                return;
            }

            const action = data.action;
            const listeners = this.listeners.get(action)
            if (listeners === undefined) {
                return;
            }


            for (const listener of listeners)  {
                listener(data)
            }
        });
    }

    addNotificationEventListener(type: string, listener: NotificationEventListener ) {
        let listeners = this.listeners.get(type)
        if (listeners === undefined) {
            this.listeners.set(type, [listener])
        }
        else {
            listeners.push(listener);
        }
    }

    removeNotificationEventListener(type: string, listener: NotificationEventListener) {
        let listeners = this.listeners.get(type)
        if (listeners === undefined) {
            return;
        }

        const index = listeners.indexOf(listener, 0);
        if (index > -1) {
            listeners.splice(index, 1);
        }
    }
}

export class NotificationsEventSource {
    ws: WebSocket
    listener:  NotificationEventListenerObject;

    constructor(ws: WebSocket) {
        this.ws = ws;
        this.listener = new NotificationEventListenerObject();
        this.ws.addEventListener("message", this.listener)
    }

    addNotificationEventListener(type: string, listener: NotificationEventListener ) {
        this.listener.addNotificationEventListener(type, listener);
    }

    removeNotificationEventListener(type: string, listener: NotificationEventListener) {
        this.listener.removeNotificationEventListener(type, listener);
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
