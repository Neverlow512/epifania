<template>
  <Teleport to="body">
    <!-- Do not change: keep modal above all UI -->
    <div v-if="show" class="modal modal-open" style="z-index: 99999;">
      <div class="modal-box bg-neutral-900 border border-primary/30 max-w-2xl max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between shrink-0">
          <h3 class="font-bold text-lg text-white flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
            Method Details
          </h3>
          <button
            type="button"
            class="btn btn-xs btn-ghost text-slate-400 hover:text-white"
            @click="showHelp = !showHelp"
            title="Understanding Method Details"
          >
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Help
          </button>
        </div>
        
        <!-- Help Section -->
        <div v-if="showHelp" class="mt-4 bg-neutral-950 rounded-lg p-4 text-xs text-slate-300 space-y-3 shrink-0 border border-primary/20">
          <div>
            <h6 class="text-cyan-400 font-medium mb-1">Method Signature</h6>
            <p class="text-slate-400 leading-relaxed">
              The full signature shows: <span class="text-emerald-400">return type</span> + 
              <span class="text-blue-400"> class name</span> + 
              <span class="text-white"> method name</span> + 
              <span class="text-amber-400"> parameters</span>. 
              This is the exact identifier Frida uses for hooking.
            </p>
          </div>

          <div>
            <h6 class="text-cyan-400 font-medium mb-1">Category & Confidence</h6>
            <p class="text-slate-400 leading-relaxed">
              <span class="font-medium text-white">Category</span> is automatically assigned during method extraction based on method name and signature patterns. 
              <span class="font-medium text-white">Confidence</span> (high/medium/low) indicates how certain the categorization is. 
              Low confidence means you should verify the method's actual purpose through dynamic analysis. Note that categorization is pattern-based, not runtime analysis.
            </p>
          </div>

          <div>
            <h6 class="text-cyan-400 font-medium mb-1">Modifiers</h6>
            <ul class="space-y-1 text-slate-400">
              <li><span class="font-medium text-purple-400">public/private/protected:</span> Visibility scope</li>
              <li><span class="font-medium text-blue-400">static:</span> Class-level method, no instance needed</li>
              <li><span class="font-medium text-emerald-400">final:</span> Cannot be overridden</li>
              <li><span class="font-medium text-amber-400">native:</span> Implemented in C/C++, bridged via JNI</li>
              <li><span class="font-medium text-pink-400">synchronized:</span> Thread-safe, locked during execution</li>
            </ul>
          </div>

          <div>
            <h6 class="text-cyan-400 font-medium mb-1">Parameters & Return Types</h6>
            <p class="text-slate-400 leading-relaxed mb-2">
              <span class="font-medium text-white">Primitive types:</span> int, long, boolean, float, etc. (passed by value)
            </p>
            <p class="text-slate-400 leading-relaxed mb-2">
              <span class="font-medium text-white">Object types:</span> String, java.lang.Object, custom classes (passed by reference)
            </p>
            <p class="text-slate-400 leading-relaxed">
              <span class="font-medium text-white">Arrays:</span> Denoted with [] (e.g., byte[], String[])
            </p>
          </div>

          <div>
            <h6 class="text-cyan-400 font-medium mb-1">How to Use This Data</h6>
            <p class="text-slate-400 leading-relaxed mb-2">
              <span class="font-medium text-emerald-400">1.</span> Copy the signature using "Copy Info" button
            </p>
            <p class="text-slate-400 leading-relaxed mb-2">
              <span class="font-medium text-blue-400">2.</span> Create a Frida hook targeting this method
            </p>
            <p class="text-slate-400 leading-relaxed mb-2">
              <span class="font-medium text-purple-400">3.</span> Use parameter types to extract and log arguments
            </p>
            <p class="text-slate-400 leading-relaxed">
              <span class="font-medium text-amber-400">4.</span> Monitor return values to understand behavior
            </p>
          </div>

          <div class="bg-blue-500/10 border border-blue-500/30 rounded p-2">
            <p class="text-blue-300 text-xs">
              <span class="font-medium">Tip:</span> Start by hooking public methods with simple parameters. 
              Native methods often contain security-critical operations worth investigating.
            </p>
          </div>
        </div>
        
        <!-- Scrollable Content -->
        <div class="mt-4 space-y-4 overflow-y-auto flex-1 pr-2">
          <!-- Method Name -->
          <div>
            <label class="text-xs text-slate-500 uppercase tracking-wider">Method Name</label>
            <div class="mt-1 font-mono text-white bg-neutral-800 p-3 rounded-lg break-all">
              {{ method.name }}
            </div>
          </div>
          
          <!-- Parent Class -->
          <div v-if="className">
            <label class="text-xs text-slate-500 uppercase tracking-wider">Parent Class</label>
            <div class="mt-1 font-mono text-sm text-slate-300 bg-neutral-800 p-2 rounded break-all">
              {{ className }}
            </div>
          </div>
          
          <!-- Full Signature -->
          <div v-if="method.signature">
            <label class="text-xs text-slate-500 uppercase tracking-wider">Full Signature</label>
            <div class="mt-1 font-mono text-xs text-slate-300 bg-neutral-800 p-3 rounded-lg break-all whitespace-pre-wrap">
              {{ method.signature }}
            </div>
          </div>
          
          <!-- Category & Confidence -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-xs text-slate-500 uppercase tracking-wider">Category</label>
              <div class="mt-1 flex items-center gap-2">
                <CategoryBadge :category="method.method_category || 'Unknown'" />
              </div>
            </div>
            <div>
              <label class="text-xs text-slate-500 uppercase tracking-wider">Confidence</label>
              <div class="mt-1">
                <span 
                  class="badge badge-sm"
                  :class="{
                    'badge-success': method.method_confidence === 'high',
                    'badge-warning': method.method_confidence === 'medium',
                    'badge-ghost': method.method_confidence === 'low' || !method.method_confidence
                  }"
                >
                  {{ method.method_confidence || 'low' }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Categorization Reason -->
          <div v-if="method.method_category_reason">
            <label class="text-xs text-slate-500 uppercase tracking-wider">Categorization Reason</label>
            <div class="mt-1 text-sm text-slate-400 bg-neutral-800/50 p-2 rounded">
              {{ method.method_category_reason }}
            </div>
          </div>
          
          <!-- Modifiers -->
          <div>
            <label class="text-xs text-slate-500 uppercase tracking-wider">Modifiers</label>
            <div class="mt-1 flex flex-wrap gap-2">
              <span v-if="method.is_public" class="badge badge-sm bg-green-700 text-white">public</span>
              <span v-if="method.is_private" class="badge badge-sm bg-red-700 text-white">private</span>
              <span v-if="method.is_protected" class="badge badge-sm bg-yellow-700 text-white">protected</span>
              <span v-if="method.is_static" class="badge badge-sm bg-blue-700 text-white">static</span>
              <span v-if="method.is_final" class="badge badge-sm bg-purple-700 text-white">final</span>
              <span v-if="method.is_native" class="badge badge-sm bg-orange-600 text-white">native</span>
              <span v-if="method.is_synchronized" class="badge badge-sm bg-cyan-700 text-white">synchronized</span>
              <span v-if="method.is_abstract" class="badge badge-sm bg-pink-700 text-white">abstract</span>
              <span v-if="!hasModifiers" class="text-slate-500 text-sm italic">None detected (may be package-private)</span>
            </div>
          </div>
          
          <!-- Return Type -->
          <div>
            <label class="text-xs text-slate-500 uppercase tracking-wider">Return Type</label>
            <div class="mt-1 font-mono text-sm bg-neutral-800 p-2 rounded">
              <span :class="getTypeColor(method.return_type)">{{ method.return_type || 'void' }}</span>
            </div>
          </div>
          
          <!-- Parameters -->
          <div>
            <label class="text-xs text-slate-500 uppercase tracking-wider">
              Parameters ({{ parameterCount }})
            </label>
            <div class="mt-1">
              <div v-if="hasParameters" class="bg-neutral-800 rounded-lg overflow-hidden">
                <table class="table table-xs w-full">
                  <thead>
                    <tr class="border-b border-neutral-700">
                      <th class="text-slate-500 text-xs w-12">#</th>
                      <th class="text-slate-500 text-xs">Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr 
                      v-for="(param, index) in normalizedParameters" 
                      :key="index"
                      class="border-b border-neutral-700/50 last:border-0"
                    >
                      <td class="text-slate-500 font-mono">{{ index }}</td>
                      <td class="font-mono text-xs">
                        <span :class="getTypeColor(param)">{{ param }}</span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="text-slate-500 text-sm italic bg-neutral-800/50 p-2 rounded">
                No parameters (void method)
              </div>
            </div>
          </div>
          
          <!-- Raw Data (for investigation) -->
          <div>
            <button 
              type="button"
              class="text-xs text-slate-500 uppercase tracking-wider flex items-center gap-1 hover:text-slate-300 transition-colors"
              @click="showRawData = !showRawData"
            >
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                class="h-3 w-3 transition-transform"
                :class="{ 'rotate-90': showRawData }"
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              Raw Method Data
            </button>
            <div v-if="showRawData" class="mt-2 bg-neutral-950 rounded-lg p-3 font-mono text-xs text-slate-400 overflow-x-auto max-h-48 overflow-y-auto">
              <pre class="whitespace-pre-wrap">{{ JSON.stringify(method, null, 2) }}</pre>
            </div>
          </div>
        </div>
        
        <!-- Footer Actions -->
        <div class="modal-action shrink-0 border-t border-neutral-800 pt-4 mt-4">
          <button 
            class="btn btn-ghost btn-sm"
            @click="copyMethodInfo"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Copy Info
          </button>
          <button class="btn btn-ghost" @click="$emit('close')">Close</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button @click="$emit('close')">close</button>
      </form>
    </div>
  </Teleport>
</template>

<script>
import { ref, computed } from 'vue'
import CategoryBadge from '../shared/CategoryBadge.vue'

export default {
  name: 'MethodDetailModal',
  components: {
    CategoryBadge
  },
  props: {
    show: {
      type: Boolean,
      required: true
    },
    method: {
      type: Object,
      default: () => ({})
    },
    className: {
      type: String,
      default: ''
    }
  },
  emits: ['close'],
  setup(props) {
    const showRawData = ref(false)
    const showHelp = ref(false)
    
    const hasModifiers = computed(() => {
      return props.method.is_public || props.method.is_private || props.method.is_protected ||
             props.method.is_static || props.method.is_final || props.method.is_native ||
             props.method.is_synchronized || props.method.is_abstract
    })
    
    const normalizedParameters = computed(() => {
      const params = props.method.parameters
      if (!params) return []
      if (Array.isArray(params)) {
        return params.map(p => typeof p === 'string' ? p : (p.type || p.name || JSON.stringify(p)))
      }
      return []
    })
    
    const parameterCount = computed(() => normalizedParameters.value.length)
    
    const hasParameters = computed(() => parameterCount.value > 0)
    
    const getTypeColor = (type) => {
      if (!type) return 'text-slate-400'
      
      if (['int', 'long', 'short', 'byte', 'float', 'double', 'boolean', 'char', 'void'].includes(type)) {
        return 'text-blue-400'
      }
      if (type.startsWith('java.lang.String') || type === 'String') {
        return 'text-green-400'
      }
      if (type.includes('[]')) {
        return 'text-yellow-400'
      }
      if (type.startsWith('android.')) {
        return 'text-orange-400'
      }
      if (type.startsWith('java.') || type.startsWith('javax.')) {
        return 'text-cyan-400'
      }
      
      return 'text-slate-300'
    }
    
    const copyMethodInfo = () => {
      const info = [
        `Method: ${props.method.name}`,
        `Class: ${props.className}`,
        `Signature: ${props.method.signature || 'N/A'}`,
        `Return Type: ${props.method.return_type || 'void'}`,
        `Parameters: ${normalizedParameters.value.join(', ') || 'none'}`,
        `Category: ${props.method.method_category || 'Unknown'} (${props.method.method_confidence || 'low'})`,
        `Modifiers: ${getModifiersString()}`
      ].join('\n')
      
      navigator.clipboard.writeText(info)
    }
    
    const getModifiersString = () => {
      const mods = []
      if (props.method.is_public) mods.push('public')
      if (props.method.is_private) mods.push('private')
      if (props.method.is_protected) mods.push('protected')
      if (props.method.is_static) mods.push('static')
      if (props.method.is_final) mods.push('final')
      if (props.method.is_native) mods.push('native')
      if (props.method.is_synchronized) mods.push('synchronized')
      if (props.method.is_abstract) mods.push('abstract')
      return mods.length > 0 ? mods.join(', ') : 'none'
    }
    
    return {
      showRawData,
      showHelp,
      hasModifiers,
      normalizedParameters,
      parameterCount,
      hasParameters,
      getTypeColor,
      copyMethodInfo
    }
  }
}
</script>
