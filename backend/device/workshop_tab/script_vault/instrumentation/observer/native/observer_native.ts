declare const rpc: {
    exports: Record<string, (...args: any[]) => any>;
};

interface NativeHookConfig {
    id: string;
    module_name: string;
    function_name: string;
    address?: string;
}

const hookStats: { [hookId: string]: { call_count: number } } = {};

rpc.exports = {
    installHooks(hooks: NativeHookConfig[]): Promise<{ success: boolean; results: any[] }> {
        return new Promise((resolve) => {
            const results: any[] = [];
            
            hooks.forEach(hook => {
                hookStats[hook.id] = { call_count: 0 };
            });
            
            for (const hook of hooks) {
                try {
                    let targetAddress: NativePointer;
                    
                    if (hook.address) {
                        targetAddress = ptr(hook.address);
                    } else {
                        const module = Process.findModuleByName(hook.module_name);
                        if (!module) {
                            results.push({
                                hook_id: hook.id,
                                success: false,
                                error: `Module ${hook.module_name} not found`
                            });
                            continue;
                        }
                        
                        const symbol = Module.findExportByName(hook.module_name, hook.function_name);
                        if (!symbol) {
                            results.push({
                                hook_id: hook.id,
                                success: false,
                                error: `Function ${hook.function_name} not found in ${hook.module_name}`
                            });
                            continue;
                        }
                        
                        targetAddress = symbol;
                    }
                    
                    Interceptor.attach(targetAddress, {
                        onEnter(args) {
                            const startTime = Date.now();
                            (this as any).startTime = startTime;
                            
                            const argsArray = [];
                            for (let i = 0; i < 6; i++) {
                                try {
                                    argsArray.push(args[i].toString());
                                } catch (e) {
                                    argsArray.push(`0x${args[i]}`);
                                }
                            }
                            
                            send({
                                type: "hook_event",
                                event_type: "entry",
                                hook_id: hook.id,
                                timestamp: new Date().toISOString(),
                                thread_id: Process.getCurrentThreadId(),
                                args: argsArray,
                                module_name: hook.module_name,
                                function_name: hook.function_name
                            });
                            
                            hookStats[hook.id].call_count++;
                        },
                        
                        onLeave(retval) {
                            const startTime = (this as any).startTime || Date.now();
                            const duration = Date.now() - startTime;
                            
                            let returnValue = "unknown";
                            try {
                                returnValue = retval.toString();
                            } catch (e) {
                                returnValue = `0x${retval}`;
                            }
                            
                            send({
                                type: "hook_event",
                                event_type: "exit",
                                hook_id: hook.id,
                                timestamp: new Date().toISOString(),
                                thread_id: Process.getCurrentThreadId(),
                                return_value: returnValue,
                                duration_ms: duration,
                                module_name: hook.module_name,
                                function_name: hook.function_name
                            });
                        }
                    });
                    
                    results.push({
                        hook_id: hook.id,
                        success: true,
                        module_name: hook.module_name,
                        function_name: hook.function_name,
                        address: targetAddress.toString()
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
    },
    
    getStats(): { [hook_id: string]: { call_count: number } } {
        return hookStats;
    }
};
