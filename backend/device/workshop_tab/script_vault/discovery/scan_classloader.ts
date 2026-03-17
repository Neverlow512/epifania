// Scan ClassLoader for Java classes using frida-java-bridge
// Uses RPC exports so the script can be loaded once and called multiple times
import Java from "frida-java-bridge";

declare const rpc: {
    exports: Record<string, (...args: any[]) => any>;
};

interface ClassLoaderResult {
    success: boolean;
    name: string;
    loader_type: string;
    loader_path: string | null;
    is_from_apk: boolean;
    error?: string;
}

rpc.exports = {
    scanClassLoader(className: string): Promise<ClassLoaderResult> {
        return new Promise((resolve) => {
            Java.perform(() => {
                try {
                    const cls = Java.use(className);
                    const loader = cls.class.getClassLoader();
                    const loaderType = loader ? loader.$className : "null";
                    const loaderPath = loader ? String(loader) : null;
                    
                    // Classes from APK use PathClassLoader, DexClassLoader, or InMemoryDexClassLoader
                    // System classes use BootClassLoader or have null loader
                    const isFromApk = loaderType !== "null" && 
                                     loaderType !== "java.lang.BootClassLoader";
                    
                    resolve({
                        success: true,
                        name: className,
                        loader_type: loaderType,
                        loader_path: loaderPath,
                        is_from_apk: isFromApk
                    });
                } catch (e: any) {
                    resolve({
                        success: false,
                        name: className,
                        loader_type: "unknown",
                        loader_path: null,
                        is_from_apk: false,
                        error: e.toString()
                    });
                }
            });
        });
    }
};
