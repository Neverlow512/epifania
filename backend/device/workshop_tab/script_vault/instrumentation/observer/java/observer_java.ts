import Java from "frida-java-bridge";

declare const rpc: {
    exports: Record<string, (...args: any[]) => any>;
};

declare const Process: {
    getCurrentThreadId(): number;
};

declare function send(message: any, data?: any): void;

interface HookConfig {
    id: string;
    class_name: string;
    method_name: string;
    signature?: string;
    return_type?: string;
    parameters?: string[];
}

const hookStats: { [hookId: string]: { call_count: number } } = {};

function parseMethodSignature(signature: string): string[] | null {
    if (!signature) return null;
    
    const paramMatch = signature.match(/\(([^)]*)\)/);
    if (!paramMatch) return null;
    
    const paramString = paramMatch[1].trim();
    if (!paramString) return [];
    
    const params: string[] = [];
    let current = '';
    let depth = 0;
    
    for (let i = 0; i < paramString.length; i++) {
        const char = paramString[i];
        if (char === '<') {
            depth++;
        } else if (char === '>') {
            depth--;
        } else if (char === ',' && depth === 0) {
            if (current.trim()) {
                params.push(current.trim());
            }
            current = '';
            continue;
        }
        current += char;
    }
    
    if (current.trim()) {
        params.push(current.trim());
    }
    
    return params;
}

rpc.exports = {
    installHooks(hooks: HookConfig[]): Promise<{ success: boolean; results: any[] }> {
        return new Promise((resolve) => {
            Java.perform(() => {
                const results: any[] = [];
                
                hooks.forEach(hook => {
                    hookStats[hook.id] = { call_count: 0 };
                });
                
                for (const hook of hooks) {
                    try {
                        const cls = Java.use(hook.class_name);
                        const methodName = hook.method_name;
                        
                        if (!cls[methodName]) {
                            results.push({
                                hook_id: hook.id,
                                success: false,
                                error: `Method ${methodName} not found`
                            });
                            continue;
                        }
                        
                        let targetMethod;
                        
                        if (hook.signature) {
                            const params = parseMethodSignature(hook.signature);
                            if (params !== null && params.length > 0) {
                                try {
                                    targetMethod = cls[methodName].overload(...params);
                                } catch (overloadError) {
                                    console.log(`Overload failed for ${hook.class_name}.${methodName}, using default: ${overloadError}`);
                                    targetMethod = cls[methodName];
                                }
                            } else if (params !== null && params.length === 0) {
                                try {
                                    targetMethod = cls[methodName].overload();
                                } catch (overloadError) {
                                    console.log(`Empty overload failed for ${hook.class_name}.${methodName}, using default: ${overloadError}`);
                                    targetMethod = cls[methodName];
                                }
                            } else {
                                targetMethod = cls[methodName];
                            }
                        } else {
                            targetMethod = cls[methodName];
                        }
                        
                        targetMethod.implementation = function(...args: any[]) {
                            const startTime = Date.now();
                            const threadId = Process.getCurrentThreadId();
                            
                            const argsStr = args.map(arg => {
                                try {
                                    if (arg === null) return "null";
                                    if (arg === undefined) return "undefined";
                                    return String(arg);
                                } catch (e) {
                                    return "[object]";
                                }
                            });
                            
                            send({
                                type: "hook_event",
                                event_type: "entry",
                                hook_id: hook.id,
                                timestamp: new Date().toISOString(),
                                thread_id: threadId,
                                args: argsStr,
                                class_name: hook.class_name,
                                method_name: hook.method_name
                            });
                            
                            hookStats[hook.id].call_count++;
                            
                            let result: any;
                            let error: any = null;
                            
                            try {
                                result = targetMethod.call(this, ...args);
                            } catch (e) {
                                error = e;
                            }
                            
                            const duration = Date.now() - startTime;
                            
                            send({
                                type: "hook_event",
                                event_type: "exit",
                                hook_id: hook.id,
                                timestamp: new Date().toISOString(),
                                thread_id: threadId,
                                return_value: error ? null : String(result),
                                error: error ? String(error) : null,
                                duration_ms: duration,
                                class_name: hook.class_name,
                                method_name: hook.method_name
                            });
                            
                            if (error) {
                                throw error;
                            }
                            
                            return result;
                        };
                        
                        results.push({
                            hook_id: hook.id,
                            success: true,
                            class_name: hook.class_name,
                            method_name: hook.method_name
                        });
                        
                    } catch (e: any) {
                        results.push({
                            hook_id: hook.id,
                            success: false,
                            error: e.toString()
                        });
                    }
                }
                
                resolve({
                    success: true,
                    results: results
                });
            });
        });
    },
    
    getStats(): { [hook_id: string]: { call_count: number } } {
        return hookStats;
    }
};
