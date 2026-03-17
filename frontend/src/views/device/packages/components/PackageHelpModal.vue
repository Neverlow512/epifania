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
      <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center p-4">
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
                  <h3 class="text-xl font-semibold text-white">Packages Tab Help</h3>
                  <p class="text-sm text-slate-400">Complete application lifecycle management</p>
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
                  <h4 class="text-lg font-semibold text-white">What is the Packages Tab?</h4>
                </div>
                <p class="text-slate-300 leading-relaxed">
                  The Packages tab provides complete application lifecycle management for Android devices. 
                  While the Processes tab shows what's currently running, the Packages tab shows all installed 
                  applications and enables installation, removal, and inspection of APKs.
                </p>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Key Features</h4>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <svg class="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                      </svg>
                      <div>
                        <h5 class="text-white font-medium mb-1">Install APK</h5>
                        <p class="text-sm text-slate-400">Install applications from local files or device storage paths.</p>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <svg class="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      <div>
                        <h5 class="text-white font-medium mb-1">Uninstall</h5>
                        <p class="text-sm text-slate-400">Remove applications with option to preserve user data.</p>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <svg class="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div>
                        <h5 class="text-white font-medium mb-1">Launch / Stop</h5>
                        <p class="text-sm text-slate-400">Control application lifecycle with launch and force stop.</p>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <svg class="w-5 h-5 text-violet-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      <div>
                        <h5 class="text-white font-medium mb-1">Extract APK</h5>
                        <p class="text-sm text-slate-400">Pull APK files from device to local computer for backup or analysis.</p>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <svg class="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      <div>
                        <h5 class="text-white font-medium mb-1">Clear Cache / Data</h5>
                        <p class="text-sm text-slate-400">Manage application storage by clearing cache or resetting app data.</p>
                      </div>
                    </div>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <svg class="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      <div>
                        <h5 class="text-white font-medium mb-1">Detailed Inspection</h5>
                        <p class="text-sm text-slate-400">View version, permissions, SDK levels, signatures, and storage usage.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Search & Filtering</h4>
                </div>
                <div class="space-y-3">
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <p class="text-sm text-slate-300 mb-2">
                      <span class="font-medium text-white">Search:</span> Filter packages by name or package ID using the search box.
                    </p>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <p class="text-sm text-slate-300 mb-2">
                      <span class="font-medium text-white">Sort:</span> Order packages by name (A-Z), size (largest first), or install date (newest first).
                    </p>
                  </div>
                  <div class="bg-black/40 rounded-lg p-4 border border-neutral-800">
                    <p class="text-sm text-slate-300">
                      <span class="font-medium text-white">Running Only:</span> Toggle to show only currently active applications with running processes.
                    </p>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Integration with Processes Tab</h4>
                </div>
                <div class="bg-gradient-to-r from-green-500/10 to-emerald-500/10 rounded-lg p-4 border border-green-500/20">
                  <p class="text-slate-300 mb-3">
                    Running applications display their Process ID (PID) with a clickable badge. 
                    Click the badge to navigate directly to the Processes tab where you can:
                  </p>
                  <ul class="space-y-2 text-sm text-slate-300">
                    <li class="flex items-start gap-2">
                      <svg class="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Monitor real-time CPU and memory usage</span>
                    </li>
                    <li class="flex items-start gap-2">
                      <svg class="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <span>View network connections and activity</span>
                    </li>
                    <li class="flex items-start gap-2">
                      <svg class="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Inspect threads and file descriptors</span>
                    </li>
                    <li class="flex items-start gap-2">
                      <svg class="w-4 h-4 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Analyze process behavior in detail</span>
                    </li>
                  </ul>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <h4 class="text-lg font-semibold text-white">Quick Tips</h4>
                </div>
                <div class="space-y-2">
                  <div class="flex items-start gap-3 text-sm text-slate-300">
                    <span class="text-cyan-400 font-bold flex-shrink-0">1.</span>
                    <p>Package details load on-demand when clicked - keeps initial load fast</p>
                  </div>
                  <div class="flex items-start gap-3 text-sm text-slate-300">
                    <span class="text-cyan-400 font-bold flex-shrink-0">2.</span>
                    <p>Use the running filter to quickly find active applications</p>
                  </div>
                  <div class="flex items-start gap-3 text-sm text-slate-300">
                    <span class="text-cyan-400 font-bold flex-shrink-0">3.</span>
                    <p>Extract APKs for offline analysis with tools like JADX-GUI</p>
                  </div>
                  <div class="flex items-start gap-3 text-sm text-slate-300">
                    <span class="text-cyan-400 font-bold flex-shrink-0">4.</span>
                    <p>Clear cache is safe - clear data resets the app completely</p>
                  </div>
                  <div class="flex items-start gap-3 text-sm text-slate-300">
                    <span class="text-cyan-400 font-bold flex-shrink-0">5.</span>
                    <p>Only the primary (visible) tab can perform actions to prevent conflicts</p>
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
  name: 'PackageHelpModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close']
}
</script>

