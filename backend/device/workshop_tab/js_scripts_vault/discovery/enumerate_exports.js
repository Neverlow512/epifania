// Enumerate exports for a specific native module
// This script runs in the target process via Frida
//
// Variables to be replaced:
//   {{MODULE_NAME}} - The module name (e.g., libnative.so)

try {
    var module = Process.getModuleByName('{{MODULE_NAME}}');
    var exports = module.enumerateExports();
    
    console.log("[Native Exports] Found " + exports.length + " exports in " + '{{MODULE_NAME}}');
    
    send({
        type: 'exports', 
        data: exports, 
        success: true
    });
} catch (e) {
    console.log("[Native Exports] Error enumerating " + '{{MODULE_NAME}}' + ": " + e.toString());
    
    send({
        type: 'exports', 
        data: [], 
        success: false, 
        error: e.toString()
    });
}

