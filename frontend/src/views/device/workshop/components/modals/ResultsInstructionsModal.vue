<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <!-- Do not change: keep modal above all UI. Note: Tailwind CSS supports arbitrary values like z-[99999] (some IDEs warn). -->
      <div v-if="show" class="fixed inset-0 z-[99999] flex items-center justify-center p-4">
        <div
          class="absolute inset-0 bg-black/70 backdrop-blur-sm"
          @click="$emit('close')"
        ></div>

        <Transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 scale-95 translate-y-4"
          enter-to-class="opacity-100 scale-100 translate-y-0"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 scale-100 translate-y-0"
          leave-to-class="opacity-0 scale-95 translate-y-4"
        >
          <div v-if="show" class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div class="flex items-center justify-between p-6 border-b border-neutral-800">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                  <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-xl font-semibold text-white">Analysis Instructions</h3>
                  <p class="text-sm text-slate-400">Understanding concepts for effective security research</p>
                </div>
              </div>
              <button
                type="button"
                class="btn btn-ghost btn-sm btn-circle"
                @click="$emit('close')"
              >
                <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div class="flex-1 overflow-y-auto p-6 space-y-6">
              
              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">What are Java Classes?</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Java classes are blueprints for objects in object-oriented programming. Each class contains methods (functions) 
                    and fields (variables). In Android apps, classes are organized into packages (namespaces) like <code class="text-cyan-400 bg-neutral-800 px-1 rounded">com.example.myapp</code>.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Key Concepts</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Package:</span> Organizational namespace (e.g., com.bumble.app.network)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Class Name:</span> Final part after the last dot (e.g., HttpClient)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Inheritance:</span> Classes can extend other classes, inheriting their methods</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Inner Classes:</span> Classes defined inside other classes, shown with $ separator</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">What are Methods?</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Methods are functions that belong to a class. They perform operations and can accept parameters and return values. 
                    Methods are the primary hooking targets for dynamic instrumentation with Frida.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Method Components</h5>
                    <div class="space-y-3 text-sm">
                      <div class="bg-neutral-900 rounded p-3 font-mono text-xs">
                        <span class="text-purple-400">public</span> <span class="text-blue-400">static</span> <span class="text-emerald-400">String</span> <span class="text-white">encrypt</span>(<span class="text-cyan-400">String data, byte[] key</span>)
                      </div>
                      <ul class="space-y-2">
                        <li class="flex items-start gap-2">
                          <span class="text-purple-400 font-bold">•</span>
                          <span><span class="font-medium text-purple-400">Access Modifier:</span> public (visible everywhere), private (class only), protected (subclasses)</span>
                        </li>
                        <li class="flex items-start gap-2">
                          <span class="text-blue-400 font-bold">•</span>
                          <span><span class="font-medium text-blue-400">Modifiers:</span> static (class-level), final (can't override), native (C/C++ implementation)</span>
                        </li>
                        <li class="flex items-start gap-2">
                          <span class="text-emerald-400 font-bold">•</span>
                          <span><span class="font-medium text-emerald-400">Return Type:</span> What the method returns (String, void, int, etc.)</span>
                        </li>
                        <li class="flex items-start gap-2">
                          <span class="text-white font-bold">•</span>
                          <span><span class="font-medium">Method Name:</span> Identifier for the function</span>
                        </li>
                        <li class="flex items-start gap-2">
                          <span class="text-cyan-400 font-bold">•</span>
                          <span><span class="font-medium text-cyan-400">Parameters:</span> Input values with types (can be empty)</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Method Modifiers Explained</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Modifiers control method behavior and accessibility. Understanding them helps you determine which methods are hookable and how they function.
                  </p>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <h5 class="text-white font-medium text-sm mb-2">public</h5>
                      <p class="text-xs text-slate-400">Accessible from anywhere. Easy to hook and commonly used for APIs.</p>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <h5 class="text-white font-medium text-sm mb-2">private</h5>
                      <p class="text-xs text-slate-400">Only accessible within the same class. Can still be hooked with Frida.</p>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <h5 class="text-white font-medium text-sm mb-2">protected</h5>
                      <p class="text-xs text-slate-400">Accessible to subclasses and same package. Common in frameworks.</p>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <h5 class="text-white font-medium text-sm mb-2">static</h5>
                      <p class="text-xs text-slate-400">Belongs to class, not instance. Called without creating objects. Common for utilities.</p>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <h5 class="text-white font-medium text-sm mb-2">final</h5>
                      <p class="text-xs text-slate-400">Cannot be overridden by subclasses. Often used for security-sensitive methods.</p>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <h5 class="text-white font-medium text-sm mb-2">native</h5>
                      <p class="text-xs text-slate-400">Implemented in C/C++ via JNI. Bridge between Java and native code.</p>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <h5 class="text-white font-medium text-sm mb-2">synchronized</h5>
                      <p class="text-xs text-slate-400">Thread-safe, only one thread can execute at a time. Important for concurrency.</p>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <h5 class="text-white font-medium text-sm mb-2">abstract</h5>
                      <p class="text-xs text-slate-400">No implementation, must be overridden by subclasses. Defines interface.</p>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">What are Native Modules?</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Native modules are shared libraries (files ending in .so) written in C or C++. Apps use them for performance-critical 
                    operations or when interfacing with hardware. They're loaded into the app's process and accessed via JNI (Java Native Interface).
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Common Native Modules</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">libssl.so:</span> OpenSSL encryption library</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">libapp.so:</span> App-specific native code (often obfuscated or sensitive logic)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">libc.so:</span> Standard C library (system functions)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">libsqlite.so:</span> SQLite database engine</span>
                      </li>
                    </ul>
                  </div>
                  <div class="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3">
                    <div class="flex gap-2">
                      <svg class="w-5 h-5 text-amber-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div class="text-sm">
                        <p class="text-amber-400 font-medium mb-1">Security Note</p>
                        <p class="text-amber-300/80">Native code is harder to reverse engineer than Java. Apps often move security-critical operations (crypto keys, anti-tampering) to native modules.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Native Exports</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Exports are functions that native modules expose for other code to call. They're the hookable entry points in native libraries.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Export Types</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">JNI Functions:</span> Java_com_example_ClassName_methodName format (called from Java)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Standard Functions:</span> Regular C functions like malloc, strcmp, SSL_read</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Custom Exports:</span> App-specific functions often related to business logic</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Categories Explained</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    The tool automatically categorizes classes and methods based on names, signatures, and patterns. Categories provide hints 
                    about functionality but are heuristic-based. Always verify with actual hooking and testing.
                  </p>
                  <div class="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-3 mb-4">
                    <div class="flex gap-2">
                      <svg class="w-5 h-5 text-cyan-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div class="text-sm">
                        <p class="text-cyan-400 font-medium mb-1">Important</p>
                        <p class="text-cyan-300/80">Categories are educated guesses. A class named "NetworkManager" might handle network operations, OR it could be a naming pattern used for other purposes. Context matters.</p>
                      </div>
                    </div>
                  </div>
                  <div class="grid grid-cols-1 gap-3">
                    <div class="bg-black/40 rounded-lg p-4 border border-blue-500/30">
                      <div class="flex items-start gap-3">
                        <span class="badge badge-info badge-sm flex-shrink-0 w-20 justify-center">Network</span>
                        <div class="text-sm flex-1">
                          <p class="text-white font-medium mb-1">Might indicate:</p>
                          <p class="text-slate-400">HTTP clients, REST APIs, WebSocket connections, URL handling, network requests. Look for okhttp, retrofit, HttpURLConnection patterns.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-purple-500/30">
                      <div class="flex items-start gap-3">
                        <span class="badge badge-secondary badge-sm flex-shrink-0 w-20 justify-center">Crypto</span>
                        <div class="text-sm flex-1">
                          <p class="text-white font-medium mb-1">Might indicate:</p>
                          <p class="text-slate-400">Encryption/decryption, hashing, key generation, certificates, HMAC, AES, RSA. Could be TLS handshakes or business logic encryption.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-green-500/30">
                      <div class="flex items-start gap-3">
                        <span class="badge badge-success badge-sm flex-shrink-0 w-20 justify-center">Storage</span>
                        <div class="text-sm flex-1">
                          <p class="text-white font-medium mb-1">Might indicate:</p>
                          <p class="text-slate-400">File I/O, SQLite databases, SharedPreferences, data persistence, cache management. Look for file paths, database queries, storage operations.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-red-500/30">
                      <div class="flex items-start gap-3">
                        <span class="badge badge-error badge-sm flex-shrink-0 w-20 justify-center">Security</span>
                        <div class="text-sm flex-1">
                          <p class="text-white font-medium mb-1">Might indicate:</p>
                          <p class="text-slate-400">Authentication, authorization, permissions, tokens, SSL pinning, root detection, integrity checks. Critical for security research.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-cyan-500/30">
                      <div class="flex items-start gap-3">
                        <span class="badge badge-accent badge-sm flex-shrink-0 w-20 justify-center">UI</span>
                        <div class="text-sm flex-1">
                          <p class="text-white font-medium mb-1">Might indicate:</p>
                          <p class="text-slate-400">Activities, fragments, views, adapters, user interface components. Usually less relevant for security but important for understanding app flow.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-amber-500/30">
                      <div class="flex items-start gap-3">
                        <span class="badge badge-warning badge-sm flex-shrink-0 w-20 justify-center">Reflection</span>
                        <div class="text-sm flex-1">
                          <p class="text-white font-medium mb-1">Might indicate:</p>
                          <p class="text-slate-400">Dynamic class loading, method invocation at runtime, Class.forName usage. Often used for plugin systems or anti-analysis techniques.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-orange-500/30">
                      <div class="flex items-start gap-3">
                        <span class="badge badge-sm bg-orange-500 border-orange-500 flex-shrink-0 w-20 justify-center">Native</span>
                        <div class="text-sm flex-1">
                          <p class="text-white font-medium mb-1">Might indicate:</p>
                          <p class="text-slate-400">JNI bridges to C/C++ code. Methods declared as native in Java but implemented in .so libraries. Performance-critical or obfuscated logic.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-slate-500/30">
                      <div class="flex items-start gap-3">
                        <span class="badge badge-sm bg-purple-600 border-purple-600 flex-shrink-0 w-20 justify-center">Obfuscated</span>
                        <div class="text-sm flex-1">
                          <p class="text-white font-medium mb-1">Might indicate:</p>
                          <p class="text-slate-400">Code processed by ProGuard/R8. Single-letter class names (a, b, c), short method names. Makes reverse engineering harder but still hookable.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-600/30">
                      <div class="flex items-start gap-3">
                        <span class="badge badge-neutral badge-sm flex-shrink-0 w-20 justify-center">Unknown</span>
                        <div class="text-sm flex-1">
                          <p class="text-white font-medium mb-1">Might indicate:</p>
                          <p class="text-slate-400">Categorization system couldn't determine purpose. Could be anything. Requires manual investigation and hooking to understand behavior.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Analysis Workflow</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">A systematic approach to using Workshop discoveries for security research.</p>
                  <div class="space-y-3">
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <span class="text-emerald-400 font-bold text-lg flex-shrink-0">1</span>
                        <div>
                          <h5 class="text-white font-medium mb-1">Start Broad</h5>
                          <p class="text-sm text-slate-400">Run discovery and use Focused mode to understand the app's own code structure. Look at category distribution and identify interesting classes.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <span class="text-blue-400 font-bold text-lg flex-shrink-0">2</span>
                        <div>
                          <h5 class="text-white font-medium mb-1">Identify Targets</h5>
                          <p class="text-sm text-slate-400">Filter by categories relevant to your research goal (e.g., Crypto for encryption analysis, Network for API research). Select interesting classes.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <span class="text-purple-400 font-bold text-lg flex-shrink-0">3</span>
                        <div>
                          <h5 class="text-white font-medium mb-1">Scan ClassLoader (Optional)</h5>
                          <p class="text-sm text-slate-400">If you want to verify which classes are in the APK vs system, select classes and scan their ClassLoaders. This adds APK/Sys badges.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <span class="text-indigo-400 font-bold text-lg flex-shrink-0">4</span>
                        <div>
                          <h5 class="text-white font-medium mb-1">Scan Modifiers (Optional)</h5>
                          <p class="text-sm text-slate-400">To understand class properties (public, final, interface, etc.), click "Choose Modifiers", select which properties to scan, then execute. Colored badges appear below class names.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <span class="text-cyan-400 font-bold text-lg flex-shrink-0">5</span>
                        <div>
                          <h5 class="text-white font-medium mb-1">Extract Methods</h5>
                          <p class="text-sm text-slate-400">Select target classes and extract their methods. Click classes to expand and review method signatures. Look for interesting parameters (tokens, keys, passwords).</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <span class="text-amber-400 font-bold text-lg flex-shrink-0">6</span>
                        <div>
                          <h5 class="text-white font-medium mb-1">Hook and Test</h5>
                          <p class="text-sm text-slate-400">Copy method signatures and create Frida hooks. Test your assumptions by observing actual behavior at runtime.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <span class="text-pink-400 font-bold text-lg flex-shrink-0">7</span>
                        <div>
                          <h5 class="text-white font-medium mb-1">Check Native</h5>
                          <p class="text-sm text-slate-400">Review native modules tab for security-critical operations moved to C/C++. Look for JNI methods that bridge Java and native.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <span class="text-violet-400 font-bold text-lg flex-shrink-0">8</span>
                        <div>
                          <h5 class="text-white font-medium mb-1">Save and Compare</h5>
                          <p class="text-sm text-slate-400">Save discoveries for different app versions to identify changes, new features, or security patches.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Important Caveats</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <div class="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <h5 class="text-red-400 font-medium mb-2">Categorization is Heuristic</h5>
                    <p class="text-sm text-red-300/80">
                      Automatic categorization uses pattern matching on class/method names. It's helpful for initial triage but not definitive. 
                      A method categorized as "Crypto" might not actually do cryptography. Always verify with dynamic analysis.
                    </p>
                  </div>
                  <div class="bg-amber-500/10 border border-amber-500/30 rounded-lg p-4">
                    <h5 class="text-amber-400 font-medium mb-2">Obfuscation Hides Intent</h5>
                    <p class="text-sm text-amber-300/80">
                      Apps using ProGuard/R8 will have classes named a, b, c with methods like a(), b(). Categories for obfuscated code 
                      are less reliable. You'll need to hook and observe behavior to understand purpose.
                    </p>
                  </div>
                  <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
                    <h5 class="text-blue-400 font-medium mb-2">Discovery is a Snapshot</h5>
                    <p class="text-sm text-blue-300/80">
                      Discovery captures what's loaded at that moment. Some classes might load dynamically later (reflection, plugin systems). 
                      Different app states (logged in vs logged out) might load different code.
                    </p>
                  </div>
                  <div class="bg-purple-500/10 border border-purple-500/30 rounded-lg p-4">
                    <h5 class="text-purple-400 font-medium mb-2">Selective Extraction for Efficiency</h5>
                    <p class="text-sm text-purple-300/80">
                      Initial discovery is fast because it only gets class names. Extracting methods for thousands of classes would be slow, 
                      which is why you do it selectively. Use filters and selection tools to work with manageable subsets.
                    </p>
                  </div>
                </div>
              </section>

            </div>

            <div class="border-t border-neutral-800 p-4 flex justify-end">
              <button
                type="button"
                class="btn btn-primary"
                @click="$emit('close')"
              >
                Got it
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
export default {
  name: 'ResultsInstructionsModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close']
}
</script>

