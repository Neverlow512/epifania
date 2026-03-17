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
                  <h3 class="text-xl font-semibold text-white">Analysis Control</h3>
                  <p class="text-sm text-slate-400">Dynamic analysis and discovery controls</p>
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
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">What is the Workshop?</h4>
                </div>
                <p class="text-slate-300 leading-relaxed">
                  The Workshop is a dynamic analysis tool that uses Frida to discover Java classes and native library exports 
                  in running Android applications. Initial discovery is fast (class names only), then you can selectively 
                  scan ClassLoaders and extract methods on-demand. This lazy approach lets you work efficiently with large apps 
                  without waiting for full analysis upfront.
                </p>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Process Selection</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Choose which process to analyze from the dropdown menu. The list shows all running processes on the device.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2 flex items-center gap-2">
                      <svg class="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Process Types
                    </h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium text-emerald-400">User Apps:</span> Third-party applications you installed</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-amber-400 font-bold">•</span>
                        <span><span class="font-medium text-amber-400">[System]:</span> Android system processes (advanced usage)</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Filter Modes</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Filter modes control what you <strong>see</strong> in the results, not what gets discovered. They work instantly 
                    on already-discovered data. You can switch between modes anytime without re-discovery.
                  </p>
                  <div class="grid grid-cols-1 gap-3">
                    <div class="bg-black/40 rounded-lg p-4 border border-emerald-500/30">
                      <div class="flex items-start gap-3">
                        <span class="text-emerald-400 font-bold text-lg">1</span>
                        <div>
                          <h5 class="text-white font-medium mb-1 flex items-center gap-2">
                            Focused
                            <span class="badge badge-xs badge-success">Recommended</span>
                          </h5>
                          <p class="text-sm text-slate-400 mb-2">Shows classes matching your configured patterns. By default, shows classes with the app's package ID (e.g., com.example.app.*).</p>
                          <p class="text-xs text-slate-500">Click "Configure" to customize patterns. Good for focusing on app-specific code.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-blue-500/30">
                      <div class="flex items-start gap-3">
                        <span class="text-blue-400 font-bold text-lg">2</span>
                        <div>
                          <h5 class="text-white font-medium mb-1 flex items-center gap-2">
                            Package
                            <span class="badge badge-xs badge-info">Requires Scanning</span>
                          </h5>
                          <p class="text-sm text-slate-400 mb-2">Shows everything bundled in the APK (app code + libraries). Initially empty until you scan ClassLoaders.</p>
                          <p class="text-xs text-slate-500">Use Focused/All mode to select classes, scan their ClassLoaders, then switch here to see APK content.</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-amber-500/30">
                      <div class="flex items-start gap-3">
                        <span class="text-amber-400 font-bold text-lg">3</span>
                        <div>
                          <h5 class="text-white font-medium mb-1">All</h5>
                          <p class="text-sm text-slate-400 mb-2">Shows everything: app classes, bundled libraries, and Android framework classes.</p>
                          <p class="text-xs text-slate-500">Can produce thousands of results. Use search and filters to navigate.</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-3">
                    <div class="flex gap-2">
                      <svg class="w-5 h-5 text-cyan-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div class="text-sm">
                        <p class="text-cyan-400 font-medium mb-1">Key Point</p>
                        <p class="text-cyan-300/80">Switching filter modes is instant and doesn't re-run discovery. All your scan/extract work persists across mode switches.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Frida Status</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Frida must be running on the device before you can perform discovery. The status indicator shows the current state.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Status Indicators</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                        <span><span class="font-medium text-emerald-400">Running:</span> Server is active and ready</span>
                      </li>
                      <li class="flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-red-500"></span>
                        <span><span class="font-medium text-red-400">Stopped:</span> Server needs to be started</span>
                      </li>
                      <li class="flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                        <span><span class="font-medium text-blue-400">Connected:</span> Tool is attached to Frida</span>
                      </li>
                    </ul>
                    <div class="mt-3 pt-3 border-t border-neutral-700">
                      <p class="text-xs text-slate-400">Use Start/Stop/Restart buttons to control the Frida server</p>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Frida Session Controls</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Controls for managing Frida's attachment to processes. You can attach to running processes or spawn new app instances.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Control Buttons</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium text-emerald-400">Attach:</span> Connect Frida to the selected running process</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-red-400 font-bold">•</span>
                        <span><span class="font-medium text-red-400">Detach:</span> Disconnect Frida from the current process</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-blue-400 font-bold">•</span>
                        <span><span class="font-medium text-blue-400">Start App:</span> Spawn a new instance of the selected app and attach to it</span>
                      </li>
                    </ul>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Spawn Mode</h5>
                    <p class="text-sm mb-2">Enable spawn mode to have Frida start and attach to an app automatically during discovery.</p>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">1.</span>
                        <span>Check "Spawn app on next discovery" to enable spawn mode</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">2.</span>
                        <span>Select a package from the dropdown (process selector becomes disabled)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">3.</span>
                        <span>Use refresh button to update package list from device</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">4.</span>
                        <span>Start discovery or use Start App button to spawn and attach</span>
                      </li>
                    </ul>
                  </div>
                  <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                    <div class="flex gap-2">
                      <svg class="w-5 h-5 text-blue-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div class="text-sm">
                        <p class="text-blue-400 font-medium mb-1">When to Use Spawn Mode</p>
                        <p class="text-blue-300/80">Use spawn mode when you need to instrument apps from the moment they start. This is useful for hooking initialization code or monitoring app startup behavior.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Control Panel Actions</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">Buttons in the control panel manage discovery lifecycle and results.</p>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <div class="flex items-start gap-2">
                        <svg class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium text-sm mb-1">Start Discovery</h5>
                          <p class="text-xs text-slate-400">Fast enumeration of class names and native modules (completes in seconds)</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <div class="flex items-start gap-2">
                        <svg class="w-5 h-5 text-violet-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium text-sm mb-1">Configure (Focused mode)</h5>
                          <p class="text-xs text-slate-400">Customize which class patterns appear in Focused mode</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <div class="flex items-start gap-2">
                        <svg class="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium text-sm mb-1">Save Discovery</h5>
                          <p class="text-xs text-slate-400">Store current discovery with all scanned/extracted data for later comparison</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <div class="flex items-start gap-2">
                        <svg class="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium text-sm mb-1">Load Saved</h5>
                          <p class="text-xs text-slate-400">Restore a previously saved discovery from the Saved Discoveries tab</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <div class="flex items-start gap-2">
                        <svg class="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium text-sm mb-1">Clear Results</h5>
                          <p class="text-xs text-slate-400">Remove current discovery from view (doesn't delete saved discoveries)</p>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                      <div class="flex items-start gap-2">
                        <svg class="w-5 h-5 text-pink-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <div>
                          <h5 class="text-white font-medium text-sm mb-1">View Logs</h5>
                          <p class="text-xs text-slate-400">See detailed operation logs for discovery and batch operations</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Auto-Save & Recovery</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Your work is automatically saved as you scan and extract. If the app crashes, you'll be prompted to recover your progress.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">How Auto-Save Works</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium">Per-class save:</span> After each class is scanned/extracted, state is saved</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-blue-400 font-bold">•</span>
                        <span><span class="font-medium">Interval save:</span> Frontend syncs every 30 seconds during active work</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-purple-400 font-bold">•</span>
                        <span><span class="font-medium">Recovery prompt:</span> On mount, shows recovery modal if unsaved work exists</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium">Conflict handling:</span> Warns when loading saved discovery with unsaved work</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-orange-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Initial Discovery</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    Initial discovery is fast - it only gets class names, not methods or detailed information. This completes in seconds regardless of app size.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">What Happens During Discovery</h5>
                    <ol class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold flex-shrink-0">1.</span>
                        <span><span class="font-medium">Attaching to process</span> - Frida connects to the target app</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold flex-shrink-0">2.</span>
                        <span><span class="font-medium">Enumerating class names</span> - Lists all loaded Java classes (names only)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold flex-shrink-0">3.</span>
                        <span><span class="font-medium">Enumerating native modules</span> - Lists loaded .so libraries and exports</span>
                      </li>
                    </ol>
                  </div>
                  <div class="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3">
                    <div class="flex gap-2">
                      <svg class="w-5 h-5 text-emerald-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <div class="text-sm">
                        <p class="text-emerald-400 font-medium mb-1">Why So Fast?</p>
                        <p class="text-emerald-300/80">We don't extract methods or scan ClassLoaders during initial discovery. You do that later, on-demand, for only the classes you care about.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">On-Demand Operations</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    After initial discovery, you manually choose which classes to analyze further. This gives you control over what gets processed.
                  </p>
                  <div class="grid grid-cols-1 gap-3">
                    <div class="bg-black/40 rounded-lg p-4 border border-blue-500/30">
                      <div class="flex items-start gap-3">
                        <svg class="w-6 h-6 text-blue-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                        </svg>
                        <div class="flex-1">
                          <h5 class="text-white font-medium mb-2">Scan ClassLoader (N)</h5>
                          <p class="text-sm text-slate-400 mb-2">Determines if selected classes are from the APK or Android system. Classes get blue "APK" or gray "Sys" badges.</p>
                          <p class="text-xs text-slate-500 mb-2"><strong>Why?</strong> Package mode only shows APK classes, so you need to scan ClassLoaders first.</p>
                          <div class="flex items-start gap-1 text-xs text-cyan-400">
                            <span>✓</span>
                            <span>Optional - only needed if you want Package mode or need to verify class origin</span>
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="bg-black/40 rounded-lg p-4 border border-purple-500/30">
                      <div class="flex items-start gap-3">
                        <svg class="w-6 h-6 text-purple-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                        </svg>
                        <div class="flex-1">
                          <h5 class="text-white font-medium mb-2">Extract Methods (N)</h5>
                          <p class="text-sm text-slate-400 mb-2">Gets the actual methods for selected classes. Initially classes show <code class="text-amber-400">0?</code> (methods unknown).</p>
                          <p class="text-xs text-slate-500 mb-2"><strong>Why?</strong> Method extraction is slow for many classes, so you do it selectively.</p>
                          <div class="flex items-start gap-1 text-xs text-amber-400">
                            <span>!</span>
                            <span>Required to see methods and create hooks - without this you only have class names</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">How to Use</h5>
                    <ol class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">1.</span>
                        <span>Select classes using checkboxes (or Page/All Visible buttons)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-blue-400 font-bold">2.</span>
                        <span>Click "Scan ClassLoader (N)" or "Extract Methods (N)"</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-purple-400 font-bold">3.</span>
                        <span>Progress modal shows current class being processed</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">4.</span>
                        <span>Results appear immediately and are auto-saved</span>
                      </li>
                    </ol>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-pink-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Stats Display</h4>
                </div>
                <div class="space-y-3 text-slate-300">
                  <p class="leading-relaxed">
                    The toolbar shows real-time statistics based on your current filter mode and what you've scanned/extracted.
                  </p>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <h5 class="text-white font-medium mb-2">Dynamic Statistics</h5>
                    <ul class="space-y-2 text-sm">
                      <li class="flex items-start gap-2">
                        <span class="text-emerald-400 font-bold">•</span>
                        <span><span class="font-medium text-emerald-400">Total Classes:</span> Number of classes visible in current filter mode</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-blue-400 font-bold">•</span>
                        <span><span class="font-medium text-blue-400">Classes Scanned:</span> How many have ClassLoader info (APK/Sys badges)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-purple-400 font-bold">•</span>
                        <span><span class="font-medium text-purple-400">Classes Extracted:</span> How many have methods extracted</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-cyan-400 font-bold">•</span>
                        <span><span class="font-medium text-cyan-400">Total Methods:</span> Sum of methods across extracted classes</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-amber-400 font-bold">•</span>
                        <span><span class="font-medium text-amber-400">Total Modules:</span> Number of native libraries (.so files)</span>
                      </li>
                      <li class="flex items-start gap-2">
                        <span class="text-pink-400 font-bold">•</span>
                        <span><span class="font-medium text-pink-400">Total Exports:</span> Number of exported native functions</span>
                      </li>
                    </ul>
                  </div>
                  <div class="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                    <div class="flex gap-2">
                      <svg class="w-5 h-5 text-blue-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div class="text-sm">
                        <p class="text-blue-400 font-medium mb-1">Dynamic Stats</p>
                        <p class="text-blue-300/80">Stats update in real-time as you scan and extract. They reflect only what's visible in your current filter mode.</p>
                      </div>
                    </div>
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
  name: 'WorkshopControlHelpModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close']
}
</script>

