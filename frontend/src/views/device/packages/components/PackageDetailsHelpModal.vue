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
      <div v-if="show" class="fixed inset-0 z-60 flex items-center justify-center p-4">
        <div
          class="absolute inset-0 bg-black/80 backdrop-blur-md"
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
          <div v-if="show" class="relative bg-neutral-900 border border-primary/30 rounded-xl shadow-2xl max-w-3xl w-full max-h-[85vh] overflow-hidden flex flex-col">
            <div class="flex items-center justify-between p-5 border-b border-neutral-800">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
                  <svg class="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-white">Package Details Help</h3>
                  <p class="text-xs text-slate-400">Understanding actions and metadata</p>
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

            <div class="flex-1 overflow-y-auto p-5 space-y-5">
              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
                  </svg>
                  <h4 class="text-base font-semibold text-white">Available Actions</h4>
                </div>
                <div class="space-y-2.5">
                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg bg-success/20 flex items-center justify-center flex-shrink-0">
                        <svg class="w-4 h-4 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </div>
                      <div class="flex-1">
                        <h5 class="text-white font-medium text-sm mb-1">Launch / Force Stop</h5>
                        <p class="text-xs text-slate-400">Start the application or force it to stop if running. Force stop immediately terminates all processes.</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                        <svg class="w-4 h-4 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                      </div>
                      <div class="flex-1">
                        <h5 class="text-white font-medium text-sm mb-1">View Process</h5>
                        <p class="text-xs text-slate-400">Navigate to the Processes tab to monitor CPU, memory, network activity, threads, and file descriptors in real-time.</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg bg-violet-500/20 flex items-center justify-center flex-shrink-0">
                        <svg class="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                      </div>
                      <div class="flex-1">
                        <h5 class="text-white font-medium text-sm mb-1">Extract APK</h5>
                        <p class="text-xs text-slate-400">Pull the APK file from device to your local filesystem for backup or analysis with external tools like JADX-GUI.</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center flex-shrink-0">
                        <svg class="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </div>
                      <div class="flex-1">
                        <h5 class="text-white font-medium text-sm mb-1">Clear Cache</h5>
                        <p class="text-xs text-slate-400"><span class="text-green-400 font-medium">Safe operation.</span> Removes temporary files and frees up storage. Does not affect user data or settings.</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-amber-500/20">
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                        <svg class="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                      </div>
                      <div class="flex-1">
                        <h5 class="text-amber-400 font-medium text-sm mb-1">Clear Data</h5>
                        <p class="text-xs text-slate-400"><span class="text-amber-400 font-medium">Destructive operation.</span> Completely resets the app to its initial state. All user data, settings, and accounts will be lost.</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-red-500/20">
                    <div class="flex items-start gap-3">
                      <div class="w-8 h-8 rounded-lg bg-red-500/20 flex items-center justify-center flex-shrink-0">
                        <svg class="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </div>
                      <div class="flex-1">
                        <h5 class="text-red-400 font-medium text-sm mb-1">Uninstall</h5>
                        <p class="text-xs text-slate-400"><span class="text-red-400 font-medium">Permanent operation.</span> Removes the application from device. Option to keep user data available during uninstall.</p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section>
                <div class="flex items-center gap-2 mb-3">
                  <svg class="w-5 h-5 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                  <h4 class="text-base font-semibold text-white">Metadata Fields Explained</h4>
                </div>
                <div class="space-y-2.5">
                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <h5 class="text-white font-medium text-sm mb-1">Version & Version Code</h5>
                    <p class="text-xs text-slate-400">Version is human-readable (e.g., "1.2.3"), version code is an integer used by Android for update ordering.</p>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <h5 class="text-white font-medium text-sm mb-1">Install Source</h5>
                    <p class="text-xs text-slate-400">Shows where the app was installed from (e.g., Play Store, sideload, package installer).</p>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <h5 class="text-white font-medium text-sm mb-1">Target SDK & Min SDK</h5>
                    <p class="text-xs text-slate-400">Target SDK: Android version the app was designed for. Min SDK: Minimum Android version required to run.</p>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <h5 class="text-white font-medium text-sm mb-1">APK Path</h5>
                    <p class="text-xs text-slate-400">Location of the APK file on the device's filesystem. Useful for manual extraction or inspection.</p>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <h5 class="text-white font-medium text-sm mb-1">Storage (APK / Data / Cache)</h5>
                    <p class="text-xs text-slate-400">APK size: application binary. Data size: user files and databases. Cache size: temporary files that can be cleared.</p>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <h5 class="text-white font-medium text-sm mb-1">Permissions</h5>
                    <p class="text-xs text-slate-400">Android permissions requested by the app. <span class="text-amber-400">Dangerous permissions</span> highlighted in amber (camera, location, contacts, etc.).</p>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <h5 class="text-white font-medium text-sm mb-1">Signing Certificate</h5>
                    <p class="text-xs text-slate-400">SHA-256 hash of the signing certificate. Used to verify app authenticity and for security analysis. Click copy button to save.</p>
                  </div>

                  <div class="bg-black/40 rounded-lg p-3 border border-neutral-800">
                    <h5 class="text-white font-medium text-sm mb-1">Main Activity</h5>
                    <p class="text-xs text-slate-400">The entry point activity that launches when you start the app. Empty if app has no launchable UI.</p>
                  </div>
                </div>
              </section>
            </div>

            <div class="border-t border-neutral-800 p-4 flex justify-end">
              <button
                type="button"
                class="btn btn-primary btn-sm"
                @click="$emit('close')"
              >
                Close
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
  name: 'PackageDetailsHelpModal',
  props: {
    show: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close']
}
</script>

<style scoped>
.z-60 {
  z-index: 60;
}
</style>

