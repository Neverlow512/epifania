<template>
  <div class="dropdown dropdown-end" @click.stop>
    <label
      tabindex="0"
      class="btn btn-ghost btn-xs"
      :class="{ 'btn-disabled': actionInProgress }"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z"
        />
      </svg>
    </label>
    <ul
      tabindex="0"
      class="dropdown-content z-[1] menu p-2 shadow-lg bg-neutral-800 border border-primary/30 rounded-box w-52"
    >
      <li v-if="pkg.is_running">
        <a
          class="text-emerald-400 hover:bg-emerald-500/10"
          @click="$emit('navigate-to-process')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
          View Process
        </a>
      </li>
      <li v-if="pkg.is_running">
        <a
          class="text-amber-400 hover:bg-amber-500/10"
          @click="$emit('stop')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
          </svg>
          Force Stop
        </a>
      </li>
      <li v-else>
        <a
          class="text-emerald-400 hover:bg-emerald-500/10"
          @click="$emit('launch')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Launch
        </a>
      </li>

      <div class="divider my-1"></div>

      <li>
        <a @click="$emit('view-details')">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          View Details
        </a>
      </li>
      <li>
        <a @click="$emit('pull')">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Extract APK
        </a>
      </li>

      <div class="divider my-1"></div>

      <li>
        <a @click="$emit('clear-cache')">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Clear Cache
        </a>
      </li>
      <li>
        <a
          class="text-amber-400 hover:bg-amber-500/10"
          @click="$emit('clear-data')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Clear Data
        </a>
      </li>

      <div class="divider my-1"></div>

      <li>
        <a
          class="text-red-400 hover:bg-red-500/10"
          @click="$emit('uninstall')"
        >
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Uninstall
        </a>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'PackageActionsMenu',
  props: {
    package: {
      type: Object,
      required: true
    },
    actionInProgress: {
      type: Boolean,
      default: false
    }
  },
  emits: [
    'view-details',
    'launch',
    'stop',
    'uninstall',
    'pull',
    'clear-cache',
    'clear-data',
    'navigate-to-process'
  ],
  computed: {
    pkg() {
      return this.package
    }
  }
}
</script>

