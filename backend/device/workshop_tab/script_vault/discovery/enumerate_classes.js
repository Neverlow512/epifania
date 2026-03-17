// Enumerate all loaded Java classes
// This script runs in the target process via Frida

function enumerateClasses() {
    try {
        var classes = Java.enumerateLoadedClassesSync();
        send({ type: 'classes', data: classes });
    } catch (e) {
        send({ type: 'classes', data: [], error: e.toString() });
    }
}

// Wait for Java VM to be ready, then enumerate
Java.performNow(enumerateClasses);

