// Enumerate all loaded Java classes using frida-java-bridge
import Java from "frida-java-bridge";

Java.perform(() => {
    const classes = Java.enumerateLoadedClassesSync();
    send({ type: 'classes', data: classes });
});

