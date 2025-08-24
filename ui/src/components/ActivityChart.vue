<template>
  <Bar :data="chartData" :options="chartOptions" />
</template>

<script setup lang="ts">
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import { Bar } from 'vue-chartjs'
import { computed } from 'vue'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const props = defineProps<{
  activityData: { date: string; count: number }[]
}>()

const chartData = computed(() => ({
  labels: props.activityData.map(d => {
    const date = new Date(d.date)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }),
  datasets: [
    {
      label: '完成数量',
      backgroundColor: '#36D399', // daisyUI success color
      borderColor: '#36D399',
      data: props.activityData.map(d => d.count),
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        stepSize: 1
      }
    }
  }
}
</script>
