// Enumerate all native modules (shared libraries)
// This script runs in the target process via Frida

console.log("[Native Module Enumeration] Starting...");

var modules = Process.enumerateModules();

console.log("[Native Module Enumeration] Found " + modules.length + " modules");

send({
    type: 'modules', 
    data: modules
});

