<template>
  <div class="toast-container">
    <!-- Regular toasts (success, info, warning) -->
    <transition-group name="toast" tag="div">
      <div
        v-for="toast in regularToasts"
        :key="toast.id"
        class="toast-item"
        :class="getToastClass(toast.type)"
      >
        <div class="toast-content">
          <div class="toast-icon">
            <svg v-if="toast.type === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else-if="toast.type === 'warning'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>

          <div class="toast-message">
            <div v-if="toast.title" class="toast-title">{{ toast.title }}</div>
            <div class="toast-text">{{ toast.message }}</div>
          </div>

          <div class="toast-actions">
            <button
              v-if="!toast.pinned"
              type="button"
              class="toast-pin-btn"
              @click="pinToast(toast.id)"
              title="Pin notification"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>
            <button
              v-else
              type="button"
              class="toast-pin-btn pinned"
              @click="unpinToast(toast.id)"
              title="Unpin notification"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>
            <button
              type="button"
              class="toast-close-btn"
              @click="removeToast(toast.id)"
              title="Close"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div v-if="!toast.pinned" class="toast-progress">
          <div
            class="toast-progress-bar"
            :style="{ animationDuration: toast.duration + 'ms' }"
          ></div>
        </div>
      </div>
    </transition-group>

    <!-- Aggregated error toasts -->
    <transition-group name="toast" tag="div">
      <div
        v-for="toast in errorToasts"
        :key="'error-' + toast.id"
        class="toast-aggregate"
      >
        <button
          type="button"
          class="toast-bubble toast-error"
          @click="toggleExpanded(toast.id)"
        >
          <span class="toast-bubble-icon">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
          <span class="toast-bubble-count">
            {{ toast.count }}
          </span>
        </button>

        <transition name="toast-panel">
          <div
            v-if="toast.expanded"
            class="toast-panel toast-error"
          >
            <div class="toast-panel-content">
              <div class="toast-panel-text">
                <div v-if="toast.title" class="toast-title">
                  {{ toast.title }}
                </div>
                <div class="toast-text">
                  {{ toast.message }}
                </div>
              </div>
              <button
                type="button"
                class="toast-close-btn"
                @click="removeToast(toast.id)"
                title="Close"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </transition>
      </div>
    </transition-group>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useToast } from '../composables/useToast'

export default {
  name: 'ToastNotification',
  setup() {
    const { toasts, removeToast, pinToast, unpinToast } = useToast()

    const regularToasts = computed(() =>
      toasts.value.filter(t => t.type !== 'error')
    )

    const errorToasts = computed(() =>
      toasts.value.filter(t => t.type === 'error')
    )

    const getToastClass = (type) => {
      const classes = {
        success: 'toast-success',
        error: 'toast-error',
        warning: 'toast-warning',
        info: 'toast-info'
      }
      return classes[type] || 'toast-info'
    }

    const toggleExpanded = (id) => {
      const toast = errorToasts.value.find(t => t.id === id)
      if (toast) {
        toast.expanded = !toast.expanded
      }
    }

    return {
      regularToasts,
      errorToasts,
      removeToast,
      pinToast,
      unpinToast,
      getToastClass,
      toggleExpanded
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  pointer-events: none;
}

.toast-item {
  pointer-events: auto;
  background: rgba(23, 23, 23, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 0.75rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
  overflow: hidden;
  min-width: 300px;
  max-width: 400px;
}

.toast-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
}

.toast-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-message {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
  color: #fff;
}

.toast-text {
  font-size: 0.875rem;
  color: rgba(255, 255, 255, 0.9);
  word-wrap: break-word;
}

.toast-actions {
  flex-shrink: 0;
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.toast-pin-btn,
.toast-close-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-pin-btn:hover,
.toast-close-btn:hover {
  color: rgba(255, 255, 255, 0.9);
  background: rgba(255, 255, 255, 0.1);
}

.toast-pin-btn.pinned {
  color: #fbbf24;
}

.toast-progress {
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.toast-progress-bar {
  height: 100%;
  width: 100%;
  background: currentColor;
  transform-origin: left;
  animation: toast-progress linear forwards;
}

@keyframes toast-progress {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

.toast-success {
  border-left: 4px solid #10b981;
}

.toast-success .toast-icon {
  color: #10b981;
}

.toast-success .toast-progress-bar {
  background: #10b981;
}

.toast-warning {
  border-left: 4px solid #f59e0b;
}

.toast-warning .toast-icon {
  color: #f59e0b;
}

.toast-warning .toast-progress-bar {
  background: #f59e0b;
}

.toast-info {
  border-left: 4px solid #3b82f6;
}

.toast-info .toast-icon {
  color: #3b82f6;
}

.toast-info .toast-progress-bar {
  background: #3b82f6;
}

.toast-aggregate {
  pointer-events: auto;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.25rem;
}

.toast-bubble {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  border-width: 2px;
  border-style: solid;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  cursor: pointer;
  padding: 0;
  gap: 0.25rem;
}

.toast-bubble-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: inherit;
}

.toast-bubble-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: inherit;
}

.toast-panel {
  background: rgba(17, 24, 39, 0.98);
  backdrop-filter: blur(12px);
  border-radius: 0.5rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.08);
  min-width: 260px;
  max-width: 360px;
}

.toast-panel-content {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem 0.9rem;
}

.toast-panel-text {
  flex: 1;
  min-width: 0;
}

.toast-error {
  border-left: 4px solid #ef4444;
  color: #ef4444;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.2s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.toast-panel-enter-active,
.toast-panel-leave-active {
  transition: all 0.15s ease;
}

.toast-panel-enter-from {
  opacity: 0;
  transform: translateY(6px);
}

.toast-panel-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
</style>

