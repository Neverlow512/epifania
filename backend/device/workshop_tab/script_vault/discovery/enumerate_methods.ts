// Enumerate methods for Java classes using frida-java-bridge
// Uses RPC exports so the script can be loaded once and called multiple times
import Java from "frida-java-bridge";

declare const rpc: {
    exports: Record<string, (...args: any[]) => any>;
};

interface MethodInfo {
    name: string;
    signature: string;
    return_type: string;
    parameters: string[];
    is_native: boolean;
    is_public: boolean;
    is_private: boolean;
    is_protected: boolean;
    is_static: boolean;
    is_final: boolean;
    is_synchronized: boolean;
    is_abstract: boolean;
}

interface MethodResult {
    success: boolean;
    class_name: string;
    methods: MethodInfo[];
    error?: string;
    error_type?: string;
}

rpc.exports = {
    getMethods(className: string): Promise<MethodResult> {
        return new Promise((resolve) => {
            Java.perform(() => {
                let cls: any;
                
                try {
                    cls = Java.use(className);
                } catch (e: any) {
                    resolve({
                        success: false,
                        class_name: className,
                        methods: [],
                        error: e.toString(),
                        error_type: "unable_to_load"
                    });
                    return;
                }
                
                try {
                    const methods: MethodInfo[] = [];
                    
                    const declaredMethods = cls.class.getDeclaredMethods();
                    for (let i = 0; i < declaredMethods.length; i++) {
                        const method = declaredMethods[i];
                        const modifiers = method.getModifiers();
                        
                        // Get parameter types safely
                        const paramTypes: string[] = [];
                        try {
                            const params = method.getParameterTypes();
                            const paramCount = params.length;
                            for (let j = 0; j < paramCount; j++) {
                                paramTypes.push(params[j].getName());
                            }
                        } catch (paramErr) {
                            // If we can't get params, leave empty
                        }
                        
                        // Get return type safely
                        let returnType = "unknown";
                        try {
                            returnType = method.getReturnType().getName();
                        } catch (retErr) {
                            // If we can't get return type, use unknown
                        }
                        
                        methods.push({
                            name: method.getName(),
                            signature: method.toString(),
                            return_type: returnType,
                            parameters: paramTypes,
                            is_native: (modifiers & 0x0100) !== 0,
                            is_public: (modifiers & 0x0001) !== 0,
                            is_private: (modifiers & 0x0002) !== 0,
                            is_protected: (modifiers & 0x0004) !== 0,
                            is_static: (modifiers & 0x0008) !== 0,
                            is_final: (modifiers & 0x0010) !== 0,
                            is_synchronized: (modifiers & 0x0020) !== 0,
                            is_abstract: (modifiers & 0x0400) !== 0
                        });
                    }
                    
                    resolve({
                        success: true,
                        class_name: className,
                        methods: methods
                    });
                } catch (e: any) {
                    resolve({
                        success: false,
                        class_name: className,
                        methods: [],
                        error: e.toString(),
                        error_type: "method_extraction_failed"
                    });
                }
            });
        });
    }
};
