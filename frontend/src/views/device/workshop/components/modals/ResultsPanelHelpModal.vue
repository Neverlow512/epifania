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
          <div v-if="show" class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div class="flex items-center justify-between p-6 border-b border-neutral-800">
              <div class="flex items-center gap-3">
                <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                  <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-xl font-semibold text-white">Results Panel Help</h3>
                  <p class="text-sm text-slate-400">Understanding discovery results and navigation</p>
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
                  <svg class="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Results Tabs Overview</h4>
                </div>
                <p class="text-slate-300 leading-relaxed mb-4">
                  Discovery results are organized into three tabs. Switch between them to view different aspects of the analyzed application.
                </p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div class="bg-black/40 rounded-lg p-4 border border-blue-500/30">
                    <div class="flex items-start gap-3">
                      <svg class="w-6 h-6 text-blue-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                      </svg>
                      <div>
                        <h5 class="text-white font-medium mb-1">Java Classes</h5>
                        <p class="text-sm text-slate-400">View Java/Kotlin classes and their methods</p>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-emerald-500/30">
                    <div class="flex items-start gap-3">
                      <svg class="w-6 h-6 text-emerald-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                      </svg>
                      <div>
                        <h5 class="text-white font-medium mb-1">Native Modules</h5>
                        <p class="text-sm text-slate-400">Browse native libraries and exported functions</p>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-purple-500/30">
                    <div class="flex items-start gap-3">
                      <svg class="w-6 h-6 text-purple-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                      </svg>
                      <div>
                        <h5 class="text-white font-medium mb-1">Saved Discoveries</h5>
                        <p class="text-sm text-slate-400">Load previously saved discovery results</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Java Classes Tab</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Displays Java and Kotlin classes discovered in the app. Click a class row to expand and view its methods.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Class Information</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Class Name:</span> Full package path (e.g., com.example.NetworkClient)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Method Count:</span> Initially shows <code class="text-amber-400">0?</code> until you extract methods. The <code class="text-amber-400">?</code> means methods haven't been extracted yet</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Category:</span> Functional classification (Network, Crypto, etc.)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Source:</span> Origin based on name patterns (App, Third-party, System)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">APK/Sys Badge:</span> Blue "APK" or gray "Sys" badge appears after scanning ClassLoader</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Modifier Badges:</span> Colored badges (green=public, red=private, etc.) appear below class name after scanning modifiers</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Checkbox:</span> Select classes for batch operations (scan or extract)</span>
                      </li>
                    </ul>
                  </div>
                  <div class="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-3">
                    <div class="flex gap-2">
                      <svg class="w-5 h-5 text-cyan-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div class="text-sm">
                        <p class="text-cyan-400 font-medium mb-1">Understanding States</p>
                        <p class="text-cyan-300/80">Classes have three independent states: <strong>Discovered</strong> (has name), <strong>Scanned</strong> (ClassLoader checked), and <strong>Extracted</strong> (methods available). You control when scanning and extraction happen.</p>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Method Information</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium">Method Name:</span> Function identifier</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium">Signature:</span> Full method signature with parameters and return type</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium">Modifiers:</span> Access level and keywords (public, static, etc.)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium">Click method:</span> Opens detailed view with all information</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Native Modules Tab</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Shows native shared libraries (.so files) loaded by the app. Click a module to expand and view exported functions.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Module Information</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Module Name:</span> Library filename (e.g., libssl.so)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Path:</span> Full filesystem path where library is loaded</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Export Count:</span> Number of exported functions</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Base Address:</span> Memory address where module is loaded</span>
                      </li>
                    </ul>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Export Information</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium">Export Name:</span> Function symbol name</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium">Type:</span> Usually "function" for hookable targets</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium">Address:</span> Memory location of the function</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Saved Discoveries Tab</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Access previously saved discoveries. Useful for comparing different app versions or revisiting past analyses.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Features</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Package Cards:</span> Each saved discovery shows as a card with metadata</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Version Info:</span> Package version, timestamp, device details</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Load Button:</span> Loads discovery into Java/Native tabs for viewing</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Delete Option:</span> Remove saved discoveries you no longer need</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Toolbar Controls</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Filter and search through results to find specific classes, methods, or modules.
                  </p>
                  <div class="grid grid-cols-1 gap-3">
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <svg class="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium mb-1">Search</h5>
                          <p class="text-sm text-slate-400">Type to search class names, method names, or module paths. Search is debounced for performance.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <svg class="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium mb-1">Category Filter</h5>
                          <p class="text-sm text-slate-400">Filter by functional category: Network, Crypto, Storage, Security, UI, Reflection, Native, Obfuscated, or Unknown.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <svg class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium mb-1">Source Filter</h5>
                          <p class="text-sm text-slate-400">Filter by origin: All, App (package-specific code), or Third-party (library code).</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                      <div class="flex items-start gap-3">
                        <svg class="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium mb-1">Items Per Page</h5>
                          <p class="text-sm text-slate-400">Adjust how many items to display per page (10, 25, 50, 100, or custom). Use +/- buttons or type directly.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Selection and Batch Operations</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Select multiple classes to perform batch operations like scanning ClassLoaders or extracting methods.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Selection Buttons</h5>
                    <div class="grid grid-cols-1 gap-2 text-sm">
                      <div class="flex items-start gap-2">
                        <span class="badge badge-sm bg-violet-600 text-white border-violet-600 flex-shrink-0">Page</span>
                        <span class="text-slate-400">Select all classes on the current page</span>
                      </div>
                      <div class="flex items-start gap-2">
                        <span class="badge badge-sm bg-indigo-600 text-white border-indigo-600 flex-shrink-0">All Visible</span>
                        <span class="text-slate-400">Select all classes in the current filtered view (all pages)</span>
                      </div>
                      <div class="flex items-start gap-2">
                        <span class="badge badge-sm bg-red-600 text-white border-red-600 flex-shrink-0">Clear</span>
                        <span class="text-slate-400">Deselect all classes</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Bulk Action Buttons</h5>
                    <div class="space-y-3 text-sm">
                      <div class="flex items-start gap-2">
                        <span class="badge badge-sm bg-emerald-600 text-white border-emerald-600 flex-shrink-0">Scan ClassLoader (N)</span>
                        <div>
                          <p class="text-slate-400 mb-1">Scans selected classes to determine if they're from the APK or Android system. Results appear as APK/Sys badges.</p>
                          <p class="text-xs text-slate-500">Required for Package mode to show results. Number shows how many classes are selected.</p>
                        </div>
                      </div>
                      <div class="flex items-start gap-2">
                        <span class="badge badge-sm bg-indigo-600 text-white border-indigo-600 flex-shrink-0">Choose Modifiers</span>
                        <div>
                          <p class="text-slate-400 mb-1">Opens modal to select class modifier types to scan. Choose from public, private, protected, static, final, interface, or abstract.</p>
                          <p class="text-xs text-slate-500">After selecting modifiers in the modal, click the Execute button to run the scan. Results appear as colored badges below the class name.</p>
                        </div>
                      </div>
                      <div class="flex items-start gap-2">
                        <span class="badge badge-sm bg-blue-600 text-white border-blue-600 flex-shrink-0">Extract Methods (N)</span>
                        <div>
                          <p class="text-slate-400 mb-1">Extracts actual methods for selected classes. Method count changes from <code class="text-amber-400">0?</code> to the real number.</p>
                          <p class="text-xs text-slate-500">Required to see methods and create hooks. Progress modal shows during extraction.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3">
                    <div class="flex gap-2">
                      <svg class="w-5 h-5 text-purple-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div class="text-sm">
                        <p class="text-purple-400 font-medium mb-1">Dynamic Stats</p>
                        <p class="text-purple-300/80">Stats in the toolbar update based on your current filter mode and selections, showing totals, scanned counts, extracted counts, and method counts.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Color Coding</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Categories are color-coded for quick visual identification. Colors appear on badges throughout the interface.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-3">Category Colors</h5>
                    <div class="grid grid-cols-2 gap-2 text-sm">
                      <div class="flex items-center gap-2">
                        <span class="badge badge-info badge-sm">Network</span>
                        <span class="text-slate-400">Blue</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-secondary badge-sm">Crypto</span>
                        <span class="text-slate-400">Purple</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-success badge-sm">Storage</span>
                        <span class="text-slate-400">Green</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-error badge-sm">Security</span>
                        <span class="text-slate-400">Red</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-accent badge-sm">UI</span>
                        <span class="text-slate-400">Cyan</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-warning badge-sm">Reflection</span>
                        <span class="text-slate-400">Yellow</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm bg-orange-500 border-orange-500">Native</span>
                        <span class="text-slate-400">Orange</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-neutral badge-sm">Unknown</span>
                        <span class="text-slate-400">Gray</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-3">Source Badges</h5>
                    <div class="space-y-2 text-sm">
                      <p class="text-slate-400 mb-3">Based on class name patterns:</p>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm bg-emerald-500 text-white border-emerald-500">App</span>
                        <span class="text-slate-400">Code specific to this application</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm bg-blue-500 text-white border-blue-500">Third-party</span>
                        <span class="text-slate-400">External libraries and dependencies</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm bg-slate-600 text-white border-slate-600">System</span>
                        <span class="text-slate-400">Android framework classes</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-3">APK/System Badges</h5>
                    <div class="space-y-2 text-sm">
                      <p class="text-slate-400 mb-3">Based on actual ClassLoader scanning (requires scanning first):</p>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm bg-blue-600 text-white border-blue-600">APK</span>
                        <span class="text-slate-400">Class is bundled in the application's APK file</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm bg-slate-500 text-white border-slate-500">Sys</span>
                        <span class="text-slate-400">Class comes from Android system/framework</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-3">Class Modifier Badges</h5>
                    <div class="space-y-2 text-sm">
                      <p class="text-slate-400 mb-3">Appear below class name after scanning modifiers (requires selecting modifier types first):</p>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm text-white border-none" style="background-color: #10b981">Public</span>
                        <span class="text-slate-400">Class is accessible from anywhere</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm text-white border-none" style="background-color: #ef4444">Private</span>
                        <span class="text-slate-400">Private inner class (only accessible within enclosing class)</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm text-white border-none" style="background-color: #eab308">Protected</span>
                        <span class="text-slate-400">Protected inner class (accessible to subclasses)</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm text-white border-none" style="background-color: #a855f7">Static</span>
                        <span class="text-slate-400">Static nested class (no reference to outer class)</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm text-white border-none" style="background-color: #f97316">Final</span>
                        <span class="text-slate-400">Cannot be extended by subclasses</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm text-white border-none" style="background-color: #06b6d4">Interface</span>
                        <span class="text-slate-400">Interface type (not a concrete class)</span>
                      </div>
                      <div class="flex items-center gap-2">
                        <span class="badge badge-sm text-white border-none" style="background-color: #ec4899">Abstract</span>
                        <span class="text-slate-400">Abstract class (cannot be instantiated directly)</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3">
                    <div class="flex gap-2">
                      <svg class="w-5 h-5 text-amber-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div class="text-sm">
                        <p class="text-amber-400 font-medium mb-1">Source vs APK/Sys vs Modifiers</p>
                        <p class="text-amber-300/80">Source badges are name-based guesses, APK/Sys comes from ClassLoader data, and modifier badges come from scanning the actual class definition. All three provide different insights.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Pagination</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Large result sets are paginated for better performance. Use controls at the bottom to navigate.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Page Counter:</span> Shows current page and total pages</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Item Range:</span> Displays which items are currently visible (e.g., "26-50 of 234")</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Navigation:</span> Use Previous and Next buttons to move between pages</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Expansion State:</span> Expanded classes remain expanded when changing pages</span>
                      </li>
                    </ul>
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
  name: 'ResultsPanelHelpModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close']
}
</script>

