// Enumerate exports for native modules
// Uses RPC exports so the script can be loaded once and called multiple times

rpc.exports = {
    getExports: function(moduleName) {
        try {
            var module = Process.getModuleByName(moduleName);
            var exports = module.enumerateExports();
            
            return {
                success: true,
                module_name: moduleName,
                exports: exports
            };
        } catch (e) {
            return {
                success: false,
                module_name: moduleName,
                exports: [],
                error: e.toString()
            };
        }
    }
};
