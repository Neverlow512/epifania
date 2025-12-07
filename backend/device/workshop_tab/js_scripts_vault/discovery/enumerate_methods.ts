// Enumerate methods for a specific Java class using frida-java-bridge
// Variables to be replaced: {{CLASS_NAME}}
import Java from "frida-java-bridge";

Java.perform(() => {
    try {
        const cls = Java.use('{{CLASS_NAME}}');
        const methods: any[] = [];
        
        const declaredMethods = cls.class.getDeclaredMethods();
        for (let i = 0; i < declaredMethods.length; i++) {
            const method = declaredMethods[i];
            const modifiers = method.getModifiers();
            
            methods.push({
                name: method.getName(),
                signature: method.toString(),
                return_type: method.getReturnType().getName(),
                parameters: Java.cast(method.getParameterTypes(), Java.use('[Ljava.lang.Class;')).map((p: any) => p.getName()),
                is_native: (modifiers & 0x0100) !== 0,
                is_public: (modifiers & 0x0001) !== 0,
                is_static: (modifiers & 0x0008) !== 0,
                is_final: (modifiers & 0x0010) !== 0,
                is_synchronized: (modifiers & 0x0020) !== 0
            });
        }
        
        send({ 
            type: 'methods', 
            class_name: '{{CLASS_NAME}}', 
            data: methods, 
            success: true 
        });
    } catch (e: any) {
        send({ 
            type: 'methods', 
            class_name: '{{CLASS_NAME}}', 
            data: [], 
            success: false, 
            error: e.toString() 
        });
    }
});

