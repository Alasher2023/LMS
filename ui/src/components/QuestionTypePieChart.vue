<template>
  <Pie :data="chartData" :options="chartOptions" />
</template>

<script setup lang="ts">
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Pie } from 'vue-chartjs';
import { computed } from 'vue';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps<{
  pieChartData: { name: string; value: number }[]
}>();

const chartData = computed(() => ({
  labels: props.pieChartData.map(d => d.name),
  datasets: [
    {
      backgroundColor: ['#41B883', '#E46651', '#00D8FF', '#DD1B16', '#FFA500', '#800080'],
      data: props.pieChartData.map(d => d.value),
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
};
</script>
