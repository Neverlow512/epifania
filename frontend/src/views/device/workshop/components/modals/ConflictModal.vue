<template>
  <div class="modal-overlay" @click.self="$emit('cancel')">
    <div class="modal-content conflict-modal">
      <h2>Unsaved Work Detected</h2>
      
      <div class="conflict-info">
        <p class="warning-message">
          You have unsaved work in the current session.
        </p>
        
        <div class="unsaved-info">
          <div class="stat-item">
            <span class="label">Classes scanned:</span>
            <span class="value">{{ unsavedStats.scanned_count }}</span>
          </div>
          <div class="stat-item">
            <span class="label">Classes extracted:</span>
            <span class="value">{{ unsavedStats.extracted_count }}</span>
          </div>
        </div>
        
        <p class="question">
          What would you like to do before loading the saved discovery?
        </p>
      </div>
      
      <div class="modal-actions">
        <button class="btn-save" @click="$emit('save')">
          Save Current Work
        </button>
        <button class="btn-discard" @click="$emit('discard')">
          Discard & Load
        </button>
        <button class="btn-cancel" @click="$emit('cancel')">
          Cancel Load
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConflictModal',
  props: {
    unsavedStats: {
      type: Object,
      required: true,
      default: () => ({ scanned_count: 0, extracted_count: 0 })
    }
  },
  emits: ['save', 'discard', 'cancel']
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
  max-width: 450px;
  width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.conflict-modal h2 {
  margin: 0 0 20px 0;
  color: var(--color-text);
  font-size: 20px;
  font-weight: 600;
}

.conflict-info {
  margin-bottom: 24px;
}

.warning-message {
  margin: 0 0 12px 0;
  color: var(--color-warning);
  font-weight: 500;
  line-height: 1.5;
}

.unsaved-info {
  background: var(--color-background);
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.stat-item:last-child {
  margin-bottom: 0;
}

.stat-item .label {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.stat-item .value {
  color: var(--color-text);
  font-size: 14px;
  font-weight: 500;
}

.question {
  margin: 0;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-save,
.btn-discard,
.btn-cancel {
  padding: 12px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.btn-save {
  background: var(--color-primary);
  color: white;
}

.btn-save:hover {
  background: var(--color-primary-hover);
}

.btn-discard {
  background: var(--color-error);
  color: white;
}

.btn-discard:hover {
  opacity: 0.9;
}

.btn-cancel {
  background: var(--color-surface-variant);
  color: var(--color-text);
}

.btn-cancel:hover {
  background: var(--color-surface-hover);
}
</style>
