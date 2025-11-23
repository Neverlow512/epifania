import { createApp } from 'vue'
import App from './App.vue'
import './style.css'
import router from './router'

// Global safeguards to avoid accidental page reloads from form submits or dummy anchors
document.addEventListener('submit', (e) => {
  e.preventDefault()
})
document.addEventListener('click', (e) => {
  const anchor = e.target && e.target.closest ? e.target.closest('a') : null
  if (anchor) {
    const href = anchor.getAttribute('href')
    if (href === '#' || href === '') {
      e.preventDefault()
    }
  }
})

// Normalize button types across the app to prevent implicit submits
const neutralizeButtons = () => {
  try {
    document.querySelectorAll('button').forEach((btn) => {
      const typeAttr = btn.getAttribute('type')
      if (typeAttr === null || typeAttr.toLowerCase() === 'submit') {
        btn.setAttribute('type', 'button')
      }
    })
  } catch {}
}
neutralizeButtons()
const mo = new MutationObserver(() => neutralizeButtons())
mo.observe(document.documentElement, { childList: true, subtree: true })

createApp(App).use(router).mount('#app')

