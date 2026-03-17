// Enumerate all loaded Java class names using frida-java-bridge
// Returns only class names for instant enumeration (<1s for any app size)
// ClassLoader extraction is done separately via scan_classloader.ts
import Java from "frida-java-bridge";

declare function send(message: any, data?: ArrayBuffer | null): void;

Java.perform(() => {
    const classes = Java.enumerateLoadedClassesSync();
    send({ type: 'classes', data: classes });
});
