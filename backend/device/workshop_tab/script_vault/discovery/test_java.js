// Test if Java is available in the process

Java.perform(function() {
    console.log("[Java Test] Inside Java.perform callback");
    console.log("[Java Test] Android Version: " + Java.androidVersion);
    send({ type: 'test', success: true, message: "Java runtime works", androidVersion: Java.androidVersion });
});

