<template>
  <main style="font-family: system-ui; padding: 1rem; max-width: 800px; margin:auto;">
    <h1>Citizen Portal</h1>
    <section style="margin: 1rem 0;">
      <h2>Case Lookup</h2>
      <input v-model="caseId" placeholder="Case ID" />
      <button @click="loadCase">Load</button>
      <pre v-if="caseData">{{ caseData }}</pre>
    </section>
    <section style="margin: 1rem 0;">
      <h2>Eligibility</h2>
      <input v-model="pnr" placeholder="Personal number" />
      <button @click="loadEligibility">Check</button>
      <pre v-if="eligibility">{{ eligibility }}</pre>
    </section>
  </main>
</template>

<script setup>
import axios from 'axios'
import { ref } from 'vue'

const caseId = ref('123')
const pnr = ref('19121212-1212')
const caseData = ref(null)
const eligibility = ref(null)

async function loadCase() {
  caseData.value = null
  try {
    const res = await axios.get(`http://localhost:8081/api/cases/${caseId.value}`)
    caseData.value = res.data
  } catch (e) {
    caseData.value = { error: String(e) }
  }
}

async function loadEligibility() {
  eligibility.value = null
  try {
    const res = await axios.get(`http://localhost:8083/api/eligibility/${pnr.value}`)
    eligibility.value = res.data
  } catch (e) {
    eligibility.value = { error: String(e) }
  }
}
</script>

<style>
button { margin-left: .5rem }
pre { background: #f6f8fa; padding: .5rem; border-radius: 4px; }
input { padding: .3rem .5rem }
</style>
