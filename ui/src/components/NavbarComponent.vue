<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

type NavbarItem = {
  title: string
  name: string
}

const router = useRouter()
const drawerToggle = ref<HTMLInputElement | null>(null)
const navbarItems = ref<NavbarItem[]>([])

const handleRouteChange = (routeName: string) => {
  router.push({ name: routeName })
  closeSidebar()
}
const loadNavbarItems = async () => {
  const items: NavbarItem[] = []

  router.options.routes?.forEach((route) => {
    if (route.name && typeof route.name === 'string') {
      const title = route.name.charAt(0).toUpperCase() + route.name.slice(1)

      items.push({
        title: title,
        name: route.name,
      })
    }
  })

  navbarItems.value = items
}

const changeTitle = (title: string | undefined | symbol) => {
  if (typeof title === 'string') return title.charAt(0).toUpperCase() + title.slice(1)
}

const closeSidebar = () => {
  if (drawerToggle.value) {
    drawerToggle.value.checked = false
  }
}

onMounted(() => {
  loadNavbarItems()
})
</script>

<template>
  <div class="drawer mx-auto max-w-[100rem]">
    <input id="my-drawer" ref="drawerToggle" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content flex flex-col">
      <!-- Navbar -->
      <div class="navbar bg-base-300 w-full">
        <div class="flex-none lg:hidden">
          <label for="my-drawer" aria-label="open sidebar" class="btn btn-square btn-ghost">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              class="inline-block h-6 w-6 stroke-current"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              ></path>
            </svg>
          </label>
        </div>
        <div class="mx-2 flex-1 px-2">
          {{ changeTitle(router.currentRoute.value.name) }}
        </div>
        <div class="hidden flex-none lg:block">
          <ul class="menu menu-horizontal">
            <!-- Navbar menu content here -->
            <li v-for="(item, index) in navbarItems" :key="index">
              <a @click="handleRouteChange(item.name)">{{ item.title }}</a>
            </li>
          </ul>
        </div>
      </div>
      <!-- Page content here -->
      <div class="box-content md:box-border m-4">
        <slot name="PageContent"></slot>
      </div>
    </div>
    <div class="drawer-side">
      <label for="my-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
      <ul class="menu bg-base-200 min-h-full w-80 p-4">
        <!-- Sidebar content here -->
        <li v-for="(item, index) in navbarItems" :key="index">
          <a @click="handleRouteChange(item.name)">{{ item.title }}</a>
        </li>
      </ul>
    </div>
  </div>
</template>
