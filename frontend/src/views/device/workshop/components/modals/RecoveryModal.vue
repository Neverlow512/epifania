<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-content recovery-modal">
      <h2>Recover Unsaved Work</h2>
      
      <div class="recovery-info">
        <p class="info-message">
          Found incomplete work from <strong>{{ formatTime(recoveryInfo.timestamp) }}</strong>
        </p>
        
        <div class="recovery-details">
          <div class="detail-item">
            <span class="label">Total classes:</span>
            <span class="value">{{ recoveryInfo.class_count }}</span>
          </div>
          
          <div class="detail-item">
            <span class="label">Classes scanned:</span>
            <span class="value">{{ recoveryInfo.scanned_count || 0 }}</span>
          </div>
          
          <div class="detail-item">
            <span class="label">Classes extracted:</span>
            <span class="value">{{ recoveryInfo.extracted_count || 0 }}</span>
          </div>
          
          <div v-if="recoveryInfo.last_saved_to" class="detail-item">
            <span class="label">Last saved to:</span>
            <span class="value">{{ recoveryInfo.last_saved_to }}</span>
          </div>
          
          <div v-if="recoveryInfo.discovery_timestamp" class="detail-item">
            <span class="label">Discovery time:</span>
            <span class="value">{{ formatTimestamp(recoveryInfo.discovery_timestamp) }}</span>
          </div>
        </div>
      </div>
      
      <div class="modal-actions">
        <button class="btn-primary" @click="$emit('recover')">
          Recover Work
        </button>
        <button class="btn-secondary" @click="$emit('discard')">
          Start Fresh
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecoveryModal',
  props: {
    recoveryInfo: {
      type: Object,
      required: true
    }
  },
  emits: ['recover', 'discard', 'cancel'],
  methods: {
    formatTime(timestamp) {
      if (!timestamp) return 'Unknown'
      try {
        const date = new Date(timestamp.replace('_', 'T'))
        return date.toLocaleString()
      } catch {
        return timestamp
      }
    },
    formatTimestamp(isoString) {
      if (!isoString) return 'Unknown'
      try {
        const date = new Date(isoString)
        return date.toLocaleString()
      } catch {
        return isoString
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 99999; /* Do not change: keep modal above all UI */
}

.modal-content {
  background: var(--color-surface);
  border-radius: 8px;
  padding: 24px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.recovery-modal h2 {
  margin: 0 0 20px 0;
  color: var(--color-text);
  font-size: 20px;
  font-weight: 600;
}

.recovery-info {
  margin-bottom: 24px;
}

.info-message {
  margin: 0 0 16px 0;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.recovery-details {
  background: var(--color-background);
  border-radius: 6px;
  padding: 12px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-item .label {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.detail-item .value {
  color: var(--color-text);
  font-size: 14px;
  font-weight: 500;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover {
  background: var(--color-primary-hover);
}

.btn-secondary {
  background: var(--color-surface-variant);
  color: var(--color-text);
}

.btn-secondary:hover {
  background: var(--color-surface-hover);
}
</style>
