<template>
  <InstrumentationToolkit
    :selectedMethodCount="selectedMethodCount"
    :fridaAttached="fridaAttached"
    :isObserving="isObserving"
    :sessionName="sessionName"
    :timeLimit="timeLimit"
    :logPath="logPath"
    :methodSelectionEnabled="methodSelectionEnabled"
    @observer-start="$emit('observer-start')"
    @observer-stop="$emit('observer-stop')"
    @update:sessionName="$emit('update:sessionName', $event)"
    @update:timeLimit="$emit('update:timeLimit', $event)"
    @update:logPath="$emit('update:logPath', $event)"
    @toggle-method-selection="$emit('toggle-method-selection')"
    @open-dashboard="$emit('open-dashboard')"
  />
</template>

<script setup>
import InstrumentationToolkit from './toolkit/InstrumentationToolkit.vue'

defineProps({
  selectedMethodCount: {
    type: Number,
    default: 0
  },
  fridaAttached: {
    type: Boolean,
    default: false
  },
  isObserving: {
    type: Boolean,
    default: false
  },
  sessionName: {
    type: String,
    default: ''
  },
  timeLimit: {
    type: Number,
    default: null
  },
  logPath: {
    type: String,
    default: ''
  },
  methodSelectionEnabled: {
    type: Boolean,
    default: false
  }
})

defineEmits([
  'observer-start',
  'observer-stop',
  'update:sessionName',
  'update:timeLimit',
  'update:logPath',
  'toggle-method-selection',
  'open-dashboard'
])
</script>

