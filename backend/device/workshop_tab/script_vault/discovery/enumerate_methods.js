// Enumerate methods for a specific Java class
// This script runs in the target process via Frida
// 
// Variables to be replaced:
//   {{CLASS_NAME}} - The fully qualified class name

Java.perform(function() {
    try {
        var cls = Java.use('{{CLASS_NAME}}');
        var methods = [];
        
        var declaredMethods = cls.class.getDeclaredMethods();
        for (var i = 0; i < declaredMethods.length; i++) {
            var method = declaredMethods[i];
            var modifiers = method.getModifiers();
            
            methods.push({
                name: method.getName(),
                signature: method.toString(),
                return_type: method.getReturnType().getName(),
                parameters: Java.cast(method.getParameterTypes(), Java.use('[Ljava.lang.Class;')).map(function(p) { 
                    return p.getName(); 
                }),
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
        
        send({ 
            type: 'methods', 
            class_name: '{{CLASS_NAME}}', 
            data: methods, 
            success: true 
        });
    } catch (e) {
        send({ 
            type: 'methods', 
            class_name: '{{CLASS_NAME}}', 
            data: [], 
            success: false, 
            error: e.toString() 
        });
    }
});

