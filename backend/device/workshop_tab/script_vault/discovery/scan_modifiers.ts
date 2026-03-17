import Java from "frida-java-bridge";

declare const rpc: {
    exports: Record<string, (...args: any[]) => any>;
};

interface ModifierResult {
    success: boolean;
    name: string;
    is_public?: boolean;
    is_private?: boolean;
    is_protected?: boolean;
    is_static?: boolean;
    is_final?: boolean;
    is_interface?: boolean;
    is_abstract?: boolean;
    error?: string;
}

rpc.exports = {
    scanModifiers(className: string, scanTypes: string[]): Promise<ModifierResult> {
        return new Promise((resolve) => {
            Java.perform(() => {
                try {
                    const cls = Java.use(className);
                    const modifiers = cls.class.getModifiers();
                    
                    const result: ModifierResult = {
                        success: true,
                        name: className
                    };
                    
                    for (const scanType of scanTypes) {
                        switch (scanType) {
                            case "is_public":
                                result.is_public = (modifiers & 0x0001) !== 0;
                                break;
                            case "is_private":
                                result.is_private = (modifiers & 0x0002) !== 0;
                                break;
                            case "is_protected":
                                result.is_protected = (modifiers & 0x0004) !== 0;
                                break;
                            case "is_static":
                                result.is_static = (modifiers & 0x0008) !== 0;
                                break;
                            case "is_final":
                                result.is_final = (modifiers & 0x0010) !== 0;
                                break;
                            case "is_interface":
                                result.is_interface = (modifiers & 0x0200) !== 0;
                                break;
                            case "is_abstract":
                                result.is_abstract = (modifiers & 0x0400) !== 0;
                                break;
                        }
                    }
                    
                    resolve(result);
                } catch (e: any) {
                    resolve({
                        success: false,
                        name: className,
                        error: e.toString()
                    });
                }
            });
        });
    }
};
